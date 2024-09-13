import logging
import re

from django_filters import rest_framework as filters
# mypass my Oauth2 schema hack for the time being:
# from myapp.schemas import MyOAuth2Auth
from oauth2_provider.contrib.rest_framework import OAuth2Authentication as MyOAuth2Auth
from oauth2_provider.contrib.rest_framework import TokenMatchesOASRequirements
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from rest_framework_json_api.views import ModelViewSet, RelationshipView

from myapp.models import Course, CourseTerm, Grade, Instructor, NonModel, Person
from myapp.serializers import (CourseSerializer, CourseTermSerializer, GradeSerializer, InstructorSerializer,
                               NonModelSerializer, PersonSerializer)
from oauth.oauth2_introspection import HasClaim

log = logging.getLogger(__name__)


class ColumbiaGroupClaimPermission(HasClaim):
    """
    Use OIDC claim 'https://api.columbia.edu/claim/group' to determine permission
    to create/update/delete stuff: If the user has the claim `demo_d_demo2`, then
    they can do writes. Read access doesn't require a claim.
    """

    #: in order to be able to do a write, the user must have claim `demo_d_demo2`
    WRITE_CLAIM = "demo_d_demo2"
    #: any user can do a read (empty string indicates so vs. None which means deny).
    READ_CLAIM = ""
    #: the name of our custom claim group
    claim = "https://api.columbia.edu/claim/group"
    #: mapping of HTTP methods to required claim group values
    claims_map = {
        "GET": READ_CLAIM,
        "HEAD": READ_CLAIM,
        "OPTIONS": READ_CLAIM,
        "POST": WRITE_CLAIM,
        "PATCH": WRITE_CLAIM,
        "DELETE": WRITE_CLAIM,
    }


class ColumbiaSubClaimPermission(HasClaim):
    """
    Use OIDC 'sub' claim to determine if the subject is from the Columbia University OIDC service.
    Combine this with the preceding ColumbiaGroupClaimPermission.
    """

    claim = "sub"
    CU_CLAIM = re.compile(".+@columbia.edu$")  # sub ends in @columbia.edu
    claims_map = {
        "GET": CU_CLAIM,
        "HEAD": CU_CLAIM,
        "OPTIONS": CU_CLAIM,
        "POST": CU_CLAIM,
        "PATCH": CU_CLAIM,
        "DELETE": CU_CLAIM,
    }


class DOTGroupClaimPermission(HasClaim):
    """
    Use OIDC custom claim 'https://api.columbia.edu/claim/group' to determine permission
    to create/update/delete stuff: If the user has the claim 'team-c' then
    they can do writes. Read access requires 'team-a'.

    With our demo environment fixture:
    - user1 is a member of team-a and team-c so can read and write.
    - user2 is a member of team-a and team-b so can only read.
    - user3 is not a member of any team so can't read or write.
    """

    WRITE_CLAIM = "team-c"
    READ_CLAIM = "team-a"
    #: the name of our custom claim group
    claim = "https://api.columbia.edu/claim/group"
    #: mapping of HTTP methods to required claim group values
    claims_map = {
        "GET": READ_CLAIM,
        "HEAD": READ_CLAIM,
        "OPTIONS": READ_CLAIM,
        "POST": WRITE_CLAIM,
        "PATCH": WRITE_CLAIM,
        "DELETE": WRITE_CLAIM,
    }


class DOTSubClaimPermission(HasClaim):
    """
    Use OIDC 'sub' claim to determine if the subject is from a service where the sub does not
    contain '@'. This is probably the local DOT but could be an external AS too.
    (It would be nice if 'iss' where part of a standard Userinfo response, but that is not the case.)
    Combine this with the preceding DOTGroupClaimPermission.
    """

    claim = "sub"
    DOT_CLAIM = re.compile("^((?!@).)*$")  # sub does not contain "@"
    claims_map = {
        "GET": DOT_CLAIM,
        "HEAD": DOT_CLAIM,
        "OPTIONS": DOT_CLAIM,
        "POST": DOT_CLAIM,
        "PATCH": DOT_CLAIM,
        "DELETE": DOT_CLAIM,
    }


class MyDjangoModelPermissions(DjangoModelPermissions):
    """
    Override `DjangoModelPermissions <https://docs.djangoproject.com/en/dev/topics/auth/#permissions>`_
    to require view permission as well: The default allows view by anybody.
    """

    #: the usual permissions map plus GET. Also, we omit PUT since we only use PATCH with {json:api}.
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        # PUT not allowed by JSON:API; use PATCH
        # 'PUT': ['%(app_label)s.change_%(model_name)s'],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }


