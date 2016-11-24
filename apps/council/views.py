# -*- encoding: utf-8 -*-
from datetime import datetime

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic import View, TemplateView, CreateView, ListView,\
    DetailView
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
        return context


class MeetingCreateView(LoginRequiredMixin, CreateView):
    form_class = council_forms.MeetingForm
    template_name = 'council/add_meeting.html'

    def form_valid(self, form):
        meeting = form.save(commit=False)
        meeting.council = council_models.FacultyCouncil.objects.get(
            pk=self.kwargs['pk'])
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
        return context


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


class PersonCreateForm(LoginRequiredMixin, CreateView):
    form_class = council_forms.PersonForm
    template_name = 'council/add_person.html'

    def get(self, request, *args, **kwargs):
        person = council_models.Person.objects.get(email=request.user.email)
        if not person.is_creator:
            return HttpResponseForbidden(u'Brak dostępu')

    def get_success_url(self):
        return reverse('person_list')


class PersonListView(LoginRequiredMixin, ListView):
    model = council_models.Person
    template_name = 'council/person_list.html'