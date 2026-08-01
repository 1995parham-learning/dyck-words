# Copyright (C) 2026 Parham Alvani
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

"""Tests for the bracket problems in :mod:`dyck.parens`."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from dyck.parens import (
    generate,
    is_balanced,
    is_balanced_multi,
    is_valid_with_wildcards,
    longest_valid,
    min_insertions_to_balance,
)

brackets = st.text(alphabet="()", max_size=24)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # trivial
        ("", True),
        ("()", True),
        ("(", False),
        (")", False),
        # nesting and sequencing
        ("(())", True),
        ("()()", True),
        ("(()())", True),
        ("((()))", True),
        ("(()(()))", True),
        # unclosed openers -- caught by the final depth check
        ("(()", False),
        ("((", False),
        ("((()", False),
        # unopened closers -- caught by the running dip check
        ("())", False),
        ("))", False),
        ("(()))", False),
        # right count, wrong order: the family a single end-of-string check misses
        (")(", False),
        ("())(", False),
        (")()(", False),
        ("())((", False),
        # characters outside the alphabet are ignored
        ("(a + b)", True),
        ("f(g(x), h(y))", True),
        ("f(g(x, h(y))", False),
        ("no brackets here", True),
        # long inputs
        ("()" * 1000, True),
        ("(" * 500 + ")" * 500, True),
        ("(" * 500 + ")" * 499, False),
        (")" + "()" * 100, False),
        ("()" * 100 + "(", False),
    ],
)
def test_is_balanced(text: str, *, expected: bool) -> None:
    assert is_balanced(text) is expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", True),
        ("{[()]}", True),
        ("()[]{}", True),
        ("{[()()]}", True),
        # interleaved rather than nested -- the case a counter cannot reject
        ("([)]", False),
        ("{[}]", False),
        ("[(])", False),
        # ordinary imbalance still fails
        ("(", False),
        ("]", False),
        ("{[()]", False),
        ("int f(a[0]) { return 1; }", True),
    ],
)
def test_is_balanced_multi(text: str, *, expected: bool) -> None:
    assert is_balanced_multi(text) is expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", 0),
        ("()", 0),
        ("(", 1),
        (")", 1),
        ("(()", 1),
        ("())", 1),
        (")(", 2),
        ("())(", 2),
        ("((((", 4),
        ("))))", 4),
        ("()))((", 4),
    ],
)
def test_min_insertions_to_balance(text: str, expected: int) -> None:
    assert min_insertions_to_balance(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", 0),
        ("(", 0),
        (")", 0),
        ("()", 2),
        (")()())", 4),
        ("(()", 2),
        ("()(()", 2),
        ("((((", 0),
        ("()(())", 6),
        # only the right-to-left pass finds this one
        ("(()()", 4),
        ("()" * 50, 100),
    ],
)
def test_longest_valid(text: str, expected: int) -> None:
    assert longest_valid(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", True),
        ("*", True),
        ("(*)", True),
        ("(*))", True),
        ("(*()", True),
        ("**", True),
        ("(((******))", True),
        (")*(", False),
        ("(((**", False),
        ("*)(", False),
        ("(()", False),
    ],
)
def test_is_valid_with_wildcards(text: str, *, expected: bool) -> None:
    assert is_valid_with_wildcards(text) is expected


@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (0, [""]),
        (1, ["()"]),
        (2, ["(())", "()()"]),
        (3, ["((()))", "(()())", "(())()", "()(())", "()()()"]),
    ],
)
def test_generate_small(n: int, expected: list[str]) -> None:
    assert list(generate(n)) == expected


def test_generate_is_sorted_and_unique() -> None:
    words = list(generate(6))
    assert words == sorted(words)
    assert len(words) == len(set(words))


def test_generate_rejects_negative() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        list(generate(-1))


@given(brackets)
def test_counter_and_stack_agree(text: str) -> None:
    """Over a single bracket type the stack version must match the counter."""
    assert is_balanced(text) == is_balanced_multi(text)


@given(brackets)
def test_balanced_iff_no_insertions_needed(text: str) -> None:
    assert is_balanced(text) == (min_insertions_to_balance(text) == 0)


@given(brackets)
def test_wildcards_generalise_plain_check(text: str) -> None:
    """With no ``*`` present the wildcard solver reduces to the plain check."""
    assert is_valid_with_wildcards(text) == is_balanced(text)


@given(brackets)
def test_longest_valid_is_even_and_bounded(text: str) -> None:
    best = longest_valid(text)
    assert best % 2 == 0
    assert 0 <= best <= len(text)


@given(brackets)
def test_longest_valid_substring_really_is_balanced(text: str) -> None:
    """The reported length must be achieved by some genuinely balanced slice."""
    best = longest_valid(text)
    if best:
        assert any(is_balanced(text[i : i + best]) for i in range(len(text) - best + 1))