class AuthnAuthzMixIn(object):
    """
    Common Authn/Authz mixin for all View and ViewSet-derived classes:
    """

    #: In production Oauth2 is preferred; Allow Basic and Session for testing and browseable API.
    #: (authentication_classes is an implied OR list)
    authentication_classes = (MyOAuth2Auth,)
    #: permissions are any one of, each requiring demo-djt-sla-* scope:
    #: 1. Authenticated Columbia user: auth-columbia scope plus required user claims.
    #: 2. Authenticated DOT user: scopes as above plus DOT required user claims.
    #: 3. Client Credentials (backend-to-backend): auth-none. No auth user. Claims don't exist.
    permission_classes = [
        TokenMatchesOASRequirements
        & (
            (IsAuthenticated & ColumbiaGroupClaimPermission & ColumbiaSubClaimPermission)
            | (IsAuthenticated & DOTGroupClaimPermission & DOTSubClaimPermission)
            # | (IsAuthenticated & DOTSubClaimPermission)
            | (~IsAuthenticated)
        )
    ]
    #: Implicit/Authorization Code scopes: user via frontend client
    USER_SCOPES = [
        "auth-columbia",
        "demo-djt-sla-bronze",
        "openid",
        "https://api.columbia.edu/scope/group",
    ]
    #: Client Credentials scopes: backend-to-backend
    BACKEND_SCOPES = ["auth-none", "demo-djt-sla-bronze"]
    #: allow either USER_SCOPES or BACKEND_SCOPES
    required_alternate_scopes = {
        "OPTIONS": [["read"]],
        "HEAD": [USER_SCOPES + ["read"], BACKEND_SCOPES + ["read"]],
        "GET": [USER_SCOPES + ["read"], BACKEND_SCOPES + ["read"]],
        "POST": [USER_SCOPES + ["create"], BACKEND_SCOPES + ["create"]],
        "PATCH": [USER_SCOPES + ["update"], BACKEND_SCOPES + ["update"]],
        "DELETE": [USER_SCOPES + ["delete"], BACKEND_SCOPES + ["delete"]],
    }


class CourseBaseViewSet(AuthnAuthzMixIn, ModelViewSet):
    """
    Base ViewSet for all our ViewSets:

    - Adds Authn/Authz
    """


usual_rels = ("exact", "lt", "gt", "gte", "lte", "in")
text_rels = ("icontains", "iexact", "contains")


class CourseViewSet(CourseBaseViewSet):
    __doc__ = Course.__doc__
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    #: See https://docs.djangoproject.com/en/stable/ref/models/querysets/#field-lookups for all the possible filters.
    filterset_fields = {
        "id": usual_rels,
        "subject_area_code": usual_rels,
        "course_name": ("exact",) + text_rels,
        "course_description": text_rels + usual_rels,
        "course_identifier": text_rels + usual_rels,
        "course_number": ("exact",),
        "course_terms__term_identifier": usual_rels,
        "school_bulletin_prefix_code": ("exact", "regex"),
    }
    #: Keyword searches are across these fields.
    search_fields = (
        "course_name",
        "course_description",
        "course_identifier",
        "course_number",
    )


class CourseTermViewSet(CourseBaseViewSet):
    __doc__ = CourseTerm.__doc__
    queryset = CourseTerm.objects.all()
    serializer_class = CourseTermSerializer
    #: defined filter[] names
    filterset_fields = {
        "id": usual_rels,
        "term_identifier": usual_rels,
        "audit_permitted_code": ["exact"],
        "exam_credit_flag": ["exact"],
        "course__id": usual_rels,
    }
    #: Keyword searches are just this one field.
    search_fields = ("term_identifier",)


class PersonViewSet(CourseBaseViewSet):
    __doc__ = Person.__doc__
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filterset_fields = {}
    search_fields = ("name", "instructor__course_terms__course__course_name")

    class Meta:
        """
        In addition to specific filters defined above, also generate some automatic filters.
        """

        model = Person
        fields = {
            "id": usual_rels,
            "name": usual_rels,
        }


