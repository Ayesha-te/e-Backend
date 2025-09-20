from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'company_name', 'logo_url']

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo and hasattr(obj.logo, 'url'):
            url = obj.logo.url
            return request.build_absolute_uri(url) if request else url
        return None

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # Make logo optional and tolerant to missing/aliases
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'phone', 'company_name', 'logo']

    def to_internal_value(self, data):
        # Map common aliases to 'logo' if 'logo' not provided
        if 'logo' not in data:
            alt = data.get('file') or data.get('image')
            if alt is not None:
                md = data.copy()
                md['logo'] = alt
                data = md
        # If 'logo' is provided but not a real file (e.g., string/empty), ignore or set None
        try:
            from django.core.files.uploadedfile import UploadedFile
            val = data.get('logo', None)
            if val is not None and not isinstance(val, UploadedFile):
                # Treat empty string/null string as clearing/no upload
                if val in [None, '', 'null']:
                    md = data.copy()
                    md['logo'] = None
                    data = md
                else:
                    # Remove invalid non-file to avoid validation error
                    md = data.copy()
                    md.pop('logo', None)
                    data = md
        except Exception:
            pass
        return super().to_internal_value(data)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user