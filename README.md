# dyck-words

Balanced brackets and the Catalan numbers that count them, in Python 3.14.

A *Dyck word* is a string of brackets where every closer matches an earlier
opener and nothing is left open at the end — `(()())` is one, `())(` is not.
Two things live here: the algorithms that answer questions about such strings,
and the arithmetic that counts them. They meet in `tests/test_cross.py`, where
enumerating every Dyck word of a given length has to produce exactly the number
the closed form predicts.

```python
>>> from dyck import is_balanced, generate, catalan_via_binomial
>>> is_balanced("(()())")
True
>>> is_balanced("())(")          # right count, wrong order
False
>>> list(generate(3))
['((()))', '(()())', '(())()', '()(())', '()()()']
>>> catalan_via_binomial(3)      # ...which is how many there are
5
```

## Brackets

| function | problem | time | space |
| --- | --- | --- | --- |
| `is_balanced` | is this a Dyck word? | O(n) | O(1) |
| `is_balanced_multi` | same, over `()` `[]` `{}` | O(n) | O(n) |
| `min_insertions_to_balance` | how far from balanced is it? | O(n) | O(1) |
| `longest_valid` | longest balanced substring | O(n) | O(1) |
| `is_valid_with_wildcards` | `*` may be `(`, `)`, or empty | O(n) | O(1) |
| `generate` | every Dyck word of `n` pairs | O(output) | O(n) |

Two details worth pulling out, since they are where the obvious implementation
goes wrong:

**A final depth of zero is not sufficient.** `")("` ends balanced and is not,
so the counter has to be checked for dipping below zero *during* the scan, not
only at the end. This is the single most common way to get the problem wrong.

**One counter answers "is it balanced", two answer "how unbalanced".** Validity
is a yes/no question that a single depth counter settles. Counting the repairs
needed is not: `min_insertions_to_balance` must track unmatched openers and
unmatched closers separately, or `"())("` — which needs two insertions —
cancels itself out to zero.

A stack appears only in `is_balanced_multi`, and it earns its place there rather
than being the reflexive choice. With one bracket type a counter is strictly
better; with several, closing a bracket means knowing which one is innermost,
and `"([)]"` is the string that a counter cannot reject.

## Catalan numbers

`1, 1, 2, 5, 14, 42, 132, 429, 1430, …` ([OEIS A000108][oeis])

Six implementations, all exact, all in arbitrary-precision integers:

| function | method | time | notes |
| --- | --- | --- | --- |
| `catalan_recursive` | segment recurrence | exponential | kept for contrast; unusable past ~25 |
| `catalan_memo` | same, memoised | O(n²) | one decorator, whole different complexity class |
| `catalan_dp` | bottom-up table | O(n²) | iterative, no recursion limit |
| `catalan_via_binomial` | `comb(2n,n) // (n+1)` | O(n) | fastest for a single value |
| `catalan_reflection` | `comb(2n,n) - comb(2n,n+1)` | O(n) | the reflection principle, as code |
| `catalan_multiplicative` | `C(k+1) = C(k)·2(2k+1)/(k+2)` | O(n) | no binomials; best for a whole prefix |

Unlike the bracket check — which has one good algorithm and several
deliberately worse ones — these differ in ways that matter. The spread from
exponential to linear is real, and the choice to stay in integers is
load-bearing: `/` instead of `//` starts losing precision somewhere past
`n = 30`, and `C(100)` is a 57-digit number.

`catalan_reflection` is the one to read for understanding rather than speed.
Of the `comb(2n, n)` strings with `n` of each bracket, the invalid ones are
exactly those that dip below depth zero; reflecting every bracket after that
first dip is a bijection onto the strings with `n+1` closers. Subtracting
`comb(2n, n+1)` therefore removes each invalid string once, which is *why* the
closed form is what it is.

## Testing

The two halves check each other. `generate` walks the strings; the closed form
counts them without looking at any; and a brute-force filter over all `2^(2n)`
strings — the dumbest method available, and so an independent witness — agrees
with both. Property-based tests via [Hypothesis][hyp] cover the invariants that
table-driven cases miss: the counter and the stack must agree on single-bracket
input, `is_balanced` must hold exactly when zero insertions are needed, and the
length reported by `longest_valid` must be achieved by some slice that really is
balanced.

```sh
uv sync
uv run pytest          # includes doctests
uv run ruff check .
uv run mypy
```

## Not here yet

The Catalan numbers count a good deal more than bracket strings — binary trees
with `n` nodes, triangulations of an `(n+2)`-gon, monotonic lattice paths under
the diagonal, ways to parenthesise a product. Implementing the *bijections*
between those is the natural next step, and each one gives another independent
route to the same count.

## License

MIT

[oeis]: https://oeis.org/A000108
[hyp]: https://hypothesis.readthedocs.io/