class InstructorFilterSet(filters.FilterSet):
    """
    Extend class `django_filters.rest_framework.FilterSet` for the Instructor model

    Includes a filter "alias" for a chained search from instructor->course_term->course
    """

    #: `filter[course_name]` is an alias for the path `course_terms.course.course_name`
    course_name = filters.CharFilter(
        field_name="course_terms__course__course_name", lookup_expr="iexact"
    )
    #: `filter[course_name_gt]` for greater-than, etc.
    course_name__gt = filters.CharFilter(
        field_name="course_terms__course__course_name", lookup_expr="gt"
    )
    course_name__gte = filters.CharFilter(
        field_name="course_terms__course__course_name", lookup_expr="gte"
    )
    course_name__lt = filters.CharFilter(
        field_name="course_terms__course__course_name", lookup_expr="lt"
    )
    course_name__lte = filters.CharFilter(
        field_name="course_terms__course__course_name", lookup_expr="lte"
    )
    #: `filter[name]` is an alias for the path `course_terms.instructor.person.name`
    name = filters.CharFilter(
        field_name="course_terms__instructor__person__name", lookup_expr="iexact"
    )
    #: `filter[name_gt]` for greater-than, etc.
    name__gt = filters.CharFilter(
        field_name="course_terms__instructor__person__name", lookup_expr="gt"
    )
    name__gte = filters.CharFilter(
        field_name="course_terms__instructor__person__name", lookup_expr="gte"
    )
    name__lt = filters.CharFilter(
        field_name="course_terms__instructor__person__name", lookup_expr="lt"
    )
    name__lte = filters.CharFilter(
        field_name="course_terms__instructor__person__name", lookup_expr="lte"
    )

    class Meta:
        """
        In addition to specific filters defined above, also generate some automatic filters.
        """

        model = Instructor
        fields = {
            "id": usual_rels,
        }


class InstructorViewSet(CourseBaseViewSet):
    __doc__ = Instructor.__doc__
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    filterset_class = InstructorFilterSet
    search_fields = ("person__name", "course_terms__course__course_name")


class GradeViewSet(CourseBaseViewSet):
    __doc__ = Grade.__doc__
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    filterset_fields = {
        "id": usual_rels,
        # 'term_identifier': usual_rels,
        # 'audit_permitted_code': ['exact'],
        # 'exam_credit_flag': ['exact'],
        # 'course__id': usual_rels,
    }
    search_fields = ("person__name", "course_terms__course__course_name")


# class NonModelViewSet(GenericViewSet, AuthnAuthzMixIn):
class NonModelViewSet(CourseBaseViewSet):
    """
    We call this a NonModel but it's really a model that has no backing database.
    This allows us to take advantage of all the model-based features.
    """

    serializer_class = NonModelSerializer
    http_method_names = ["get", "head", "options"]
    description = "this is a demo"
    queryset = NonModel.objects

    def retrieve(self, request, pk, *args, **kwargs):
        foo = NonModel(id="123", field1="hi there")
        serializer_instance = self.get_serializer(foo, context={"request": request})
        return Response(serializer_instance.data)

    def list(self, request, *args, **kwargs):
        # instead of the queryset coming from a database Model, create it right here:
        # TODO: Make this actually base the querset on query parameters.
        self.queryset = [NonModel(field1=f"hi there {k}") for k in range(100)]
        # queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer_instance = self.get_serializer(
            self.queryset, many=True, context={"request": request}
        )
        return Response(serializer_instance.data)


# Relationship views:


class CourseRelationshipView(AuthnAuthzMixIn, RelationshipView):
    """
    View for courses.relationships
    """

    queryset = Course.objects
    self_link_view_name = "course-relationships"


class CourseTermRelationshipView(AuthnAuthzMixIn, RelationshipView):
    """
    View for course_terms.relationships
    """

    queryset = CourseTerm.objects
    self_link_view_name = "course_term-relationships"


class InstructorRelationshipView(AuthnAuthzMixIn, RelationshipView):
    """
    View for instructors.relationships
    """

    queryset = Instructor.objects
    self_link_view_name = "instructor-relationships"


class PersonRelationshipView(AuthnAuthzMixIn, RelationshipView):
    """
    View for people.relationships
    """

    queryset = Person.objects
    self_link_view_name = "person-relationships"


class GradeRelationshipView(AuthnAuthzMixIn, RelationshipView):
    """
    View for grades.relationships
    """

    queryset = Grade.objects
    self_link_view_name = "grade-relationships"
