from django import forms
from django.utils import timezone
from .models import Goal, Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color']
        widgets = {
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'style': 'width: 100%; height: 40px; padding: 0;'
            }),
        }

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['title', 'description', 'category', 'target_date', 'status', 'priority', 'parent_goal']
        widgets = {
            'target_date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date().isoformat()}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filter parent_goal choices to only show goals that belong to the user
            self.fields['parent_goal'].queryset = Goal.objects.filter(user=user)
            # Filter category choices to only show categories that belong to the user
            self.fields['category'].queryset = Category.objects.filter(user=user)

    def clean_target_date(self):
        target_date = self.cleaned_data.get('target_date')
        if target_date and target_date < timezone.now().date():
            raise forms.ValidationError("Target date cannot be in the past. Please select today or a future date.")
        return target_date 