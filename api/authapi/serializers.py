from rest_framework import serializers
from .models import CustomUser, Company
from django.contrib.auth.password_validation import validate_password


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'company_name', 'company_address', 'phone_number']



class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True,
                                     validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'phone_number', 'password',
            'confirm_password', 'role', 'company']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')

        company_name = validated_data.pop('company', None)
        company = None
        if company_name:
            company = Company.objects.filter(company_name=company_name).first()  # Use company_name or another field
            if not company:
                raise serializers.ValidationError({
                                                      "company": "Company with the provided name does not exist."})

        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            role=validated_data['role']
        )

        if company:
            user.company = company
        user.save()
        return user

