# -*- encoding: utf-8 -*-
import StringIO
import json

from django.shortcuts import redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.mail import send_mail
from django.views.generic import View, TemplateView, CreateView, ListView,\
    DetailView, UpdateView
from django.http import HttpResponseForbidden, JsonResponse

from RWE.mixins import LoginRequiredMixin, CheckGroupMixin
import apps.council.functions as council_functions
import apps.council.models as council_models
import apps.council.forms as council_forms
import apps.council.dictionaries as council_dicts


class CouncilListView(LoginRequiredMixin, ListView):
    model = council_models.FacultyCouncil
    template_name = 'council/council_list.html'

    def get_queryset(self):
        person = get_person_by_email(self.request.user.email)
        if is_supervisor(person):
            return council_models.FacultyCouncil.objects.all()
        councils = council_models.FacultyCouncilMember.objects.filter(
            person=person).values_list('council', flat=True).distinct()
        return council_models.FacultyCouncil.objects.filter(pk__in=councils)


class CouncilCreateView(LoginRequiredMixin, CheckGroupMixin, CreateView):
    required_group = 'supervisor'

    form_class = council_forms.CouncilForm
    template_name = 'council/add_council.html'

    def form_valid(self, form):
        council = form.save()
        members = council_models.Person.objects.filter(
            group__in=[council_dicts.BIG_QUORUM_GROUP,
                       council_dicts.SMALL_QUORUM_GROUP])
        for m in members:
            council_models.FacultyCouncilMember.objects.create(
                person=m,
                council=council)
        return super(CouncilCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('council_detail', args=(self.object.pk,))


class CouncilDetailView(LoginRequiredMixin, DetailView):
    model = council_models.FacultyCouncil
    template_name = 'council/council_detail.html'

    def get(self, request, *args, **kwargs):
        person = get_person_by_email(request.user.email)
        if is_supervisor(person) or \
                council_models.FacultyCouncilMember.objects.filter(
                    person=person, council__pk=kwargs.get('pk')).exists():
            return super(CouncilDetailView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden(u'Brak dostępu')

    def get_context_data(self, **kwargs):
        context = super(CouncilDetailView, self).get_context_data(**kwargs)
        context['meeting_list'] = council_models.Meeting.objects.filter(
            council=self.object).order_by('number')
        context['members_list'] = council_models.FacultyCouncilMember.objects.\
            filter(council=self.object).order_by('person__last_name')
        return context


class CouncilUpdateView(LoginRequiredMixin, CheckGroupMixin, UpdateView):
    required_group = 'supervisor'

    model = council_models.FacultyCouncil
    form_class = council_forms.CouncilForm
    template_name = 'council/add_council.html'

    def get_context_data(self, **kwargs):
        context = super(CouncilUpdateView, self).get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('council_list')


class CouncilDelete(LoginRequiredMixin, CheckGroupMixin, View):
    required_group = 'supervisor'

    def dispatch(self, request, *args, **kwargs):
        c_pk = kwargs['pk']
        council = council_models.FacultyCouncil.objects.get(pk=c_pk)
        meetings = council_models.Meeting.objects.filter(council=council)
        for meeting in meetings:
            points = council_models.Point.objects.filter(meeting=meeting)
            for point in points:
                council_models.ResolutionPoint.objects.filter(
                    point=point).delete()
                council_models.Attachment.objects.filter(point=point).delete()
                council_models.VoteOutcome.objects.filter(point=point).delete()
                council_models.Access.objects.filter(point=point).delete()
                point.delete()
            council_models.Attachment.objects.filter(meeting=meeting).delete()
            meeting.delete()
        council_models.FacultyCouncilMember.objects.filter(
            council=council).delete()
        council.delete()
        return redirect(reverse_lazy('council_list'))


class CouncilMemberCreateView(LoginRequiredMixin, CheckGroupMixin, TemplateView):
    required_group = 'supervisor'

    template_name = 'council/add_council_members.html'

    def get_context_data(self, **kwargs):
        context = super(CouncilMemberCreateView, self).get_context_data(
            **kwargs)
        context['persons'] = council_models.Person.objects.all().order_by(
            'last_name')
        context['council'] = council_models.FacultyCouncil.objects.get(
            pk=kwargs['pk'])
        return context

    def post(self, request, *args, **kwargs):
        council_pk = request.POST.get('council_pk', None)
        council = council_models.FacultyCouncil.objects.get(pk=council_pk)
        persons = request.POST.get('persons', '').split(',')
        if persons != ['']:
            for per in persons:
                council_models.FacultyCouncilMember.objects.get_or_create(
                    council=council,
                    person=council_models.Person.objects.get(pk=per))
        return redirect(reverse_lazy('council_detail', args=(council_pk,)))


class CouncilMemberDelete(LoginRequiredMixin, CheckGroupMixin, View):
    required_group = 'supervisor'

    def dispatch(self, request, *args, **kwargs):
        member = council_models.FacultyCouncilMember.objects.get(
            pk=kwargs['m_pk'])
        council_pk = member.council.pk
        member.delete()
        return redirect(reverse_lazy('council_detail', args=(council_pk,)))


class MeetingCreateView(LoginRequiredMixin, CheckGroupMixin, CreateView):
    required_group = 'supervisor'

    form_class = council_forms.MeetingForm
    template_name = 'council/add_meeting.html'

    def form_valid(self, form):
        meeting = form.save(commit=False)
        council = council_models.FacultyCouncil.objects.get(
            pk=self.kwargs['pk'])
        meeting.council = council
        super(MeetingCreateView, self).form_valid(form)
        members = council_models.FacultyCouncilMember.objects.filter(
            council=council)
        persons = [m.person for m in members]
        for p in persons:
            council_models.Invited.objects.create(person=p,
                                                  meeting=self.object)
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(MeetingCreateView, self).get_context_data(**kwargs)
        context['council'] = council_models.FacultyCouncil.objects.get(
            pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return reverse_lazy('meeting_detail', args=(self.object.pk,))


class MeetingDetailView(LoginRequiredMixin, DetailView):
    model = council_models.Meeting
    template_name = 'council/meeting_detail.html'

    def get(self, request, *args, **kwargs):
        person = get_person_by_email(request.user.email)
        if is_supervisor(person) or council_models.Invited.objects.filter(
                person=person, meeting__pk=self.kwargs['pk']).exists():
            return super(MeetingDetailView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden(u'Brak dostępu')

    def get_context_data(self, **kwargs):
        context = super(MeetingDetailView, self).get_context_data(**kwargs)
        context['meeting'] = self.object
        context['point_list'] = council_models.Point.objects.filter(
            meeting=self.object).order_by('number')
        context['invited_list'] = council_models.Invited.objects.filter(
            meeting=self.object).order_by('person__last_name')
        context['attachment_list'] = council_models.Attachment.objects.filter(
            meeting=self.object)
        return context


class MeetingUpdateView(LoginRequiredMixin, CheckGroupMixin, UpdateView):
    required_group = 'supervisor'

    model = council_models.Meeting
    form_class = council_forms.MeetingForm
    template_name = 'council/add_meeting.html'

    def form_valid(self, form):
        form.save(commit=False)
        return super(MeetingUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(MeetingUpdateView, self).get_context_data(**kwargs)
        context['council'] = self.object.council
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('council_detail', args=(self.object.council.pk,))


class MeetingDelete(LoginRequiredMixin, CheckGroupMixin, View):
    required_group = 'supervisor'

    def dispatch(self, request, *args, **kwargs):
        meeting = council_models.Meeting.objects.get(pk=kwargs['pk'])
        council_pk = meeting.council.pk
        points = council_models.Point.objects.filter(meeting=meeting)
        for point in points:
            council_models.ResolutionPoint.objects.filter(
                point=point).delete()
            council_models.Attachment.objects.filter(point=point).delete()
            council_models.VoteOutcome.objects.filter(point=point).delete()
            council_models.Access.objects.filter(point=point).delete()
            point.delete()
        council_models.Invited.objects.filter(meeting=meeting).delete()
        council_models.Attachment.objects.filter(meeting=meeting).delete()
        meeting.delete()
        return redirect(reverse_lazy('council_detail', args=(council_pk,)))


class PointCreateView(LoginRequiredMixin, CreateView):
    form_class = council_forms.PointForm
    template_name = 'council/add_point.html'

    def get(self, request, *args, **kwargs):
        person = get_person_by_email(request.user.email)
        if is_supervisor(person) or council_models.Invited.objects.filter(
                person=person, meeting__pk=self.kwargs['pk']).exists():
            return super(PointCreateView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden(u'Brak dostępu')

    def get_initial(self):
        return {'meeting_pk': self.kwargs['pk']}

    def form_valid(self, form):
        point = form.save(commit=False)
        meeting_pk = self.kwargs['pk']
        point.meeting = council_models.Meeting.objects.get(pk=meeting_pk)
        point.owner = council_models.Invited.objects.get(
            person=get_person_by_email(self.request.user.email))
        super(PointCreateView, self).form_valid(form)
        invited = council_models.Invited.objects.filter(meeting__pk=meeting_pk)
        for i in invited:
            council_models.Access.objects.create(invited=i, point=point)
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(PointCreateView, self).get_context_data(**kwargs)
        context['meeting'] = council_models.Meeting.objects.get(
            pk=self.kwargs['pk'])
        context['categories'] = json.dumps([
            {
                'id': p.category,
                'text': p.category
            } for p in council_models.Point.objects.all()
        ])
        return context

    def get_success_url(self):
        return reverse('point_detail', args=(self.object.pk,))


class PointDetailView(LoginRequiredMixin, DetailView):
    model = council_models.Point
    template_name = 'council/point_detail.html'

    def get(self, request, *args, **kwargs):
        person = get_person_by_email(request.user.email)
        council_models.Access.objects.filter(point__pk=self.kwargs['pk'])
        if is_supervisor(person) or council_models.Access.objects.filter(
                invited__person=person, point__pk=self.kwargs['pk']).exists():
            return super(PointDetailView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden(u'Brak dostępu')

    def get_context_data(self, **kwargs):
        context = super(PointDetailView, self).get_context_data(**kwargs)
        context['attachment_list'] = council_models.Attachment.objects.filter(
            point=self.object)
        context['vote_outcome_list'] = council_models.VoteOutcome.objects.\
            filter(point=self.object)
        return context


class PointUpdateView(LoginRequiredMixin, UpdateView):
    model = council_models.Point
    form_class = council_forms.PointForm
    template_name = 'council/add_point.html'

    def get(self, request, *args, **kwargs):
        person = get_person_by_email(request.user.email)
        point = self.get_object()
        if is_supervisor(person) or point.owner.person == person:
            return super(PointUpdateView, self).get(PointUpdateView, request,
                                                    *args, **kwargs)
        else:
            return HttpResponseForbidden(u'Brak dostępu')

    def form_valid(self, form):
        form.save(commit=False)
        return super(PointUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(PointUpdateView, self).get_context_data(**kwargs)
        context['meeting'] = self.object.meeting
        context['is_edit'] = True
        context['categories'] = json.dumps([
           {
               'id': p.category,
               'text': p.category
           } for p in council_models.Point.objects.all()
        ])
        return context

    def get_success_url(self):
        return reverse('meeting_detail', args=(self.object.meeting.pk,))


class PointDelete(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        point = council_models.Point.objects.get(pk=kwargs['pk'])
        person = get_person_by_email(request.user.email)
        if is_supervisor(person) or point.owner.person == person:
            meeting_pk = point.meeting.pk
            council_models.ResolutionPoint.objects.filter(point=point).delete()
            council_models.Attachment.objects.filter(point=point).delete()
            council_models.VoteOutcome.objects.filter(point=point).delete()
            council_models.Access.objects.filter(point=point).delete()
            point.delete()
            return redirect(reverse_lazy('meeting_detail', args=(meeting_pk,)))
        else:
            return HttpResponseForbidden(u'Brak dostępu')


class PersonCreateForm(LoginRequiredMixin, CheckGroupMixin, CreateView):
    required_group = 'supervisor'

    form_class = council_forms.PersonForm
    template_name = 'council/add_person.html'

    def get_success_url(self):
        return reverse('person_list')


class PersonListView(LoginRequiredMixin, CheckGroupMixin, ListView):
    required_group = 'supervisor'

    model = council_models.Person
    template_name = 'council/person_list.html'


class InviteAllCouncilMembers(LoginRequiredMixin, CheckGroupMixin, View):
    required_group = 'supervisor'

    def dispatch(self, request, *args, **kwargs):
        meeting_pk = kwargs['pk']
        meeting = council_models.Meeting.objects.get(pk=meeting_pk)
        members = council_models.FacultyCouncilMember.objects.filter(
            council=meeting.council)
        for m in members:
            i, created = council_models.Invited.objects.get_or_create(
                person=m.person, meeting=meeting)
            if created:
                i.save()
        return redirect(reverse_lazy('meeting_detail', args=(meeting_pk,)))


class InvitedCreateView(LoginRequiredMixin, CheckGroupMixin, TemplateView):
    required_group = 'supervisor'

    template_name = 'council/add_invited.html'

    def get_context_data(self, **kwargs):
        context = super(InvitedCreateView, self).get_context_data(
            **kwargs)
        context['persons'] = council_models.Person.objects.all()
        context['meeting'] = council_models.Meeting.objects.get(
            pk=kwargs['pk'])
        return context

    def post(self, request, *args, **kwargs):
        meeting_pk = request.POST.get('meeting_pk', None)
        meeting = council_models.Meeting.objects.get(pk=meeting_pk)
        persons = request.POST.get('persons', '').split(',')
        if persons != ['']:
            for per in persons:
                council_models.Invited.objects.get_or_create(
                    meeting=meeting,
                    person=council_models.Person.objects.get(pk=per))
        return redirect(reverse_lazy('meeting_detail', args=(meeting_pk,)))


class InvitedDelete(LoginRequiredMixin, CheckGroupMixin, View):
    required_group = 'supervisor'

    def dispatch(self, request, *args, **kwargs):
        invited = council_models.Invited.objects.get(pk=kwargs['pk'])
        meeting_pk = invited.meeting.pk
        invited.delete()
        return redirect(reverse_lazy('meeting_detail', args=(meeting_pk,)))


class UploadMeetingAttachment(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        meeting = council_models.Meeting.objects.get(pk=kwargs['pk'])
        try:
            att = council_models.Attachment(
                meeting=meeting,
                file=request.FILES['file'])
            att.save()

            return JsonResponse({'status': 'ok'})
        except:
            return JsonResponse({'status': 'error'})


class UploadPointAttachment(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        point = council_models.Point.objects.get(pk=kwargs['pk'])
        try:
            att = council_models.Attachment(
                point=point,
                file=request.FILES['file'])
            att.save()

            return JsonResponse({'status': 'ok'})
        except:
            return JsonResponse({'status': 'error'})


class AttachmentUpdateView(LoginRequiredMixin, UpdateView):
    model = council_models.Attachment
    form_class = council_forms.AttachmentForm
    template_name = 'council/edit_attachment.html'

    def form_valid(self, form):
        form.save(commit=False)
        return super(AttachmentUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AttachmentUpdateView, self).get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def get_success_url(self):
        if self.object.point:
            return reverse('point_detail', args=(self.object.point.pk,))
        else:
            return reverse('meeting_detail', args=(self.object.meeting.pk,))


class AttachmentDelete(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        attachment = council_models.Attachment.objects.get(pk=kwargs['pk'])
        if attachment.meeting:
            url = 'meeting_detail'
            obj_pk = attachment.meeting.pk
        elif attachment.point:
            url = 'point_detail'
            obj_pk = attachment.point.pk
        attachment.delete()
        return redirect(reverse_lazy(url, args=(obj_pk,)))


class VoteOutcomeCreateView(LoginRequiredMixin, CreateView):
    form_class = council_forms.VoteOutcomeForm
    template_name = 'council/add_vote.html'

    def form_valid(self, form):
        vote_outcome = form.save(commit=False)
        point = council_models.Point.objects.get(
            pk=self.kwargs['pk'])
        vote_outcome.point = point
        return super(VoteOutcomeCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(VoteOutcomeCreateView, self).get_context_data(**kwargs)
        context['point'] = council_models.Point.objects.get(
            pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return reverse_lazy('point_detail', args=(self.kwargs['pk'],))


class VoteOutcomeUpdateview(LoginRequiredMixin, UpdateView):
    model = council_models.VoteOutcome
    form_class = council_forms.VoteOutcomeForm
    template_name = 'council/add_vote.html'

    def form_valid(self, form):
        vote_outcome = form.save(commit=False)
        return super(VoteOutcomeUpdateview, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(VoteOutcomeUpdateview, self).get_context_data(**kwargs)
        context['point'] = self.object.point
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('point_detail', args=(self.object.point.pk,))


class VoteOutcomeDelete(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        vote = council_models.VoteOutcome.objects.get(pk=kwargs['pk'])
        point_pk = vote.point.pk
        vote.delete()
        return redirect(reverse_lazy('point_detail', args=(point_pk,)))


class GetAttendanceList(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        meeting = council_models.Meeting.objects.get(pk=kwargs['pk'])
        document = council_functions.generate_attendance_list(meeting=meeting)
        f = StringIO.StringIO()
        document.save(f)
        length = f.tell()
        f.seek(0)
        response = HttpResponse(
            f.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.' +
                         'wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename=example.docx'
        response['Content-Length'] = length
        return response


class GetInvitationLetter(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        meeting = council_models.Meeting.objects.get(pk=kwargs['pk'])
        document = council_functions.generate_invitation_letter(
            meeting=meeting)
        f = StringIO.StringIO()
        document.save(f)
        length = f.tell()
        f.seek(0)
        response = HttpResponse(
            f.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.' +
                         'wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename=example.docx'
        response['Content-Length'] = length
        return response


class SendInvitation(LoginRequiredMixin, CheckGroupMixin, View):
    required_group = 'supervisor'

    def get(self, request, *args, **kwargs):
        meeting = council_models.Meeting.objects.get(pk=kwargs['pk'])
        receivers = [inv.person.email for inv in
                     council_models.Invited.objects.filter(meeting=meeting)]

        subject = u'Zaproszenie na spotkanie Rady Wydziału Elektroniki'
        message = u'Przykładowe zaproszenie\n'
        message += u'Spotkanie: {}'.format(meeting)

        send_mail(subject=subject,
                  message=message,
                  from_email=u'Rada Wydziału Elektroniki',
                  recipient_list=receivers,
                  fail_silently=False)
        return redirect(reverse_lazy('meeting_detail', args=(meeting.pk,)))


def is_supervisor(person):
    if person:
        return person.group == council_dicts.SUPERVISOR_GROUP
    return False


def get_person_by_email(email):
    try:
        return council_models.Person.objects.get(email=email)
    except council_models.Person.DoesNotExist:
        return None
