import jsonapi_requests
import logging
import argparse
from pprint import pprint, pformat
from jsonapi_demo_cli import OAuth2Session

log = logging.getLogger(__name__)

class MyDemo(object):
    def __init__(self, opt):
        self.opt = opt
        self.oauth = None
        self.api = None

    def login(self):
        """
        Perform an OAuth login.
        Handles "all the flavors" of grants.
        Will automatically refresh if a refresh_token is available.
        """
        # TODO: Take a look at using `tenacity` or `jsonapi_requests` to refresh the token automagically.

        log.debug("logging in...")
        if self.oauth is None or self.oauth.access_token is None or self.oauth.refresh_token is None:
            # initial session establishment
            self.oauth = OAuth2Session(oauth_server=self.opt.oauth_url,
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


    @staticmethod
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

    @staticmethod
    def print_jsonapi_metadata(response):
        """
        print some response metadata (non-ORM style)
        """
        print("links: {}".format(pformat(response.content.links, indent=2)))
        print("meta: {}".format(pformat(response.content.meta, indent=2)))
        print("there are {} items in this page:".format(len(response.data)))
        if hasattr(response.content, 'included'):
            print("there are also {} included items".format(len(response.content.included)))

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
        courses = collections['courses']['endpoint'].get()
        self.print_jsonapi_metadata(courses)
        for c in courses.data:
            self.print_jsonapi_item(c)

        ####
        # Get the second page of the (paginated) /v1/courses collection.
        # Mix things up a bit and add some filtering and compound document stuff.
        # Query parameters are just passed in the `params` kwarg for get.
        ####
        print("{}\nGetting 2nd page of filtered courses collection:".format('='*70))
        courses = collections['courses']['endpoint'].get(params={'page[number]': 2,
                                                                 'filter[search]': 'research',
                                                                 'include': 'course_terms'})
        self.print_jsonapi_metadata(courses)
        print("let's just look at the 3rd item on the 2nd page:")
        self.print_jsonapi_item(courses.data[2])

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
    myapp.try_non_ORM()
    ####
    # Try to get a new access_token via refresh_token: login() figures it out.
    # If there is no refresh_token then a new web login will pop up for authorization_code or implicit grants.
    ####
    print("refreshing the login and repeating")
    myapp.login()
    myapp.try_non_ORM()



if __name__ == '__main__':
    main()
