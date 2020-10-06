#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
# Written by Paul Wayper for Red Hat in September 2020

import re

from django.db.models import Q


def filter_deep_object_param(
    request, filter_prefix, param_name='filter', field_prefix=None
):
    """
    Find a parameter starting with the given param_name (= 'filter') and
    subsequent square-bracketed filter parts, and return a Q() expression
    that filters on that structured value within that field (or the parameter
    name as a field if no field is given).  All parts within square brackets
    must be word-characters - i.e. `[A-Za-z0-9_]+`.

    As an example, this will match query parameters like:

    1. `system_profile[sap_system]=true`
    2. `system_profile[cpu_flags][contains]=clzero`
    3. `system_profile[system_memory_bytes][gt]=4000000000`

    And produce a filter equivalent to:

    1. `system_profile__sap_system=True`
    2. `system_profile__cpu_flags__contains='clzero'`
    3. `system_profile__system_memory_bytes__gt=4000000000`

    Note that for the `gt` operator the value is converted to a number, and
    the special values '`true`', '`True`', '`false`' and '`False`' are
    converted to Python `True` and `False` boolean values respectively.

    Numbers do not match strings in JSON value introspection, so
    `system_profile[number_of_sockets]=1` will convert to the filter
    `system_profile__number_of_sockets='1'` and will not match a record where
    number of sockets is the number `1`.  A value that is wholly digits will
    be converted to an integer if the 'eq' or 'ne' operators are given, so
    `system_profile[number_of_sockets][eq]=1` will match an integer number
    of sockets value.

    All these would be matched by an openapi.Parameter with the name
    `system_profile`.  If more than one of these parameter constructions
    appears in the parameters supplied, these will be ANDed together in the
    returned filter.

    The operators supported are based on:

    https://github.com/RedHatInsights/insights-api-common-rails#usage

    NOTE: also, because we don't attempt to bar any other comparator, because
    they might also be a key in a dictionary, this also allows us to accept
    all standard Django filter operators.  E.g. we accept both 'starts_with'
    and 'startswith'.
    This is roughly compliant with OpenAPI 3's 'deepObject' object parameter
    style, but OpenAPI 2 does not recognise them at all and there is no way
    to express such a parameter in OpenAPI 2.  Therefore, we do not use or
    provide an OpenAPI 'Parameter' object to include in the parameter spec.
    """
    end_filter = Q()
    fre = re.compile(r'^(?P<prefix>\w+)(?P<brackets>(?:\[\w+\])+)$')
    comparator_translations = {
        'eq_i': 'iexact', 'contains_i': 'icontains',
        'starts_with_i': 'istartswith', 'ends_with_i': 'iendswith',
        'starts_with': 'startswith', 'ends_with': 'endswith'
    }

    param_prefix = param_name + '[' + filter_prefix + ']['
    for this_param, param_value in request.query_params.items():
        # We only want to report invalid parameters for ones we care about.
        # Other filter parameters may have some new weird syntax we don't
        # understand.  So we're specific as possible with this direct match.
        if not this_param.startswith(param_prefix):
            continue
        m = fre.match(this_param)
        # We matched the param_prefix but not the regex - parameter is mangled
        if not m:
            raise BadRequest(
                f"The '{param_name}' parameter is incorrectly formatted"
            )
        filter_parts = m.group('brackets')[1:-1].split('][')
        # Keep the filter prefix here though
        last_part = filter_parts[-1]
        # Convert value type if necessary
        if param_value in {'true', 'True', 'false', 'False'}:
            param_value = param_value in {'true', 'True'}
        if last_part in ('gt', 'gte', 'lt', 'lte'):
            if param_value.isdigit():
                param_value = int(param_value)
            else:
                raise BadRequest(
                    f"The '{param_name}' value needs expects an integer when "
                    f"given the 'gt', 'gte', 'lt' or 'lte' operators"
                )
        elif last_part in ('eq', 'ne') and param_value.isdigit():
            # Special case to support direct numeric comparisons
            param_value = int(param_value)
        # Convert comparator if necessary
        filter_not_equal = False
        if last_part == 'eq':
            filter_parts.pop()
            last_part = filter_parts[-1]
        elif last_part == 'ne':
            filter_not_equal = True
            filter_parts.pop()
            last_part = filter_parts[-1]
        if last_part in {'nil', 'not_nil'}:
            # If we haven't been given true or false, just assume true.
            if not isinstance(param_value, bool):
                param_value = True
            if last_part == 'not_nil':
                param_value = not param_value
            # Now replace the actual last filter part
            filter_parts[-1] = 'isnull'
        if last_part in comparator_translations:
            filter_parts[-1] = comparator_translations[last_part]
        # Join it all together in a filter with (field_prefix__)filter_parts=value
        if field_prefix is not None:
            filter_parts.insert(0, field_prefix)
        this_filter = Q(**{'__'.join(filter_parts): param_value})
        # Invert Q sense if `__ne`.
        if filter_not_equal:
            this_filter = ~this_filter
        # Add it to the expression
        end_filter = end_filter & this_filter

    return end_filter
