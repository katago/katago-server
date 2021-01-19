from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = "pages/account.html"
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
