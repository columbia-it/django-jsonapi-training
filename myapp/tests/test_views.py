import json
import math
from datetime import datetime, timedelta, timezone
from unittest import expectedFailure, skip

from django.contrib.auth.models import Permission, User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from myapp.models import Course, CourseTerm
from oauth import models as oauth_models

HEADERS = {
    'HTTP_ACCEPT': 'application/vnd.api+json',
    'content_type': 'application/vnd.api+json'
}

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

COURSE_POST_WITH_REL = {
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
        },
        "relationships": {
            "course_terms": {
                "data": [{
                    "type": "course_terms",
                    "id": "e2060fb7-bc0e-4259-8077-2b678fff0c5f"
                }]
            }
        }
    }
}

COURSE_TERM_POST = {
    "data": {
        "type": "course_terms",
        # "id": "e724c43c-f443-4246-8947-a8bb8953699c",
        "attributes": {
            "term_identifier": "20181FILM3119X",
            "audit_permitted_code": 0,
            "exam_credit_flag": False,
            "effective_start_date": None,
            "effective_end_date": None,
            "last_mod_user_name": "alan",
            "last_mod_date": "2018-03-10"
        }
    }
}

COURSE_TERM_REL_PATCH = {
    "data": [{
        "type": "course_terms",
        "id": "e724c43c-f443-4246-8947-a8bb8953699c"
    }]
}


