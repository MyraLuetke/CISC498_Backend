from django.urls import path
from . import views

urlpatterns = [
    path('checkin/', views.CustomerList.as_view()),
    path('checkin/create_account/', views.CustomerCreate.as_view()),
    #path('checkin/<int:pk>/', views.CustomerDetail),
]
