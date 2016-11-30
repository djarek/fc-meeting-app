# -*- encoding: utf-8 -*-
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic import View, TemplateView, CreateView, ListView,\
    DetailView, UpdateView
from django.http import HttpResponseForbidden

from RWE.mixins import LoginRequiredMixin
import apps.council.models as council_models
import apps.council.forms as council_forms


class CouncilListView(LoginRequiredMixin, ListView):
    model = council_models.FacultyCouncil
    template_name = 'council/council_list.html'


class CouncilCreateView(LoginRequiredMixin, CreateView):
    form_class = council_forms.CouncilForm
    template_name = 'council/add_council.html'

    def get_success_url(self):
        return reverse_lazy('council_detail', args=(self.object.pk,))


class CouncilDetailView(LoginRequiredMixin, DetailView):
    model = council_models.FacultyCouncil
    template_name = 'council/council_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CouncilDetailView, self).get_context_data(**kwargs)
        context['meeting_list'] = council_models.Meeting.objects.filter(
            council=self.object)
        context['members_list'] = council_models.FacultyCouncilMember.objects. \
            filter(council=self.object)
        return context


class CouncilUpdateView(LoginRequiredMixin, UpdateView):
    model = council_models.FacultyCouncil
    form_class = council_forms.CouncilForm
    template_name = 'council/add_council.html'

    def get_success_url(self):
        return reverse_lazy('council_detail', args=(self.object.pk,))


class CouncilDelete(LoginRequiredMixin, View):
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


class CouncilMemberCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'council/add_council_members.html'

    def get_context_data(self, **kwargs):
        context = super(CouncilMemberCreateView, self).get_context_data(
            **kwargs)
        context['persons'] = council_models.Person.objects.all()
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


class CouncilMemberDelete(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        member = council_models.FacultyCouncilMember.objects.get(
            pk=kwargs['m_pk'])
        council_pk = member.council.pk
        member.delete()
        return redirect(reverse_lazy('council_detail', args=(council_pk,)))


class MeetingCreateView(LoginRequiredMixin, CreateView):
    form_class = council_forms.MeetingForm
    template_name = 'council/add_meeting.html'

    def form_valid(self, form):
        meeting = form.save(commit=False)
        council = council_models.FacultyCouncil.objects.get(
            pk=self.kwargs['pk'])
        meeting.council = council
        return super(MeetingCreateView, self).form_valid(form)

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

    def get_context_data(self, **kwargs):
        context = super(MeetingDetailView, self).get_context_data(**kwargs)
        context['meeting'] = self.object
        context['point_list'] = council_models.Point.objects.filter(
            meeting=self.object)
        context['invited_list'] = council_models.Invited.objects.filter(
            meeting=self.object)
        return context


class MeetingUpdateView(LoginRequiredMixin, UpdateView):
    model = council_models.Meeting
    form_class = council_forms.MeetingForm
    template_name = 'council/add_meeting.html'

    def form_valid(self, form):
        form.save(commit=False)
        return super(MeetingUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(MeetingUpdateView, self).get_context_data(**kwargs)
        context['council'] = self.object.council
        return context

    def get_success_url(self):
        return reverse_lazy('meeting_detail', args=(self.object.pk,))


class MeetingDelete(LoginRequiredMixin, View):
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

    def form_valid(self, form):
        point = form.save(commit=False)
        meeting_pk = self.kwargs['pk']
        point.meeting = council_models.Meeting.objects.get(pk=meeting_pk)
        return super(PointCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(PointCreateView, self).get_context_data(**kwargs)
        context['meeting'] = council_models.Meeting.objects.get(
            pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return reverse('point_detail', args=(self.object.pk,))


class PointDetailView(LoginRequiredMixin, DetailView):
    model = council_models.Point
    template_name = 'council/point_detail.html'


class PointUpdateView(LoginRequiredMixin, UpdateView):
    model = council_models.Point
    form_class = council_forms.PointForm
    template_name = 'council/add_point.html'

    def form_valid(self, form):
        form.save(commit=False)
        return super(PointUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(PointUpdateView, self).get_context_data(**kwargs)
        context['meeting'] = self.object.meeting
        return context

    def get_success_url(self):
        return reverse('point_detail', args=(self.object.pk,))


class PointDelete(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        point = council_models.Point.objects.get(pk=kwargs['pk'])
        meeting_pk = point.meeting.pk
        council_models.ResolutionPoint.objects.filter(point=point).delete()
        council_models.Attachment.objects.filter(point=point).delete()
        council_models.VoteOutcome.objects.filter(point=point).delete()
        council_models.Access.objects.filter(point=point).delete()
        point.delete()
        return redirect(reverse_lazy('meeting_detail', args=(meeting_pk,)))


class PersonCreateForm(LoginRequiredMixin, CreateView):
    form_class = council_forms.PersonForm
    template_name = 'council/add_person.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            person = council_models.Person.objects.filter(
                email=request.user.email).first()
            if person and not person.is_creator:
                return HttpResponseForbidden(u'Brak dostępu')
        return super(PersonCreateForm, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('person_list')


class PersonListView(LoginRequiredMixin, ListView):
    model = council_models.Person
    template_name = 'council/person_list.html'


class InviteAllCouncilMembers(LoginRequiredMixin, View):
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


class InvitedCreateView(LoginRequiredMixin, TemplateView):
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
