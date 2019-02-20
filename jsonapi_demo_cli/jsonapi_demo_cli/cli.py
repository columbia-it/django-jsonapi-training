import jsonapi_requests
import logging
import argparse
from pprint import pprint, pformat
from jsonapi_demo_cli import MyOAuth2Session

log = logging.getLogger(__name__)

class MyDemo(object):
    """
    A simple demo of doing an OAuth 2 login, and using ORM and "raw" (non-ORM) styles of access to the resources.

    N.B. This code does limited error checking and works best when the jsonapi resource server has loaded the
    standard test cases::

        ./manage.py loaddata myapp/fixtures/testcases.yaml

    """
    def __init__(self, opt):
        self.opt = opt
        self.oauth = None
        self.api = None

    def login(self):
        """
        Perform an OAuth login.
        Handles "all the flavors" of grants.
        """
        # TODO: Take a look at using `jsonapi_requests` to refresh the token automagically.

        log.debug("logging in...")
        if self.oauth is None or self.oauth.access_token is None or self.oauth.refresh_token is None:
            # initial session establishment
            self.oauth = MyOAuth2Session(oauth_server=self.opt.oauth_url,
                                  client_id=self.opt.id,
                                  client_secret=self.opt.secret,
                                  redirect_url=self.opt.redirect_url,
                                  grant=self.opt.grant,
                                  scopes=self.opt.requested_scopes,
                                  refresh_token=self.opt.refresh_token)
            grant_func = {
                'authorization_code': self.oauth.do_authorization_code,
                'refresh_token': self.oauth.do_refresh_token,
                'client_credentials': self.oauth.do_client_credentials,
                'implicit': self.oauth.do_implicit,
            }
            if self.opt.grant in grant_func:
                log.debug("... using {} grant".format(self.opt.grant))
                grant_func[self.opt.grant]()
            else:
                log.error("{} grant not (yet) implemented".format(self.opt.grant))
                exit(1)
            log.debug(pformat(self.oauth.oauth_tokens))
        else:
            # assume an access_token expiration if there's an available refresh_token
            log.debug("... by refreshing the access token with refresh: {}".format(self.oauth.refresh_token))
            if self.oauth.refresh_token:
                self.oauth.do_refresh_token()
        print("logged in access_token: {} and refresh_token: {}".format(self.oauth.access_token,
                                                                        self.oauth.refresh_token))

    def get_api(self):
        ####
        # Initialize the API's root, using OAuth Bearer tokens.
        ####
        self.api = jsonapi_requests.orm.OrmApi.config({
            'API_ROOT': self.opt.api_url,
            'AUTH': self.oauth.BearerAuth(self.oauth.access_token),
            'VALIDATE_SSL': self.opt.redirect_url.startswith('https'),
            'TIMEOUT': 1,
        })

    def try_ORM(self):
        """
        Try out the ORM style
        """

        ####
        # Define classes for each resource type. These look a lot like our models/serializers on the server.
        ####
        class Course(jsonapi_requests.orm.ApiModel):
            class Meta:
                type = 'courses'
                api = self.api

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

            def __str__(self):
                return 'Course %s: %s %s' % (self.id, self.course_identifier, self.course_name)

        class CourseTerm(jsonapi_requests.orm.ApiModel):
            class Meta:
                type = 'course_terms'
                api = self.api

            # attributes:
            term_identifier = jsonapi_requests.orm.AttributeField('term_identifier')
            audit_permitted_code = jsonapi_requests.orm.AttributeField('audit_permitted_code')
            exam_credit_flag = jsonapi_requests.orm.AttributeField('exam_credit_flag')
            # relationships:
            course = jsonapi_requests.orm.RelationField('course')
            instructors = jsonapi_requests.orm.RelationField('instructors')

            def __str__(self):
                return 'CourseTerm %s: %s %s' % (
                self.id, self.term_identifier, self.course.course_identifier if self.course else 'NONE')

        class Person(jsonapi_requests.orm.ApiModel):
            class Meta:
                type = 'people'
                api = self.api

            # attributes:
            name = jsonapi_requests.orm.AttributeField('name')

            def __str__(self):
                return 'Person {}: {}'.format(self.id, self.name)

        class Instructor(jsonapi_requests.orm.ApiModel):
            class Meta:
                type = 'instructors'
                api = self.api

            # relationships
            person = jsonapi_requests.orm.RelationField('person')
            course_terms = jsonapi_requests.orm.RelationField('course_terms')

            def __str__(self):
                return 'Instructor {}'.format(self.id)

        print("\nORM demo\n")
        ####
        # Now try out a few ORM operations:
        #  1. get a list of courses that match the search filter for "accounting"
        #  2. for each course, see which course_term instances they are offered.
        #  3. or each course_term, identifier the instructor(s) teaching that instance.
        #  4. and, if an instructor is teaching more than one course, show the others.
        ####
        courses = Course.get_list(params={'filter[search]': 'accounting'})
        print("Retrieved {} courses on this page".format(len(courses)))
        for c in courses:
            print("{}: terms: {}".format(c, len(c.course_terms)))
            for t in c.course_terms:
                print("  {}".format(t))
                for i in t.instructors:
                    teaching = set([q.course.course_identifier for q in i.course_terms])
                    also_teaching = teaching - set([t.course.course_identifier])
                    if also_teaching:
                        print("    {}: {} (also teaching {})".format(i, i.person.name, also_teaching))
                    else:
                        print("    {}: {}".format(i, i.person.name))

        ####
        # Just show that we can chain ORM relationships right around in a circle:
        ####
        one = courses[0]
        thisterm = one.course_terms[0]
        self_ref = thisterm.course
        print("Expected circular reference: {} {} {}".format(self_ref.id,
                                                             '==' if self_ref.id == one.id else '!=',
                                                             one.id))

    def try_non_ORM(self):
        """
        Mess around with some jsonapi endpoint(s) using the non-ORM style.
        """
        ####
        # Unfortunately the DJA root GET response is not properly-formatted jsonapi so we have to special-case getting
        # the list of collections offered at the root. This is because it is just inheriting from DRF's coreapi schema.
        # There are GET and OPTIONS responses that are both useful, just not jsonapi-formatted. Technically, the jsonapi
        # standard doesn't come into play until we know a given resource collection's URL. Jsonapi doesn't
        # actually describe collections of collections; it's a flat structure.
        #
        # Having said that, let's get the root anyway to find out what collections are below it.
        # (This will like not work correctly with a different jsonapi service)
        ####
        def print_jsonapi_item(i):
            """
            print a collection item (non-ORM style)
            """
            print("-" * 70)
            print("type: {} id: {}:".format(i.type, i.id))
            print("attributes:\n{}".format(pformat(i.attributes, indent=2)))
            print("links:\n{}".format(pformat(i.links, indent=2)))
            print("relationships:")
            for r in i.relationships:
                print("relationship {}:\n{}".format(r, pformat(i.relationships[r].data, indent=2)))
                print("links:\n{}".format(pformat(i.relationships[r].links, indent=2)))

        def print_jsonapi_metadata(response):
            """
            print some response metadata (non-ORM style)
            """
            print("links: {}".format(pformat(response.content.links, indent=2)))
            print("meta: {}".format(pformat(response.content.meta, indent=2)))
            print("there are {} items in this page:".format(len(response.data)))
            if hasattr(response.content, 'included'):
                print("there are also {} included items".format(len(response.content.included)))

        print("\nraw (non-ORM) demo\n")
        root = self.api.endpoint('/').get()
        log.debug('root response (not JSONAPI format):\n{}'.format(pformat(root.payload, indent=2)))
        collections = {}
        for c in root.payload['data']:
            collections[c] = {'url': root.payload['data'][c], 'endpoint': self.api.endpoint(c)}
            print("Collection {}: {}".format(c, root.payload['data'][c]))

        ####
        # Get the first page of the (paginated) /v1/courses collection.
        ####
        print("{}\nGetting first page of courses collection:".format('='*70))
        courses = collections['courses']['endpoint'].get(params={'page[size]': 5})
        print_jsonapi_metadata(courses)
        for c in courses.data:
            print_jsonapi_item(c)

        ####
        # Get the second page of the (paginated) /v1/courses collection.
        # Mix things up a bit and add some filtering and compound document stuff.
        # Query parameters are just passed in the `params` kwarg for get.
        ####
        print("{}\nGetting 2nd page of filtered courses collection:".format('='*70))
        courses = collections['courses']['endpoint'].get(params={'page[size]': 5,
                                                                 'page[number]': 2,
                                                                 'include': 'course_terms'})
        print_jsonapi_metadata(courses)
        print("let's just look at the 3rd item on the 2nd page:")
        print_jsonapi_item(courses.data[2])


