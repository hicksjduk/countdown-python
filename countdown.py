from types import SimpleNamespace
import logging
logging.basicConfig(level=logging.INFO)
from time import monotonic

priority = SimpleNamespace(low=0, high=1, atomic=2)

operator = SimpleNamespace(
    add=SimpleNamespace(symbol="+", priority=priority.low, evaluator=lambda a, b: a + b, commutative=True),
    subtract=SimpleNamespace(symbol="-", priority=priority.low, evaluator=lambda a, b: a - b, commutative=False),
    multiply=SimpleNamespace(symbol="*", priority=priority.high, evaluator=lambda a, b: a * b, commutative=True),
    divide=SimpleNamespace(symbol="/", priority=priority.high, evaluator=lambda a, b: int(a / b), commutative=False),
)

class Expression:
    def __init__(self, value, priority, string, numbers):
        self.value = value
        self.priority = priority
        self.string = string
        self.numbers = numbers

    def __str__(self):
        return f'{self.string()} = {self.value}'

def number_expression(number):
    def to_string():
        return f'{number}'
    return Expression(value=number, priority=priority.atomic, string=to_string, numbers=[number])

def arithmetic_expression(left_operand, operator, right_operand):
    def to_string():
        return format_expr(left_operand, operator, right_operand)
    return Expression(value=operator.evaluator(left_operand.value, right_operand.value), priority=operator.priority,
                      string=to_string, numbers=[*left_operand.numbers, *right_operand.numbers])

def format_expr(leftOperand, operator, rightOperand):
    elements = [
        format_operand(leftOperand, leftOperand.priority < operator.priority),
        operator.symbol,
        format_operand(rightOperand, rightOperand.priority < operator.priority or
                       (rightOperand.priority == operator.priority and not operator.commutative))
    ]
    return " ".join(elements)

def format_operand(operand, parenthesesNeeded):
    return f'({operand.string()})' if parenthesesNeeded else operand.string()

def add_combiner(a):
    def combiner(b):
        return arithmetic_expression(a, operator.add, b)
    return combiner

def subtract_combiner(a):
    if a.value < 3:
        return None
    def combiner(b):
        if a.value <= b.value or a.value == b.value * 2:
            return None
        return arithmetic_expression(a, operator.subtract, b)
    return combiner

def multiply_combiner(a):
    if a.value == 1:
        return None
    def combiner(b):
        if b.value == 1:
            return None
        return arithmetic_expression(a, operator.multiply, b)
    return combiner

def divide_combiner(a):
    if a.value == 1:
        return None
    def combiner(b):
        if b.value == 1 or a.value % b.value or a.value == b.value ** 2:
            return None
        return arithmetic_expression(a, operator.divide, b)
    return combiner

combiner_creators = [add_combiner, subtract_combiner, multiply_combiner, divide_combiner]

def combiners_using(expr):
    return (c for c in (cc(expr) for cc in combiner_creators) if c)

def permute(expressions):
    if len(expressions) == 1:
        yield expressions
    elif expressions:
        used = used_checker(lambda e: e.value)
        for i in range(len(expressions)):
            value = expressions[i]
            if not used(value):
                yield [value]
                others = [*expressions[0:i], *expressions[i+1:]]
                for p in permute(others):
                    yield [value, *p]

def used_checker(idGenerator):
    usedValues = set()
    def used(value):
        id = idGenerator(value)
        if id in usedValues:
            return True
        usedValues.add(id)
        return False
    return used

def expressions(permutation):
    if len(permutation) == 1:
        yield permutation[0]
    elif permutation:
        used = used_checker(lambda e: e.value)
        for i in range(1, len(permutation)):
            for left in expressions(permutation[:i]):
                combiners = combiners_using(left)
                for right in expressions(permutation[i:]):
                    for combine in combiners:
                        expr = combine(right)
                        if expr and not used(expr):
                            yield expr

def better_checker(target):
    def better(expr1, expr2):
        diff1, diff2 = (11 if not e else abs(target - e.value) for e in (expr1, expr2))
        if diff1 > 10 and diff2 > 10:
            return None
        if diff1 != diff2:
            return expr1 if diff1 < diff2 else expr2
        return expr1 if len(expr1.numbers) <= len(expr2.numbers) else expr2
    return better

def solutions(target, numbers):
    answer = None
    better = better_checker(target)
    for p in permute([number_expression(n) for n in numbers]):
        for e in expressions(p):
            b = better(answer, e)
            if b != answer:
                answer = b
                yield b

def solve(target, *numbers):
    log = logging.info
    log("--------------------------------")
    log(f"Target: {target}, numbers: {numbers}")
    start = monotonic()
    answer = None
    for s in solutions(target, numbers):
        log(s)
        answer = s
    end = monotonic()
    if not answer:
        log("No solution found")
    log(f"Completed in {end-start}s")
    log("--------------------------------")
    return answer
