from django.shortcuts import get_object_or_404
from django.views.generic import ListView, TemplateView

from src.apps.runs.models import Run

from . import view_utils


class RunsListView(ListView):
    template_name = "pages/runs.html"
    context_object_name = "run_list"

    def get_queryset(self):
        return Run.objects.order_by("status", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_run"] = Run.objects.select_current_or_latest()
        return context


class RunInfoView(TemplateView):
    template_name = "pages/run_info.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        run = get_object_or_404(Run, name=kwargs["run"])
        current_run = Run.objects.select_current_or_latest()
        context["run"] = run
        if run:
            view_utils.add_run_stats_context(run, context)

        context["is_older_run"] = run != current_run
        context["show_older_runs"] = Run.objects.count() > 1
        return context
