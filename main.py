from tokenizer import Lexeme, tokenize_file
from ast import AST
from etc import LookaheadStream

symbols = [',', '=', '==', '!', '!=']#'!', '=', '==', '!=', '+', '-', ',']
keywords = ['if', 'elif', 'else', 'pass', 'def', 'return']#'and', 'or']

def parse_identifier(stream):
    lexeme = stream.advance('word')
    return AST('ident', string=lexeme.string)

def parse_argv(stream):
    argv = AST('argv', [])
    stream.advance('lparen')
    stream.ignore('newline')
    while not stream.is_category('rparen'):
        argv.append(parse_identifier(stream))
        stream.ignore('symbol', string=',')
        stream.ignore('newline')
    stream.advance('rparen')
    return argv

def parse_call(stream, callee):
    call = AST('call', [callee])
    stream.advance('lparen')
    stream.ignore('newline')
    while not stream.is_category('rparen'):
        call.append(parse_expression(stream))
        stream.ignore('symbol', string=',')
        stream.ignore('newline')
    stream.advance('rparen')
    return call

def parse_expression(stream):
    current = stream.advance()
    expr = AST(current.type, string=current.string)
    while stream.can_advance('lparen'):
        expr = parse_call(stream, expr)
    while stream.can_advance('symbol', string='=='):
        stream.advance()
        rhs = parse_expression(stream)
        expr = AST('eq', [expr, rhs])
    return expr

def has_sub_block(stream, indent):
    return stream.ahead.number > indent
    
def parse_sub_block(stream, indent):
    assert stream.ahead.number > indent
    block = parse_block(stream, stream.ahead.number)
    if stream.ahead.number > indent:
        raise Exception("indentation mismatch")
    return block

def parse_block(stream, indent):
    block = AST('block', [])
    while stream.can_advance('newline', number=indent):
        stream.advance('newline', number=indent)
        if stream.ignore('keyword', string='pass'):
            pass
        elif stream.ignore('keyword', string='def'):
            stmt = AST('def', [])
            if stream.can_advance('word'):
                stmt.string = stream.advance('word').string
            stmt.append(parse_argv(stream))
            stmt.extend(parse_sub_block(stream, indent))
            block.append(stmt)
        elif stream.ignore('keyword', string='return'):
            stmt = AST('return', [])
            stmt.append(parse_expression(stream))
            block.append(stmt)
        elif stream.ignore('keyword', string='if'):
            stmt = AST('if', [])
            stmt.append(parse_expression(stream))
            stmt.append(parse_sub_block(stream, indent))
            block.append(stmt)
        elif stream.ignore('keyword', string='elif'):
            stmt = AST('elif', [])
            stmt.append(parse_expression(stream))
            stmt.append(parse_sub_block(stream, indent))
            block.append(stmt)
        elif stream.ignore('keyword', string='else'):
            stmt = AST('else', [])
            stmt.append(parse_sub_block(stream, indent))
            block.append(stmt)
        else:
            expr = parse_expression(stream)
            if has_sub_block(stream, indent):
                expr = AST('call', [expr])
                expr.extend(parse_sub_block(stream, indent))
            block.append(expr)
    return block

if __name__=='__main__':
    path = 'input'
    stream = LookaheadStream(tokenize_file(path, symbols, keywords), Lexeme('eof'))
    root = parse_block(stream, 0)
    print root.repr()
    if not stream.can_advance('eof'):
        raise Exception("parsing halts")


#    for lexeme in 
#        print lexeme.repr()
