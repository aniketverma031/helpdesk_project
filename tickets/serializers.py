# tickets/serializers.py

from rest_framework import serializers
from .models import Ticket, Comment
from django.contrib.auth.models import User

# Serializer for User (to show who created ticket or comment)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

# Serializer for Comment
class CommentSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'ticket', 'content', 'created_by', 'created_at']

# Serializer for Ticket
class TicketSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id',
            'title',
            'description',
            'created_by',
            'sla_deadline',
            'status',
            'updated_at',
            'comments'
        ]
