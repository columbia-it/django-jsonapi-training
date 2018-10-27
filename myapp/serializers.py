from datetime import datetime

from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api.serializers import HyperlinkedModelSerializer

from myapp.models import Course, CourseTerm


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