def main(args=None):
    parser = argparse.ArgumentParser(usage='%(prog)s [options]')
    parser.add_argument('-o', '--oauth_url', default='https://oauth.cc.columbia.edu',
                        help='base URL of OAuth 2.0/OIDC server [default: %(default)s]')
    parser.add_argument('-a', '--api_url', default='http://localhost:8000/v1',
                        help='base URL of jsonapi resource server [default: %(default)s]')
    parser.add_argument('-i', '--id', help='client ID')
    parser.add_argument('-r', '--redirect_url', default='http://localhost:5432/oauth2client', help='redirect url')
    parser.add_argument('-s', '--secret', help='client secret')
    parser.add_argument('-g', '--grant',
                        choices=['authorization_code', 'implicit', 'refresh_token', 'client_credentials'],
                        default='authorization_code',
                        help='grant type [default: %(default)s]')
    parser.add_argument('-S', '--requested_scopes',
                        default='auth-columbia read openid profile email https://api.columbia.edu/scope/group',
                        help='requested scope(s) [default: %(default)s]')
    parser.add_argument('-R', '--refresh_token', help='login with an existing refresh token')
    parser.add_argument('-d', '--debug', type=int, help='debug logging level')
    opt = parser.parse_args(args)

    logging.basicConfig(level=logging.DEBUG if opt.debug else logging.INFO)

    myapp = MyDemo(opt)
    myapp.login()
    myapp.get_api()
    myapp.try_ORM()
    ####
    # Try to get a new access_token via refresh_token: login() figures it out.
    # If there is no refresh_token then a new web login will pop up for authorization_code or implicit grants.
    ####
    print("refreshing the login")
    myapp.login()
    myapp.try_non_ORM()


if __name__ == '__main__':
    main()
