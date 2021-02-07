from django.urls import path
from . import views

urlpatterns = [
    path('checkin/', views.CustomerList.as_view()),
    #path('checkin/<int:pk>/', views.CustomerDetail),
]
