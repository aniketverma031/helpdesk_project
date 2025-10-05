# tickets/api_urls.py

from django.urls import path
from . import api_views

urlpatterns = [
    # Tickets list and create
    path('tickets/', api_views.TicketListCreateAPI.as_view(), name='api_tickets_list_create'),

    # Ticket retrieve and update (PATCH)
    path('tickets/<int:id>/', api_views.TicketRetrieveUpdateAPI.as_view(), name='api_ticket_detail'),

    # Create comment for a ticket
    path('tickets/<int:id>/comments/', api_views.CommentCreateAPI.as_view(), name='api_ticket_comment_create'),
]
