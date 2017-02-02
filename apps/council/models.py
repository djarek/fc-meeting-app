# -*- encoding: utf-8 -*-
import os
from datetime import datetime
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.council.dictionaries import TITLES_CHOICES, GROUPS


def attachment_directory_path(instance, filename):
    if instance.meeting:
        return os.path.join(
            settings.MEDIA_ROOT, 'uploads', instance._meta.app_label,
            'meeting', str(instance.meeting.pk), filename)
    elif instance.point:
        return os.path.join(
            settings.MEDIA_ROOT, 'uploads', instance._meta.app_label,
            'point', str(instance.point.pk), filename)
    elif instance.resolution:
        return os.path.join(
            settings.MEDIA_ROOT, 'uploads', instance._meta.app_label,
            'resolution', str(instance.resolution.pk), filename)


class Person(models.Model):
    first_name = models.CharField(
        max_length=50,
        verbose_name=u'Imię')
    last_name = models.CharField(
        max_length=50,
        verbose_name=u'Nazwisko')
    scientific_title = models.CharField(
        max_length=1, blank=True, null=True,
        choices=TITLES_CHOICES,
        verbose_name=u'Tytuł/stopień naukowy')
    lookup = models.CharField(
        blank=True,
        max_length=150)
    email = models.EmailField(
        verbose_name=u'Adres e-mail',
        unique=True)
    group = models.CharField(
        max_length=12,
        choices=GROUPS,
        verbose_name=u'Grupa')
    is_active = models.BooleanField(
        default=True,
        verbose_name=u'Aktywne konto')
    is_member = models.BooleanField(
        default=False,
        verbose_name=u'Członek rady')

    def save(self, *args, **kwargs):
        if self.scientific_title:
            self.lookup = u'{} {} {}'.format(
                TITLES_CHOICES[int(self.scientific_title)-1][1],
                self.first_name,
                self.last_name)
            if int(self.scientific_title) >= 5:
                self.in_small_quorum = True
        else:
            self.lookup = u'{} {}'.format(self.first_name, self.last_name)
        super(Person, self).save(*args, **kwargs)

    def get_title_verbose(self):
        titles = dict(TITLES_CHOICES)
        if self.scientific_title in titles.keys():
            return titles[self.scientific_title]
        return u''

    def __unicode__(self):
        return u'{}'.format(self.lookup)


class FacultyCouncil(models.Model):
    term = models.PositiveIntegerField(
        unique=True,
        verbose_name=u'Kadencja')
    begin_date = models.DateField(
        verbose_name=u'Data rozpoczęcia')
    end_date = models.DateField(
        verbose_name=u'Data zakończenia')
    dean = models.CharField(
        max_length=100, verbose_name=u'Dziekan')

    def __unicode__(self):
        return u'Rada Wydziału {} {}-{}'.format(
            self.term, self.begin_date.isocalendar()[0],
            self.end_date.isocalendar()[0])


class FacultyCouncilMember(models.Model):
    person = models.ForeignKey('Person', verbose_name=u'Osoba')
    council = models.ForeignKey('FacultyCouncil', null=True,
                                verbose_name=u'Rada wydziału')

    def __unicode__(self):
        return u'{} {}'.format(self.person, self.council)


