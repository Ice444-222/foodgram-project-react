from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api.serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")
        access_token = AccessToken.for_user(user)
        response_data = {
            "auth_token": str(access_token),
        }
        return Response(response_data, status=status.HTTP_200_OK)
