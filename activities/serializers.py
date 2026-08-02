from rest_framework import serializers

from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    target_type = serializers.SerializerMethodField()
    target_id = serializers.SerializerMethodField()
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            "id",
            "action",
            "details",
            "content_type",
            "object_id",
            "target_type",
            "target_id",
            "user",
            "user_email",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_target_type(self, obj):
        return obj.content_type.model if obj.content_type else None

    def get_target_id(self, obj):
        return obj.object_id
