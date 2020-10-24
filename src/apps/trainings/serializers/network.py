from rest_framework.serializers import HyperlinkedModelSerializer

from src.apps.trainings.models import Network


class NetworkSerializer(HyperlinkedModelSerializer):
    """
    Serializer for general display of networks for their info pages, and upload.
    """

    class Meta:
        model = Network
        fields = [
            "url",
            "run",
            "name",
            "created_at",
            "network_size",
            "is_random",
            "training_games_enabled",
            "rating_games_enabled",
            "model_file",
            "model_file_bytes",
            "model_file_sha256",
            "model_zip_file",
            "parent_network",
            "train_step",
            "total_num_data_rows",
            "extra_stats",
            "notes",
            "log_gamma",
            "log_gamma_uncertainty",
            "log_gamma_lower_confidence",
            "log_gamma_upper_confidence",
        ]
        extra_kwargs = {
            "url": {"lookup_field": "name"},
            "run": {"lookup_field": "name"},
            "parent_network": {"lookup_field": "name"}
        }

    def create(self, validated_data):
        data = validated_data.copy()
        if "parent_network" in data:
            if data["parent_network"]:
                data["log_gamma"] = data["parent_network"].log_gamma
                data["log_gamma_uncertainty"] = 2.0
                data["log_gamma_lower_confidence"] = data["log_gamma"] - 2 * data["log_gamma_uncertainty"]
                data["log_gamma_upper_confidence"] = data["log_gamma"] + 2 * data["log_gamma_uncertainty"]
        if "log_gamma" in data and "log_gamma_uncertainty" not in data:
            data["log_gamma_uncertainty"] = 2.0
        if "log_gamma" in data and "log_gamma_uncertainty" in data:
            if "log_gamma_lower_confidence" not in data:
                data["log_gamma_lower_confidence"] = data["log_gamma"] - 2 * data["log_gamma_uncertainty"]
            if "log_gamma_upper_confidence" not in data:
                data["log_gamma_upper_confidence"] = data["log_gamma"] + 2 * data["log_gamma_uncertainty"]

        return super().create(data)

class NetworkSerializerForTasks(HyperlinkedModelSerializer):
    """
    Serializer exposing only the fields of a network that a self-play client needs.
    """

    class Meta:
        model = Network
        fields = [
            "url",
            "run",
            "name",
            "created_at",
            "is_random",
            "model_file",
            "model_file_bytes",
            "model_file_sha256",
        ]
        extra_kwargs = {
            "url": {"lookup_field": "name"},
            "run": {"lookup_field": "name"},
        }

class NetworkSerializerForElo(HyperlinkedModelSerializer):
    """
    Serializer exposing only the fields of a network for plotting the network strength over time
    """

    class Meta:
        model = Network
        fields = [
            "name",
            "created_at",
            "network_size",
            "total_num_data_rows",
            "log_gamma",
            "log_gamma_uncertainty",
        ]
