from datetime import datetime

from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api.serializers import HyperlinkedModelSerializer

from myapp.models import Course, CourseTerm, Grade, Instructor, NonModel, Person


class HyperlinkedModelSerializer(HyperlinkedModelSerializer):
    """
    Common serializer class for all model serializers.
    Extends :py:class:`.models.CommonModel` to set `last_mod_user_name` and `...date` from auth.user on a
    POST/PATCH, not from the client app.
    This silently *ignores* anything CREATEd or PATCHed for these fields.
    """

    class Meta:
        """
        In order for this Meta inner class to be inherited by the various serializers,
        one must explicitly inherit it as in this example::

            class MySerializer(HyperlinkedModelSerializer):
                class Meta(HyperlinkedModelSerializer.Meta):
                    model = MyModel
        """

        #: serialize all model fields unless otherwise overridden
        fields = "__all__"
        #: mark these fields as read-only
        read_only_fields = ("last_mod_user_name", "last_mod_date")

    def _last_mod(self, validated_data):
        """
        override any last_mod_user_name or date with current auth user and current date.
        """
        # N.B. if OAuth2 Client Credentials is used, there is no user *and* the `client_id` is not
        # currently properly tracked for an external AS: https://github.com/jazzband/django-oauth-toolkit/issues/664
        validated_data["last_mod_user_name"] = str(self.context["request"].user)
        validated_data["last_mod_date"] = datetime.now().date()

    def create(self, validated_data):
        """
        extend `ModelSerializer.create()` to set last_mod_user/date
        """
        self._last_mod(validated_data)
        return super(HyperlinkedModelSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        """
        extend `ModelSerializer.update()` to set last_mod_user/date
        """
        self._last_mod(validated_data)
        return super(HyperlinkedModelSerializer, self).update(instance, validated_data)


class CourseSerializer(HyperlinkedModelSerializer):
    """
    (de-)serialize the Course model.
    """

    class Meta(HyperlinkedModelSerializer.Meta):
        model = Course

    course_terms = ResourceRelatedField(
        model=CourseTerm,
        many=True,
        read_only=False,
        allow_null=True,
        required=False,
        queryset=CourseTerm.objects.all(),
        self_link_view_name="course-relationships",
        related_link_view_name="course-related",
    )
    """#: a course has zero or more course_term instances"""

    #: `{json:api} compound document <https://jsonapi.org/format/#document-compound-documents>`_
    #: (also used for `related_serializers` for DJA 2.6.0)
    included_serializers = {
        "course_terms": "myapp.serializers.CourseTermSerializer",
    }
    # Uncomment this and the course_terms will be included by default,
    # otherwise '?include=course_terms' must be added to the URL.
    # class JSONAPIMeta:
    #    included_resources = ['course_terms']


class CourseTermSerializer(HyperlinkedModelSerializer):
    """
    (de-)serialize the CourseTerm model.
    """

    class Meta(HyperlinkedModelSerializer.Meta):
        model = CourseTerm

    #: a course_term has zero or one parent courses
    course = ResourceRelatedField(
        model=Course,
        many=False,
        read_only=False,
        allow_null=True,
        required=False,
        queryset=Course.objects.all(),
        self_link_view_name="course_term-relationships",
        related_link_view_name="course_term-related",
    )
    #: a course_term can have many instructors
    instructors = ResourceRelatedField(
        model=Instructor,
        many=True,
        read_only=False,
        allow_null=True,
        required=False,
        queryset=Instructor.objects.all(),
        self_link_view_name="course_term-relationships",
        related_link_view_name="course_term-related",
    )

    #: ``?include=course`` or ``?include=instructors``
    #: `{json:api} compound document <https://jsonapi.org/format/#document-compound-documents>`_
    included_serializers = {
        "course": "myapp.serializers.CourseSerializer",
        "instructors": "myapp.serializers.InstructorSerializer",
    }


class PersonSerializer(HyperlinkedModelSerializer):
    """
    (de-)serialize the Person model.
    """

    class Meta(HyperlinkedModelSerializer.Meta):
        model = Person

    #: a person is an instructor
    instructor = ResourceRelatedField(
        model=Instructor,
        many=False,
        read_only=False,
        allow_null=True,
        required=False,
        queryset=Instructor.objects.all(),
        self_link_view_name="person-relationships",
        related_link_view_name="person-related",
    )

    #: `{json:api} compound document <https://jsonapi.org/format/#document-compound-documents>`_
    included_serializers = {
        "instructor": "myapp.serializers.InstructorSerializer",
    }


class InstructorSerializer(HyperlinkedModelSerializer):
    """
    (de-)serialize the Instructor model.
    """

    class Meta(HyperlinkedModelSerializer.Meta):
        model = Instructor
        fields = "__all__"

    #: an instructor teaches zero or more course instances
    course_terms = ResourceRelatedField(
        model=CourseTerm,
        many=True,
        read_only=False,
        allow_null=True,
        required=False,
        queryset=CourseTerm.objects.all(),
        self_link_view_name="instructor-relationships",
        related_link_view_name="instructor-related",
    )

    #: an instructor is a person
    person = ResourceRelatedField(
        model=Person,
        many=False,
        read_only=False,
        allow_null=True,
        required=False,
        queryset=Person.objects.all(),
        self_link_view_name="instructor-relationships",
        related_link_view_name="instructor-related",
    )

    #: `{json:api} compound document <https://jsonapi.org/format/#document-compound-documents>`_
    included_serializers = {
        "course_terms": "myapp.serializers.CourseTermSerializer",
        "person": "myapp.serializers.PersonSerializer",
    }


class GradeSerializer(HyperlinkedModelSerializer):
    """
    (de-)serialize the Grade model.
    """

    class Meta(HyperlinkedModelSerializer.Meta):
        model = Grade
        fields = "__all__"

    #: a grade has one course_term
    course_term = ResourceRelatedField(
        model=CourseTerm,
        many=False,
        read_only=False,
        allow_null=False,
        required=True,
        queryset=CourseTerm.objects.all(),
        self_link_view_name="grade-relationships",
        related_link_view_name="grade-related",
    )

    #: a grade has one person
    person = ResourceRelatedField(
        model=Person,
        many=False,
        read_only=False,
        allow_null=False,
        required=True,
        queryset=Person.objects.all(),
        self_link_view_name="grade-relationships",
        related_link_view_name="grade-related",
    )

    included_serializers = {
        "course_terms": "myapp.serializers.CourseTermSerializer",
        "person": "myapp.serializers.PersonSerializer",
    }


class NonModelSerializer(HyperlinkedModelSerializer):
    """Serialize the fields that come from the NonModel Model."""

    class Meta:
        model = NonModel
        fields = "__all__"  # limit to fewer fields by name if you want.
