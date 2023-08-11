from django.utils.decorators import method_decorator
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from accounts.models import User
from .serializers import ReadProfileSerializer, WriteProfileSerializer


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Показать информацию о пользователе и его рефералах",
    operation_summary="Показать информацию о пользовтеле"))
@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_description="вести инвайт-код пригласившего",
    operation_summary="Ввести инвайт-код"))
@method_decorator(name='patch', decorator=swagger_auto_schema(
    operation_description="Ввести инвайт-код пригласившего",
    operation_summary="Ввести инвайт-код"))
class ProfileView(generics.RetrieveUpdateAPIView):
    """View для просмотра профиля пользователя и сохранения инвайт-кода"""
    queryset = User.objects.all()
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return WriteProfileSerializer

        return ReadProfileSerializer

    def perform_update(self, serializer):
        serializer.save()

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user = self.get_object()

        serializer = ReadProfileSerializer(instance=user)

        return Response(serializer.data, status=status.HTTP_200_OK)
