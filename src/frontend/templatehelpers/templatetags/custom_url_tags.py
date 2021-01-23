from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()

# These are performance hacks that directly build a relative URL for certain pages
# instead of relying on django reverse(), which seems to be very slow when called
# hundreds of times, once for each different item in a lst.


@register.simple_tag
def training_games_list_by_network(run_name, network_name):
    return f"/networks/{run_name}/{network_name}/training-games/"


@register.simple_tag
def rating_games_list_by_network(run_name, network_name):
    return f"/networks/{run_name}/{network_name}/rating-games/"


@register.simple_tag
def training_games_list_by_user(user_name):
    return f"/contributions/{user_name}/training-games/"


@register.simple_tag
def rating_games_list_by_user(user_name):
    return f"/contributions/{user_name}/rating-games/"


@register.simple_tag
def sgfplayer(kind, id_number):
    return f"/sgfplayer/{kind}-games/{id_number}/"


download_translated = _("Download")


@register.filter
def file_download_link_html(uploaded_file_obj):
    if uploaded_file_obj:
        return f'<a href="{uploaded_file_obj.url}">[{download_translated}]</a>'
    return ""


@register.filter
def download_link_html(file_url):
    if file_url:
        return f'<a href="{file_url}">[{download_translated}]</a>'
    return ""
