# -*- encoding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden

from apps.council.models import Person


class LoginRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return super(LoginRequiredMixin, self).dispatch(request,
                                                            *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('login'))


class CheckGroupMixin(object):
    required_group = None

    def dispatch(self, request, *args, **kwargs):
        if self.required_group:
            person = Person.objects.get(email=request.user.email)
            if person.group != self.required_group:
                return HttpResponseForbidden(u'Brak dostępu')
        return super(CheckGroupMixin, self).dispatch(request,
                                                        *args, **kwargs)