# tickets/forms.py
from django import forms
from .models import CustomUser, Ticket, Comment

ROLE_CHOICES = (
    ('user', 'User'),
    ('agent', 'Agent'),
    ('admin', 'Admin'),
)

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}),
        label="Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}),
        label="Confirm Password"
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Role")

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'password2', 'role']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password != password2:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'assigned_to', 'status']

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        agents = CustomUser.objects.filter(role='agent')
        # Build choices with data-image for DiceBear avatars
        self.fields['assigned_to'].widget = forms.Select(attrs={'class': 'form-control', 'id': 'assigned_to'})
        self.fields['assigned_to'].choices = [
            (agent.id, agent.username) for agent in agents
        ]
        # Attach avatar URLs in the widget options dynamically in template


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']