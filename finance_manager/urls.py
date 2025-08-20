from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Redirect '/' to base.html
def home_redirect(request):
    return redirect('base')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tracker.urls')),  # Include app URLs
]
