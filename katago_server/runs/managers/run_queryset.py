from django.db.models import QuerySet


class RunQuerySet(QuerySet):
    def select_current(self):
        self.order_by("-created_at").first()
