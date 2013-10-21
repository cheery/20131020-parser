class LookaheadStream(object):
    def __init__(self, lexemes, eof):
        self.lexemes = lexemes
        self.index = 0
        self.length = len(lexemes)
        self.eof = eof

    @property
    def ahead(self):
        if self.index < self.length:
            return self.lexemes[self.index]
        return self.eof

    def is_category(self, *types):
        return self.ahead.type in types

    def ignore(self, type=None, string=None, number=None):
        if self.can_advance(type, string, number):
            self.advance()
            return True

    def can_advance(self, type=None, string=None, number=None):
        current = self.ahead
        if type is not None and current.type != type:
            return False
        if string is not None and current.string != string:
            return False
        if number is not None and current.number != number:
            return False
        return True

    def advance(self, type=None, string=None, number=None):
        current = self.ahead
        if type is not None:
            assert current.type == type
        if number is not None:
            assert current.number == number
        self.index += 1
        return current
