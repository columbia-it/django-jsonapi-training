#!/usr/bin/env python3
"""
This tests a race condition django-oauth-toolkit in which multiple parallel requests come in with a new access token
that hasn't been cached yet. In order to reproduce:
1. Make sure the version of django-oauth-toolkit==1.2.0

2. Make sure you have a fresh access token (use Postman)
   You can reuse the same token by deleting it via http://127.0.0.1:8000/admin/oauth2_provider/accesstoken/

3. Make sure you are using SQL Server. sqlite3 will always break as it just doesn't handle locking well.
   Also run as multiple workers under gunicorn: ./sqlserver.sh gunicorn -w 4 training.wsgi

4. Run the test. You should see some 500 errors here and, in the server:
request to http://localhost:8000/v1/course_terms?sort=term_identifier status:        200
request to http://localhost:8000/v1/course_terms         status:        500
request to http://localhost:8000/v1/course_terms response data: IntegrityError at /v1/course_terms/
('23000', "[23000] [FreeTDS][SQL Server]Violation of UNIQUE KEY constraint 'oauth2_provider_accesstoken_token_8af090f8_uniq'. Cannot insert duplicate key in object 'dbo.oauth2_provider_accesstoken'. The duplicate key value is (qb4aIqLfwYEVEyjGjH595B5TtfrJ). (2627) (SQLExecDirectW)")

This demonstrates the race condition.

To test the fix, replace django-oauth-toolkit requirement like this:
$ pip uninstall django-oauth-toolkit
$ pip install git+https://github.com/n2ygk/django-oauth-toolkit.git@issue-609
"""


import requests
from threading import Thread
from queue import Queue
from sys import argv

base_url = "http://localhost:8000"
urls = [
    "/v1/courses",
    "/v1/courses?sort=-course_number",
    "/v1/course_terms",
    "/v1/course_terms?sort=term_identifier",
] * 2

if len(argv) != 2:
    print("Usage: {} <access_token>".format(argv[0]))
    exit(1)

access_token = argv[1]

headers = {
    'Authorization': 'Bearer {}'.format(access_token),
}


def print_request_response(url):
    response = requests.request("GET", url, headers=headers)
    print("request to {} status:        {}".format(url, response.status_code))
    if response.status_code == 500:
        r = response.content.decode()
        print(url,r[:r.find("\n\nRequest Method:")])


def send_request():
    url = q.get()
    print_request_response(url)
    q.task_done()


q = Queue(len(urls) * 2)
for i in range(len(urls)):
    t = Thread(target=send_request)
    t.daemon = True
    t.start()
try:
    for url in urls:
        q.put(base_url + url)
    q.join()
except KeyboardInterrupt:
    exit(1)
