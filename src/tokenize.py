from src.constants import NUM, OPER, EOF

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

def tokenize(expr) -> list:
    ''' Creates a list of Token() objects out of str expression
        or throws exceptions if the expression format is bad'''
    tokens = []
    i = 0
    prev = ''
    n = len(expr)
    digit_buffer = ''
    got_dot = False

    def add_number():
        nonlocal digit_buffer, got_dot, tokens
        if digit_buffer != '':
            if digit_buffer[0] == '.' or digit_buffer[-1] == '.':
                raise Exception("Bad expression")
            tokens.append(Token(NUM, float(digit_buffer)))
            if '.' in digit_buffer:
                got_dot = False
            digit_buffer = ''

    while i < n:
        cur = expr[i]
        if cur == ' ':
            add_number()
        elif cur in '+-':
            if prev in '+-*/' or prev == '':
                if digit_buffer == '':
                    digit_buffer += cur
                else:
                    raise Exception("Bad expression")
            elif prev.isdigit():
                add_number()
                tokens.append(Token(OPER, cur))
        elif cur in '*/':
            if prev in '+-*/' or prev == '':
                raise Exception("Bad expression")
            else:
                add_number()
                tokens.append(Token(OPER, cur))
        elif cur.isdigit():
            digit_buffer += cur
        elif cur == '.':
            if got_dot:
                raise Exception("Bad expression")
            else:
                got_dot = True
                digit_buffer += '.'
        else:
            raise Exception("Unknown types")
        i += 1
        prev = cur
    add_number()
    if tokens == []:
        raise Exception("Empty expression")
    elif prev in '*/+-':
        raise Exception("Bad expression")
    tokens.append(Token(EOF))
    return tokens
expr = '-0+-2.254-3*4.58'
for token in tokenize(expr):
    print(token.type, token.value)
