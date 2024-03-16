from rest_framework import serializers
from Scheduler.models import Task, VirtualEnvironments

class GeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = None


def get_my_serializer(model, fields):
        GeneralSerializer.Meta.model = model
        GeneralSerializer.Meta.fields = fields
        return GeneralSerializer


class SomeTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ["created_at", "updated_at"]
        

class VirtualEnvironmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualEnvironments
        fields = "__all__"