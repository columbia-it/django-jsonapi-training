## A Command Line Client

**UNDER CONSTRUCTION**

See `jsonapi_demo_cli`.

This client demonstrates a rudimentary Python command-line tool that interacts with our demo
JSONAPI project. It:
1. performs an OAuth 2.0 login to acquire the Bearer token. If the type of OAuth 2.0 grant
   requires an browser login, a browser window is opened to perform the login.
2. uses the [`jsonapi-requests`](https://github.com/socialwifi/jsonapi-requests/) library
   to do a few queries.

It's not the best example by far and doesn't (currently) handle automated refresh token use,
among other things.

N.B. there are a number of
[JSONAPI client libraries](https://jsonapi.org/implementations/#client-libraries)
available for many languages. This just uses one of them (and poorly;-).

There are also a number of OAuth 2.0/Openid Connect 1.0 client libraries. I've chosen just
to base this example on [oauthlib](https://github.com/oauthlib/oauthlib)
(which isn't the best for clients; it's more of a server library).

TODO: There's also some OAuth client support in
[requests-oauthlib](https://requests-oauthlib.readthedocs.io) but it's not clear how this
would work `jsonapi-requests`.

### Installation

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

### Usage

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

### Example

```test
(env) jsonapi_demo_cli$ PYTHONPATH=$PWD python jsonapi_demo_cli/__main__.py -i demo_client -s b322573a7176A49FCBEF46554d3381d5 -r http://localhost:5432/oauth2client -o https://oauth-test.cc.columbia.edu -S 'auth-columbia read openid'
Collection courses: http://localhost:8000/v1/courses/
Collection course_terms: http://localhost:8000/v1/course_terms/
Collection people: http://localhost:8000/v1/people/
Collection instructors: http://localhost:8000/v1/instructors/
======================================================================
Getting first page of courses collection:
links: { 'first': 'http://localhost:8000/v1/courses/?page%5Bnumber%5D=1',
  'last': 'http://localhost:8000/v1/courses/?page%5Bnumber%5D=448',
  'next': 'http://localhost:8000/v1/courses/?page%5Bnumber%5D=2',
  'prev': None}
meta: {'pagination': {'count': 4473, 'page': 1, 'pages': 448}}
there are 10 items in this page:
there are also 0 included items
----------------------------------------------------------------------
type: courses id: c823b5de-6018-4878-80e9-932d20eaa18a:
attributes:
{ 'course_description': 'foo bar',
  'course_identifier': 'ENGL3189X',
  'course_name': 'POSTMODERNISM',
  'course_number': '00217',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2019-02-01',
  'last_mod_user_name': 'admin',
  'school_bulletin_prefix_code': 'CEFKX9',
  'subject_area_code': 'ENGB',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/c823b5de-6018-4878-80e9-932d20eaa18a/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': 'a1d34785-cc25-4c1c-9806-9d05a98068c7'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/c823b5de-6018-4878-80e9-932d20eaa18a/course_terms/',
  'self': 'http://localhost:8000/v1/courses/c823b5de-6018-4878-80e9-932d20eaa18a/relationships/course_terms/'}
----------------------------------------------------------------------
type: courses id: e92164fc-4d87-4a27-867a-bd05c1a5d108:
attributes:
{ 'course_description': 'SOCIAL PSYCHOLOGY-LEC',
  'course_identifier': 'PSYC1138X',
  'course_name': 'SOCIAL PSYCHOLOGY-LEC',
  'course_number': '00241',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2018-10-07',
  'last_mod_user_name': 'admin',
  'school_bulletin_prefix_code': 'XCEFK9',
  'subject_area_code': 'PSYB',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/e92164fc-4d87-4a27-867a-bd05c1a5d108/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': '70034667-3159-4f0d-9158-a7e256d37931'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/e92164fc-4d87-4a27-867a-bd05c1a5d108/course_terms/',
  'self': 'http://localhost:8000/v1/courses/e92164fc-4d87-4a27-867a-bd05c1a5d108/relationships/course_terms/'}
----------------------------------------------------------------------
type: courses id: 2b205052-a329-40ee-b5eb-1e8bd2fcc941:
attributes:
{ 'course_description': 'SR SEM: SHORT FICT AMER WOMEN',
  'course_identifier': 'ENGL3907X',
  'course_name': 'SR SEM: SHORT FICT AMER WOMEN',
  'course_number': '00252',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2018-10-07',
  'last_mod_user_name': 'admin',
  'school_bulletin_prefix_code': 'X',
  'subject_area_code': 'ENGB',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/2b205052-a329-40ee-b5eb-1e8bd2fcc941/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': '881fd75c-fca9-4492-b46d-9cf786ac8675'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/2b205052-a329-40ee-b5eb-1e8bd2fcc941/course_terms/',
  'self': 'http://localhost:8000/v1/courses/2b205052-a329-40ee-b5eb-1e8bd2fcc941/relationships/course_terms/'}
----------------------------------------------------------------------
type: courses id: e9decab5-c806-4a60-ae97-000c91d0c7b9:
attributes:
{ 'course_description': 'INTRO TO LANGUAGE & CULTURE',
  'course_identifier': 'ANTH1009V',
  'course_name': 'INTRO TO LANGUAGE & CULTURE',
  'course_number': '00267',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2018-10-07',
  'last_mod_user_name': 'admin',
  'school_bulletin_prefix_code': 'CEFKX',
  'subject_area_code': 'ANTB',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/e9decab5-c806-4a60-ae97-000c91d0c7b9/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': '1d56cd36-86a7-47b1-8cb6-d495b5ce1011'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/e9decab5-c806-4a60-ae97-000c91d0c7b9/course_terms/',
  'self': 'http://localhost:8000/v1/courses/e9decab5-c806-4a60-ae97-000c91d0c7b9/relationships/course_terms/'}
----------------------------------------------------------------------
type: courses id: 6844f209-8b57-4504-995c-2fc6641436c3:
attributes:
{ 'course_description': "THE QUR'AN:A COMPAR PERSPECTV",
  'course_identifier': 'RELI3314V',
  'course_name': "THE QUR'AN:A COMPAR PERSPECTV",
  'course_number': '00269',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2018-10-07',
  'last_mod_user_name': 'admin',
  'school_bulletin_prefix_code': 'XCEFK9',
  'subject_area_code': 'RELB',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/6844f209-8b57-4504-995c-2fc6641436c3/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': '49cba2ec-5a50-4716-ab50-3587fb66372f'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/6844f209-8b57-4504-995c-2fc6641436c3/course_terms/',
  'self': 'http://localhost:8000/v1/courses/6844f209-8b57-4504-995c-2fc6641436c3/relationships/course_terms/'}
----------------------------------------------------------------------
type: courses id: 85f35510-d603-414f-92f9-eb0356b51f71:
attributes:
{ 'course_description': 'foo bar',
  'course_identifier': 'WMST4302W',
  'course_name': "2ND WAVE & JEWISH WOMEN'S ART",
  'course_number': '00295',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2019-02-01',
  'last_mod_user_name': 'admin',
  'school_bulletin_prefix_code': 'RXCEIGFKU',
  'subject_area_code': 'WSTB',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/85f35510-d603-414f-92f9-eb0356b51f71/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': '86d6f2fe-8b9f-4550-bbf6-d33ea383fa6d'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/85f35510-d603-414f-92f9-eb0356b51f71/course_terms/',
  'self': 'http://localhost:8000/v1/courses/85f35510-d603-414f-92f9-eb0356b51f71/relationships/course_terms/'}
----------------------------------------------------------------------
type: courses id: c7d863c5-fe2f-42df-ba8a-8f17504d4699:
attributes:
{ 'course_description': 'FIELD METHOD ARCHAEOLO',
  'course_identifier': 'ANTH2011X',
  'course_name': 'FIELD METHOD ARCHAEOLOGY',
  'course_number': '00301',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2018-10-07',
  'last_mod_user_name': 'admin',
  'school_bulletin_prefix_code': 'CEFKGRUXI',
  'subject_area_code': 'ANTB',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/c7d863c5-fe2f-42df-ba8a-8f17504d4699/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': '9b601a89-3c0e-4bd9-bf2b-0a530f738fe9'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/c7d863c5-fe2f-42df-ba8a-8f17504d4699/course_terms/',
  'self': 'http://localhost:8000/v1/courses/c7d863c5-fe2f-42df-ba8a-8f17504d4699/relationships/course_terms/'}
----------------------------------------------------------------------
type: courses id: 6911e0d5-8abf-4bbd-937a-33ae2949d448:
attributes:
{ 'course_description': 'LAB METHODS ARCHAEOLOGY',
  'course_identifier': 'ANTH2012X',
  'course_name': 'LAB METHODS ARCHAEOLOGY',
  'course_number': '00302',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2018-10-07',
  'last_mod_user_name': 'admin',
  'school_bulletin_prefix_code': 'CEFKGRUXI',
  'subject_area_code': 'ANTB',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/6911e0d5-8abf-4bbd-937a-33ae2949d448/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': '08e07046-68a3-4388-bbc7-50d5ac091edf'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/6911e0d5-8abf-4bbd-937a-33ae2949d448/course_terms/',
  'self': 'http://localhost:8000/v1/courses/6911e0d5-8abf-4bbd-937a-33ae2949d448/relationships/course_terms/'}
----------------------------------------------------------------------
type: courses id: c905b170-9d9f-41fb-bfe4-5af6dfb871a0:
attributes:
{ 'course_description': 'SR SEM:INTL TOPICS URB STDIES',
  'course_identifier': 'URBS3997V',
  'course_name': 'SR SEM:INTL TOPICS URB STUDIES',
  'course_number': '00350',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2018-10-07',
  'last_mod_user_name': 'admin',
  'school_bulletin_prefix_code': 'XCEFK9',
  'subject_area_code': 'URSB',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/c905b170-9d9f-41fb-bfe4-5af6dfb871a0/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': 'b9888866-5244-4601-aa03-a17a8d458b57'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/c905b170-9d9f-41fb-bfe4-5af6dfb871a0/course_terms/',
  'self': 'http://localhost:8000/v1/courses/c905b170-9d9f-41fb-bfe4-5af6dfb871a0/relationships/course_terms/'}
----------------------------------------------------------------------
type: courses id: c4a20c04-5426-49c4-a517-23cde9bd74c2:
attributes:
{ 'course_description': 'RUSSIA AND THE WEST',
  'course_identifier': 'POLS4875W',
  'course_name': 'RUSSIA AND THE WEST',
  'course_number': '00352',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2018-10-07',
  'last_mod_user_name': 'admin',
  'school_bulletin_prefix_code': 'RXCEIGFKU',
  'subject_area_code': 'PLSB',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/c4a20c04-5426-49c4-a517-23cde9bd74c2/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': '3d3219d7-715b-4148-96a1-f360d69de238'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/c4a20c04-5426-49c4-a517-23cde9bd74c2/course_terms/',
  'self': 'http://localhost:8000/v1/courses/c4a20c04-5426-49c4-a517-23cde9bd74c2/relationships/course_terms/'}
======================================================================
Getting 2nd page of filtered courses collection:
links: { 'first': 'http://localhost:8000/v1/courses/?filter%5Bsearch%5D=research&include=course_terms&page%5Bnumber%5D=1',
  'last': 'http://localhost:8000/v1/courses/?filter%5Bsearch%5D=research&include=course_terms&page%5Bnumber%5D=19',
  'next': 'http://localhost:8000/v1/courses/?filter%5Bsearch%5D=research&include=course_terms&page%5Bnumber%5D=3',
  'prev': 'http://localhost:8000/v1/courses/?filter%5Bsearch%5D=research&include=course_terms&page%5Bnumber%5D=1'}
meta: {'pagination': {'count': 184, 'page': 2, 'pages': 19}}
there are 10 items in this page:
there are also 10 included items
let's just look at the 3rd item on the 2nd page:
----------------------------------------------------------------------
type: courses id: a478546a-8629-432d-97ac-9a70aab311e3:
attributes:
{ 'course_description': 'SENIOR RESEARCH SEMINAR',
  'course_identifier': 'AHIS3960X',
  'course_name': 'SENIOR RESEARCH SEMINAR',
  'course_number': '05407',
  'effective_end_date': None,
  'effective_start_date': None,
  'last_mod_date': '2018-10-07',
  'last_mod_user_name': 'admin',
  'school_bulletin_prefix_code': 'XCEFK9',
  'subject_area_code': 'ARHB',
  'suffix_two': '00'}
links:
{ 'self': 'http://localhost:8000/v1/courses/a478546a-8629-432d-97ac-9a70aab311e3/'}
relationships:
relationship course_terms:
DynamicCollection.from_data([{'type': 'course_terms', 'id': '835870fa-87cd-4be3-9050-0542ac725a12'}])
links:
{ 'related': 'http://localhost:8000/v1/courses/a478546a-8629-432d-97ac-9a70aab311e3/course_terms/',
  'self': 'http://localhost:8000/v1/courses/a478546a-8629-432d-97ac-9a70aab311e3/relationships/course_terms/'}
(env) jsonapi_demo_cli$ 
```

### TODO

- Mash up [`jsonapi_requests`](https://github.com/socialwifi/jsonapi-requests/)
  with [`requests_oauthlib`](https://requests-oauthlib.readthedocs.io) 
  perhaps using https://github.com/jd/tenacity#custom-callbacks (which `jsonapi_requests` already uses)
  to automate using a refresh token to get a new access token when the old one expires.
- Look at [`jsonapi_client`](https://github.com/qvantel/jsonapi-client) as an alternative to `jsonapi_requests`. 
