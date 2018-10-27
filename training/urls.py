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
from django.urls import include, path
from django.views.generic.base import RedirectView
from rest_framework import routers

from myapp import views

API_TITLE = 'Demo API'

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'courses', views.CourseViewSet)
router.register(r'course_terms', views.CourseTermViewSet)

urlpatterns = [
    path('', RedirectView.as_view(url='/v1', permanent=False)),
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
        path('^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
