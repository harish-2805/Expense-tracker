from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.full_name}! Your account has been created.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.full_name or user.email}!')
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

# Add this import at the top of accounts/views.py
from .models import CustomUser, Friendship
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q


@login_required
def friends_list(request):
    friends = request.user.get_friends()
    pending_received = request.user.get_pending_requests()
    pending_sent = Friendship.objects.filter(from_user=request.user, status='pending')

    return render(request, 'accounts/friends.html', {
        'friends': friends,
        'pending_received': pending_received,
        'pending_sent': pending_sent,
    })


@login_required
def send_friend_request(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Please enter an email address.')
            return redirect('friends_list')

        if email == request.user.email:
            messages.error(request, "You can't add yourself as a friend.")
            return redirect('friends_list')

        try:
            to_user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, f'No user found with email: {email}')
            return redirect('friends_list')

        # Check if already friends or request exists
        existing = Friendship.objects.filter(
            Q(from_user=request.user, to_user=to_user) |
            Q(from_user=to_user, to_user=request.user)
        ).first()

        if existing:
            if existing.status == 'accepted':
                messages.info(request, f'You are already friends with {to_user.email}.')
            elif existing.status == 'pending':
                messages.info(request, f'A friend request already exists with {to_user.email}.')
            elif existing.status == 'rejected':
                # Allow re-sending if previously rejected
                existing.status = 'pending'
                existing.from_user = request.user
                existing.to_user = to_user
                existing.save()
                messages.success(request, f'Friend request sent to {to_user.email}!')
        else:
            Friendship.objects.create(from_user=request.user, to_user=to_user)
            messages.success(request, f'Friend request sent to {to_user.email}!')

    return redirect('friends_list')


@login_required
def respond_friend_request(request, pk, action):
    friendship = get_object_or_404(Friendship, pk=pk, to_user=request.user)

    if action == 'accept':
        friendship.status = 'accepted'
        friendship.save()
        messages.success(request, f'You are now friends with {friendship.from_user.email}!')
    elif action == 'reject':
        friendship.status = 'rejected'
        friendship.save()
        messages.info(request, f'Friend request from {friendship.from_user.email} rejected.')

    return redirect('friends_list')


@login_required
def remove_friend(request, pk):
    user = request.user
    friend = get_object_or_404(CustomUser, pk=pk)

    friendship = Friendship.objects.filter(
        Q(from_user=user, to_user=friend) |
        Q(from_user=friend, to_user=user),
        status='accepted'
    ).first()

    if friendship:
        friendship.delete()
        messages.success(request, f'{friend.email} removed from friends.')
    else:
        messages.error(request, 'Friendship not found.')

    return redirect('friends_list')