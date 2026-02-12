"""
URL configuration for MySite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from API.view import (render_index, login_view, register_view, user_page_view, 
                      admin_page_view, api_list_users, api_delete_user, api_add_user,
                      api_list_complaints, api_add_complaint)

urlpatterns = [
    path('', render_index, name='index'),
    path('admin-panel/', admin_page_view, name='admin_page'),
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('user/', user_page_view, name='user_page'),
    path('api/users/', api_list_users, name='api_list_users'),
    path('api/users/delete/', api_delete_user, name='api_delete_user'),
    path('api/users/add/', api_add_user, name='api_add_user'),
    path('api/complaints/', api_list_complaints, name='api_list_complaints'),
    path('api/complaints/add/', api_add_complaint, name='api_add_complaint'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
