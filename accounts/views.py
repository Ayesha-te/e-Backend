from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .serializers import SignupSerializer, UserSerializer

User = get_user_model()

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user, context={'request': request}).data)

class VendorListView(generics.ListAPIView):
    queryset = User.objects.filter(role='vendor')
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]