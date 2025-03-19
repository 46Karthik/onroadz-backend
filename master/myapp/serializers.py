from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User as AuthUser

# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
#     email = serializers.EmailField(required=True)
#     phone = serializers.CharField(required=False, allow_blank=True)
#     role = serializers.IntegerField(required=False, default=0)
#     is_active = serializers.IntegerField(required=False, default=2)

#     class Meta:
#         model = AuthUser
#         fields = ['username', 'email', 'password', 'phone', 'role', 'is_active']

#     def create(self, validated_data):
#         phone = validated_data.pop('phone', None)
#         role = validated_data.pop('role', 0)  # Default role to 0 if not provided

#         user = AuthUser.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )

#         Profile.objects.create(
#             user=user,
#             name=user.username,
#             phone=phone,
#             email=validated_data['email'],
#             role=role,  # Assign role directly
#             is_active=validated_data['is_active']
#         )

#         return user

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    role = serializers.IntegerField(required=False, default=0)
    is_active = serializers.IntegerField(required=False, default=2)

    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'email', 'password', 'phone', 'role', 'is_active']

    def create(self, validated_data):
        phone = validated_data.pop('phone', None)
        role = validated_data.pop('role', 0)  # Default role to 0 if not provided

        user = AuthUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        Profile.objects.create(
            user=user,
            name=user.username,
            phone=phone,
            email=validated_data['email'],
            role=role,  # Assign role directly
            is_active=validated_data['is_active']
        )

        return user

    def update(self, instance, validated_data):
        """Update user fields"""
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])  # Hash password before saving
        instance.save()

        # Update profile details
        profile = instance.profile
        profile.phone = validated_data.get('phone', profile.phone)
        profile.role = validated_data.get('role', profile.role)
        profile.is_active = validated_data.get('is_active', profile.is_active)
        profile.save()

        return instance

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"

class CityKmModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityKmModel
        fields = "__all__"

class HubsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hubs    
        fields = "__all__"
        extra_kwargs = {
            'created_by': {'required': False},
            'updated_by': {'required': False},
        }

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = "__all__"
        extra_kwargs = {
            'created_by': {'required': False},
            'updated_by': {'required': False},
            'car_image': {'required': False},
        }

class FeetCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeetCity
        fields = "__all__"


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = "__all__"


class FeetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fleet
        fields = "__all__"

class FeetDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FleetDocument
        fields = "__all__"