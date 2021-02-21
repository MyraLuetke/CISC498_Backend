from django.urls import path
from . import views

urlpatterns = [
    path('checkin/', views.CustomerList.as_view()),
    path('checkin/create_account/', views.CustomerCreate.as_view()),
    path('checkin/<uuid:pk>/', views.CustomerDetail.as_view()),

    path('checkin/business/', views.BusinessList.as_view()),
    path('checkin/create_business_account/', views.BusinessCreate.as_view()),
    path('checkin/business/<uuid:pk>/', views.BusinessDetail.as_view()),
]
