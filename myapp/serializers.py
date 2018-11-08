from datetime import datetime

from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api.serializers import HyperlinkedModelSerializer

from myapp.models import Course, CourseTerm


class HyperlinkedModelSerializer(HyperlinkedModelSerializer):
    """
    .models.CommonModel.last_mod_user_name/date should come from auth.user on a POST/PATCH, not from the client app.
    """
    read_only_fields = ('last_mod_user_name', 'last_mod_date')

    def _last_mod(self, validated_data):
        """
        override any last_mod_user_name or date with current auth user and current date.
        """
        # N.B. if OAuth2 Client Credentials is used, there is no user *and* the `client_id` is not
        # currently properly tracked for an external AS: https://github.com/jazzband/django-oauth-toolkit/issues/664
        validated_data['last_mod_user_name'] = str(self.context['request'].user)
        validated_data['last_mod_date'] = datetime.now().date()

    def create(self, validated_data):
        """
        extended ModelSerializer to set last_mod_user/date
        """
        self._last_mod(validated_data)
        return super(HyperlinkedModelSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        """
        extended ModelSerializer to set last_mod_user/date
        """
        self._last_mod(validated_data)
        return super(HyperlinkedModelSerializer, self).update(instance, validated_data)


class CourseSerializer(HyperlinkedModelSerializer):
    """
    (de-)serialize the Course.
    """
    class Meta:
        model = Course
        fields = (
            'url',
            'school_bulletin_prefix_code', 'suffix_two', 'subject_area_code',
            'course_number', 'course_identifier', 'course_name', 'course_description',
            'effective_start_date', 'effective_end_date',
            'last_mod_user_name', 'last_mod_date',
            'course_terms')

    course_terms = ResourceRelatedField(
        model=CourseTerm,
        many=True,
        read_only=False,
        allow_null=True,
        required=False,
        queryset=CourseTerm.objects.all(),
        self_link_view_name='course-relationships',
        related_link_view_name='course-related',
    )

    # json api 'included' support (also used for `related_serializers` for DJA 2.6.0)
    included_serializers = {
        'course_terms': 'myapp.serializers.CourseTermSerializer',
    }
    # Uncomment this and the course_terms will be included by default,
    # otherwise '?include=course_terms' must be added to the URL.
    # class JSONAPIMeta:
    #    included_resources = ['course_terms']


class CourseTermSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = CourseTerm
        fields = (
            'url',
            'term_identifier', 'audit_permitted_code',
            'exam_credit_flag',
            'effective_start_date', 'effective_end_date',
            'last_mod_user_name', 'last_mod_date',
            'course')

    course = ResourceRelatedField(
        model=Course,
        many=False,  # this breaks new 2.6.0 related support. Only works when True.
        read_only=False,
        allow_null=True,
        required=False,
        queryset=Course.objects.all(),
        self_link_view_name='course_term-relationships',
        related_link_view_name='course_term-related',
    )

    # json api 'included' support
    included_serializers = {
        'course': 'myapp.serializers.CourseSerializer',
    }
