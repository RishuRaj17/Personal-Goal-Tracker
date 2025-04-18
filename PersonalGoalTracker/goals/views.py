from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Goal, Category, Notification, Streak
from .forms import GoalForm, CategoryForm
from django.http import JsonResponse
from .utils import get_unread_notifications_count, mark_notification_as_read
from django.views.decorators.http import require_POST
import random
import datetime

# List of motivational quotes
MOTIVATIONAL_QUOTES = [
    {
        "quote": "The only way to do great work is to love what you do.",
        "author": "Steve Jobs"
    },
    {
        "quote": "Success is not final, failure is not fatal: it is the courage to continue that counts.",
        "author": "Winston Churchill"
    },
    {
        "quote": "Believe you can and you're halfway there.",
        "author": "Theodore Roosevelt"
    },
    {
        "quote": "Don't watch the clock; do what it does. Keep going.",
        "author": "Sam Levenson"
    },
    {
        "quote": "The future depends on what you do today.",
        "author": "Mahatma Gandhi"
    },
    {
        "quote": "Your time is limited, don't waste it living someone else's life.",
        "author": "Steve Jobs"
    },
    {
        "quote": "It does not matter how slowly you go as long as you do not stop.",
        "author": "Confucius"
    },
    {
        "quote": "Everything you've ever wanted is on the other side of fear.",
        "author": "George Addair"
    },
    {
        "quote": "Success is walking from failure to failure with no loss of enthusiasm.",
        "author": "Winston Churchill"
    },
    {
        "quote": "The way to get started is to quit talking and begin doing.",
        "author": "Walt Disney"
    }
]

def get_daily_quote():
    """Get a motivational quote that stays the same for the entire day"""
    # Use the day of the year as a seed for random selection
    today = datetime.date.today()
    day_of_year = today.timetuple().tm_yday
    
    # Use the day of year to select a quote
    # This ensures the same quote is shown all day, but changes each day
    quote_index = day_of_year % len(MOTIVATIONAL_QUOTES)
    return MOTIVATIONAL_QUOTES[quote_index]

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('goal_list')
    else:
        form = UserCreationForm()
    return render(request, 'goals/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('goal_list')
    else:
        form = AuthenticationForm()
    return render(request, 'goals/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def goal_list(request):
    category_id = request.GET.get('category')
    goals = Goal.objects.filter(user=request.user)
    
    if category_id:
        goals = goals.filter(category_id=category_id)
    
    categories = Category.objects.filter(user=request.user)
    
    # Get daily motivational quote
    daily_quote = get_daily_quote()
    
    return render(request, 'goals/goal_list.html', {
        'goals': goals,
        'categories': categories,
        'selected_category': category_id,
        'daily_quote': daily_quote
    })

@login_required
def goal_create(request):
    if request.method == 'POST':
        form = GoalForm(request.POST, user=request.user)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            
            # Update user's streak
            streak, created = Streak.objects.get_or_create(user=request.user)
            streak.update_streak()
            
            messages.success(request, 'Goal created successfully!')
            return redirect('goal_list')
    else:
        form = GoalForm(user=request.user)
    return render(request, 'goals/goal_form.html', {'form': form, 'action': 'Create'})

@login_required
def goal_update(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal, user=request.user)
        if form.is_valid():
            form.save()
            
            # Update user's streak
            streak, created = Streak.objects.get_or_create(user=request.user)
            streak.update_streak()
            
            messages.success(request, 'Goal updated successfully!')
            return redirect('goal_list')
    else:
        form = GoalForm(instance=goal, user=request.user)
    return render(request, 'goals/goal_form.html', {'form': form, 'action': 'Update'})

@login_required
def goal_delete(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Goal deleted successfully!')
        return redirect('goal_list')
    return render(request, 'goals/goal_confirm_delete.html', {'goal': goal})

@login_required
def goal_complete(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    goal.status = 'completed'
    goal.completed_date = timezone.now()
    goal.save()
    
    # Update user's streak
    streak, created = Streak.objects.get_or_create(user=request.user)
    streak.update_streak()
    
    messages.success(request, 'Goal marked as completed!')
    return redirect('goal_list')

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'goals/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'goals/category_form.html', {'form': form, 'action': 'Create'})

@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'goals/category_form.html', {'form': form, 'action': 'Update'})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('category_list')
    return render(request, 'goals/category_confirm_delete.html', {'category': category})

def get_notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({'notifications': []})
    
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_date')
    
    notifications_data = [{
        'id': notification.id,
        'title': notification.title,
        'message': notification.message,
        'created_at': notification.created_date.strftime('%B %d, %Y %I:%M %p'),
        'notification_type': notification.notification_type
    } for notification in notifications]
    
    return JsonResponse({'notifications': notifications_data})

@require_POST
def mark_notification_read(request, notification_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'})
    
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user,
            is_read=False
        )
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'})

@login_required
def test_notification(request):
    # Create a test notification
    notification = Notification.objects.create(
        user=request.user,
        goal=Goal.objects.filter(user=request.user).first(),
        title="Test Notification",
        message="This is a test notification to verify the notification system is working.",
        notification_type='notification'
    )
    
    # Create a test alarm
    alarm = Notification.objects.create(
        user=request.user,
        goal=Goal.objects.filter(user=request.user).first(),
        title="Test Alarm",
        message="This is a test alarm to verify the alarm system is working.",
        notification_type='alarm'
    )
    
    return JsonResponse({'status': 'success'})

@require_POST
def mark_all_notifications_read(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'})
    
    try:
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def streak_board(request):
    streak, created = Streak.objects.get_or_create(user=request.user)
    
    # Get priority filter from query params
    priority_filter = request.GET.get('priority', None)
    
    # Get total completed goals count
    completed_goals_query = Goal.objects.filter(user=request.user, status='completed')
    if priority_filter:
        completed_goals_query = completed_goals_query.filter(priority=priority_filter)
    
    total_completed = completed_goals_query.count()
    
    # Get recently completed goals (last 5)
    completed_goals = completed_goals_query.order_by('-completed_date')[:5]
    
    # Get all priorities for filter options
    priorities = dict(Goal.PRIORITY_CHOICES)
    
    return render(request, 'goals/streak_board.html', {
        'streak': streak,
        'current_date': timezone.now().date(),
        'total_completed': total_completed,
        'completed_goals': completed_goals,
        'priorities': priorities,
        'current_priority': priority_filter
    })
