"""The link between the two halves of the library.

Everything here asserts the same fact from different directions: the ``n``-th
Catalan number counts the Dyck words of length ``2n``. The enumeration in
:mod:`dyck.parens` and the arithmetic in :mod:`dyck.catalan` share no code, so
agreement between them is genuine evidence rather than a tautology.
"""

from itertools import product

import pytest
from hypothesis import given
from hypothesis import strategies as st

from dyck.catalan import catalan_via_binomial, sequence
from dyck.parens import (
    generate,
    is_balanced,
    is_valid_with_wildcards,
    longest_valid,
    min_insertions_to_balance,
)


def brute_force_count(n: int) -> int:
    """Count Dyck words of length ``2n`` by testing all ``2 ** (2n)`` strings.

    Deliberately the dumbest possible method, and the reason it is trustworthy:
    it shares no logic with either the backtracking generator or the closed
    form, so it is an independent witness to both.
    """
    return sum(is_balanced("".join(letters)) for letters in product("()", repeat=2 * n))


@pytest.mark.parametrize("n", range(8))
def test_generator_count_matches_catalan(n: int) -> None:
    assert sum(1 for _ in generate(n)) == catalan_via_binomial(n)


@pytest.mark.parametrize("n", range(7))
def test_brute_force_count_matches_catalan(n: int) -> None:
    assert brute_force_count(n) == catalan_via_binomial(n)


@pytest.mark.parametrize("n", range(7))
def test_generator_finds_exactly_the_balanced_strings(n: int) -> None:
    """The generator's output must equal the filtered universe of strings."""
    exhaustive = {
        "".join(letters) for letters in product("()", repeat=2 * n) if is_balanced("".join(letters))
    }
    assert set(generate(n)) == exhaustive


def test_counts_line_up_with_the_sequence() -> None:
    counts = [sum(1 for _ in generate(n)) for n in range(9)]
    assert counts == list(sequence(8))


@pytest.mark.parametrize("n", range(7))
def test_every_generated_word_is_balanced(n: int) -> None:
    for word in generate(n):
        assert is_balanced(word)
        assert len(word) == 2 * n
        assert min_insertions_to_balance(word) == 0
        assert longest_valid(word) == 2 * n
        assert is_valid_with_wildcards(word)


@given(st.integers(min_value=0, max_value=6))
def test_generator_is_deterministic(n: int) -> None:
    assert list(generate(n)) == list(generate(n))


def test_wildcard_string_of_stars_counts_nothing_out() -> None:
    """``"*" * 2n`` can spell any string, so it is always satisfiable."""
    for n in range(10):
        assert is_valid_with_wildcards("*" * (2 * n))
