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

@then("a solution is found whose value equals the target number")
def step(context):
    assert_that(context.result.value, equal_to(context.target))

@then(parsers.parse("a solution is found whose value equals {value}"))
def step(context, value):
    assert_that(context.result.value, equal_to(int(value)))

@then(parsers.parse("the solution found uses {count} numbers"))
@then(parsers.parse("the solution found uses <count> numbers"))
def step(context, count):
    assert_that(context.result.count, equal_to(int(count)))

@then("no solution is found")
def step(context):
    assert_that(context.result, none())