# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View

class LoginObrigatorio(LoginRequiredMixin, View):
    redirect_field_name = "redirecionar"
    login_url = "/login"