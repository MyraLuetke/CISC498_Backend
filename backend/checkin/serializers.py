from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Customer, User, Business, Visit


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


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ChangeEmailSerializer(serializers.Serializer):

    email = serializers.CharField(required=True)


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Customer
        fields = ['user', 'first_name', 'last_name', 'phone_num', 'email_verification']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['is_customer'] = True
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        customer, created = Customer.objects.update_or_create(user=user, first_name=validated_data.pop('first_name'),
                                                              last_name=validated_data.pop('last_name'),
                                                              phone_num=validated_data.pop('phone_num'))
        return customer


class BusinessSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Business
        fields = ['user', 'name', 'phone_num', 'address', 'capacity']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        business, created = Business.objects.update_or_create(
            user=user,
            name=validated_data.pop('name'),
            phone_num=validated_data.pop('phone_num'),
            address=validated_data.pop('address'),
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
