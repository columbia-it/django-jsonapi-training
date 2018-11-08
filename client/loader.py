#!/usr/bin/env python
# A simple course data loader with demo data from http://opendataservice.columbia.edu/.
#
# The data is de-normalized and some of the fields don't match, but it's good
# enough to populate the models with some reasonable-looking data.

import json
from pprint import pprint
import requests
import base64
import copy

# what a jsonapi GET/POST response/request should look like
COURSE_POST = {
    "data": {
        "type": "courses",
        # "id": "0c1761cf-ee02-4fdb-8cdd-dfa11ec8ac7a",
        "attributes": {
            "school_bulletin_prefix_code": "CEFKGRUXI",
            "suffix_two": "00",
            "subject_area_code": "IF",
            "course_number": "61044",
            "course_identifier": "AHIS2321W",
            "course_name": "ROME BEYOND ROME-DISC 4",
            "course_description": "blah blah",
            "effective_start_date": None,
            "effective_end_date": None,
            "last_mod_user_name": "alan",
            "last_mod_date": "2018-03-10"
        }
    }
}

COURSE_TERM_POST = {
    "data": {
        "type": "course_terms",
        # "id": "e724c43c-f443-4246-8947-a8bb8953699c",
        "attributes": {
            "term_identifier": "20181",
            "audit_permitted_code": 0,
            "exam_credit_flag": False,
            "effective_start_date": None,
            "effective_end_date": None,
            "last_mod_user_name": "alan",
            "last_mod_date": "2018-03-10"
        }
    }
}

# work around inability to directly PATCH the relationships with the course and/or term
# by separately updating the course relationship
COURSE_TERM_REL_PATCH = {
    "data": [
        {
            "type": "course_terms",
            "id": "e724c43c-f443-4246-8947-a8bb8953699c"
        }
    ]
}


def basic_auth(user,password):
    return base64.b64encode((user + ':' + password).encode("utf-8")).decode("utf-8")


HEADERS = {
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/vnd.api+json",
    "Authorization": "Basic " + basic_auth("admin", "admin123")
}


def post_course(url, data):
    """
    add a course first. NB the opendataservice data is not 1:1 with this schema. Just fake it.
    :param url: url to post to
    :param data: item from ods-courses
    :return: id of newly-created course or None
    """

    cdata = COURSE_POST["data"]["attributes"]
    cdata["school_bulletin_prefix_code"] = data["BulletinFlags"]
    cdata["suffix_two"] = "00"
    cdata["subject_area_code"] = data["DepartmentCode"]
    cdata["course_number"] = data["CallNumber"]
    cdata["course_identifier"] = data["Course"][:9] # chop off the section.
    cdata["course_name"] = data["CourseTitle"]
    cdata["course_description"] = data["CourseSubtitle"]
    cdata["last_mod_user_name"] = "loader"

    response = requests.post(url, data=json.dumps(COURSE_POST), headers=HEADERS)
    if response.status_code == 201:
        return json.loads(response.content)["data"]["id"]
    else:
        print("post_course error {}: {} {}".format(response.status_code, cdata["course_identifier"], json.loads(response.content)))
        return None


def post_term(url, cid, data):
    """
    add a course-term mapping, but can't add the relationship in a single POST due to a bug
    See https://gitlab.cc.columbia.edu/ac45/django-training/issues/1
    TODO: confirm if this is still a bug

    :param url: url to post to
    :param cid: course id to link back to
    :param data: item from ods-course
    :return: URL to newly created term or None
    """

    cdata = COURSE_TERM_POST["data"]["attributes"]
    cdata["term_identifier"] = data["Term"]
    cdata["audit_permitted_code"] = 0
    cdata["exam_credit_flag"] = False
    cdata["last_mod_user_name"] =  "loader"
    response = requests.post(url, data=json.dumps(COURSE_TERM_POST), headers=HEADERS)
    if response.status_code == 201:
        return json.loads(response.content)["data"]["id"]
    else:
        print("post_term error {}: {} {}".format(response.status_code, cid, json.loads(response.content)))
        return None


def patch_course_term_relationship(url, cid, tid):
    """
    update the given course (cid) by PATCHing a course_terms (tid) relationship
    :param url: baseurl for courses
    :param cid: course ID
    :param tid: term ID
    :return: cid or None
    """
    rel = COURSE_TERM_REL_PATCH["data"][0]
    rel["id"] = tid
    response = requests.patch(url + cid + "/relationships/course_terms/", data=json.dumps(COURSE_TERM_REL_PATCH), headers=HEADERS)
    if response.status_code == 200:
        return json.loads(response.content)["data"][0]["id"]
    else:
        print("patch_course_term_relationship error {}: {} {}".format(response.status_code, cid, json.loads(response.content)))
        return None


infile = open('ods-courses.json')
j = json.load(infile)
infile.close()
lastcourse = ""
i = 0
for item in j:
    # need to check for sections of the same course and only add the first.
    if item["Course"][:9] != lastcourse:
        cid = post_course("http://localhost:8000/v1/courses/", item)
        if cid:
            tid = post_term("http://localhost:8000/v1/course_terms/", cid, item)
            if tid:
                patch_course_term_relationship("http://localhost:8000/v1/courses/", cid, tid)
        lastcourse = item["Course"][:9]
        i += 1

print("{} courses added".format(i))


