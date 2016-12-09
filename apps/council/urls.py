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

    url(r'^meeting/(?P<pk>\d+)/upload$',
        views.UploadMeetingAttachment.as_view(), name='upload_meeting_attachment'),

    url(r'^meeting/(?P<pk>\d+)/attendancelist$',
        views.GetAttendanceList.as_view(), name='attendance_list'),

    url(r'^meeting/(?P<pk>\d+)/invitationletter$',
        views.GetInvitationLetter.as_view(), name='invitation_letter'),

    url(r'^point/(?P<pk>\d+)/upload$',
        views.UploadPointAttachment.as_view(), name='upload_point_attachment'),

    url(r'^point/(?P<pk>\d+)/addvoting$',
        views.VoteOutcomeCreateView.as_view(), name='add_vote_outcome'),

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

    url(r'^attachment/edit/(?P<pk>\d+)$',
        views.AttachmentUpdateView.as_view(), name='attachment_update'),

    url(r'^attachment/delete/(?P<pk>\d+)$',
        views.AttachmentDelete.as_view(), name='attachment_delete'),

    url(r'^voteoutcome/edit/(?P<pk>\d+)$',
        views.VoteOutcomeUpdateview.as_view(), name='vote_update'),

    url(r'^voteoutcome/delete/(?P<pk>\d+)$',
        views.VoteOutcomeDelete.as_view(), name='vote_delete'),
]
