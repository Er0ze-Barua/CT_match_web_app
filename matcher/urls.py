# matcher/urls.py
from django.urls import path
from . import views
from .views import login_view, register_view , forgot_password_view, home_view

urlpatterns = [
    path('', login_view, name='login'),
    path('register/' , views.register_view , name='register'),
    path('forgot-password/' , forgot_password_view, name ='forgot_password') ,
    path('home/' , home_view, name = 'home') ,
    path('download_results/', views.download_results, name='download_results'),
    path('logout/', views.user_logout, name='logout'),
    path('update_email/', views.update_email_view, name='update_email'),
]
