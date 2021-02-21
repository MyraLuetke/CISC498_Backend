from django.urls import path
from . import views

urlpatterns = [
    path('checkin/', views.CustomerList.as_view()),
    path('checkin/create_account/', views.CustomerCreate.as_view()),
    #path('checkin/<int:pk>/', views.CustomerDetail),
    path('checkin/business/', views.BusinessList.as_view()),
    path('checkin/create_business_account/', views.BusinessCreate.as_view()),
]
