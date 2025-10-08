from src.calculator_M1 import Calculator

def main() -> None:
    calc = Calculator()
    while True:
        expr = str(input('Write your expression: '))
        if expr.lower() in ['stop', 'end', 'finish', 'done', 'q']:
            break
        else:
            try:
                print(calc.evaluate(expr))
            except Exception as e:
                print(f"{'\033[91m'}{'\033[1m'}Error: {'\033[0m'}{'\033[91m'}{e}{'\033[0m'}")
if __name__ == "__main__":
    main()
