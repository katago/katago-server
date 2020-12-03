from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from src.apps.runs.models import Run

from . import view_utils

class AccountView(LoginRequiredMixin, TemplateView):
  template_name = "pages/account.html"
  login_url = '/accounts/login/'
  redirect_field_name = 'redirect_to'
