from rest_framework import serializers
from Application.models import SomeTaskReview

class SomeTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SomeTaskReview
        exclude = ["created_at", "updated_at"]