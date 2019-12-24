from django.contrib.postgres.fields import JSONField
from django.db.models import Model, IntegerField, FileField, DateTimeField, ForeignKey, PROTECT


class Network(Model):
    """
    This class create a table to hold the different networks trained
    """
    nb_blocks = IntegerField()
    nb_channels = IntegerField()
    model_architecture = JSONField()

    created = DateTimeField(auto_now_add=True)
    elo = IntegerField()

    file = FileField()


class Gating(Model):
    """
    This class create a table to hold the different gating trained
    """
    reference_network = ForeignKey(Network, on_delete=PROTECT, related_name='%(class)s_gate_matches_as_reference')
    tested_network = ForeignKey(Network, on_delete=PROTECT, related_name='%(class)s_gate_matches_as_tested')

    nb_requested_matches = IntegerField()
    nb_won_by_reference_matches = IntegerField()
    nb_won_by_testes_matches = IntegerField()
    nb_draw_matches = IntegerField()
    nb_no_result_matches = IntegerField()

    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    elo_difference = IntegerField()

    file = FileField()
