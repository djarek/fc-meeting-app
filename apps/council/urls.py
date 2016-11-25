from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^councillist/',
        views.CouncilListView.as_view(), name='council_list'),

    url(r'^addcouncil$',
        views.CouncilCreateView.as_view(), name='add_council'),

    url(r'(?P<pk>\d+)/$',
        views.CouncilDetailView.as_view(), name='council_detail'),

    url(r'(?P<pk>\d+)/edit$',
        views.CouncilUpdateView.as_view(), name='council_update'),

    url(r'^(?P<pk>\d+)/addmeeting$',
        views.MeetingCreateView.as_view(), name='add_meeting'),

    url(r'^(?P<pk>\d+)/addmembers$',
        views.CouncilMemberCreateView.as_view(), name='add_council_members'),

    url(r'^meeting/(?P<pk>\d+)$',
        views.MeetingDetailView.as_view(), name='meeting_detail'),

    url(r'^meeting/edit/(?P<pk>\d+)',
        views.MeetingUpdateView.as_view(), name='meeting_update'),

    url(r'^meeting/(?P<pk>\d+)/addpoint$',
        views.PointCreateView.as_view(), name='add_point'),

    url(r'^pointdetail/(?P<pk>\d+)$',
        views.PointDetailView.as_view(), name='point_detail'),

    url(r'^pointdetail/edit/(?P<pk>\d+)$',
        views.PointUpdateView.as_view(), name='point_update'),

    url(r'^personlist/addperson$',
        views.PersonCreateForm.as_view(), name='add_person'),

    url(r'^personlist/$',
        views.PersonListView.as_view(), name='person_list'),
]