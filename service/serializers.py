import logging
from rest_framework import serializers
from accounts.models import User


logger = logging.getLogger(__name__)


class ReadProfileSerializer(serializers.ModelSerializer):
    invited_users = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone', 'referralcode', 'invitecode', 'invited_users']

    def get_invited_users(self, user):
        invited_users = User.objects.filter(is_invited=True, invitecode=user.referralcode)

        return invited_users.values('phone', 'created_at')


class WriteProfileSerializer(serializers.ModelSerializer):
    invitecode = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['invitecode']

    def validate(self, data):
        invitecode = data.get('invitecode')

        if len(str(invitecode)) != 6:
            raise serializers.ValidationError('Инвайт-код состоит из 6 символов')

        try:
            User.objects.filter(referralcode=data.get('invitecode'))[:1].get()

        except User.DoesNotExist:
            raise serializers.ValidationError('Приглашающий не найден')

        return data

    def update(self, instance, validated_data):
        if instance.invitecode:
            raise serializers.ValidationError('Инвайт-код уже был введен')

        invitecode = validated_data.get('invitecode')

        inviter = User.objects.get(referralcode=invitecode)

        inviter.is_inviter = True   # помечаем User как имеющего реферралов для будущей логики
        inviter.save()

        instance.invitecode = invitecode
        instance.is_invited = True   # помечаем User как приглашенного в сервис - для будущей логики
        instance.save()

        logger.info(f'Пользователь [{instance}] зарегистрировал инвайт-код.\nПриглашение от пользователя: [{inviter}]')

        return instance
