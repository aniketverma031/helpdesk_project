# tickets/api_views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Ticket, Comment
from .serializers import TicketSerializer, CommentSerializer
from django.db import transaction

# List and Create Tickets
class TicketListCreateAPI(generics.ListCreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        search = self.request.query_params.get('search', '')
        queryset = Ticket.objects.all()
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(
                description__icontains=search
            ) | queryset.filter(
                comments__content__icontains=search
            ).distinct()
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# Retrieve and Update Tickets (PATCH)
class TicketRetrieveUpdateAPI(generics.RetrieveUpdateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Ticket.objects.all()

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        ticket = self.get_object()
        # Optimistic locking using `updated_at`
        client_updated_at = request.data.get('updated_at')
        if client_updated_at and str(ticket.updated_at) != client_updated_at:
            return Response(
                {"detail": "Conflict: Ticket was updated by someone else."},
                status=status.HTTP_409_CONFLICT
            )
        return self.partial_update(request, *args, **kwargs)

# Create Comment for a Ticket
class CommentCreateAPI(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        ticket_id = self.kwargs['id']
        ticket = get_object_or_404(Ticket, id=ticket_id)
        serializer.save(ticket=ticket, created_by=self.request.user)
