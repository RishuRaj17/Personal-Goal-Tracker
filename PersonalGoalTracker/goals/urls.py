from django.urls import path
from . import views

urlpatterns = [
    path('', views.goal_list, name='goal_list'),
    path('goal/create/', views.goal_create, name='goal_create'),
    path('goal/<int:pk>/update/', views.goal_update, name='goal_update'),
    path('goal/<int:pk>/delete/', views.goal_delete, name='goal_delete'),
    path('goal/<int:pk>/complete/', views.goal_complete, name='goal_complete'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('category/create/', views.category_create, name='category_create'),
    path('category/<int:pk>/update/', views.category_update, name='category_update'),
    path('category/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/test/', views.test_notification, name='test_notification'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('streak/', views.streak_board, name='streak_board'),
] 