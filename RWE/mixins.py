# -*- encoding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


class LoginRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return super(LoginRequiredMixin, self).dispatch(request,
                                                            *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('login'))