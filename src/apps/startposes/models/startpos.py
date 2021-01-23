import os
import random

import numpy as np
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import PROTECT, BigAutoField, CharField, DateTimeField, FloatField, ForeignKey, Model, QuerySet
from django.utils.translation import gettext_lazy as _

from src.apps.runs.models import Run


class StartPosQuerySet(QuerySet):
    def select_weighted_random(self):
        current_run = Run.objects.select_current()
        if current_run is None:
            return None
        if current_run.startpos_locked:
            return None
        total_weight = current_run.startpos_total_weight
        if total_weight <= 0:
            return None
        r = random.random() * total_weight
        return self.filter(run=current_run, cumulative_weight__gte=r).order_by("cumulative_weight").first()


def validate_weight(value):
    if np.isnan(value) or value <= 0 or value > 1e200:
        raise ValidationError(
            _("%(value)s must be positive and not absurdly large"),
            params={"value": value},
        )


class StartPos(Model):
    """
    A startpos is a starting position for selfplay training. With some probability, clients requesting games will be given
    starting positions for those games to begin at.
    """

    objects = StartPosQuerySet.as_manager()

    class Meta:
        verbose_name = _("StartPos")
        verbose_name_plural = _("StartPoses")
        ordering = ["-created_at"]
        db_table = "startposes_startpos"

    id = BigAutoField(primary_key=True)
    run = ForeignKey(
        Run,
        verbose_name=_("run"),
        on_delete=PROTECT,
        null=False,
        blank=False,
        related_name="%(class)s_games",
        db_index=True,
    )
    created_at = DateTimeField(_("creation date"), auto_now_add=True, db_index=True)
    data = JSONField(
        _("data"),
        null=False,
        blank=False,
        help_text=_("JSON object describing the position."),
        db_index=False,
    )
    weight = FloatField(
        _("weight"),
        null=False,
        help_text=_("Weight for random selection. Please RERUN celery task to recompute cumulative if changing this!"),
        validators=[validate_weight],
        db_index=True,
    )
    cumulative_weight = FloatField(
        _("cumulative_weight"),
        default=-1,
        null=False,
        help_text=_("Cumulative weight, for efficient random selection."),
        db_index=True,
    )
    notes = CharField(
        _("notes"),
        max_length=1024,
        default="",
        null=False,
        blank=True,
        help_text=_("Special notes or info about this startpos."),
        db_index=False,
    )


class StartPosCumWeightOnly(Model):
    """
    An unmanaged version of StartPos to allow for updating without expensively loading the data field.
    """

    class Meta:
        managed = False
        db_table = "startposes_startpos"

    id = BigAutoField(primary_key=True)
    cumulative_weight = FloatField(
        _("cumulative_weight"),
        default=-1,
        null=False,
        help_text=_("Cumulative weight, for efficient random selection."),
        db_index=True,
    )
