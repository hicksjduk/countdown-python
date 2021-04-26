from pytest import fixture
from pytest_bdd import scenarios, when, then, parsers
from types import SimpleNamespace
from countdown import solve
from hamcrest import assert_that, equal_to, none

scenarios("./countdown.feature")

@fixture
def context():
    return SimpleNamespace()

@when(parsers.parse("I call the solver with target number <target> and numbers <numbers>"))
@when(parsers.parse("I call the solver with target number {target} and numbers {numbers}"))
def step(context, target, numbers):
    context.target = int(target)
    nums = [int(n.strip()) for n in numbers.split(",")]
    context.result = solve(context.target, *nums)

@then(parsers.parse("a solution is found whose value equals the target number and which uses <count> numbers"))
def step(context, count):
    check_found_result(context.result, context.target, int(count))

@then(parsers.parse("a solution is found whose value equals {value} and which uses {count} numbers"))
def step(context, value, count):
    check_found_result(context.result, int(value), int(count))

def check_found_result(result, value, count):
    assert_that(result.value, equal_to(int(value)))
    assert_that(result.count, equal_to(int(count)))

@then("no solution is found")
def step(context):
    assert_that(context.result, none())