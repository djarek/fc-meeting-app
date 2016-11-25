# -*- encoding: utf-8 -*-

from datetime import datetime

from django import forms
from bootstrap3_datetime.widgets import DateTimePicker

from functools import partial

import apps.council.models as council_models


class CouncilForm(forms.ModelForm):
    class Meta:
        model = council_models.FacultyCouncil
        fields = '__all__'


class MeetingForm(forms.ModelForm):
    class Meta:
        model = council_models.Meeting
        exclude = ['council', 'code']


class PointForm(forms.ModelForm):
    class Meta:
        model = council_models.Point
        exclude = ('meeting', 'owner')


class PersonForm(forms.ModelForm):
    class Meta:
        model = council_models.Person
        fields = ('scientific_title', 'first_name', 'last_name',
                  'email', 'is_creator', 'is_member')
        exclude = ('lookup', 'is_active')

