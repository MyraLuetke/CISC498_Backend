from django.contrib.auth import update_session_auth_hash
from rest_framework import mixins, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Customer, User, Business, Visit
from .serializers import CustomerSerializer, UserSerializer, BusinessSerializer, ChangePasswordSerializer, \
    VisitSerializer, CustomTokenObtainPairSerializer, ChangeEmailSerializer, BusinessAddedVisitSerializer, \
    BusinessAddedUnregisteredVisitSerializer, DeactivateUserSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomerCreate(mixins.CreateModelMixin,
                     APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(status=status.HTTP_201_CREATED)
        try:
            if 'user with this email address already exists' in serializer.errors['user']['email'][0] and len(serializer.errors) == 1:
                user = User.objects.get(email=serializer.data['user']['email'])
                if user.is_active:
                    return Response(serializer.error_messages, status=status.HTTP_403_FORBIDDEN)
                else:
                    user.is_active = True
                    user.set_password(serializer.data.get("user").get("password"))
                    customer = Customer.objects.get(user=user)
                    customer.first_name = serializer.data.get("first_name")
                    customer.last_name = serializer.data.get("last_name")
                    customer.phone_num = serializer.data.get("phone_num")
                    customer.contact_pref = serializer.data.get("contact_pref")
                    user.is_customer = True
                    user.save()
                    customer.save()
                    return Response(status=status.HTTP_201_CREATED)
        except TypeError:
            return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class CustomerList(mixins.ListModelMixin,
                   generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CustomerDetail(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'user__id'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        user = self.get_object().user
        serializer = DeactivateUserSerializer(data=request.data)
        if serializer.is_valid():
            if not user.check_password(serializer.data.get("password")):
                return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
            user.is_active = False
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class BusinessCreate(mixins.CreateModelMixin,
                     APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = BusinessSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(status=status.HTTP_201_CREATED)
        try:
            if 'user with this email address already exists' in serializer.errors['user']['email'][0] and len(serializer.errors) == 1:
                user = User.objects.get(email=serializer.data['user']['email'])
                if user.is_active:
                    return Response(serializer.error_messages, status=status.HTTP_403_FORBIDDEN)
                else:
                    user.is_active = True
                    user.set_password(serializer.data.get("user").get("password"))
                    business = Business.objects.get(user=user)
                    business.name = serializer.data.get("name")
                    business.phone_num = serializer.data.get("phone_num")
                    business.street_address = serializer.data.get("street_address")
                    business.city = serializer.data.get("city")
                    business.postal_code = serializer.data.get("postal_code")
                    business.province = serializer.data.get("province")
                    business.capacity = serializer.data.get("capacity")
                    business.contact_pref = serializer.data.get("contact_pref")
                    user.save()
                    business.save()
                    return Response(status=status.HTTP_201_CREATED)
        except TypeError:
            return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class BusinessList(mixins.ListModelMixin,
                   generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BusinessDetail(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    lookup_field = 'user__id'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs,)

    def delete(self, request, *args, **kwargs):
        user = self.get_object().user
        serializer = DeactivateUserSerializer(data=request.data)
        if serializer.is_valid():
            if not user.check_password(serializer.data.get("password")):
                return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
            user.is_active = False
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)

class ChangePassword(mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.data.get("old_password")):
                return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            user.set_password(serializer.data.get("new_password"))
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmail(mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = ChangeEmailSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user.email = serializer.data.get("email")
            user.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class VisitCreate(mixins.CreateModelMixin, APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = VisitSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['customer'].user.is_active and serializer.validated_data['business'].user.is_active:
                serializer.create(validated_data=request.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class BusinessAddedVisitCreate(mixins.CreateModelMixin, APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = BusinessAddedVisitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class BusinessAddUnregisteredVisitCreate(mixins.CreateModelMixin, APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = BusinessAddedUnregisteredVisitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


# TEMP: just for database viewing purposes. Can delete
class VisitList(mixins.ListModelMixin, generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Visit.objects.all()
    serializer_class = VisitSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
