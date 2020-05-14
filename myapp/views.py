from django_filters import rest_framework as filters
from oauth2_provider.contrib.rest_framework import (
    OAuth2Authentication, TokenMatchesOASRequirements)
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
# from rest_framework_json_api.schemas.openapi import AutoSchema as JSONAPIAutoSchema
from rest_framework_json_api.views import ModelViewSet, RelationshipView

from myapp import (__author__, __copyright__, __license__, __license_url__,
                   __title__, __version__)
from myapp.models import Course, CourseTerm, Instructor, Person
from myapp.serializers import (CourseSerializer, CourseTermSerializer,
                               InstructorSerializer, PersonSerializer)
from oauth.oauth2_introspection import HasClaim


# TODO: define claims for demo_djt_view & _upd:
class MyClaimPermission(HasClaim):
    """
    Use OIDC claim 'https://api.columbia.edu/claim/group' to determine permission
    to create/update/delete stuff: If the user has the claim `demo_d_demo2`, then
    they can do writes. Read access doesn't require a claim.
    """
    #: in order to be able to do a write, the user must have claim `demo_d_demo2`
    WRITE_CLAIM = 'demo_d_demo2'
    #: any user can do a read (empty string indicates so vs. None which means deny).
    READ_CLAIM = ''
    #: the name of our custom claim group
    claim = 'https://api.columbia.edu/claim/group'
    #: mapping of HTTP methods to required claim group values
    claims_map = {
        'GET': READ_CLAIM,
        'HEAD': READ_CLAIM,
        'OPTIONS': READ_CLAIM,
        'POST': WRITE_CLAIM,
        'PATCH': WRITE_CLAIM,
        'DELETE': WRITE_CLAIM,
        }


class MyDjangoModelPermissions(DjangoModelPermissions):
    """
    Override `DjangoModelPermissions <https://docs.djangoproject.com/en/dev/topics/auth/#permissions>`_
    to require view permission as well: The default allows view by anybody.
    """
    #: the usual permissions map plus GET. Also, we omit PUT since we only use PATCH with {json:api}.
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        # PUT not allowed by JSON:API; use PATCH
        # 'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class AuthnAuthzMixIn(object):
    """
    Common Authn/Authz mixin for all View and ViewSet-derived classes:
    """
    #: In production Oauth2 is preferred; Allow Basic and Session for testing and browseable API.
    #: (authentication_classes is an implied OR list)
    authentication_classes = (OAuth2Authentication, BasicAuthentication, SessionAuthentication,)
    #: permissions are any one of:
    #: 1. auth-columbia scope, which means there's an authenticated user, plus required claim, or
    #: 2. auth-none scope (a server-to-server integration) where there's no authenticated user, or
    #: 3. an authenticated user (session or basic auth) using user-based model permissions.
    # which only support & and |.
    permission_classes = [
        (TokenMatchesOASRequirements & IsAuthenticated & MyClaimPermission)
        | (TokenMatchesOASRequirements & ~IsAuthenticated)
        | (IsAuthenticated & MyDjangoModelPermissions)
    ]
    # TODO: replace cas-tsc-sla-gold scope with demo-djt-sla-bronze once available in oauth-test
    #: Implicit/Authorization code scopes
    CU_SCOPES = ['auth-columbia', 'cas-tsc-sla-gold', 'openid', 'https://api.columbia.edu/scope/group']
    #: Client Credentials scopes
    NONE_SCOPES = ['auth-none', 'cas-tsc-sla-gold']
    #: allow either CU_SCOPES or NONE_SCOPES
    required_alternate_scopes = {
        'OPTIONS': [['read']],
        'HEAD': [CU_SCOPES + ['read'], NONE_SCOPES + ['read']],
        'GET': [CU_SCOPES + ['read'], NONE_SCOPES + ['read']],
        'POST': [CU_SCOPES + ['create'], NONE_SCOPES + ['create']],
        'PATCH': [CU_SCOPES + ['update'], NONE_SCOPES + ['update']],
        'DELETE': [CU_SCOPES + ['delete'], NONE_SCOPES + ['delete']],
    }


class SchemaMixin(object):
    """
    (temporarily deprecated) OAS 3.0 schema stuff pending updates to DJA to support it officially.
    """
    #: fill in some of the openapi schema
    openapi_schema = {
        'info': {
            'version': __version__,
            'title': __title__,
            'description':
                '![alt-text](https://cuit.columbia.edu/sites/default/files/logo/CUIT_Logo_286_web.jpg "CUIT logo")'
                '\n'
                '\n'
                '\n'
                'A sample API that uses courses as an example to demonstrate representing\n'
                '[JSON:API 1.0](http://jsonapi.org/format) in the OpenAPI 3.0 specification.\n'
                '\n'
                '\n'
                'See [https://columbia-it-django-jsonapi-training.readthedocs.io]'
                '(https://columbia-it-django-jsonapi-training.readthedocs.io)\n'
                'for more about this.\n'
                '\n'
                '\n' + __copyright__,
            'contact': {
                'name': __author__
            },
            'license': {
                'name': __license__,
                'url': __license_url__
            }
        },
        'servers': [
            {'url': 'https://localhost/v1', 'description': 'local docker'},
            {'url': 'http://localhost:8000/v1', 'description': 'local dev'},
            {'url': 'https://ac45devapp01.cc.columbia.edu/v1', 'description': 'demo'},
            {'url': '{serverURL}', 'description': 'provide your server URL',
             'variables': {'serverURL': {'default': 'http://localhost:8000/v1'}}}
        ]
    }
    # schema = JSONAPIAutoSchema(openapi_schema=openapi_schema)


