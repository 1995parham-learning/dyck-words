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

"""Dyck words and the Catalan numbers that count them."""

from dyck.catalan import (
    catalan_dp,
    catalan_memo,
    catalan_multiplicative,
    catalan_recursive,
    catalan_reflection,
    catalan_via_binomial,
    sequence,
)
from dyck.parens import (
    generate,
    is_balanced,
    is_balanced_multi,
    is_valid_with_wildcards,
    longest_valid,
    min_insertions_to_balance,
)

__all__ = [
    "catalan_dp",
    "catalan_memo",
    "catalan_multiplicative",
    "catalan_recursive",
    "catalan_reflection",
    "catalan_via_binomial",
    "generate",
    "is_balanced",
    "is_balanced_multi",
    "is_valid_with_wildcards",
    "longest_valid",
    "min_insertions_to_balance",
    "sequence",
]
