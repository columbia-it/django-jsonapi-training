from rest_framework_json_api.views import ModelViewSet, RelationshipView

from myapp.models import Course, CourseTerm
from myapp.serializers import CourseSerializer, CourseTermSerializer

class CourseViewSet(ModelViewSet):
    """
    API endpoint that allows course to be viewed or edited.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseTermViewSet(ModelViewSet):
    """
    API endpoint that allows CourseTerm to be viewed or edited.
    """
    queryset = CourseTerm.objects.all()
    serializer_class = CourseTermSerializer


class CourseRelationshipView(RelationshipView):
    """
    view for relationships.course
    """
    queryset = Course.objects
    self_link_view_name = 'course-relationships'


class CourseTermRelationshipView(RelationshipView):
    """
    view for relationships.course_terms
    """
    queryset = CourseTerm.objects
    self_link_view_name = 'course_term-relationships'
