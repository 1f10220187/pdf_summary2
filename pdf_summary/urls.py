from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('detail/<int:pk>/', views.detail, name='detail'),
    path('delete/<int:pk>/', views.delete_pdf, name='delete_pdf'),
]