from rest_framework import serializers

from .models import Customer, User


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ['email', 'password']


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Customer
        fields = ['user', 'first_name', 'last_name', 'phone_num', 'email_verification']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        customer, created = Customer.objects.update_or_create(user=user, first_name=validated_data.pop('first_name'),
                                                              last_name=validated_data.pop('last_name'),
                                                              phone_num=validated_data.pop('phone_num'))
        return customer
