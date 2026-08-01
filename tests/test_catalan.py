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

"""Tests for the Catalan implementations in :mod:`dyck.catalan`."""

from collections.abc import Callable

import pytest

from dyck.catalan import (
    catalan_dp,
    catalan_memo,
    catalan_multiplicative,
    catalan_recursive,
    catalan_reflection,
    catalan_via_binomial,
    sequence,
)

#: OEIS A000108.
# fmt: off
KNOWN = [
    1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796, 58786, 208012, 742900,
    2674440, 9694845, 35357670, 129644790, 477638700, 1767263190, 6564120420,
]
# fmt: on

#: Every implementation, with the largest ``n`` it can reach in reasonable time.
IMPLEMENTATIONS: list[tuple[Callable[[int], int], int]] = [
    (catalan_recursive, 14),
    (catalan_memo, 200),
    (catalan_dp, 200),
    (catalan_via_binomial, 200),
    (catalan_reflection, 200),
    (catalan_multiplicative, 200),
]

ALL_FUNCS = [func for func, _ in IMPLEMENTATIONS]


@pytest.mark.parametrize(("func", "limit"), IMPLEMENTATIONS)
def test_matches_known_values(func: Callable[[int], int], limit: int) -> None:
    for n, expected in enumerate(KNOWN[: limit + 1]):
        assert func(n) == expected, f"{func.__name__}({n})"


@pytest.mark.parametrize("func", ALL_FUNCS)
def test_rejects_negative(func: Callable[[int], int]) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        func(-1)


def test_all_implementations_agree() -> None:
    """The six must agree everywhere they overlap, not merely on known values."""
    for n in range(15):
        values = {func(n) for func in ALL_FUNCS}
        assert len(values) == 1, f"disagreement at n={n}: {values}"


def test_fast_implementations_agree_at_scale() -> None:
    """Past ``n = 30`` a float-based closed form would drift. These must not."""
    fast: list[Callable[[int], int]] = [
        catalan_memo,
        catalan_dp,
        catalan_via_binomial,
        catalan_reflection,
        catalan_multiplicative,
    ]
    for n in (50, 100, 200, 500):
        values = {func(n) for func in fast}
        assert len(values) == 1, f"disagreement at n={n}"


def test_large_value_is_exact() -> None:
    """C(100) is a 57-digit integer; exactness is the whole point of using ints."""
    value = catalan_via_binomial(100)
    assert value == 896519947090131496687170070074100632420837521538745909320
    assert catalan_multiplicative(100) == value


def test_segment_recurrence_holds() -> None:
    """Every value must satisfy the recurrence the closed form is derived from."""
    for n in range(1, 40):
        assert catalan_memo(n) == sum(catalan_memo(i) * catalan_memo(n - 1 - i) for i in range(n))


def test_multiplicative_recurrence_holds() -> None:
    for n in range(60):
        assert catalan_via_binomial(n + 1) * (n + 2) == catalan_via_binomial(n) * 2 * (2 * n + 1)


def test_sequence_matches_known_prefix() -> None:
    assert list(sequence(len(KNOWN) - 1)) == KNOWN


def test_sequence_matches_pointwise() -> None:
    assert list(sequence(80)) == [catalan_via_binomial(n) for n in range(81)]


def test_sequence_of_zero() -> None:
    assert list(sequence(0)) == [1]


def test_sequence_rejects_negative() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        list(sequence(-1))


def test_growth_ratio_approaches_four() -> None:
    """C(n+1)/C(n) tends to 4, so the sequence grows like ``4**n / n**1.5``."""
    ratio = catalan_via_binomial(2001) / catalan_via_binomial(2000)
    assert 3.99 < ratio < 4.0
