from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'role', 'phone', 'company_name'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Automatically create a Shop for every new user (customer, vendor, dropshipper)
        # Name preference: company_name or "<username>'s Shop"
        try:
            from shop.models import Shop  # Local import to avoid circular imports at module load
            default_name = user.company_name or f"{user.username}'s Shop"
            Shop.objects.get_or_create(
                vendor=user,
                defaults={
                    'name': default_name,
                    'company_name': user.company_name or '',
                },
            )
        except Exception:
            # Avoid breaking signup if shop creation has any issue
            pass

        return user

class VendorSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'company_name', 'logo_url']

    def get_logo_url(self, obj):
        logo = getattr(obj, 'logo', None)
        if logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(logo.url)
            return logo.url
        return None