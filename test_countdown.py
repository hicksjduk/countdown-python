from pytest import fixture, fail
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
    context.numbers = [int(n.strip()) for n in numbers.split(",")]
    context.result = solve(context.target, *context.numbers)

@then(parsers.parse("a solution is found whose value equals the target number and which uses <count> numbers"))
def step(context, count):
    check_found_result(context.result, context.target, int(count), context.numbers)

@then(parsers.parse("a solution is found whose value equals {value} and which uses {count} numbers"))
def step(context, value, count):
    check_found_result(context.result, int(value), int(count), context.numbers)

def check_found_result(result, expected_value, expected_count, expected_numbers):
    assert_that(result.value, equal_to(expected_value))
    assert_that(len(result.numbers), equal_to(expected_count))
    for n in result.numbers:
        try:
            expected_numbers.remove(n)
        except:
            fail(f"Unexpected number {n}")


@then("no solution is found")
def step(context):
    assert_that(context.result, none())