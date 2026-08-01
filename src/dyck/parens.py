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

"""Balanced-parenthesis problems.

A *Dyck word* is a string of brackets in which every closing bracket matches an
earlier opening one and nothing is left open at the end. Every function here is
some question asked about that definition: is this a Dyck word, how far from one
is it, what is the longest one inside it, and how do I enumerate them all.
"""

from collections.abc import Iterator

__all__ = [
    "PAIRS",
    "generate",
    "is_balanced",
    "is_balanced_multi",
    "is_valid_with_wildcards",
    "longest_valid",
    "min_insertions_to_balance",
]

#: Closing bracket -> matching opening bracket, for :func:`is_balanced_multi`.
PAIRS = {")": "(", "]": "[", "}": "{"}


def is_balanced(s: str) -> bool:
    """Return whether ``s`` is a Dyck word over ``()``.

    A single depth counter is sufficient. The subtlety is that a final depth of
    zero is *not* enough on its own -- ``")("`` ends at zero yet is invalid --
    so the counter must also never dip below zero along the way.

    Characters other than ``(`` and ``)`` are ignored, which lets this run over
    source text directly.

    Runs in O(n) time and O(1) space, which is optimal: no approach can decide
    this without reading every character.

    >>> is_balanced("(()())")
    True
    >>> is_balanced(")(")
    False
    """
    depth = 0
    for char in s:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def is_balanced_multi(s: str) -> bool:
    """Return whether ``s`` is balanced over ``()``, ``[]`` and ``{}``.

    This is where a stack stops being wasteful. With one bracket type a counter
    suffices because every closer matches the same opener; with several, closing
    a bracket requires knowing *which* one is innermost, and only a stack
    remembers that. ``"([)]"`` is the case a counter cannot reject.

    Runs in O(n) time and O(n) space -- the space is the price of the extra
    bracket types, not a free choice.

    >>> is_balanced_multi("{[()]}")
    True
    >>> is_balanced_multi("([)]")
    False
    """
    stack: list[str] = []
    openers = set(PAIRS.values())
    for char in s:
        if char in openers:
            stack.append(char)
        elif char in PAIRS and (not stack or stack.pop() != PAIRS[char]):
            return False
    return not stack


def min_insertions_to_balance(s: str) -> int:
    """Return how many brackets must be inserted to make ``s`` balanced.

    Two counters are genuinely required here, because the answer distinguishes
    the two ways a string can fail. ``unmatched_close`` accrues closers that
    arrive with nothing open; ``open_count`` holds openers still waiting at the
    end. A single counter would let those cancel, reporting ``"())("`` -- which
    needs two insertions -- as balanced.

    Runs in O(n) time and O(1) space.

    >>> min_insertions_to_balance("())(")
    2
    >>> min_insertions_to_balance("(()")
    1
    """
    open_count = 0
    unmatched_close = 0
    for char in s:
        if char == "(":
            open_count += 1
        elif char == ")":
            if open_count > 0:
                open_count -= 1
            else:
                unmatched_close += 1
    return open_count + unmatched_close


def longest_valid(s: str) -> int:
    """Return the length of the longest balanced *contiguous* substring.

    The two-pass trick avoids both the stack and the DP table that this problem
    is usually solved with. Scanning left to right, a run is a candidate answer
    whenever opens equal closes, and is dead once closes exceed opens -- at that
    point no extension can recover, so both counters reset. That pass alone
    misses runs that stay open-heavy to the very end, such as ``"(()"``, so a
    mirrored right-to-left pass catches those.

    Runs in O(n) time and O(1) space.

    >>> longest_valid(")()())")
    4
    >>> longest_valid("(()")
    2
    """

    def scan(text: str, opener: str, closer: str) -> int:
        best = opened = closed = 0
        for char in text:
            if char == opener:
                opened += 1
            elif char == closer:
                closed += 1
            if opened == closed:
                best = max(best, opened + closed)
            elif closed > opened:
                opened = closed = 0
        return best

    return max(scan(s, "(", ")"), scan(s[::-1], ")", "("))


def is_valid_with_wildcards(s: str) -> bool:
    """Return whether ``s`` can be balanced when ``*`` is ``(``, ``)`` or empty.

    Rather than branching three ways per wildcard -- exponential -- track the
    *interval* of depths still reachable. ``hi`` assumes every ``*`` so far was
    an opener, ``lo`` assumes every one was a closer. If ``hi`` ever goes
    negative there are more closers than any reading can absorb, and ``lo`` is
    clamped at zero because a reading that would go negative is simply not one
    of the surviving possibilities. Depth zero is reachable at the end exactly
    when ``lo`` is zero.

    Runs in O(n) time and O(1) space.

    >>> is_valid_with_wildcards("(*)")
    True
    >>> is_valid_with_wildcards(")*(")
    False
    """
    lo = hi = 0
    for char in s:
        if char == "(":
            lo += 1
            hi += 1
        elif char == ")":
            lo -= 1
            hi -= 1
        else:
            lo -= 1
            hi += 1
        if hi < 0:
            return False
        lo = max(lo, 0)
    return lo == 0


def generate(n: int) -> Iterator[str]:
    """Yield every Dyck word built from ``n`` bracket pairs, in sorted order.

    Backtracking that only ever extends a valid prefix: an opener is available
    while fewer than ``n`` have been placed, and a closer while some opener is
    still unmatched. Because no invalid prefix is ever explored, the work is
    proportional to the size of the output rather than to the ``2 ** (2 * n)``
    strings that exist over the alphabet.

    That output size is the ``n``-th Catalan number -- see :mod:`dyck.catalan`,
    which computes it directly without enumerating anything.

    >>> list(generate(3))
    ['((()))', '(()())', '(())()', '()(())', '()()()']

    :raises ValueError: if ``n`` is negative.
    """
    if n < 0:
        msg = f"n must be non-negative, got {n}"
        raise ValueError(msg)

    buffer: list[str] = []

    def build(opened: int, closed: int) -> Iterator[str]:
        if len(buffer) == 2 * n:
            yield "".join(buffer)
            return
        if opened < n:
            buffer.append("(")
            yield from build(opened + 1, closed)
            buffer.pop()
        if closed < opened:
            buffer.append(")")
            yield from build(opened, closed + 1)
            buffer.pop()

    yield from build(0, 0)
