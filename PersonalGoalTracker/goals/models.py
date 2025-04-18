from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#2d3436')  # Hex color code
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

class Goal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='goals')
    parent_goal = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_goals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    completed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # If this is a sub-goal, update parent goal status based on sub-goals
        if self.parent_goal:
            sub_goals = self.parent_goal.sub_goals.all()
            if sub_goals.exists():
                if all(goal.status == 'completed' for goal in sub_goals):
                    self.parent_goal.status = 'completed'
                    self.parent_goal.completed_date = timezone.now()
                    self.parent_goal.save()
                elif any(goal.status == 'in_progress' for goal in sub_goals):
                    self.parent_goal.status = 'in_progress'
                    self.parent_goal.save()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_date']

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    notification_type = models.CharField(max_length=20, default='reminder')

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    class Meta:
        ordering = ['-created_date']

class Streak(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streaks')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    total_days_active = models.IntegerField(default=0)

    def update_streak(self):
        today = timezone.now().date()
        print(f"Updating streak for {self.user.username}")
        print(f"Current date: {today}")
        print(f"Last activity date: {self.last_activity_date}")
        
        # Always update last_activity_date to today and increment total_days_active
        if not self.last_activity_date or self.last_activity_date != today:
            self.total_days_active += 1
            
            # Update streak count
            if not self.last_activity_date:
                # First activity ever
                self.current_streak = 1
            elif (today - self.last_activity_date).days == 1:
                # Consecutive day
                self.current_streak += 1
            else:
                # Streak broken
                if self.current_streak > self.longest_streak:
                    self.longest_streak = self.current_streak
                self.current_streak = 1
            
            # Update last activity date
            self.last_activity_date = today
            print(f"Updated last activity date to: {self.last_activity_date}")
            print(f"Current streak: {self.current_streak}")
            print(f"Total days active: {self.total_days_active}")
            self.save()

    def __str__(self):
        return f"{self.user.username}'s Streak: {self.current_streak} days"
