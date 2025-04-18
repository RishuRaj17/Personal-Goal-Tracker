from django.utils import timezone
from .models import Goal, Notification
import datetime

def check_reminders():
    """
    Check for goals with upcoming reminders and create notifications.
    This function should be called by a scheduled task (e.g., cron job or Celery task).
    """
    now = timezone.now()
    # Find goals with reminders that are due within the next minute and haven't been sent yet
    upcoming_reminders = Goal.objects.filter(
        reminder_date__lte=now + datetime.timedelta(minutes=1),
        reminder_date__gt=now - datetime.timedelta(minutes=1),
        reminder_sent=False
    )
    
    for goal in upcoming_reminders:
        # Create notification
        notification = Notification.objects.create(
            user=goal.user,
            goal=goal,
            title=f"Reminder: {goal.title}",
            message=f"Your goal '{goal.title}' has a reminder scheduled for now.",
            notification_type='reminder'
        )
        
        # Mark reminder as sent
        goal.reminder_sent = True
        goal.save()

def get_unread_notifications_count(user):
    """Get the count of unread notifications for a user"""
    return Notification.objects.filter(user=user, is_read=False).count()

def mark_notification_as_read(notification_id, user):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=user)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return True
    except Notification.DoesNotExist:
        return False 