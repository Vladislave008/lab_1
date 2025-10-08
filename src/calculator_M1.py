import warnings
from src.constants import NUM, OPER, BRACE


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value


class Calculator():

    def __init__(self):
        self.ind: int = 0 # global index of the current token which is being processed is stored there
        self.tokens: list[Token] = [] # the original expression converted in a list of tokens is stored there
        warnings.simplefilter('always')

    def tokenize(self, expr: str) -> list[Token]:
        ''' Creates a list of Token objects out of given string
            Args:
                expr: string expression
            Returns:
                list[Token]: a list of Token objects extracted from the given expression
            Might throw:
                SyntaxError: when the given expression format is invalid '''
        i = 0
        self.tokens = []
        tokens = [] # local list for this function, is copied to self.tokens only if tokenization finishes without errors
        digit_buffer: str = '' # string used to collect digits and dots of a number
        dot_count = 0
        n = len(expr)
        while i < n:
            cur = expr[i]
            if cur == ' ' or cur == '\t':
                pass
            elif cur in ['+', '-', '*', '/', '%']:
                if cur == '*' and i+1 < n and expr[i+1] == '*':
                    tokens.append(Token(OPER, '**'))
                    i += 1
                elif cur == '/' and i+1 < n and expr[i+1] == '/':
                    tokens.append(Token(OPER, '//'))
                    i += 1
                else:
                    tokens.append(Token(OPER, cur))
            elif cur in ['(', ')']:
                tokens.append(Token(BRACE, cur))
            elif cur.isdigit() or cur == '.':
                digit_buffer = ''
                dot_count = 0
                while i < n and (expr[i].isdigit() or expr[i] == '.'):
                    digit_buffer += expr[i]
                    if expr[i] == '.':
                        dot_count += 1
                    if dot_count > 1:
                        raise SyntaxError('Too many dots in float')
                    i+=1
                i-=1
                if digit_buffer == '.':
                    raise SyntaxError('Bad input format')
                elif digit_buffer.startswith('.'):
                    digit_buffer = '0' + digit_buffer
                elif digit_buffer.endswith('.'):
                    digit_buffer += '0'
                if '.' in digit_buffer:
                    tokens.append(Token(NUM, float(digit_buffer)))
                else:
                    tokens.append(Token(NUM, int(digit_buffer)))
            else:
                raise SyntaxError('Unknown char in expression')
            i += 1
        if tokens == []:
            raise SyntaxError('Empty expression')
        self.tokens = tokens[:]
        return tokens

    @staticmethod
    def colored_warning(message, category, filename, lineno, file=None, line=None):
        ''' Colors warnings in console output '''
        reset = '\033[0m'
        bold = '\033[1m'
        orange = '\033[38;5;208m'
        print(f'{orange}{bold}{category.__name__}{reset}{orange}: {message}{reset}')
    warnings.showwarning = colored_warning

    def tokens_correct(self):
        ''' Raises warning or SyntaxError if current list of tokens contains mistakes '''
        show_warn: bool = False # used to store information about the need of a warning
        for i in range(1, len(self.tokens)):
            if (self.tokens[i].type == NUM and self.tokens[i-1].type == NUM) or (self.tokens[i].value == '(' and self.tokens[i-1].value == ')') or \
            (self.tokens[i].value == '(' and self.tokens[i-1].type == NUM) or (self.tokens[i].type == NUM and self.tokens[i-1].value == ')'):
                raise SyntaxError('No operator between expressions')
            elif (self.tokens[i].type == OPER and self.tokens[i-1].type == OPER):
                right = self.tokens[i].value
                left = self.tokens[i-1].value
                if (left in ['+', '-'] and right in ['/', '//', '*', '**', '%']) or (left in ['/', '//', '*', '**', '%'] and right in ['/', '//', '*', '**', '%']):
                    raise SyntaxError('A few operators in a row')
                show_warn = True
        if show_warn:
            warnings.warn('A few operators in a row')

    def evaluate(self, expr: str) -> int | float | complex: # complex example: '(-1)**0.5' = (6.123233995736766e-17+1j)
        ''' Main function which returns the result of the given expression
            Args:
                expr: string expression
            Returns:
                Result of the expression (possible types: int/float/complex)
            Might throw:
                SyntaxError: if the given expression format is invalid '''
        try:
            self.tokens = []
            self.ind = 0
            self.tokenize(expr)
            self.tokens_correct()
            if expr.count('(') != expr.count(')'):
                raise SyntaxError("Braces don't match")
            result = self.expr()
            if type(result) is float:
                result = round(result, 2)
            return result
        except Exception:
            self.ind = 0
            self.tokens = []
            raise

    def primary(self) -> float | int | complex:
        ''' Processes lower-level parts of exression (Extracts NUM token value or expression in braces value)
            Returns:
                Value of the current lower-level part of the expression
            Might throw:
                SyntaxError: if the given expression format is invalid '''
        if self.ind < len(self.tokens) and self.tokens[self.ind].type == NUM:
            token = self.tokens[self.ind]
            self.ind += 1
            return token.value
        elif self.ind < len(self.tokens) and self.tokens[self.ind].value == '(':
            self.ind += 1 # skip the opening brace
            res = self.expr() # inside of braces must be a full expression
            if self.ind >= len(self.tokens) or self.tokens[self.ind].value != ')': # brace must be closed
                raise SyntaxError("Braces don't match")
            self.ind += 1 # skip the closing brace
            return res
        else:
            raise SyntaxError('Bad input format') # expression must start with NUM Token or '(' Token

    def unary(self) -> float | int | complex:
        ''' Processes unary signs for lower-level parts of the expression
            Returns:
                Value of the current lower-level part of expression multiplicated by its unary sign (or a few of them, if they are in a row) '''
        if self.ind < len(self.tokens) and self.tokens[self.ind].value in ['+', '-']:
            token = self.tokens[self.ind]
            self.ind += 1
            res = self.pow() # if there is a pow, we need to do the pow first, then change the sign (example: -2**2 = -4)
            if token.value == '+':
                return +res
            else:
                return -res
        return self.primary() # if there is no leading sign then it's just a primary() expression

    def pow(self) -> float | int | complex:
        ''' Processes exponentation operations
            Returns:
                Value of the current exponentation operation (or a few exponentation operations, if they are in a row)
            Might throw:
                ValueError: if the right-hand operand of the current exponentation operation is bigger than 10**5 '''
        res = self.unary()
        if self.ind < len(self.tokens) and self.tokens[self.ind].value == '**':
            self.ind += 1
            rvalue = self.pow() # priority for right-hand pows
            if isinstance(rvalue, (int, float)) and rvalue > 10**5:
                raise ValueError('Too big operand for pow')
            return res ** rvalue # returns the result of pow operation if got '**'
        return res # returns unary() if no '**' found

    def mul(self) -> float | int | complex:
        ''' Processes multiplicative operations
            Returns:
                Value of the current multiplicative operation (or a few multiplicative operations, if they are in a row)
            Might throw:
                ZeroDivisionError: if a division by zero appears
                ValueError: if a mod/floor division with a float/complex operand appears '''
        res = self.pow()
        while self.ind < len(self.tokens) and self.tokens[self.ind].value in ['*','/','//','%','**']:
            operator = self.tokens[self.ind]
            self.ind += 1
            rvalue = self.pow()
            if operator.value == '*':
                res *= rvalue
            elif operator.value == '/':
                if rvalue == 0:
                    raise ZeroDivisionError('Division by zero')
                res /= rvalue
            elif operator.value == '//':
                if isinstance(rvalue, complex) or isinstance(res,complex):
                    raise ValueError('Unable to perform some operations with complex-typed values')
                if rvalue == 0:
                    raise ZeroDivisionError('Division by zero')
                elif rvalue % 1 != 0 or res % 1 != 0:
                    raise ValueError('Floor division with float appeared')
                res = int(res) // int(rvalue)
            elif operator.value == '%':
                if isinstance(rvalue, complex) or isinstance(res,complex):
                    raise ValueError('Unable to perform some operations with complex-typed values')
                if rvalue == 0:
                    raise ZeroDivisionError('Division by zero')
                elif rvalue % 1 != 0 or res % 1 != 0:
                    raise ValueError('Mod operation with float appeared')
                res = int(res) % int(rvalue)
        return res

    def add(self) -> float | int | complex:
        ''' Processes sums
            Returns:
                Value of the current sum (or a few sums, if they are in a row) '''
        res = self.mul()
        while self.ind < len(self.tokens) and self.tokens[self.ind].value in ['+', '-']:
            operator = self.tokens[self.ind]
            self.ind += 1
            rvalue = self.mul()
            if operator.value == '+':
                res += rvalue
            else:
                res -= rvalue
        return res

    def expr(self) -> float | int | complex:
        ''' Starts evaluating '''
        return self.add()