class CourseBaseViewSet(AuthnAuthzMixIn, ModelViewSet):
    """
    Base ViewSet for all our ViewSets:

    - Adds Authn/Authz
    """


usual_rels = ('exact', 'lt', 'gt', 'gte', 'lte', 'in')
text_rels = ('icontains', 'iexact', 'contains')


class CourseViewSet(CourseBaseViewSet):
    __doc__ = Course.__doc__
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    #: See https://docs.djangoproject.com/en/stable/ref/models/querysets/#field-lookups for all the possible filters.
    filterset_fields = {
        'id': usual_rels,
        'subject_area_code': usual_rels,
        'course_name': ('exact', ) + text_rels,
        'course_description': text_rels + usual_rels,
        'course_identifier': text_rels + usual_rels,
        'course_number': ('exact', ),
        'course_terms__term_identifier': usual_rels,
        'school_bulletin_prefix_code': ('exact', 'regex'),
    }
    #: Keyword searches are across these fields.
    search_fields = ('course_name', 'course_description', 'course_identifier',
                     'course_number')


class CourseTermViewSet(CourseBaseViewSet):
    __doc__ = CourseTerm.__doc__
    queryset = CourseTerm.objects.all()
    serializer_class = CourseTermSerializer
    #: defined filter[] names
    filterset_fields = {
        'id': usual_rels,
        'term_identifier': usual_rels,
        'audit_permitted_code': ['exact'],
        'exam_credit_flag': ['exact'],
        'course__id': usual_rels,
    }
    #: Keyword searches are just this one field.
    search_fields = ('term_identifier', )


class PersonViewSet(CourseBaseViewSet):
    __doc__ = Person.__doc__
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filterset_fields = {}
    search_fields = ('name', 'instructor__course_terms__course__course_name')

    class Meta:
        """
        In addition to specific filters defined above, also generate some automatic filters.
        """
        model = Person
        fields = {
            'id': usual_rels,
            'name': usual_rels,
        }


class InstructorFilterSet(filters.FilterSet):
    """
    Extend :py:class:`django_filters.rest_framework.FilterSet` for the Instructor model

    Includes a filter "alias" for a chained search from instructor->course_term->course
    """
    #: `filter[course_name]` is an alias for the path `course_terms.course.course_name`
    course_name = filters.CharFilter(field_name="course_terms__course__course_name", lookup_expr="iexact")
    #: `filter[course_name_gt]` for greater-than, etc.
    course_name__gt = filters.CharFilter(field_name="course_terms__course__course_name", lookup_expr="gt")
    course_name__gte = filters.CharFilter(field_name="course_terms__course__course_name", lookup_expr="gte")
    course_name__lt = filters.CharFilter(field_name="course_terms__course__course_name", lookup_expr="lt")
    course_name__lte = filters.CharFilter(field_name="course_terms__course__course_name", lookup_expr="lte")
    #: `filter[name]` is an alias for the path `course_terms.instructor.person.name`
    name = filters.CharFilter(field_name="course_terms__instructor__person__name", lookup_expr="iexact")
    #: `filter[name_gt]` for greater-than, etc.
    name__gt = filters.CharFilter(field_name="course_terms__instructor__person__name", lookup_expr="gt")
    name__gte = filters.CharFilter(field_name="course_terms__instructor__person__name", lookup_expr="gte")
    name__lt = filters.CharFilter(field_name="course_terms__instructor__person__name", lookup_expr="lt")
    name__lte = filters.CharFilter(field_name="course_terms__instructor__person__name", lookup_expr="lte")

    class Meta:
        """
        In addition to specific filters defined above, also generate some automatic filters.
        """
        model = Instructor
        fields = {
            'id': usual_rels,
        }


class InstructorViewSet(CourseBaseViewSet):
    __doc__ = Instructor.__doc__
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    filterset_class = InstructorFilterSet
    search_fields = ('person__name', 'course_terms__course__course_name')


class CourseRelationshipView(AuthnAuthzMixIn, RelationshipView):
    """
    View for courses.relationships
    """
    queryset = Course.objects
    self_link_view_name = 'course-relationships'


class CourseTermRelationshipView(AuthnAuthzMixIn, RelationshipView):
    """
    View for course_terms.relationships
    """
    queryset = CourseTerm.objects
    self_link_view_name = 'course_term-relationships'


class InstructorRelationshipView(AuthnAuthzMixIn, RelationshipView):
    """
    View for instructors.relationships
    """
    queryset = Instructor.objects
    self_link_view_name = 'instructor-relationships'


class PersonRelationshipView(AuthnAuthzMixIn, RelationshipView):
    """
    View for people.relationships
    """
    queryset = Person.objects
    self_link_view_name = 'person-relationships'
