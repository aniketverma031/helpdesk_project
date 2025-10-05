# tickets/forms.py
from django import forms
from .models import CustomUser, Ticket, Comment

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password', 'class': 'form-control'}),
        label="Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password', 'class': 'form-control'}),
        label="Confirm Password"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

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
        
        # Apply form-control class to all fields
        for field_name, field in self.fields.items():
            if field_name == 'description':
                field.widget.attrs.update({'class': 'form-control', 'rows': '4'})
            elif field_name == 'title':
                field.widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder': 'Enter ticket title'})
            elif field_name in ['assigned_to', 'status']:
                field.widget.attrs.update({'class': 'form-select'})
            else:
                 field.widget.attrs.update({'class': 'form-control'})

        agents = CustomUser.objects.filter(role='agent')
        self.fields['assigned_to'].choices = [
            (agent.id, agent.username) for agent in agents
        ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Type your comment here...'}),
        }

# NEW FORM: For Admin to change user roles
class RoleAssignmentForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES, 
        label="Select New Role",
        widget=forms.Select(attrs={'class': 'form-select'}) # Bootstrap class applied here
    )

    class Meta:
        model = CustomUser
        fields = ['role']