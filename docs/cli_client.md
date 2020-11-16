# A Command Line Client

**UNDER CONSTRUCTION**

See `jsonapi_demo_cli`.

This client demonstrates a rudimentary Python command-line tool that interacts with our demo
JSONAPI project. 

It:
1. performs an OAuth 2.0 login to acquire the Bearer token. If the type of OAuth 2.0 grant
   requires a browser login, a browser window is opened to perform the login.
2. uses the [`jsonapi-requests`](https://github.com/socialwifi/jsonapi-requests/) library
   to do a few queries.

This demo client is overly complicated (I couldn't resist;-) as it automates the web browser popup and
callback handling for the Authorization Code or Implicit grants. Below is a simplified description
of the key stuff you will likely actually need to do if you are writing a "headless" backend client,
probably to implement some sort of "batch" activities where the client backend is trusted (rather than needing
an end-user to login).

## Oauth 2.0 Login

The first step is to end up with a "bearer" Access Token that gets put into the `Authorization` header.
Using [oauthlib](https://github.com/oauthlib/oauthlib) you first initialize the library, which differs
based on the type of grant. You'll want to include a list of requested scopes based on what the Resource Server
(our demo DJA app) requires.

There are a number of OAuth 2.0/Openid Connect 1.0 client libraries. I've chosen just
to base this example on [oauthlib](https://github.com/oauthlib/oauthlib).

TODO: There's also integrated OAuth client support in [requests-oauthlib](https://requests-oauthlib.readthedocs.io)
including automated token refresh.

### OAuth 2.0 Service Endpoints

You need to know the various endpoints of the OAuth2 server. You can hard code them or query the
server itself via the `/.well-known/openid-configuration` URL.

```python
import requests

oauth_server = 'https://oauth-test.cc.columbia.edu'

r = requests.get(oauth_server + '/.well-known/openid-configuration')
if r.status_code == 200:
    oauth_endpoints = r.json()

```

### Oauth 2.0 Client Basic Auth

In most all cases you need to use HTTP Basic Auth to authenticate your client to the OAuth 2.0 Authorization Server
using pre-registered client credentials (`client_id` and `client_secret`). This creates an HTTP header
that looks like `Authorization: Basic YWRtaW46YWRtaW4xMjM=`.

The standard Python `requests` library has an `HTTPBasicAuth()` function that does the right thing.

```python
client_id = 'demo_trusted_client'
client_secret = 's9ht0XNvHEkvXfUhVD1Ka9DtXFxRHfTm'

oauth_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
```

### A Backend (Client Credentials) Client

A "backend" client uses a very simple OAuth 2.0 grant: Client Credentials -- which uses the
OAuth 2.0 `token` endpoint.

Use an instance of oauthlib's `BackendApplicationClient` to `prepare_token_request()` and post it.
(The oauthlib `prepare_*` functions fill in everything needed for the HTTP request except the
authorization info, which we've already set up, above.) 

```python
from oauthlib.oauth2 import BackendApplicationClient

scopes = 'auth-none read'

oauth_client = BackendApplicationClient(client_id)
(token_url, headers, body) = oauth_client.prepare_token_request(oauth_endpoints['token_endpoint'], scope=scopes)
token_response = requests.post(token_url, headers=headers, data=body, auth=oauth_auth)
``` 
A successful token response will look like this:

```json
{
    "access_token": "jAjCraG0uJ7YGXvIDWaCgl3eRDEm",
    "expires_in": 7199,
    "token_type": "Bearer",
}
```

```python
if token_response.status_code == 200:
    access_token = token_response.json()['access_token']
    
```

## JSONAPI client

There are a number of
[JSONAPI client libraries](https://jsonapi.org/implementations/#client-libraries)
available for many languages. You can also just directly manipulate the JSON responses
and requests as we did in the examples with Postman.

The examples use [jsonapi-requests](https://github.com/socialwifi/jsonapi-requests/) which has both
an ORM and raw (non-ORM) style. Let's start with the ORM style. You'll have to define your classes but then operations
are really easy, looking similar to Django's model managers.

### ORM Style

```python
import jsonapi_requests

api_url = 'http://localhost:8000/v1'


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, access_token = None):
        if access_token:
            self.access_token = access_token
    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.access_token
        return r

api = jsonapi_requests.orm.OrmApi.config({
    'API_ROOT': api_url,
    'AUTH': BearerAuth(access_token),
    'VALIDATE_SSL': False,
    'TIMEOUT': 1,
})

class Course(jsonapi_requests.orm.ApiModel):
    class Meta:
        type = 'courses'
        api = api
    # attributes:
    school_bulletin_prefix_code = jsonapi_requests.orm.AttributeField('school_bulletin_prefix_code')
    suffix_two = jsonapi_requests.orm.AttributeField('suffix_two')
    subject_area_code = jsonapi_requests.orm.AttributeField('subject_area_code')
    course_number = jsonapi_requests.orm.AttributeField('course_number')
    course_identifier = jsonapi_requests.orm.AttributeField('course_identifier')
    course_name = jsonapi_requests.orm.AttributeField('course_name')
    course_description = jsonapi_requests.orm.AttributeField('course_description')
    # relationships
    course_terms = jsonapi_requests.orm.RelationField('course_terms')

class CourseTerm(jsonapi_requests.orm.ApiModel):
    class Meta:
        type = 'course_terms'
        api = api
    # attributes:
    term_identifier = jsonapi_requests.orm.AttributeField('term_identifier')
    audit_permitted_code = jsonapi_requests.orm.AttributeField('audit_permitted_code')
    exam_credit_flag = jsonapi_requests.orm.AttributeField('exam_credit_flag')
    # relationships:
    course = jsonapi_requests.orm.RelationField('course')

courses = Course.get_list(params={'filter[search]': 'accounting'})
print("Retrieved {} courses on this page".format(len(courses)))
for c in courses:
    print("Course {}: {} {}".format(c.id, c.course_identifier, c.course_name))

```

Sample exeution of the above: 
```text
django-jsonapi-training$ python
Python 3.6.6 (default, Jul 27 2018, 14:31:43) 
[GCC 4.2.1 Compatible Apple LLVM 9.1.0 (clang-902.0.39.2)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import requests
>>> 
>>> oauth_server = 'https://oauth-test.cc.columbia.edu'
>>> 
>>> r = requests.get(oauth_server + '/.well-known/openid-configuration')
>>> if r.status_code == 200:
...     oauth_endpoints = r.json()
... 
>>> client_id = 'demo_trusted_client'
>>> client_secret = 's9ht0XNvHEkvXfUhVD1Ka9DtXFxRHfTm'
>>> 
>>> oauth_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
>>> from oauthlib.oauth2 import BackendApplicationClient
>>> 
>>> scopes = 'auth-none read'
>>> oauth_client = BackendApplicationClient(client_id)
>>> (token_url, headers, body) = oauth_client.prepare_token_request(oauth_endpoints['token_endpoint'], scope=scopes)
>>> token_response = requests.post(token_url, headers=headers, data=body, auth=oauth_auth)
>>> if token_response.status_code == 200:
...     access_token = token_response.json()['access_token']
... 
>>> import jsonapi_requests
>>> api_url = 'http://localhost:8000/v1'
>>> class BearerAuth(requests.auth.AuthBase):
...     def __init__(self, access_token = None):
...         if access_token:
...             self.access_token = access_token
...     def __call__(self, r):
...         r.headers['Authorization'] = 'Bearer ' + self.access_token
...         return r
... 
>>> api = jsonapi_requests.orm.OrmApi.config({
...     'API_ROOT': api_url,
...     'AUTH': BearerAuth(access_token),
...     'VALIDATE_SSL': False,
...     'TIMEOUT': 1,
... })
>>> class Course(jsonapi_requests.orm.ApiModel):
...     class Meta:
...         type = 'courses'
...         api = api
...     # attributes:
...     school_bulletin_prefix_code = jsonapi_requests.orm.AttributeField('school_bulletin_prefix_code')
...     suffix_two = jsonapi_requests.orm.AttributeField('suffix_two')
...     subject_area_code = jsonapi_requests.orm.AttributeField('subject_area_code')
...     course_number = jsonapi_requests.orm.AttributeField('course_number')
...     course_identifier = jsonapi_requests.orm.AttributeField('course_identifier')
...     course_name = jsonapi_requests.orm.AttributeField('course_name')
...     course_description = jsonapi_requests.orm.AttributeField('course_description')
...     # relationships
...     course_terms = jsonapi_requests.orm.RelationField('course_terms')
... 
>>> class CourseTerm(jsonapi_requests.orm.ApiModel):
...     class Meta:
...         type = 'course_terms'
...         api = api
...     # attributes:
...     term_identifier = jsonapi_requests.orm.AttributeField('term_identifier')
...     audit_permitted_code = jsonapi_requests.orm.AttributeField('audit_permitted_code')
...     exam_credit_flag = jsonapi_requests.orm.AttributeField('exam_credit_flag')
...     # relationships:
...     course = jsonapi_requests.orm.RelationField('course')
... 
>>> courses = Course.get_list(params={'filter[search]': 'accounting'})
>>> print("Retrieved {} courses on this page".format(len(courses)))
Retrieved 2 courses on this page
>>> for c in courses:
...     print("Course {}: {} {}".format(c.id, c.course_identifier, c.course_name))
... 
Course 00fb17bb-e4a0-49a0-a27e-6939e3e04b62: ACCT8122B Accounting for Consultants
Course 016659e9-e29f-49b4-b85d-d25da0724dbb: ACCT7022B Accounting for Value
>>> 
```

N.B. Each RelationField you create must have a corresponding class definition or you'll get a key error.

### Raw (non-ORM) Style
```python
import jsonapi_requests
from pprint import pprint, pformat

api_url = 'http://localhost:8000/v1'


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, access_token = None):
        if access_token:
            self.access_token = access_token
    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.access_token
        return r

api = jsonapi_requests.Api.config({
    'API_ROOT': api_url,
    'AUTH': BearerAuth(access_token),
    'VALIDATE_SSL': False,
    'TIMEOUT': 1,
})

courses = api.endpoint('courses').get(params={'filter[search]': 'research dance', 'include': 'course_terms'})
print("found {} courses that match the filter".format(len(courses.data)))
one = courses.data[0]
pprint(one.attributes, indent=2)
for r in one.relationships:
    print("relationship {}:\n{}".format(r, pformat(one.relationships[r].data, indent=2)))
    print("links:\n{}".format(pformat(one.relationships[r].links, indent=2)))
# take a look at what was included:
print(courses.payload['included'][0]['id'])
pprint(courses.payload['included'][0]['attributes'], indent=2)
```

See the demo app source code for more sophisticated ORM operations.

Following is a sample execution of the above code snippets. Your mileage may vary based on what data is in
your resource server.
```text
django-jsonapi-training$ python
Python 3.6.6 (default, Jul 27 2018, 14:31:43) 
[GCC 4.2.1 Compatible Apple LLVM 9.1.0 (clang-902.0.39.2)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import requests
>>> oauth_server = 'https://oauth-test.cc.columbia.edu'
>>> r = requests.get(oauth_server + '/.well-known/openid-configuration')
>>> if r.status_code == 200:
...     oauth_endpoints = r.json()
... 
>>> client_id = 'demo_trusted_client'
>>> client_secret = 's9ht0XNvHEkvXfUhVD1Ka9DtXFxRHfTm'
>>> oauth_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
>>> from oauthlib.oauth2 import BackendApplicationClient
>>> scopes = 'auth-none read'
>>> oauth_client = BackendApplicationClient(client_id)
>>> (token_url, headers, body) = oauth_client.prepare_token_request(oauth_endpoints['token_endpoint'], scope=scopes)
>>> token_response = requests.post(token_url, headers=headers, data=body, auth=oauth_auth)
>>> token_response
<Response [200]>
>>> if token_response.status_code == 200:
...     access_token = token_response.json()['access_token']
... 
>>> access_token
'KFmOrqrQjLBWHrLZQiAooyvtIxMW'
>>> import jsonapi_requests
>>> from pprint import pprint, pformat
>>> api_url = 'http://localhost:8000/v1'
>>> class BearerAuth(requests.auth.AuthBase):
...     def __init__(self, access_token = None):
...         if access_token:
...             self.access_token = access_token
...     def __call__(self, r):
...         r.headers['Authorization'] = 'Bearer ' + self.access_token
...         return r
... 
>>> api = jsonapi_requests.Api.config({
...     'API_ROOT': api_url,
...     'AUTH': BearerAuth(access_token),
...     'VALIDATE_SSL': False,
...     'TIMEOUT': 1,
... })
>>> courses = api.endpoint('courses').get(params={'filter[search]': 'research dance', 'include': 'course_terms'})
>>> print("found {} courses that match the filter".format(len(courses.data)))
found 1 courses that match the filter
>>> one = courses.data[0]
>>> pprint(one.attributes, indent=2)
{ 'course_description': 'SR PROJECT:RESEARCH FOR DANCE',
  'course_identifier': 'DNCE3592X',
  'course_name': 'SR PROJECT: RESEARCH FOR DANCE',
  'course_number': '03467',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2018-10-07',
  'last_mod_user_name': 'admin',
  'school_bulletin_prefix_code': 'XCEFG',
  'subject_area_code': 'DANB',
  'suffix_two': '00'}
>>> for r in one.relationships:
...     print("relationship {}:\n{}".format(r, pformat(one.relationships[r].data, indent=2)))
...     print("links:\n{}".format(pformat(one.relationships[r].links, indent=2)))
... 
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': 'd7db932c-daf2-426a-8e5b-8df1a4f9ecdb'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/18839a7f-dde3-4dfb-95e8-2b0e4c58d4ce/course_terms/',
  'self': 'http://localhost:8000/v1/courses/18839a7f-dde3-4dfb-95e8-2b0e4c58d4ce/relationships/course_terms/'}
>>> print(courses.payload['included'][0]['id'])
d7db932c-daf2-426a-8e5b-8df1a4f9ecdb
>>> pprint(courses.payload['included'][0]['attributes'], indent=2)
{ 'audit_permitted_code': 0,
  'effective_end_date': None,
  'effective_start_date': None,
  'exam_credit_flag': False,
  'last_mod_date': '2018-10-07',
  'last_mod_user_name': 'admin',
  'term_identifier': '20181DNCE3592X'}
>>> 
```
## Installing and running the demo client

Make sure you have a local pypi repo that has this package installed and:

`pip install demo-jsonapi-cli`

Or, if you don't have the repo:

```text
pip install jsonapi_demo_cli/dist/jsonapi*whl
```
or just run as

```text
cd jsonapi_demo_cli; PYTHONPATH=$PWD python jsonapi_demo_cli/__main__.py
```

```text
usage: jsonapi-demo-cli [options]

optional arguments:
  -h, --help            show this help message and exit
  -o OAUTH_URL, --oauth_url OAUTH_URL
                        base URL of OAuth 2.0/OIDC server [default:
                        https://oauth.cc.columbia.edu]
  -a API_URL, --api_url API_URL
                        base URL of jsonapi resource server [default:
                        http://localhost:8000/v1]
  -i ID, --id ID        client ID
  -r REDIRECT_URL, --redirect_url REDIRECT_URL
                        redirect url
  -s SECRET, --secret SECRET
                        client secret
  -g {authorization_code,implicit,refresh_token,client_credentials}, --grant {authorization_code,implicit,refresh_token,client_credentials}
                        grant type [default: authorization_code]
  -S REQUESTED_SCOPES, --requested_scopes REQUESTED_SCOPES
                        requested scope(s) [default: auth-columbia read openid
                        profile email https://api.columbia.edu/scope/group]
  -R REFRESH_TOKEN, --refresh_token REFRESH_TOKEN
                        login with an existing refresh token
```

## Example

```text
jsonapi-demo-cli -i demo_trusted_client -s s9ht0XNvHEkvXfUhVD1Ka9DtXFxRHfTm -r http://localhost:5432/oauth2client -o https://oauth-test.cc.columbia.edu -g client_credentials -S "auth-none read"
logged in access_token: yUhXV3vn2gZS1aA5wU1AZZTCi2zJ and refresh_token: None

ORM demo

Retrieved 2 courses on this page
Course 00fb17bb-e4a0-49a0-a27e-6939e3e04b62: ACCT8122B Accounting for Consultants: terms: 2
  CourseTerm 52cc86dd-7a78-48b8-a6a5-76c1fc7fc9be: 20181ACCT8122B ACCT8122B
  CourseTerm 00d14ddb-9fb5-4cff-9954-d52fc33217e7: 20191ACCT8122B ACCT8122B
    Instructor 0a879dc6-63d4-4a79-aae6-63ee2b379b32: John Jay (also teaching {'ACCT7022B'})
    Instructor 40678ab5-07fa-4c93-a680-bceda8a34735: Samuel Johnson (also teaching {'ANTH3160V'})
    Instructor aae87c7f-8515-44cf-b1c7-79c6f81cc5c5: Gouverneur Morris
Course 016659e9-e29f-49b4-b85d-d25da0724dbb: ACCT7022B Accounting for Value: terms: 2
  CourseTerm 39ca7b38-f273-4fa3-9494-5a422780aebd: 20181ACCT7022B ACCT7022B
    Instructor 0a879dc6-63d4-4a79-aae6-63ee2b379b32: John Jay (also teaching {'ACCT8122B'})
  CourseTerm 010a7ff7-ef5a-4b36-b3ff-9c34e30b76e8: 20191ACCT7022B ACCT7022B
Expected circular reference: 00fb17bb-e4a0-49a0-a27e-6939e3e04b62 == 00fb17bb-e4a0-49a0-a27e-6939e3e04b62
refreshing the login
logged in access_token: kupU8a4hqbyqoOqJd4awbSBjjRBi and refresh_token: None

raw (non-ORM) demo

Collection courses: http://localhost:8000/v1/courses/
Collection course_terms: http://localhost:8000/v1/course_terms/
Collection people: http://localhost:8000/v1/people/
Collection instructors: http://localhost:8000/v1/instructors/
======================================================================
Getting first page of courses collection:
links: { 'first': 'http://localhost:8000/v1/courses/?page%5Bnumber%5D=1&page%5Bsize%5D=5',
  'last': 'http://localhost:8000/v1/courses/?page%5Bnumber%5D=2&page%5Bsize%5D=5',
  'next': 'http://localhost:8000/v1/courses/?page%5Bnumber%5D=2&page%5Bsize%5D=5',
  'prev': None}
meta: {'pagination': {'count': 10, 'page': 1, 'pages': 2}}
there are 5 items in this page:
there are also 0 included items
----------------------------------------------------------------------
type: courses id: 01ca197f-c00c-4f24-a743-091b62f1d500:
attributes:
{ 'course_description': 'SENIOR RESEARCH ESSAY SEMINAR',
  'course_identifier': 'AMST3704X',
  'course_name': 'SENIOR RESEARCH ESSAY SEMINAR',
  'course_number': '00373',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2018-08-03',
  'last_mod_user_name': 'loader',
  'school_bulletin_prefix_code': 'XCEFK9',
  'subject_area_code': 'AMSB',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/01ca197f-c00c-4f24-a743-091b62f1d500/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': 'f9aa1a51-bf3b-45cf-b1cc-34ce47ca9913'}, {'type': 'course_terms', 'id': '01163a94-fc8f-47fe-bb4a-5407ad1a35fe'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/01ca197f-c00c-4f24-a743-091b62f1d500/course_terms/',
  'self': 'http://localhost:8000/v1/courses/01ca197f-c00c-4f24-a743-091b62f1d500/relationships/course_terms/'}
----------------------------------------------------------------------
type: courses id: 001b55e0-9a60-4386-98c7-4c856bb840b4:
attributes:
{ 'course_description': 'THE BODY AND SOCIETY',
  'course_identifier': 'ANTH3160V',
  'course_name': 'THE BODY AND SOCIETY',
  'course_number': '04961',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2018-08-03',
  'last_mod_user_name': 'loader',
  'school_bulletin_prefix_code': 'XCEFK9',
  'subject_area_code': 'ANTB',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/001b55e0-9a60-4386-98c7-4c856bb840b4/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': '243e2b9c-a3c6-4d40-9b9a-2750d6c03250'}, {'type': 'course_terms', 'id': '00290ba0-ebae-44c0-9f4b-58a5f27240ed'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/001b55e0-9a60-4386-98c7-4c856bb840b4/course_terms/',
  'self': 'http://localhost:8000/v1/courses/001b55e0-9a60-4386-98c7-4c856bb840b4/relationships/course_terms/'}
----------------------------------------------------------------------
type: courses id: 03e32754-3da7-4005-be6b-8de0e088816a:
attributes:
{ 'course_description': 'IND STUDIES-CIVIL ENGIN-SENIOR',
  'course_identifier': 'CIEN3304E',
  'course_name': 'IND STUDIES-CIVIL ENGIN-SENIOR',
  'course_number': '26118',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2018-08-03',
  'last_mod_user_name': 'loader',
  'school_bulletin_prefix_code': 'XCEF',
  'subject_area_code': 'CEEM',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/03e32754-3da7-4005-be6b-8de0e088816a/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': '964ff272-acb8-4adc-9a7e-21a241e63ff1'}, {'type': 'course_terms', 'id': '035c31c5-398d-43b7-a55b-19f6d1472797'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/03e32754-3da7-4005-be6b-8de0e088816a/course_terms/',
  'self': 'http://localhost:8000/v1/courses/03e32754-3da7-4005-be6b-8de0e088816a/relationships/course_terms/'}
----------------------------------------------------------------------
type: courses id: 046741cd-c700-4752-b57a-e37a948ebc44:
attributes:
{ 'course_description': 'FinTech: Consumer Financial Se',
  'course_identifier': 'BUEC7255B',
  'course_name': 'FinTech: Consumer Financial Se',
  'course_number': '72074',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2018-08-03',
  'last_mod_user_name': 'loader',
  'school_bulletin_prefix_code': 'B',
  'subject_area_code': 'BUEC',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/046741cd-c700-4752-b57a-e37a948ebc44/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': 'bca761f7-03f6-4ff5-bbb8-b58467ef3970'}, {'type': 'course_terms', 'id': '0378c6c0-b658-4cf6-b8ba-6fa19614e3aa'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/046741cd-c700-4752-b57a-e37a948ebc44/course_terms/',
  'self': 'http://localhost:8000/v1/courses/046741cd-c700-4752-b57a-e37a948ebc44/relationships/course_terms/'}
----------------------------------------------------------------------
type: courses id: 00fb17bb-e4a0-49a0-a27e-6939e3e04b62:
attributes:
{ 'course_description': 'Accounting for Consultants',
  'course_identifier': 'ACCT8122B',
  'course_name': 'Accounting for Consultants',
  'course_number': '73272',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2018-08-03',
  'last_mod_user_name': 'loader',
  'school_bulletin_prefix_code': 'B',
  'subject_area_code': 'ACCT',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/00fb17bb-e4a0-49a0-a27e-6939e3e04b62/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': '52cc86dd-7a78-48b8-a6a5-76c1fc7fc9be'}, {'type': 'course_terms', 'id': '00d14ddb-9fb5-4cff-9954-d52fc33217e7'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/00fb17bb-e4a0-49a0-a27e-6939e3e04b62/course_terms/',
  'self': 'http://localhost:8000/v1/courses/00fb17bb-e4a0-49a0-a27e-6939e3e04b62/relationships/course_terms/'}
======================================================================
Getting 2nd page of filtered courses collection:
links: { 'first': 'http://localhost:8000/v1/courses/?include=course_terms&page%5Bnumber%5D=1&page%5Bsize%5D=5',
  'last': 'http://localhost:8000/v1/courses/?include=course_terms&page%5Bnumber%5D=2&page%5Bsize%5D=5',
  'next': None,
  'prev': 'http://localhost:8000/v1/courses/?include=course_terms&page%5Bnumber%5D=1&page%5Bsize%5D=5'}
meta: {'pagination': {'count': 10, 'page': 2, 'pages': 2}}
there are 5 items in this page:
there are also 8 included items
let's just look at the 3rd item on the 2nd page:
----------------------------------------------------------------------
type: courses id: 02e2e004-326e-4be8-aecc-aa67ece50fdf:
attributes:
{ 'course_description': 'MODERN iOS APPLICATION DEVELOP',
  'course_identifier': 'COMS3102W',
  'course_name': 'DEVELOPMENT TECHNOLOGY',
  'course_number': '84695',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2018-08-03',
  'last_mod_user_name': 'loader',
  'school_bulletin_prefix_code': 'RXCEIGF2U',
  'subject_area_code': 'COMS',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/02e2e004-326e-4be8-aecc-aa67ece50fdf/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': '2d763c14-a566-4600-860f-329e44cbbd4a'}, {'type': 'course_terms', 'id': '02e877b2-35c4-47d4-b72c-25bab1e87065'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/02e2e004-326e-4be8-aecc-aa67ece50fdf/course_terms/',
  'self': 'http://localhost:8000/v1/courses/02e2e004-326e-4be8-aecc-aa67ece50fdf/relationships/course_terms/'}
```

## TODO

- Mash up [`jsonapi_requests`](https://github.com/socialwifi/jsonapi-requests/)
  with [`requests_oauthlib`](https://requests-oauthlib.readthedocs.io) 
  perhaps using https://github.com/jd/tenacity#custom-callbacks (which `jsonapi_requests` already uses)
  to automate using a refresh token to get a new access token when the old one expires.
- Look at [`jsonapi_client`](https://github.com/qvantel/jsonapi-client) as an alternative to `jsonapi_requests`. 
