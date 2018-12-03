from django_filters import rest_framework as filters
from oauth2_provider.contrib.rest_framework import (OAuth2Authentication,
                                                    TokenMatchesOASRequirements)
from rest_condition import And, Or
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework_json_api.views import ModelViewSet, RelationshipView

from myapp.models import Course, CourseTerm, Instructor
from myapp.serializers import (CourseSerializer, CourseTermSerializer,
                               InstructorSerializer)

# TODO: simplify the following
#: For a given HTTP method, a list of valid alternative required scopes.
#: For instance, GET will be allowed if "auth-columbia read" OR "auth-none read" scopes are provided.
#: Note that even HEAD and OPTIONS require the client to be authorized with at least "read" scope.
REQUIRED_SCOPES_ALTS = {
    'GET': [['auth-columbia', 'read'], ['auth-none', 'read']],
    'HEAD': [['read']],
    'OPTIONS': [['read']],
    'POST': [
        ['auth-columbia', 'demo-netphone-admin', 'create'],
        ['auth-none', 'demo-netphone-admin', 'create'],
    ],
    # 'PUT': [
    #     ['auth-columbia', 'demo-netphone-admin', 'update'],
    #     ['auth-none', 'demo-netphone-admin', 'update'],
    # ],
    'PATCH': [
        ['auth-columbia', 'demo-netphone-admin', 'update'],
        ['auth-none', 'demo-netphone-admin', 'update'],
    ],
    'DELETE': [
        ['auth-columbia', 'demo-netphone-admin', 'delete'],
        ['auth-none', 'demo-netphone-admin', 'delete'],
    ],
}


class MyDjangoModelPermissions(DjangoModelPermissions):
    """
    Override `DjangoModelPermissions <https://docs.djangoproject.com/en/dev/topics/auth/#permissions>`_
    to require view permission as well: The default allows view by anybody.
    """
    # TODO: refactor to just add the GET key to super().perms_map
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
    authentication_classes = (BasicAuthentication, SessionAuthentication, OAuth2Authentication, )
    #: Either use Scope-based OAuth 2.0 token checking OR authenticated user w/Model Permissions.
    permission_classes = [
        Or(TokenMatchesOASRequirements,
           And(IsAuthenticated, MyDjangoModelPermissions))
    ]
    #: list of alternatives for required scopes
    required_alternate_scopes = REQUIRED_SCOPES_ALTS


class CourseBaseViewSet(AuthnAuthzMixIn, ModelViewSet):
    """
    Base ViewSet for all our ViewSets:

    - Adds Authn/Authz
    """
    pass


class CourseViewSet(CourseBaseViewSet):
    __doc__ = Course.__doc__
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    usual_rels = ('exact', 'lt', 'gt', 'gte', 'lte', 'in')
    text_rels = ('icontains', 'iexact', 'contains')
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
    usual_rels = ('exact', 'lt', 'gt', 'gte', 'lte')
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

    class Meta:
        """
        In addition to specific filters defined above, also generate some automatic filters.
        """
        usual_rels = ('exact', 'lt', 'gt', 'gte', 'lte')
        model = Instructor
        fields = {
            'id': usual_rels,
            'name': usual_rels,
        }


class InstructorViewSet(CourseBaseViewSet):
    __doc__ = Instructor.__doc__
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    filterset_class = InstructorFilterSet
    search_fields = ('name', 'course_terms__course__course_name')


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
