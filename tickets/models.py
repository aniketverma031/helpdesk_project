# tickets/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# ------------------------
# Custom User
# ------------------------
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('agent', 'Agent'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    # ADDED: Method to generate the DiceBear avatar URL
    def get_avatar_url(self):
        """Generates the DiceBear avatar URL for the user based on their username."""
        return f"https://api.dicebear.com/9.x/bottts/svg?seed={self.username}&size=80&backgroundColor=b6e3f4"
    
    # Avoid clashes with default User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

# ------------------------
# Ticket
# ------------------------
class Ticket(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(CustomUser, related_name='tickets_created', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(CustomUser, related_name='tickets_assigned', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    sla_deadline = models.DateTimeField()
    is_breached = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.status})"

# ------------------------
# Comment
# ------------------------
class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='comments', on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUser, related_name='comments_created', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.created_by.username} on {self.ticket.title}"