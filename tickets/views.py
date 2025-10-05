# tickets/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Ticket, Comment, CustomUser
from .forms import TicketForm, CommentForm, UserRegistrationForm, RoleAssignmentForm

# --------------------
# TICKET VIEWS
# --------------------
@login_required
def tickets_list(request):
    if request.user.role == 'user':
        tickets = Ticket.objects.filter(created_by=request.user).order_by('-created_at')
    else:
        tickets = Ticket.objects.all().select_related('created_by', 'assigned_to').order_by('-created_at')

    return render(request, 'tickets_list.html', {'tickets': tickets})

@login_required
def ticket_new(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.sla_deadline = timezone.now() + timezone.timedelta(hours=48)
            ticket.save()
            messages.success(request, 'Ticket created successfully!')
            return redirect('tickets_list')
    else:
        form = TicketForm()

    # CRITICAL CHANGE: Fetch ALL users instead of just filtering for role='agent'
    all_users = CustomUser.objects.all().order_by('username') 

    # Pass the collection of all users to the template
    return render(request, 'ticket_new.html', {'form': form, 'all_users': all_users})





@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket.objects.select_related('created_by', 'assigned_to'), id=ticket_id)
    comments = ticket.comments.select_related('created_by').order_by('created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.created_by = request.user
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = CommentForm()

    ticket.is_breached = timezone.now() > ticket.sla_deadline
    ticket.save(update_fields=['is_breached'])

    return render(request, 'ticket_detail.html', {
        'ticket': ticket,
        'comments': comments,
        'comment_form': form
    })

# --------------------
# AUTH VIEWS
# --------------------
def custom_login(request):
    if request.user.is_authenticated:
        return redirect('tickets_list') # Stays here if already logged in

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            
            # --- NEW REDIRECT LOGIC ---
            if user.role == 'admin':
                # Redirect Admin to the management page
                return redirect('user_role_management') 
            else:
                # Redirect everyone else to the ticket list
                return redirect('tickets_list')
            # --- END NEW REDIRECT LOGIC ---

        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')



@login_required
def custom_logout(request):
    logout(request)
    return redirect('custom_login')

def register(request):
    if request.user.is_authenticated:
        return redirect('tickets_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            
            # CRITICAL SECURITY FIX: Force role to 'user' for public registration
            user.role = 'user'
            
            user.save()
            messages.success(request, "Account created! You can login now")
            return redirect('custom_login')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

# --------------------
# ADMIN VIEWS (NEW)
# --------------------
@login_required
def user_role_management(request):
    # SECURITY CHECK: Only allow users with the 'admin' role to access this page
    if request.user.role != 'admin':
        messages.error(request, "Access denied. You must be an administrator.")
        return redirect('tickets_list')

    users = CustomUser.objects.all().order_by('username')
    forms = {} # Dictionary to hold a form instance for each user

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user_to_update = get_object_or_404(CustomUser, id=user_id)
        
        form = RoleAssignmentForm(request.POST, instance=user_to_update)

        if form.is_valid():
            # Prevent accidental superuser demotion (good practice)
            if user_to_update.is_superuser and form.cleaned_data['role'] != user_to_update.role:
                 messages.error(request, f"Cannot change the role of Superuser {user_to_update.username} from the front-end.")
            else:
                form.save()
                messages.success(request, f"Role for {user_to_update.username} updated to {user_to_update.role}.")
            
            return redirect('user_role_management')
        else:
             forms[user_to_update.id] = form

    # Initialize forms for all users (or use the invalid form instance if available)
    for user in users:
        if user.id not in forms:
            forms[user.id] = RoleAssignmentForm(instance=user)

    return render(request, 'user_role_management.html', {
        'users': users,
        'forms': forms
    })