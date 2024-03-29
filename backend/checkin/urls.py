from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from . import views

urlpatterns = [
    path('api/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    path('checkin/customer/', views.CustomerList.as_view()),
    path('checkin/customer/create_account/', views.CustomerCreate.as_view()),
    path('checkin/customer/<user__id>/', views.CustomerDetail.as_view()),

    path('checkin/business/', views.BusinessList.as_view()),
    path('checkin/business/create_account/', views.BusinessCreate.as_view()),
    path('checkin/business/<user__id>/', views.BusinessDetail.as_view()),

    path('checkin/change_password/<id>/', views.ChangePassword.as_view()),
    path('checkin/change_email/<id>/', views.ChangeEmail.as_view()),

    path('checkin/visit/', views.VisitList.as_view()),
    path('checkin/visit/create_visit/', views.VisitCreate.as_view()),
    path('checkin/visit/business_create_visit/', views.BusinessAddedVisitCreate.as_view()),
    path('checkin/visit/business_create_unregistered_visit/', views.BusinessAddUnregisteredVisitCreate.as_view()),
]
