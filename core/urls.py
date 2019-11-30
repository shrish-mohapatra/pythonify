from django.conf.urls import url, include

from .views import *

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^index$', index, name='index'),

    url(r'^admin_dashboard$', admin_dashboard, name='admin_dashboard'),
    url(r'^manage$', manage, name='manage'),

    url(r'^approve_student/(?P<pk>\d+)$', approve_student, name='approve_student'),
    url(r'^reject_student/(?P<pk>\d+)$', reject_student, name='reject_student'),
    url(r'^create_codes$', create_codes, name='create_codes'),
    url(r'^delete_codes$', delete_codes, name='delete_codes'),

    url(r'^signup$', signup, name='signup'),
    url(r'^signin$', signin, name='signin'),

    url(r'^view_set$', view_set, name='view_set'),
    url(r'^edit_set/(?P<pk>\d+)$', edit_set, name='edit_set'),
    url(r'^create_set', create_set, name='create_set'),
    url(r'^delete_set/(?P<pk>\d+)$', delete_set, name='delete_set'),
    url(r'^set_sets_ref/(?P<id>\d+)$', set_sets_ref, name='set_sets_ref'),

    url(r'^view_prompt/(?P<pk>\d+)$', view_prompt, name='view_prompt'),
    url(r'^edit_prompt/(?P<pk>\d+)$', edit_prompt, name='edit_prompt'),
    url(r'^create_prompt$', create_prompt, name='create_prompt'),
    url(r'^delete_prompt/(?P<pk>\d+)$', delete_prompt, name='delete_prompt'),
]