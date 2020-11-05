"""training URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.staticfiles.views import serve
from django.urls import include, path
from django.views.generic.base import RedirectView, TemplateView
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from myapp import views, schemas, __title__ as API_TITLE

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'courses', views.CourseViewSet)
router.register(r'course_terms', views.CourseTermViewSet)
router.register(r'people', views.PersonViewSet)
router.register(r'instructors', views.InstructorViewSet)

urlpatterns = [

    # redirect the base URL to something useful, the Swagger UI:
    path('', RedirectView.as_view(url='/swagger-ui/', permanent=False)),
    path('v1/', include(router.urls)),
    # TODO: Is there a Router than can generate these for me? If not, create one.
    # course relationships:
    path('v1/courses/<pk>/relationships/<related_field>/',
        views.CourseRelationshipView.as_view(),
        name='course-relationships'),
    # use new `retrieve_related` functionality in DJA 2.6.0 which hangs all the related serializers off the parent.
    # (we only have one relationship in the current model so this doesn't really demonstrate the power).
    path('v1/courses/<pk>/<related_field>/',
        views.CourseViewSet.as_view({'get': 'retrieve_related'}),
        name='course-related'),
    # course_terms relationships
    path('v1/course_terms/<pk>/relationships/<related_field>/',
        views.CourseTermRelationshipView.as_view(),
        name='course_term-relationships'),
    # use new `retrieve_related` functionality in DJA 2.6.0:
    path('v1/course_terms/<pk>/<related_field>/',
        views.CourseTermViewSet.as_view({'get': 'retrieve_related'}), # a toOne relationship
        name='course_term-related'),
    # person relationships
    path('v1/people/<pk>/relationships/<related_field>/',
        views.PersonRelationshipView.as_view(),
        name='person-relationships'),
    # use new `retrieve_related` functionality in DJA 2.6.0:
    path('v1/people/<pk>/<related_field>/',
        views.PersonViewSet.as_view({'get': 'retrieve_related'}),
        name='person-related'),
    # instructor relationships
    path('v1/instructors/<pk>/relationships/<related_field>/',
        views.InstructorRelationshipView.as_view(),
        name='instructor-relationships'),
    # use new `retrieve_related` functionality in DJA 2.6.0:
    path('v1/instructors/<pk>/<related_field>/',
        views.InstructorViewSet.as_view({'get': 'retrieve_related'}), # a toMany relationship
        name='instructor-related'),
    # path /v1/openapi is the OAS 3.0 schema document for this app.
    # path /swagger-ui is the swagger user interface that uses that schema document.
    # (v1/openapi and swagger-ui fail if the user is not logged in as the routers are not public.
    # so set public=True since the endpoint documentation is not a secret, just the content.)
    path('v1/openapi', get_schema_view(generator_class=schemas.SchemaGenerator, public=True),
         name='openapi-schema'),
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema', 'title': API_TITLE}
    ), name='swagger-ui'),
    # The default request_uri is /oauth2-redirect.html (no /static prefix) so just pass it into staticfiles serve():
    path('oauth2-redirect.html', serve, {'path': 'oauth2-redirect.html'}),
    # browseable API and admin stuff. TODO: Consider leaving out except when debugging.
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view()),
    path('accounts/logout/', auth_views.LogoutView.as_view(), {'next_page': '/'}, name='logout'),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