class Meeting(models.Model):
    number = models.PositiveIntegerField(
        verbose_name=u'Numer spotkania w roku',
        validators=[MinValueValidator(1), MaxValueValidator(9999)])
    council = models.ForeignKey(
        'FacultyCouncil',
        verbose_name=u'Rada Wydziału')
    date = models.DateTimeField(
        verbose_name=u'Data i godzina spotkania')
    code = models.CharField(
        blank=True,
        max_length=9,
        verbose_name=u'Kod spotkania')
    place = models.CharField(
        max_length=255,
        verbose_name=u'Miejsce spotkania')

    def save(self, *args, **kwargs):
        year = self.date.isocalendar()[0]
        num = Meeting.objects.filter(council=self.council,
                                     date__gte=datetime(year, 1, 1),
                                     date__lte=datetime(year+1, 1, 1)).count()
        self.number = num + 1
        self.code = u'{}/{}'.format(self.number,
                                    year)
        super(Meeting, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'Spotkanie Rady Wydziału {}'.format(self.code)


class Invited(models.Model):
    person = models.ForeignKey('Person', verbose_name=u'Osoba')
    meeting = models.ForeignKey('Meeting',
                                verbose_name=u'Spotkanie Rady Wydziału')
    is_present = models.BooleanField(default=False, verbose_name=u'Obecny')

    def __unicode__(self):
        return u'Zaproszona osoba: {}'.format(self.person)


class Access(models.Model):
    point = models.ForeignKey('Point', verbose_name=u'Punkt spotkania')
    invited = models.ForeignKey('Invited', verbose_name=u'Zaproszona osoba')


class Point(models.Model):
    number = models.PositiveIntegerField(
        verbose_name=u'Numer punktu',
        validators=[MinValueValidator(1), MaxValueValidator(9999)])
    title = models.CharField(
        max_length=255,
        verbose_name=u'Tytuł')
    meeting = models.ForeignKey(
        'Meeting',
        verbose_name=u'Spotkanie')
    owner = models.ForeignKey(
        'Invited', null=True,
        verbose_name=u'Opiekun')
    category = models.CharField(
        max_length=50,
        verbose_name=u'Rodzaj sprawy')
    description = models.TextField(
        verbose_name=u'Opis')
    is_final_agenda = models.BooleanField(
        default=True,
        verbose_name=u'Zakwalifikowany')

    def __unicode__(self):
        return u'{}) {}'.format(self.number, self.title)


class VoteOutcome(models.Model):
    number = models.PositiveIntegerField(
        verbose_name=u'Numer głosowania',
        validators=[MinValueValidator(1), MaxValueValidator(9999)])
    point = models.ForeignKey(
        'Point',
        verbose_name=u'Punkt')
    description = models.TextField(
        blank=True,
        verbose_name=u'Opis głosowania')
    valid_votes = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=u'Ważne głosy')
    yes_votes = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=u'Głosy za')
    no_votes = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=u'Głosy przeciw')
    abstain_votes = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=u'Głosy wstrzymania')
    all_votes = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=u'Wszystkie głosy')
    is_public = models.BooleanField(
        default=True,
        verbose_name=u'Głosowanie publiczne')
    small_quorum = models.BooleanField(
        default=False,
        verbose_name=u'Tylko małe kworum')
    ballot = models.ForeignKey(
        'Ballot', null=True, blank=True,
        verbose_name=u'Karta do głosowania')

    def __unicode__(self):
        return u'Punkt: {}, za: {}, przeciw: {}, wstrzymało się: {}'.format(
            self.point.title,
            self.yes_votes,
            self.no_votes,
            self.abstain_votes)


class Ballot(models.Model):
    number = models.PositiveIntegerField(
        verbose_name=u'Numer karty',
        validators=[MinValueValidator(1), MaxValueValidator(99)])
    point = models.ForeignKey(
        'Point',
        verbose_name=u'Punkt')
    description = models.TextField(
        verbose_name=u'Opis')

    def __unicode__(self):
        return u'Karta nr {}'.format(self.number)


class Attachment(models.Model):
    point = models.ForeignKey(
        'Point',
        null=True, blank=True,
        verbose_name=u'Punkt')
    description = models.TextField(
        blank=True,
        verbose_name=u'Opis załącznika')
    resolution = models.ForeignKey(
        'Resolution',
        blank=True, null=True,
        verbose_name=u'Uchwała')
    meeting = models.ForeignKey(
        'Meeting',
        blank=True, null=True,
        verbose_name=u'Spotkanie')
    file = models.FileField(
        verbose_name=u'Załączony plik',
        upload_to=attachment_directory_path)

    def __unicode__(self):
        if self.meeting:
            return u'{} {}'.format(
                self.meeting.code, os.path.basename(self.file.name))
        elif self.point:
            return u'{} {}'.format(
                self.point.number, os.path.basename(self.file.name))
        elif self.resolution:
            return u'{} {}'.format(
                self.resolution.number, os.path.basename(self.file.name))


class ResolutionPoint(models.Model):
    resolution = models.ForeignKey(
        'Resolution',
        verbose_name=u'Uchwała')
    point = models.ForeignKey(
        'Point',
        verbose_name=u'Punkt')


class Resolution(models.Model):
    title = models.CharField(max_length=250, verbose_name=u'Tytuł')
    description = models.TextField(verbose_name=u'Opis')
    number = models.IntegerField(unique=True, verbose_name=u'Numer uchwały')
    date = models.DateField(auto_now=True, verbose_name=u'Data')