class DJATestCase(APITestCase):
    """
    test cases using Django REST Framework drf-json-api (DJA)
    """
    # TODO: add tests of query parameters: page, filter, fields, sort, include, and combinations thereof
    # TODO: add failure test cases (e.g. get of related where the id is invalid returns 500 instead of 404).
    fixtures = ('auth', 'oauth2', 'testcases',)

    def setUp(self):
        # Users are defined in 'auth' fixture:
        # | username | password       | staff   | su        | group memberships |
        # | -------- | -------------- | -----   | --------- | ----------------- |
        # | admin    | admin123       | &#9745; | &#9745;   | (none)            |
        # | user1    | user1password1 | &#9745; |           | team-a, team-c    |
        # | user2    | user2password2 | &#9745; |           | team-a, team-b    |
        # | user3    | user3password3 | &#9745; |           | (none)            |
        self.read_write_user = User.objects.filter(username='user1').first()
        # `somebody` can view course but not anything else
        self.someuser = User.objects.create_user('somebody', is_superuser=False)
        self.someuser.user_permissions.add(Permission.objects.get(codename='view_course').id)
        # `nobody` has no permissions
        self.noneuser = User.objects.create_user('nobody', is_superuser=False)
        # most tests just use the read_write_user
        self.user1_token = oauth_models.MyAccessToken(  # nosec B106
            token='User1Token',
            user=self.read_write_user,
            expires=datetime.isoformat(datetime.now(tz=timezone.utc)+timedelta(seconds=3600)),
            scope='auth-columbia demo-djt-sla-bronze read create update openid '
                  'profile email https://api.columbia.edu/scope/group',
            userinfo='{"sub": "user1", "given_name": "First", "family_name": "User", "name": "First User", '
                     '"email": "user1@example.com", "https://api.columbia.edu/claim/group": "team-a team-c"}'
        )
        self.user1_token.save()
        # self.client.force_authenticate(user=self.read_write_user)
        HEADERS['Authorization'] = 'Bearer User1Token'
        self.courses = Course.objects.all()
        self.courses_url = reverse('course-list')
        self.course_terms = CourseTerm.objects.all()
        self.course_terms_url = reverse('courseterm-list')

    def test_post_course_term(self):
        response = self.client.post(self.courses_url,
                                    data=json.dumps(COURSE_POST),
                                    **HEADERS)
        self.assertEqual(response.status_code, 201, msg=response.content)
        course_id = json.loads(response.content)['data']['id']
        # violate database constraint: get a course_identifier uniqueness error
        response = self.client.post(
            self.courses_url, data=json.dumps(COURSE_POST), **HEADERS)
        self.assertEqual(response.status_code, 400, msg=response.content)
        # expect this error: {"errors":[{"detail": "course with this course identifier already exists."}]}
        self.assertEqual('course with this course identifier already exists.',
                         json.loads(response.content)['errors'][0]['detail'])
        response = self.client.post(self.course_terms_url,
                                    data=json.dumps(COURSE_TERM_POST),
                                    **HEADERS)
        self.assertEqual(response.status_code, 201, msg=response.content)
        term_id = json.loads(response.content)['data']['id']
        # now patch in the relationship
        COURSE_TERM_REL_PATCH['data'][0]['id'] = term_id
        response = self.client.patch(
            self.courses_url + course_id + "/relationships/course_terms/",
            data=json.dumps(COURSE_TERM_REL_PATCH),
            **HEADERS)
        self.assertEqual(response.status_code, 200, msg=response.content)

    def test_post_primary_rel(self):
        """
        I should be able to POST the primary data and relationships together.
        """
        response = self.client.post(
            self.course_terms_url,
            data=json.dumps(COURSE_TERM_POST),
            **HEADERS)
        self.assertEqual(response.status_code, 201, msg=response.content)
        term_id = json.loads(response.content)['data']['id']
        COURSE_POST_WITH_REL['data']['relationships']['course_terms']['data'][
            0]['id'] = term_id
        # print("posting:")
        # pprint(COURSE_POST_WITH_REL)
        response = self.client.post(
            self.courses_url,
            data=json.dumps(COURSE_POST_WITH_REL),
            **HEADERS)
        self.assertEqual(response.status_code, 201, msg=response.content)
        # course_id = json.loads(response.content)['data']['id']
        # print("course_id: {}".format(course_id))
        # print("response:")
        # pprint(json.loads(response.content))
        j = json.loads(
            response.content)['data']['relationships']['course_terms']['data']
        self.assertEqual(len(j), 1, msg="missing relationships")
        self.assertEqual(
            j[0]['id'],
            term_id,
            msg="missing relationship data for {}".format(term_id))

    @skip("test_patch_primary_rel not yet implemented")
    def test_patch_primary_rel(self):
        """
        Make sure we can PATCH the attributes *and* relationships
        """
        # TODO: I should be able to PATCH the primary data and updated relationships.
        pass

    @skip("test_patch_rel not yet implemented")
    def test_patch_rel(self):
        """
        See https://jsonapi.org/format/#crud-updating-resource-relationships
        """
        # TODO: I should be able to PATCH the relationships.

        pass

    def test_page_size(self):
        """
        test rest_framework_json_api.pagination.JsonApiPageNumberPagination: page[size] and page[number]
        """
        response = self.client.get(self.courses_url,
                                   data={"page[size]": 3, "page[number]": 2},
                                   **HEADERS)
        j = json.loads(response.content)
        # pprint(j)
        self.assertEqual(len(j['data']), 3)
        # pprint(j['meta']['pagination'])
        self.assertEqual(j['meta']['pagination']['count'], len(self.courses))
        self.assertEqual(j['meta']['pagination']['page'], 2)
        self.assertEqual(j['meta']['pagination']['pages'],
                         math.ceil(len(self.courses) / 3))
        self.assertEqual(
            j['links']['next'],
            'http://testserver/v1/courses/?page%5Bnumber%5D=3&page%5Bsize%5D=3'
        )

    def test_filter_search(self):
        """
        test keyword search (rest_framework.filters.SearchFilter): filter[all]=keywords
        """
        response = self.client.get(self.courses_url,
                                   data={"filter[search]": "research seminar"},
                                   **HEADERS)
        self.assertEqual(response.status_code, 200, msg=response.content)
        j = json.loads(response.content)
        self.assertGreater(len(j['data']), 0)
        for c in j['data']:
            attr = c['attributes']
            self.assertTrue(
                'research' in (attr['course_name'] + ' ' +
                               attr['course_description']).lower()
                and 'seminar' in (attr['course_name'] + ' ' +
                                  attr['course_description']).lower())

        response = self.client.get(self.courses_url,
                                   data={"filter[search]": "nonesuch"},
                                   **HEADERS)
        self.assertEqual(response.status_code, 200, msg=response.content)
        j = json.loads(response.content)
        self.assertEqual(len(j['data']), 0)

    def test_filter_fields(self):
        """
        test field search (django_filters.rest_framework.DjangoFilterBackend): filter[<field>]=values
        """
        response = self.client.get(self.courses_url,
                                   data={"filter[subject_area_code]": "ANTB"},
                                   **HEADERS)
        self.assertEqual(response.status_code, 200, msg=response.content)
        j = json.loads(response.content)
        self.assertEqual(
            len(j['data']),
            len([
                k for k in self.courses
                if k.subject_area_code == 'ANTB'
            ]))

    def test_filter_fields_union_list(self):
        """
        test field for a list of values (ORed): ?filter[field.in]=ANTB,BIOB,XXXX
        """
        response = self.client.get(self.courses_url,
                                   data={"filter[subject_area_code.in]": "ANTB,BIOB,XXXX"},
                                   **HEADERS)
        j = response.json()
        self.assertEqual(
            len(j['data']),
            len([
                k for k in self.courses
                if k.subject_area_code == 'ANTB'
            ]) + len([
                k for k in self.courses
                if k.subject_area_code == 'BIOB'
            ]) + len([
                k for k in self.courses
                if k.subject_area_code == 'XXXX'
            ]),
            msg="filter field list (union)")

    def test_filter_fields_intersection(self):
        """
        test fields (ANDed): ?filter[subject_area_code]=ANTB&filter[course_number]=1234
        """
        response = self.client.get(self.courses_url,
                                   data={"filter[subject_area_code]": "ANTB",
                                         "filter[school_bulletin_prefix_code]": "XCEFK9"},
                                   **HEADERS)
        self.assertEqual(response.status_code, 200)
        j = json.loads(response.content)
        self.assertEqual(
            len(j['data']),
            len([
                k for k in self.courses
                if k.subject_area_code == 'ANTB'
                and k.school_bulletin_prefix_code == 'XCEFK9'
            ]))

    def test_sparse_fieldsets(self):
        """
        test sparse fieldsets
        """
        response = self.client.get("{}{}/".format(self.courses_url, self.courses[5].id),
                                   data={"fields[courses]": "course_name,course_description"},
                                   **HEADERS)
        self.assertEqual(response.status_code, 200)
        j = json.loads(response.content)
        self.assertEqual(len(j['data']['attributes']), 2)
        self.assertIn('course_name', j['data']['attributes'])
        self.assertIn('course_description', j['data']['attributes'])

    def test_sort(self):
        """
        test sort
        """
        response = self.client.get(self.courses_url,
                                   data={"sort": "subject_area_code,-course_number"},
                                   **HEADERS)
        j = json.loads(response.content)
        areas = [c['attributes']['subject_area_code'] for c in j['data']]
        sorted_areas = [
            c['attributes']['subject_area_code'] for c in j['data']
        ]
        sorted_areas.sort()
        self.assertEqual(areas, sorted_areas)
        prev_area = None
        prev_code = None
        for c in j['data']:
            area = c['attributes']['subject_area_code']
            code = c['attributes']['course_number']
            if area == prev_area:
                self.assertLess(code, prev_code)
            prev_code = code
            prev_area = area

    def test_sort_badfield(self):
        """
        test sort of nonexistent field
        """
        response = self.client.get(self.courses_url,
                                   data={"sort": "nonesuch,-not_a_field,subject_area_code"},
                                   **HEADERS)
        self.assertEqual(response.status_code, 400, msg=response.content)

    def test_include(self):
        """
        test include
        """
        response = self.client.get(self.courses_url,
                                   data={"include": "course_terms"},
                                   **HEADERS)
        j = response.json()
        self.assertIn('included', j)
        self.assertEqual(len(j['included']), sum([len(k.course_terms.all()) for k in self.courses]))
        kids = [str(k.id) for k in self.courses]
        for i in j['included']:
            self.assertIn(i['relationships']['course']['data']['id'], kids)

    def test_related_course_course_terms(self):
        """
        test toMany relationship and related links for courses.related.course_terms
        """
        # look up a random course
        course_response = self.client.get("{}{}/".format(self.courses_url, self.courses[5].id),
                                          **HEADERS)
        self.assertEqual(course_response.status_code, 200, msg=course_response.content)
        course = course_response.json()

        # check the relationship link /courses/<id>/relationships/course_terms/
        relationship_link = course['data']['relationships']['course_terms']['links']['self']
        relationship_response = self.client.get(relationship_link, **HEADERS)
        self.assertEqual(relationship_response.status_code, 200, msg=relationship_response.content)
        relationship = relationship_response.json()
        # check the self link:
        self.assertEqual(relationship_link, relationship['links']['self'])
        # confirm that the list of relationships returned for URL /courses/<id>/ matches the list
        # for URL /courses/<id>/relationships/course_terms/
        self.assertEqual(course['data']['relationships']['course_terms']['data'],
                         relationship['data'],
                         msg="course relationships data and self link data mismatch")

        # check the related link /courses/<id>/course_terms/
        related_link = course['data']['relationships']['course_terms']['links']['related']
        related_response = self.client.get(related_link, **HEADERS)
        self.assertEqual(related_response.status_code, 200, msg=related_response.content)
        related = related_response.json()
        # compare resource identifiers from course_response with those from the related link URL
        # N.B. the `data` for the former is only [{"type": <type>, "id": <id>}, ...] while the
        # later includes `attributes` and so on. Slice out just the type,id into course_term_res_ids:
        course_term_res_ids = [{'type': k['type'], 'id': k['id']} for k in related['data']]
        self.assertEqual(course['data']['relationships']['course_terms']['data'],
                         course_term_res_ids)
        # self link is not present. Should it be?
        # self.assertEqual(related_link, related['links']['self'])

        # look up the /course_terms/<id>. It should be the same content as the related link's
        course_terms_data = []
        for res_id in course_term_res_ids:
            course_term_response = self.client.get("{}{}/".format(self.course_terms_url, res_id['id']),
                                                   **HEADERS)
            self.assertEqual(course_term_response.status_code, 200, msg=course_term_response.content)
            course_term = course_term_response.json()
            course_terms_data.append(course_term['data'])
        self.assertEqual(course_terms_data, related['data'])

    def test_related_course_terms_course(self):
        """
        test toOne relationship and related links for course_terms.related.course
        """
        # look up a random course_term
        course_term_response = self.client.get("{}{}/".format(self.course_terms_url, self.course_terms[5].id),
                                               **HEADERS)
        self.assertEqual(course_term_response.status_code, 200, msg=course_term_response.content)
        course_term = course_term_response.json()

        # check the relationship link /course_terms/<id>/relationships/course/
        relationship_link = course_term['data']['relationships']['course']['links']['self']
        relationship_response = self.client.get(relationship_link, **HEADERS)
        self.assertEqual(relationship_response.status_code, 200, msg=relationship_response.content)
        relationship = relationship_response.json()
        # check the self link:
        self.assertEqual(relationship_link, relationship['links']['self'])
        # confirm that the list of relationships returned for URL /course_terms/<id>/ matches the list
        # for URL /course_terms/<id>/relationships/course/
        self.assertEqual(course_term['data']['relationships']['course']['data'],
                         relationship['data'],
                         msg="course_term relationships data and self link data mismatch")

        # check the related link /course_terms/<id>/course/
        related_link = course_term['data']['relationships']['course']['links']['related']
        related_response = self.client.get(related_link, **HEADERS)
        self.assertEqual(related_response.status_code, 200, msg=related_response.content)
        related = related_response.json()
        # N.B. data is singular for a toOne relationship
        # Compare resource identifier from course_term_response with those from the related link URL
        # The later includes `attributes` and so on. Slice out just the type,id into course_res_id:
        course_res_id = {'type': related['data']['type'], 'id': related['data']['id']}
        self.assertEqual(course_term['data']['relationships']['course']['data'],
                         course_res_id)

        # look up the /courses/<id>. It should be the same content as the related link's
        course_response = self.client.get("{}{}/".format(self.courses_url, course_res_id['id']),
                                          **HEADERS)
        self.assertEqual(course_response.status_code, 200, msg=course_response.content)
        course = course_response.json()
        self.assertEqual(course['data'], related['data'])

    @expectedFailure
    def test_permission_course_course_terms(self):
        """
        See if permissions are correctly implemented.
        """
        # authenticate as user with no permissions:
        self.client.force_authenticate(user=self.noneuser)
        course_response = self.client.get("{}{}/".format(self.courses_url, self.courses[5].id),
                                          **HEADERS)
        self.assertEqual(course_response.status_code, 403, msg=course_response.content)
        self.assertIn("You do not have permission", course_response.json()['errors'][0]['detail'])

        # authenticate as user with model permission to view course but not course_term
        self.client.force_authenticate(user=self.someuser)
        # Look up a random course. In theory the course_terms should be suppressed. In practice, not so.
        course_response = self.client.get("{}{}/".format(self.courses_url, self.courses[5].id),
                                          data={"include": "course_terms"},
                                          **HEADERS)
        self.assertEqual(course_response.status_code, 200, msg=course_response.content)
        course = course_response.json()
        # this should return zero (I think) but instead course_terms inherits permissions from course.
        self.assertEqual(len(course['data']['relationships']['course_terms']['data']), 0)

        # put back the default user
        self.client.force_authenticate(user=self.read_write_user)

    def test_permission_course_terms(self):
        """
        confirm that `somebody` lacks course_terms view permission
        """
        self.client.force_authenticate(user=self.someuser)
        # Look up a random course. In theory the course_terms should be suppressed. In practice, not so.
        term_response = self.client.get("{}{}/".format(self.course_terms_url, self.course_terms[5].id),
                                        **HEADERS)
        self.assertEqual(term_response.status_code, 403, msg=term_response.content)
        term = term_response.json()
        self.assertIn("You do not have permission", term['errors'][0]['detail'])

        # put back the default user
        self.client.force_authenticate(user=self.read_write_user)
