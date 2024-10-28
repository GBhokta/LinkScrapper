from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('scrapper.urls')),  # Include URLs from the scraper app
]
