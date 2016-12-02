# -*- encoding: utf-8 -*-
from django import forms
import apps.council.models as council_models


class CouncilForm(forms.ModelForm):
    class Meta:
        model = council_models.FacultyCouncil
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CouncilForm, self).__init__(*args, **kwargs)
        self.fields['begin_date'] = forms.DateField(
            label=u'Data rozpoczęcia',
            input_formats=['%m/%Y'])
        self.fields['end_date'] = forms.DateField(
            label=u'Data zakończenia',
            input_formats=['%m/%Y'])


class MeetingForm(forms.ModelForm):
    class Meta:
        model = council_models.Meeting
        exclude = ['council', 'code', 'number']

    def __init__(self, *args, **kwargs):
        super(MeetingForm, self).__init__(*args, **kwargs)
        self.fields['date'] = forms.DateTimeField(
            input_formats=['%d.%m.%Y - %H:%M'])


class PointForm(forms.ModelForm):
    class Meta:
        model = council_models.Point
        exclude = ('meeting', 'owner',)


class PersonForm(forms.ModelForm):
    class Meta:
        model = council_models.Person
        fields = ('scientific_title', 'first_name', 'last_name',
                  'email', 'is_creator', 'is_member')
        exclude = ('lookup', 'is_active')


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = council_models.Attachment
        fields = ['description']
