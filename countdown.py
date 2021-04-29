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
    def __init__(self, value, priority, string, count):
        self.value = value
        self.priority = priority
        self.string = string
        self.count = count

    def __str__(self):
        return f'{self.string} = {self.value}'

def numberExpression(number):
    return Expression(value=number, priority=priority.atomic, string=f'{number}', count=1)

def arithmeticExpression(leftOperand, operator, rightOperand):
    return Expression(value=operator.evaluator(leftOperand.value, rightOperand.value), priority=operator.priority,
            string=formatExpr(leftOperand, operator, rightOperand), count=leftOperand.count + rightOperand.count)

def formatExpr(leftOperand, operator, rightOperand):
    elements = [
        formatOperand(leftOperand, leftOperand.priority < operator.priority),
        operator.symbol,
        formatOperand(rightOperand, rightOperand.priority < operator.priority or
                      (rightOperand.priority == operator.priority and not operator.commutative))
    ]
    return " ".join(elements)

def formatOperand(operand, parenthesesNeeded):
    return f'({operand.string})' if parenthesesNeeded else operand.string

def addCombiner(a, b):
    return arithmeticExpression(a, operator.add, b)

def subtractCombiner(a, b):
    if a.value <= b.value or a.value == b.value * 2:
        return None
    return arithmeticExpression(a, operator.subtract, b)

def multiplyCombiner(a, b):
    if a.value == 1 or b.value == 1:
        return None
    return arithmeticExpression(a, operator.multiply, b)

def divideCombiner(a, b):
    if b.value == 1 or a.value % b.value or a.value == b.value ** 2:
        return None
    return arithmeticExpression(a, operator.divide, b)

combiners = [addCombiner, subtractCombiner, multiplyCombiner, divideCombiner]

def permute(expressions):
    if len(expressions) == 1:
        yield expressions
    elif expressions:
        used = usedChecker(lambda e: e.value)
        for i in range(len(expressions)):
            value = expressions[i]
            if not used(value):
                yield [value]
                others = [*expressions[0:i], *expressions[i+1:]]
                for p in permute(others):
                    yield [value, *p]

def usedChecker(idGenerator):
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
        used = usedChecker(lambda e: e.value)
        for i in range(1, len(permutation)):
            for left in expressions(permutation[:i]):
                for right in expressions(permutation[i:]):
                    for comb in combiners:
                        expr = comb(left, right)
                        if expr and not used(expr):
                            yield expr

def betterChecker(target):
    def better(expr1, expr2):
        diff1, diff2 = (1000 if not e else abs(target - e.value) for e in (expr1, expr2))
        if diff1 > 10 and diff2 > 10:
            return None
        if diff1 != diff2:
            return expr1 if diff1 < diff2 else expr2
        return expr1 if expr1.count <= expr2.count else expr2
    return better

def logIt(msg):
    logging.info(msg)

def solveIt(target, numbers, log):
    log("--------------------------------")
    log(f"Target: {target}, numbers: {numbers}")
    start = monotonic()
    answer = None
    for s in solution(target, numbers):
        log(s)
        answer = s
    end = monotonic()
    if not answer:
        log("No solution found")
    log(f"Completed in {end-start}s")
    log("--------------------------------")
    return answer

def solution(target, numbers):
    answer = None
    better = betterChecker(target)
    for p in permute([numberExpression(n) for n in numbers]):
        for e in expressions(p):
            b = better(answer, e)
            if b != answer:
                answer = b
                yield b

def solve(target, *numbers):
    return solveIt(target, numbers, log=logIt)