# -*- encoding: utf-8 -*-
import ldap

from django.views.generic import TemplateView, View
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group, Permission

from RWE.mixins import LoginRequiredMixin
from apps.council.models import Person


class HomeTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email', None)
        username = email.split('@')[0]
        password = request.POST.get('password', None)

        try:
            person = Person.objects.get(email=email)
        except Person.DoesNotExist:
            messages.error(request, u'Logowanie zakończyło się niepowodzeniem.')
            return redirect('login')

        if not person.is_active:
            messages.error(request, u'Logowanie zakończyło się niepowodzeniem.')
            return redirect('login')

        if request.POST.get('ldap_login', None):
            ldap.set_option(ldap.OPT_REFERRALS, 0)
            ldap.protocol_version = 3
            conn = ldap.initialize('ldap://z-student.pwr.wroc.pl/')
            if 'student' in email:
                q = "uid={}, ou=People, o=student.pwr.wroc.pl, o=pracownicy". \
                    format(username)
            else:
                q = "uid={}, ou=People, o=pwr.wroc.pl, o=pracownicy". \
                    format(username)

            try:
                res = conn.simple_bind_s(q, password)
            except ldap.INVALID_CREDENTIALS:
                messages.error(request,
                               u'Logowanie zakończyło się niepowodzeniem.')
                return redirect('login')

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            User.objects.create_user(username=email,
                                     email=email,
                                     password=password)
        user = authenticate(username=email, password=password)

        if user is None:
            messages.error(request,
                           u'Logowanie zakończyło się niepowodzeniem.')
            return redirect('login')

        login(request, user)
        if person.is_member:
            member_group, c = Group.objects.get_or_create(name='member')
            member_group.user_set.add(user)
        if person.is_small_quorum:
            small_quorum_group, c = Group.objects.get_or_create(
                name='small_quorum')
            small_quorum_group.user_set.add(user)
        if person.is_creator:
            creator_group, c = Group.objects.get_or_create(name='creator')
            creator_group.user_set.add(user)

        return redirect('home')




