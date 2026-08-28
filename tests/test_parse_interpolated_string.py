from assertpy import assert_that

from pycep import BicepParser


def test_parse_interpolation_with_nested_quoted_string() -> None:
    # given
    content = """
param prefix string

var resourceName = '${prefix}${uniqueString(resourceGroup().id, 'stable-salt')}'
"""

    # when
    result = BicepParser().parse(text=content)

    # then
    assert_that(result["variables"]["resourceName"]["value"]).is_equal_to(
        "${prefix}${uniqueString(resourceGroup().id, 'stable-salt')}"
    )


def test_parse_interpolation_with_nested_interpolation() -> None:
    # given
    content = """
param environment string
param suffix string

var resourceName = '${environment == 'development' ? '-${suffix}' : ''}'
"""

    # when
    result = BicepParser().parse(text=content)

    # then
    assert_that(result["variables"]["resourceName"]["value"]).is_equal_to(
        "${environment == 'development' ? '-${suffix}' : ''}"
    )


def test_parse_interpolation_with_escaped_quote() -> None:
    # given
    content = r"""
param name string

var message = 'It\'s ${name}'
"""

    # when
    result = BicepParser().parse(text=content)

    # then
    assert_that(result["variables"]["message"]["value"]).is_equal_to(r"It\'s ${name}")


def test_parse_multi_line_string_separately_from_interpolation() -> None:
    # given
    content = """
var message = '''
This is a multi-line string.
The ${placeholder} syntax remains literal.
'''
"""

    # when
    result = BicepParser().parse(text=content)

    # then
    assert_that(result["variables"]["message"]["value"]).is_equal_to(
        "This is a multi-line string.\nThe ${placeholder} syntax remains literal.\n"
    )


def test_parse_many_interpolated_strings() -> None:
    # given
    variable_count = 200
    declarations = "\n".join(
        (
            f"var generatedName{index} = "
            f"'${{prefix}}-${{uniqueString(resourceGroup().id, 'salt-{index}')}}"
            f"${{environment == 'development' ? '-${{suffix}}' : ''}}'"
        )
        for index in range(variable_count)
    )
    content = f"""
param prefix string
param environment string
param suffix string

{declarations}
"""

    # when
    result = BicepParser().parse(text=content)

    # then
    assert_that(result["variables"]).is_length(variable_count)
    assert_that(result["variables"]["generatedName199"]["value"]).is_equal_to(
        "${prefix}-${uniqueString(resourceGroup().id, 'salt-199')}${environment == 'development' ? '-${suffix}' : ''}"
    )
