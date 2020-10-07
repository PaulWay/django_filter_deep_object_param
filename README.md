# django_filter_deep_object_param
Create Django filters from OpenAPI 3 `deepObject` parameters.

# OpenAPI 3 `deepObject` parameters

As defined here:

https://swagger.io/docs/specification/serialization/#query

This allows users to query deep object structures, or relationships between
models, in one mostly-uniform syntax.  With some databases such as PostgreSQL
supporting deep querying of JSON objects, and the utility of being able to
introspect through models in query parameters, it makes sense to support this
parameter syntax.

# Examples

| Parameter | Filter |
|-----------|--------|
| `filter[system_profile][num_cpus][gt]=4` | `system_profile__num_cpus__gt=4` |

# Operational description
