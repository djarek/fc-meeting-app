# -*- encoding: utf-8 -*-
import os
from django.db import models
from django.conf import settings


TITLES_CHOICES = [
    ('1', u'inż.'),
    ('2', u'mgr inż.'),
    ('3', u'dr'),
    ('4', u'dr inż.'),
    ('5', u'dr hab.'),
    ('6', u'dr hab. inż.'),
    ('7', u'prof. dr hab.'),
    ('8', u'prof. dr hab. inż.'),
]


def attachment_directory_path(instance, filename):
    return os.path.join(
        settings.MEDIA_ROOT, 'uploads',
        instance._meta.app_label, str(instance.incsalary.pk), filename)


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
        verbose_name=u'Adres e-mail')
    is_active = models.BooleanField(
        default=True,
        verbose_name=u'Aktywne konto')
    is_creator = models.BooleanField(
        default=False,
        verbose_name=u'Konto zarządzające')
    is_member = models.BooleanField(
        default=False,
        verbose_name=u'Członek rady')
    is_small_quorum = models.BooleanField(
        default=False,
        verbose_name=u'Członek małego kworum')

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


class Group(models.Model):
    name = models.CharField(max_length=50, verbose_name=u'Nazwa grupy')

    def __unicode__(self):
        return self.name


class FacultyCouncil(models.Model):
    term = models.PositiveIntegerField(
        unique=True,
        verbose_name=u'Kadencja')
    begin_year = models.PositiveIntegerField(
        verbose_name=u'Rok rozpoczęcia')
    end_year = models.PositiveIntegerField(
        verbose_name=u'Rok zakończenia')
    dean = models.CharField(
        max_length=100, verbose_name=u'Dziekan')

    def __unicode__(self):
        return u'Rada Wydziału {} {}-{}'.format(self.term,
                                                self.begin_year,
                                                self.end_year)


class FacultyCouncilMember(models.Model):
    person = models.ForeignKey('Person', verbose_name=u'Osoba')
    council = models.ForeignKey('FacultyCouncil',
                                verbose_name=u'Rada wydziału')

    def __unicode__(self):
        return u'{} {}'.format(self.person, self.council)


class Meeting(models.Model):
    council = models.ForeignKey(
        'FacultyCouncil',
        verbose_name=u'Rada Wydziału')
    date = models.DateField(
        verbose_name=u'Data spotkania')
    code = models.CharField(
        blank=True,
        max_length=8,
        verbose_name=u'Kod spotkania')
    place = models.CharField(
        blank=True,
        max_length=255,
        verbose_name=u'Miejsce spotkania')

    def save(self, *args, **kwargs):
        self.code = u'{}/{}'.format(self.date.isocalendar()[0],
                                    self.date.isocalendar()[1])
        super(Meeting, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'Spotkanie Rady Wydziału {}'.format(self.code)


class Invited(models.Model):
    person = models.ForeignKey('Person', verbose_name=u'Osoba')
    meeting = models.ForeignKey('Meeting',
                                verbose_name=u'Spotkanie Rady Wydziału')
    group = models.ForeignKey('Group', verbose_name=u'Grupa')
    is_present = models.BooleanField(default=False, verbose_name=u'Obecny')

    def __unicode__(self):
        return u'Zaproszona osoba: {}'.format(self.person)


class Access(models.Model):
    point = models.ForeignKey('Point', verbose_name=u'Punkt spotkania')
    invited = models.ForeignKey('Invited', verbose_name=u'Zaproszona osoba')
    group = models.ForeignKey('Group', verbose_name=u'Grupa')

    def __unicode__(self):
        return u'{} {}'.format(self.point, self.group)


class Point(models.Model):
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
        return u'Punkt: {}'.format(self.title)


class VoteOutcome(models.Model):
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
    not_entitled = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=u'Niepodpisane')
    is_public = models.BooleanField(
        default=True,
        verbose_name=u'Głosowanie publiczne')

    def __unicode__(self):
        return u'Punkt: {}, za: {}, przeciw: {}, wstrzymało się: {}'.format(
            self.point.title,
            self.yes_votes,
            self.no_votes,
            self.abstain_votes)


class Attachment(models.Model):
    point = models.ForeignKey(
        'Point',
        verbose_name=u'Punkt')
    file = models.FileField(
        verbose_name=u'Załączony plik',
        upload_to=attachment_directory_path,
        null=True, blank=True)
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

    def __unicode__(self):
        return u'{} {}'.format(
            self.incsalary.title, os.path.basename(self.file.name))


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
