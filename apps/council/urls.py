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

    url(r'(?P<pk>\d+)/delete',
        views.CouncilDelete.as_view(), name='council_delete'),

    url(r'^(?P<pk>\d+)/addmeeting$',
        views.MeetingCreateView.as_view(), name='add_meeting'),

    url(r'^(?P<pk>\d+)/addmembers$',
        views.CouncilMemberCreateView.as_view(), name='add_council_members'),

    url(r'^deletemember/(?P<m_pk>\d+)$',
        views.CouncilMemberDelete.as_view(), name='delete_council_member'),

    url(r'^meeting/(?P<pk>\d+)$',
        views.MeetingDetailView.as_view(), name='meeting_detail'),

    url(r'^meeting/edit/(?P<pk>\d+)',
        views.MeetingUpdateView.as_view(), name='meeting_update'),

    url(r'^meeting/delete/(?P<pk>\d+)',
        views.MeetingDelete.as_view(), name='meeting_delete'),

    url(r'^meeting/(?P<pk>\d+)/addpoint$',
        views.PointCreateView.as_view(), name='add_point'),

    url(r'^meeting/(?P<pk>\d+)/addinvited$',
        views.InvitedCreateView.as_view(), name='add_invited'),

    url(r'^meeting/(?P<pk>\d+)/inviteallmembers$',
        views.InviteAllCouncilMembers.as_view(), name='invite_all_members'),

    url(r'^point/(?P<pk>\d+)$',
        views.PointDetailView.as_view(), name='point_detail'),

    url(r'^point/edit/(?P<pk>\d+)$',
        views.PointUpdateView.as_view(), name='point_update'),

    url(r'^point/delete/(?P<pk>\d+)$',
        views.PointDelete.as_view(), name='point_delete'),

    url(r'^personlist/addperson$',
        views.PersonCreateForm.as_view(), name='add_person'),

    url(r'^personlist/$',
        views.PersonListView.as_view(), name='person_list'),
]
