"""Six ways to compute the Catalan numbers.

The Catalan numbers begin ``1, 1, 2, 5, 14, 42, 132, 429, 1430`` and count,
among many other things, the Dyck words of :mod:`dyck.parens`. Unlike the
balanced-bracket check -- which has one good algorithm and several worse ones --
these implementations differ in ways that actually matter: exponential versus
quadratic versus linear, and exact integer arithmetic versus arithmetic that
would lose precision if it ever touched a float.

They must all agree. ``tests/test_cross.py`` is where that is enforced, against
brute-force enumeration as an independent witness.
"""

from collections.abc import Iterator
from functools import cache
from math import comb

__all__ = [
    "catalan_dp",
    "catalan_memo",
    "catalan_multiplicative",
    "catalan_recursive",
    "catalan_reflection",
    "catalan_via_binomial",
    "sequence",
]


def _check(n: int) -> None:
    if n < 0:
        msg = f"n must be non-negative, got {n}"
        raise ValueError(msg)


def catalan_recursive(n: int) -> int:
    """Compute ``C(n)`` from the segment recurrence, without memoisation.

    The recurrence ``C(n) = sum(C(i) * C(n - 1 - i))`` reads directly off the
    structure of a Dyck word: the opening bracket closes somewhere, splitting
    the rest into an inner word of ``i`` pairs and a trailing word of the rest.

    This is the honest exponential version, kept for contrast rather than use --
    it recomputes the same subproblems repeatedly and is unusable past roughly
    ``n = 25``. :func:`catalan_memo` is the same recurrence made practical.

    >>> catalan_recursive(5)
    42
    """
    _check(n)
    if n == 0:
        return 1
    return sum(catalan_recursive(i) * catalan_recursive(n - 1 - i) for i in range(n))


@cache
def catalan_memo(n: int) -> int:
    """Compute ``C(n)`` from the same recurrence, with memoisation.

    One decorator turns the exponential blow-up into O(n**2) multiplications:
    there are ``n`` subproblems and each sums ``n`` products. Results are cached
    across calls for the life of the process.

    >>> catalan_memo(15)
    9694845
    """
    _check(n)
    if n == 0:
        return 1
    return sum(catalan_memo(i) * catalan_memo(n - 1 - i) for i in range(n))


def catalan_dp(n: int) -> int:
    """Compute ``C(n)`` bottom-up, filling a table from ``C(0)`` upward.

    Identical arithmetic to :func:`catalan_memo` and identical O(n**2) cost, but
    iterative -- so it neither consumes recursion depth nor holds a cache alive
    between calls. This is the version to reach for if ``n`` is large enough
    that recursion limits start to bite.

    >>> catalan_dp(10)
    16796
    """
    _check(n)
    table = [1] + [0] * n
    for size in range(1, n + 1):
        table[size] = sum(table[i] * table[size - 1 - i] for i in range(size))
    return table[n]


def catalan_via_binomial(n: int) -> int:
    """Compute ``C(n)`` from the closed form ``comb(2n, n) // (n + 1)``.

    The fastest of the six for a single value. The division is exact -- ``n + 1``
    always divides ``comb(2n, n)`` -- so floor division is not an approximation
    here, and staying in Python's arbitrary-precision integers means the result
    is exact at any size. Using ``/`` instead would silently lose precision
    somewhere past ``n = 30``.

    >>> catalan_via_binomial(20)
    6564120420
    """
    _check(n)
    return comb(2 * n, n) // (n + 1)


def catalan_reflection(n: int) -> int:
    """Compute ``C(n)`` as ``comb(2n, n) - comb(2n, n + 1)``.

    Numerically the least interesting and conceptually the most: it is the
    reflection principle written as code. Of the ``comb(2n, n)`` strings with
    ``n`` of each bracket, the invalid ones are those dipping below depth zero.
    Reflecting every bracket after that first dip maps each invalid string to a
    distinct string with ``n + 1`` closers, and that map is a bijection -- so
    subtracting ``comb(2n, n + 1)`` removes each invalid string exactly once.

    That argument is why the closed form of :func:`catalan_via_binomial` is what
    it is, rather than a formula to be taken on faith.

    >>> catalan_reflection(8)
    1430
    """
    _check(n)
    return comb(2 * n, n) - comb(2 * n, n + 1)


def catalan_multiplicative(n: int) -> int:
    """Compute ``C(n)`` by iterating ``C(k + 1) = C(k) * 2 * (2k + 1) // (k + 2)``.

    Linear time with no binomial coefficient and no table. Each step's division
    is exact because the running value is a Catalan number at every iteration,
    so the sequence never leaves the integers -- the ordering of ``*`` before
    ``//`` is load-bearing and must not be "simplified".

    The practical choice when every ``C(0..n)`` is wanted, since each value costs
    one multiply and one divide. See :func:`sequence`.

    >>> catalan_multiplicative(12)
    208012
    """
    _check(n)
    value = 1
    for k in range(n):
        value = value * 2 * (2 * k + 1) // (k + 2)
    return value


def sequence(n: int) -> Iterator[int]:
    """Yield ``C(0)`` through ``C(n)`` inclusive.

    Streams the multiplicative recurrence, so producing the whole prefix costs
    the same as producing its last term.

    >>> list(sequence(8))
    [1, 1, 2, 5, 14, 42, 132, 429, 1430]
    """
    _check(n)
    value = 1
    for k in range(n + 1):
        yield value
        value = value * 2 * (2 * k + 1) // (k + 2)
