class Lexeme(object):
    def __init__(self, type, string='', number=0):
        self.type = type
        self.string = string
        self.number = number
        self.start  = -1
        self.stop   = -1
        self.path   = None

    def repr(self):
        return "[%i:%i]@%s %s: %r %i" % (self.start, self.stop, self.path, self.type, self.string, self.number)

class Tokenizer(object):
    string = ''
    number = 0

    @property
    def lexeme(self):
        return Lexeme(self.type, self.string, self.number)

class Comment(Tokenizer):
    def __init__(self, block, string):
        self.block = block
        self.string = string

    def character(self, ch):
        if ch == '\n':
            return Newline(self.block, self.string)
        self.string += ch
        return self

    def pull(self):
        return self.block.pull()

class Newline(Tokenizer):
    type = 'newline'
    def __init__(self, block, string):
        self.block = block
        self.string = string

    def character(self, ch):
        if ch == '\n':
            self.string += ch
            self.number = 0
            return self
        if ch == '#':
            self.string += ch
            return Comment(self.block, self.string)
        if ch == ' ':
            self.string += ch
            self.number += 1
            return self
        return self.block.append(self).character(ch)

    def pull(self):
        return self.block.pull()

class Word(Tokenizer):
    type = 'word'
    def __init__(self, block, string):
        self.block = block
        self.string = string

    def character(self, ch):
        if ch.isalnum() or ch == '_':
            self.string += ch
            return self
        return self.block.append(self).character(ch)

    def pull(self):
        return self.block.append(self).pull()

class String(Tokenizer):
    type = 'string'
    def __init__(self, block, string):
        self.block = block
        self.string = string
        self.terminator = string[-1]
        self.escape = False

    def character(self, ch):
        if self.escape:
            self.escape = False
            self.string += ch
            return self
        if ch == self.terminator:
            self.string += ch
            return self.block.append(self)
        if ch == '\\':
            self.escape = True
        self.string += ch
        return self

    def pull(self):
        raise Exception("missing %r" % self.terminator)

class Symbol(Tokenizer):
    type = 'symbol'
    def __init__(self, block, string):
        self.block = block
        self.string = string

    def character(self, ch):
        symbol = self.string + ch
        if symbol in self.block.symbols:
            self.string = symbol
            return self
        return self.block.append(self).character(ch)

    def pull(self):
        return self.block.append(self).pull()

class Number(Tokenizer):
    type = 'number'
    def __init__(self, block, string):
        self.block = block
        self.string = string

    def character(self, ch):
        if self.string.startswith('0x'):
            if ch in 'abcdefABCDEF':
                self.string += ch
                return self
        elif ch == '.':
            self.string += ch
            return self
        if ch.isdigit():
            self.string += ch
            return self
        return self.block.append(self).character(ch)

    def pull(self):
        return self.block.append(self).pull()

class Sign(Tokenizer):
    def __init__(self, block, string):
        self.block = block
        self.string = string

    def character(self, ch):
        if (ch == '"' or ch == "'"):
            return String(self.block, self.string + ch)
        return self.block.character(self.string, True).character(ch)

    def pull(self):
        return self.block.character(self.string, True).pull()

class Member(Tokenizer):
    def __init__(self, block, string):
        self.block = block
        self.string = string

    def character(self, ch):
        if ch.isalpha():
            word = Word(self.block, ch)
            word.type = 'member'
            return word
        if ch.isdigit():
            return Number(self.block, self.string + ch)
        return self.block.character(self.string, True).character(ch)

    def pull(self):
        return self.block.character(self.string, True).pull()

class Idle(Tokenizer):
    type = 'block'
    def __init__(self, path, symbols, keywords):
        self.lexemes = []
        self.path = path
        self.symbols = symbols
        self.keywords = keywords
        self.start = 0
        self.stop  = 0

    def character(self, ch, suppressSign=False):
        self.start = self.stop
        if (ch == 'r' or ch == 'b') and not suppressSign:
            return Sign(self, ch)
        if ch.isalpha() or ch == '_':
            return Word(self, ch)
        if ch.isdigit():
            return Number(self, ch)
        if ch == '.':
            return Member(self, '')
        if ch == '"' or ch == "'":
            return String(self, ch)
        if ch == ' ':
            return self
        if ch == '\n':
            return Newline(self, '\n')
        if ch == '#':
            return Comment(self)
        if ch == '(':
            self.append(Lexeme('lparen', ch))
            return self
        if ch == ')':
            self.append(Lexeme('rparen', ch))
            return self
        if ch == '[':
            self.append(Lexeme('lbrace', ch))
            return self
        if ch == ']':
            self.append(Lexeme('rbrace', ch))
            return self
        if ch == '{':
            self.append(Lexeme('lbracket', ch))
            return self
        if ch == '}':
            self.append(Lexeme('rbracket', ch))
            return self
        if ch in self.symbols:
            return Symbol(self, ch)
        raise Exception("bad character %r" % ch)

    def append(self, obj):
        lexeme = obj.lexeme if isinstance(obj, Tokenizer) else obj
        if lexeme.type == 'word' and lexeme.string in self.keywords:
            lexeme.type = 'keyword'
        lexeme.start = self.start
        lexeme.stop  = self.stop
        lexeme.path  = self.path
        self.start = self.stop
        self.lexemes.append(lexeme)
        return self

    def pull(self):
        return self.lexemes
    
def tokenize(source, path, symbols, keywords):
    idle = Idle(path, symbols, keywords)
    tokenizer = Newline(idle, '')
    for index, ch in enumerate(source):
        idle.stop = index
        tokenizer = tokenizer.character(ch)
    idle.stop = len(source)
    return tokenizer.pull()

def tokenize_file(path, symbols, keywords):
    with open(path) as fd:
        source = fd.read()
    return tokenize(source, path, symbols, keywords)

if __name__=='__main__':
    path = 'input'
    with open(path) as fd:
        source = fd.read()
    symbols = ['!', '=', '==', '!=', '+', '-', ',']
    keywords = ['and', 'or']
    for lexeme in tokenize(source, path, symbols, keywords):
        print lexeme.repr()
