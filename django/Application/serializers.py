from rest_framework import serializers
from Application.models import SomeTaskReview, VenvTracker

class SomeTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SomeTaskReview
        exclude = ["created_at", "updated_at"]
        

class VenvTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenvTracker
        fields = "__all__"