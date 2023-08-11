import logging
from rest_framework import serializers
from passlib.hash import bcrypt

from .models import passcode_generator
from .models import TemporaryUser, User


logger = logging.getLogger(__name__)


class LoginSerializer(serializers.ModelSerializer):
    phone = serializers.DecimalField(max_digits=100, decimal_places=0)

    class Meta:
        model = TemporaryUser
        fields = ['phone']

    def validate(self, data):
        phone = data.get('phone')

        if not phone:
            raise serializers.ValidationError('Введите номер телефона (только цифры)')

        if len(phone.as_tuple().digits) != 11:
            raise serializers.ValidationError('Номер должен быть 11-значным')

        return data

    def create(self, validated_data):
        phone = validated_data.get('phone')

        passcode = passcode_generator()

        hashed_passcode = bcrypt.hash(passcode)   # хэшируем passcode для безопасного хранения в БД  (TemporaryUser)

        try:
            tmp_user = TemporaryUser.objects.filter(phone=phone)[:1].get()

            tmp_user.passcode = hashed_passcode

            tmp_user.save()

        except TemporaryUser.DoesNotExist:
            try:
                user = User.objects.filter(phone=phone)[:1].get()

                user.passcode = hashed_passcode

                user.save()

            except User.DoesNotExist:
                TemporaryUser.objects.create(phone=phone, passcode=hashed_passcode)

                logger.info(f'Создан Временный Пользователь для номера: [{phone}].')

        return {'phone': phone, 'passcode': passcode}


class CodeSerializer(serializers.Serializer):  # noqa
    phone = serializers.DecimalField(max_digits=100, decimal_places=0)
    passcode = serializers.CharField()
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(phone=obj.phone)

        return {
            'access': user.tokens()['access'],
            'refresh': user.tokens()['refresh']
        }

    def validate(self, data):
        passcode = data.get('passcode')

        phone = data.get('phone')

        if len(str(passcode)) != 4:
            raise serializers.ValidationError('Код должен быть 4-значным')

        try:
            TemporaryUser.objects.filter(phone=phone)[:1].get()

        except TemporaryUser.DoesNotExist:
            try:
                User.objects.filter(phone=phone)[:1].get()

            except User.DoesNotExist:
                raise serializers.ValidationError('Некорректный номер телефона')

        return data

    def create(self, validated_data):
        passcode = validated_data.get('passcode')

        phone = validated_data.get('phone')

        try:
            tmp_user = TemporaryUser.objects.filter(phone=phone)[:1].get()   # если найден TemporaryUser - создаем User

            if bcrypt.verify(str(passcode), tmp_user.passcode):
                new_passcode = bcrypt.hash(passcode_generator())

                user = User.objects.create(
                    phone=tmp_user.phone,
                    password=str(passcode),   # используем полученный passcode для генерации пароля при создании User
                    passcode=new_passcode,   # меняем passcode, чтобы повторный POST запрос уже вызвал исключение
                )

                tmp_user.delete()   # удаляем TemporaryUser за ненадобностью

                logger.info(f'Временный Пользователь для [{phone}] удален.\nСоздан постоянный Пользователь.')

                return user

        except TemporaryUser.DoesNotExist:
            try:
                user = User.objects.filter(phone=phone)[:1].get()

                if bcrypt.verify(str(passcode), user.passcode):
                    new_passcode = bcrypt.hash(passcode_generator())

                    user.password = str(passcode)   # на всякий случай меняем пароль пользователю ... (не обязательно)

                    user.passcode = new_passcode  # меняем passcode, чтобы предотвратить повторный POST запрос

                    user.save()

                    return user

            except User.DoesNotExist:
                pass

        logger.error(f'Введен неверный верификационный код для Пользователя: [{phone}].')

        raise serializers.ValidationError('Неверный код')
