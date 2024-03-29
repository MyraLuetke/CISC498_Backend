from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Customer, User, Business, Visit, UnregisteredVisit


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # The default result (access/refresh tokens)
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        data.update({'id': self.user.id})
        data.update({'is_customer': self.user.is_customer})
        return data


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ['id', 'email', 'password']

class DeactivateUserSerializer(serializers.Serializer):

    password = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ChangeEmailSerializer(serializers.Serializer):

    email = serializers.CharField(required=True)


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Customer
        fields = ['user', 'first_name', 'last_name', 'phone_num', 'email_verification', 'contact_pref']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['is_customer'] = True
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        customer, created = Customer.objects.update_or_create(user=user, first_name=validated_data.pop('first_name'),
                                                              last_name=validated_data.pop('last_name'),
                                                              phone_num=validated_data.pop('phone_num'),
                                                              contact_pref=validated_data.pop('contact_pref'))
        return customer


class BusinessSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Business
        fields = ['user', 'name', 'phone_num', 'street_address', 'city', 'postal_code', 'province', 'capacity']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        business, created = Business.objects.update_or_create(
            user=user,
            name=validated_data.pop('name'),
            phone_num=validated_data.pop('phone_num'),
            street_address=validated_data.pop('street_address'),
            city=validated_data.pop('city'),
            postal_code=validated_data.pop('postal_code'),
            province=validated_data.pop('province'),
            capacity=validated_data.pop('capacity'))
        return business


class VisitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Visit
        fields = ['dateTime', 'customer', 'business', 'numVisitors']

    def create(self, validated_data):

        customer = Customer.objects.get(user__id=validated_data.pop("customer"))
        business = Business.objects.get(user__id=validated_data.pop("business"))

        visit = Visit.objects.create(
            dateTime=validated_data.pop('dateTime'),
            customer=customer,
            business=business,
            numVisitors=validated_data.pop('numVisitors'))

        return visit


class BusinessAddedUnregisteredVisitSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnregisteredVisit
        fields = ['dateTime', 'first_name', 'last_name', 'phone_num', 'business', 'numVisitors']

    def create(self, validated_data):

        business = Business.objects.get(user__id=validated_data.pop("business"))

        unregisteredvisit = UnregisteredVisit.objects.create(
            dateTime=validated_data.pop('dateTime'),
            first_name=validated_data.pop('first_name'),
            last_name=validated_data.pop('last_name'),
            phone_num=validated_data.pop('phone_num'),
            business=business,
            numVisitors=validated_data.pop('numVisitors'))

        return unregisteredvisit


class BusinessAddedVisitSerializer(serializers.Serializer):

    dateTime = serializers.DateTimeField(required=True)
    customer = serializers.CharField(required=True)
    business = serializers.CharField(required=True)
    numVisitors = serializers.IntegerField(required=True)

    def create(self, validated_data):
        customer = Customer.objects.get(user__email=validated_data.pop("customer"))
        business = Business.objects.get(user__id=validated_data.pop("business"))

        visit = Visit.objects.create(
            dateTime=validated_data.pop('dateTime'),
            customer=customer,
            business=business,
            numVisitors=validated_data.pop('numVisitors'))

        return visit
