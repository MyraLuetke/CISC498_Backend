from django.urls import path
from . import views

urlpatterns = [
    path('checkin/customer/', views.CustomerList.as_view()),
    path('checkin/customer/create_account/', views.CustomerCreate.as_view()),
    path('checkin/customer/<user__email>/', views.CustomerDetail.as_view()),

    path('checkin/business/', views.BusinessList.as_view()),
    path('checkin/business/create_account/', views.BusinessCreate.as_view()),
    path('checkin/business/<user__email>/', views.BusinessDetail.as_view()),

    path('checkin/visit/', views.VisitList.as_view()),
    path('checkin/visit/create_visit/', views.VisitCreate.as_view()),


]
