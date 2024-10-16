# DJA OAS example vs. API response

This is a comparison of the [OAS schema](schemas/openapi.yaml) generated by DRF/DJA's legacy OAS schema generator vs.
the actual API presented by the server.

## Actual API response for List of /v1/courses/

Here's a `GET /v1/courses/?filter[id]=c823b5de-6018-4878-80e9-932d20eaa18a` (a list filtered to one result):

```json
{
    "links": {
        "first": "http://localhost:8000/v1/courses/?filter%5Bid%5D=c823b5de-6018-4878-80e9-932d20eaa18a&page%5Bnumber%5D=1",
        "last": "http://localhost:8000/v1/courses/?filter%5Bid%5D=c823b5de-6018-4878-80e9-932d20eaa18a&page%5Bnumber%5D=1",
        "next": null,
        "prev": null
    },
    "data": [
        {
            "type": "courses",
            "id": "c823b5de-6018-4878-80e9-932d20eaa18a",
            "attributes": {
                "effective_start_date": null,
                "effective_end_date": null,
                "last_mod_user_name": "admin",
                "last_mod_date": "2018-10-07",
                "school_bulletin_prefix_code": "CEFKX9",
                "suffix_two": "00",
                "subject_area_code": "ENGB",
                "course_number": "00217",
                "course_identifier": "ENGL3189X",
                "course_name": "POSTMODERNISM",
                "course_description": "POSTMODERNISM"
            },
            "relationships": {
                "course_terms": {
                    "meta": {
                        "count": 1
                    },
                    "data": [
                        {
                            "type": "course_terms",
                            "id": "a1d34785-cc25-4c1c-9806-9d05a98068c7"
                        }
                    ],
                    "links": {
                        "self": "http://localhost:8000/v1/courses/c823b5de-6018-4878-80e9-932d20eaa18a/relationships/course_terms/",
                        "related": "http://localhost:8000/v1/courses/c823b5de-6018-4878-80e9-932d20eaa18a/course_terms/"
                    }
                }
            },
            "links": {
                "self": "http://localhost:8000/v1/courses/c823b5de-6018-4878-80e9-932d20eaa18a/"
            }
        }
    ],
    "meta": {
        "pagination": {
            "page": 1,
            "pages": 1,
            "count": 1
        }
    }
}
```

## DJA example

Here's an example response generated by drf-spectacular-jsonapi:

```json
{
  "data": [
    {
      "type": "string",
      "id": "string",
      "links": {
        "self": "string"
      },
      "attributes": {
        "effective_start_date": "2024-07-29",
        "effective_end_date": "2024-07-29",
        "last_mod_user_name": "string",
        "last_mod_date": "2024-07-29",
        "school_bulletin_prefix_code": "string",
        "suffix_two": "st",
        "subject_area_code": "string",
        "course_number": "string",
        "course_identifier": "stringstr",
        "course_name": "string",
        "course_description": "string"
      },
      "relationships": {
        "course_terms": {
          "links": {
            "self": "string",
            "related": "string",
            "additionalProp1": {}
          },
          "data": [
            {
              "type": "string",
              "id": "string",
              "meta": {
                "additionalProp1": {}
              }
            }
          ],
          "meta": {
            "additionalProp1": {}
          }
        }
      }
    }
  ],
  "included": [
    {
      "type": "string",
      "id": "string",
      "attributes": {},
      "relationships": {},
      "links": {
        "additionalProp1": "string",
        "additionalProp2": "string",
        "additionalProp3": "string"
      },
      "meta": {
        "additionalProp1": {}
      }
    }
  ],
  "links": {
    "first": "string",
    "last": "string",
    "prev": "string",
    "next": "string",
    "additionalProp1": "string",
    "additionalProp2": "string",
    "additionalProp3": "string"
  },
  "jsonapi": {
    "version": "string",
    "meta": {
      "additionalProp1": {}
    }
  }
}
```

## Differences vs. API

The optional `included` schema is in the DJA example.


(scroll left-right to see the two columns.)

<table>
<tr>
<th>API response
</th>
<th>DJA example</th>
</tr>
<tr valign=top align=left>
<td colspan=2>
HTTP links are all present but also have a bunch of `additionalPropN` attributes.

The top-level pagination `meta` object is missing.

The other `meta` objects are present but only have a generic `additionalProp1` attribute rather than `pagination` and `count`.
</td>
</tr>
<tr valign=top>
<td>

