from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import LoginSerializer, CodeSerializer

import time


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_description="Запросить код верификации для пользователя с номером телефона",
    operation_summary="Запросить код верификации",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Номер телефона пользователя')
        }
    ),
    responses={
        status.HTTP_201_CREATED: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'passcode': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Код верификации'
                )
            }
        )
    }
))
class CodeView(APIView):
    """View для получения верификационного 4-х значного кода"""

    render_classes = [JSONRenderer]

    def post(self, request):
        phone = request.data.get('phone')

        phone_serializer = LoginSerializer(data={'phone': phone})

        phone_serializer.is_valid(raise_exception=True)

        tmp_user_data = phone_serializer.save()

        time.sleep(1)

        return Response({'passcode': tmp_user_data.get('passcode')}, status=status.HTTP_201_CREATED)


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_description="Подтвердить код верификации для пользователя с номером телефона",
    operation_summary="Подтвердить код верификации",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Номер телефона пользователя'),
            'passcode': openapi.Schema(type=openapi.TYPE_STRING, description='Код верификации')
        }
    ),
    responses={
        status.HTTP_201_CREATED: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'tokens': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access Token'),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh Token')
                    }
                )
            }
        )
    }
))
class VerificationView(APIView):
    """View для проверки верификационного 4-х значного кода"""

    render_classes = [JSONRenderer]

    def post(self, request):
        code_serializer = CodeSerializer(data=request.data)

        code_serializer.is_valid(raise_exception=True)

        code_serializer.save()

        tokens = code_serializer.data.get('tokens')

        return Response({'tokens': tokens}, status=status.HTTP_201_CREATED)
