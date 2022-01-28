from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer

from src.apps.trainings.models import Network

class NetworkFileField(serializers.FileField):
    def get_attribute(self, instance):
        # Pass the entire object instance, not just the field
        return instance

    def to_representation(self, obj):
        if not obj:
            return None
        url = obj.model_download_url
        if not url:
            return None
        request = self.context.get("request", None)
        if request is not None:
            return request.build_absolute_uri(url)
        return url

class NetworkZipFileField(serializers.FileField):
    def get_attribute(self, instance):
        # Pass the entire object instance, not just the field
        return instance

    def to_representation(self, obj):
        if not obj:
            return None
        url = obj.model_zip_download_url
        if not url:
            return None
        request = self.context.get("request", None)
        if request is not None:
            return request.build_absolute_uri(url)
        return url


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
            "log_gamma_game_count",
            "log_gamma_offset",
        ]
        extra_kwargs = {
            "url": {"lookup_field": "name"},
            "run": {"lookup_field": "name"},
            "parent_network": {"lookup_field": "name"},
        }

    model_file = NetworkFileField()
    model_zip_file = NetworkZipFileField()

    def validate(self, data):
        # Allow blank file only if random
        no_model_file = "model_file" not in data or len(data["model_file"]) <= 0
        if no_model_file and not ("is_random" in data and data["is_random"]):
            raise ValidationError("model_file is only allowed to be blank when is_random is True")
        return data

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
        if "log_gamma_offset" not in data:
            data["log_gamma_offset"] = 0.0

        return super().create(data)


class NetworkDownloadField(serializers.Field):
    def get_attribute(self, instance):
        # Pass the entire object instance, not just the field
        return instance

    def to_representation(self, obj):
        if not obj:
            return None
        url = obj.model_download_url
        if not url:
            return None
        request = self.context.get("request", None)
        if request is not None:
            return request.build_absolute_uri(url)
        return url

    def to_internal_value(self, data):
        raise serializers.ValidationError("NetworkDownloadField only supports output serialization")


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

    model_file = NetworkDownloadField()


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