```json

"links": {
    "first": "http://localhost:8000/v1/courses/?filter%5Bid%5D=c823b5de-6018-4878-80e9-932d20eaa18a&page%5Bnumber%5D=1",
    "last": "http://localhost:8000/v1/courses/?filter%5Bid%5D=c823b5de-6018-4878-80e9-932d20eaa18a&page%5Bnumber%5D=1",
    "next": null,
    "prev": null
},
"meta": {
    "pagination": {
        "page": 1,
        "pages": 1,
        "count": 1
    }
}
```
</td>
<td>

```json
"links": {
  "first": "string",
  "last": "string",
  "prev": "string",
  "next": "string",
  "additionalProp1": "string",
  "additionalProp2": "string",
  "additionalProp3": "string"
},

```

</td>
</tr>

<tr valign=top align=left>
<td colspan=2>
Extra top-level jsonapi object

This object is in the schema example but not returned by the API.
</td>
</tr>
<tr valign=top>
<td>

```json
"jsonapi": {
    "version": "string",
    "meta": {
      "additionalProp1": {}
    }
  }
```
</td>

<td>
</td>
</tr>
<tr valign=top align=left>
<td colspan=2>
Excess `metas` and `additionalPropN`.
</td>
</tr>

<tr valign=top>
<td>

```json
"relationships": {
    "course_terms": {
        "meta": {
            "count": 1
        },
        "data": [
            {
                "type": "course_terms",
                "id": "a1d34785-cc25-4c1c-9806-9d05a98068c7"
            }
        ],
        "links": {
            "self": "http://localhost:8000/v1/courses/c823b5de-6018-4878-80e9-932d20eaa18a/relationships/course_terms/",
            "related": "http://localhost:8000/v1/courses/c823b5de-6018-4878-80e9-932d20eaa18a/course_terms/"
        }
    }
},
```

</td>
<td>

```json
"relationships": {
    "course_terms": {
        "links": {
            "self": "string",
            "related": "string",
            "additionalProp1": {}
        },
        "data": [
            {
                "type": "string",
                "id": "string",
                "meta": {
                    "additionalProp1": {}
                }
            }
        ],
        "meta": {
            "additionalProp1": {}
        }
    }
}

```
</td>
</tr>
<tr valign=top align=left>
<td colspan=2>
Optional generic included is included in the OAS example but a real included is much more complex.

Following example created by adding `include=course_terms` to the API invocation query parameters.
</td>
</tr>
<tr valign=top>
<td>

```json
"included": [
    {
        "type": "course_terms",
        "id": "a1d34785-cc25-4c1c-9806-9d05a98068c7",
        "attributes": {
            "effective_start_date": null,
            "effective_end_date": null,
            "last_mod_user_name": "admin",
            "last_mod_date": "2018-10-07",
            "term_identifier": "20181ENGL3189X",
            "audit_permitted_code": 0,
            "exam_credit_flag": false
        },
        "relationships": {
            "course": {
                "links": {
                    "self": "http://localhost:8000/v1/course_terms/a1d34785-cc25-4c1c-9806-9d05a98068c7/relationships/course/",
                    "related": "http://localhost:8000/v1/course_terms/a1d34785-cc25-4c1c-9806-9d05a98068c7/course/"
                },
                "data": {
                    "type": "courses",
                    "id": "c823b5de-6018-4878-80e9-932d20eaa18a"
                }
            },
            "instructors": {
                "meta": {
                    "count": 0
                },
                "data": [],
                "links": {
                    "self": "http://localhost:8000/v1/course_terms/a1d34785-cc25-4c1c-9806-9d05a98068c7/relationships/instructors/",
                    "related": "http://localhost:8000/v1/course_terms/a1d34785-cc25-4c1c-9806-9d05a98068c7/instructors/"
                }
            }
        },
        "links": {
            "self": "http://localhost:8000/v1/course_terms/a1d34785-cc25-4c1c-9806-9d05a98068c7/"
        }
    }
],
```

</td>
<td>

```json
"included": [
    {
        "type": "string",
        "id": "string",
        "attributes": {},
        "relationships": {},
        "links": {
            "additionalProp1": "string",
            "additionalProp2": "string",
            "additionalProp3": "string"
        },
        "meta": {
          "additionalProp1": {}
        }
    }
],
```
</td>
</tr>
</table>

