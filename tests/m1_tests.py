import sys
import os
import pytest # type: ignore
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.calculator_M1 import Calculator # type: ignore

def test_unary_operators_priority():
    ''' Тест приоритета унарных операторов над другими операциями '''
    calc = Calculator()
    assert calc.evaluate('-2**2') == -4
    assert calc.evaluate('+3*4') == 12
    assert calc.evaluate('-5+10') == 5
    assert calc.evaluate('-.5+10') == 9.5

def test_exponentiation():
    ''' Тест правоассоциативности возведения в степень '''
    calc = Calculator()
    assert calc.evaluate('2**3**2') == 512
    assert calc.evaluate('4**1**2') == 4
    assert calc.evaluate('2**2**3') == 256

def test_multiplication_and_division_priority():
    ''' Тест приоритета умножения и деления над сложением и вычитанием '''
    calc = Calculator()
    assert calc.evaluate('2+3*4') == 14
    assert calc.evaluate('10-8/   2') == 6
    assert calc.evaluate('5*2+3') == 13
    assert calc.evaluate('12  /3-1') == 3
    assert calc.evaluate('4+6*2-10/5') == 14

def test_braces_priority():
    ''' Тест изменения приоритета операций при помощи скобок '''
    calc = Calculator()
    assert calc.evaluate('(2+3)*4') == 20
    assert calc.evaluate('2*(3+4)') == 14
    assert calc.evaluate('(10-3)*(2+1)') == 21
    assert calc.evaluate('(2**3)**2') == 64
    assert calc.evaluate('2**(3*2)') == 64

def test_mod_and_integer_division():
    ''' Тест целочисленного деления и взятия остатка '''
    calc = Calculator()
    assert calc.evaluate('10//3.') == 3
    assert calc.evaluate('17%5.0') == 2
    assert calc.evaluate('10//3*2') == 6
    assert calc.evaluate('15%4+2') == 5
    assert calc.evaluate('(10+6.)//(3+2)') == 3

def test_complex_expressions():
    ''' Тест сложных выражений '''
    calc = Calculator()
    assert calc.evaluate('2.**3*4+15//2-10%3') == 38
    assert calc.evaluate('(5+3)*2**2//4-1') == 7
    assert calc.evaluate('10%3*4/2+5//2') == 4
    assert calc.evaluate('2.5**2+3.14/2-1') == 6.82

def test_nested_expressions():
    ''' Тест выражений со вложенными скобками '''
    calc = Calculator()
    assert calc.evaluate('((2+3)*4)-1') == 19
    assert calc.evaluate('(3*(4-1))**2') == 81
    assert calc.evaluate('((10-3)*2)**(4//2)') == 196
    assert calc.evaluate('(2+(3*(4-1)))//2') == 5

def test_error_cases():
    ''' Тест обработки ошибок '''
    calc = Calculator()
    with pytest.raises(SyntaxError, match = 'Bad input format'):
        calc.evaluate('4-6*()')
    with pytest.raises(SyntaxError, match = 'Bad input format'):
        calc.evaluate('()')
    with pytest.raises(SyntaxError, match = 'Bad input format'):
        calc.evaluate('4+5*7-')
    with pytest.raises(SyntaxError, match = 'Bad input format'):
        calc.evaluate('6 + 8*(9+)')
    with pytest.raises(SyntaxError, match = 'Empty expression'):
        calc.evaluate('                 ')
    with pytest.raises(SyntaxError, match = 'No operator between expressions'):
        calc.evaluate('6  7 + (0 -2)')
    with pytest.raises(SyntaxError, match = 'No operator between expressions'):
        calc.evaluate('5/(1+4)(3)')
    with pytest.raises(SyntaxError, match = 'No operator between expressions'):
        calc.evaluate('4(0 -2)')
    with pytest.raises(SyntaxError, match = 'No operator between expressions'):
        calc.evaluate('(0   -2)4 -  5')
    with pytest.raises(SyntaxError, match = 'No operator between expressions'):
        calc.evaluate('0.    5') # интерпретируется токенизатором как 0.0 5
    with pytest.raises(SyntaxError, match = "Braces don't match"):
        calc.evaluate('(0 -2')
    with pytest.raises(SyntaxError, match = 'A few operators in a row'):
        calc.evaluate('2+*3')
    with pytest.raises(SyntaxError, match = 'Too many dots in float'):
        calc.evaluate('2.0.1+*3')
    with pytest.raises(ZeroDivisionError):
        calc.evaluate('10/0')
    with pytest.raises(ZeroDivisionError):
        calc.evaluate('5//0')
    with pytest.raises(ZeroDivisionError):
        calc.evaluate('10%0')
    with pytest.raises(ValueError, match = 'Mod operation with float'):
        calc.evaluate('(2.5+1.5)%(1.0+0.2)')
    with pytest.raises(ValueError, match = 'Floor division with float'):
        calc.evaluate('(2//4.3)')
    with pytest.raises(ValueError, match='Too big operand for pow'):
        calc.evaluate('2**10**6')
    with pytest.raises(ValueError, match='Unable to perform some operations with complex-typed values'):
        calc.evaluate('((-1)**0.5)//2')


def test_warning_cases():
    '''Тест ситуаций с появлением предупреждений'''
    calc = Calculator()
    with pytest.warns(UserWarning, match='A few operators in a row'):
        result = calc.evaluate('2*-+-(3--4)')
        assert result == 14
