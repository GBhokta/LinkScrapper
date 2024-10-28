from django.urls import path
from . import views

urlpatterns = [
    path('', views.scrape_url, name='scrape_url'),      # Home page with form
    path('download_pdf/', views.download_pdf, name='download_pdf'),  # Download PDF
]
