"""
run in terminal:
export DJANGO_SETTINGS_MODULE=referral_service.settings

then use one of the options:
pytest --ignore=volumes/db/  # to avoid Permission denied
pytest service/tests/test_provide_invite_code.py -s  # it will trigger logger
python3 -m pytest service/tests/test_provide_invite_code.py -s  # it will trigger logger
"""

import pytest
from rest_framework.test import APIClient

from accounts.models import User


first_client = APIClient()
second_client = APIClient()


@pytest.mark.django_db
def test_save_invitecode() -> None:
    """
    Тестируем сохранение инвайт-кода и изменение данных обоих Пользователей
    :return:
    """
    phone_payload_first = {'phone': '+79995551122'}
    phone_payload_second = {'phone': '+79995552211'}

    response_create_first = first_client.post('/api/accounts/code', data=phone_payload_first, format='json')
    response_create_second = second_client.post('/api/accounts/code', data=phone_payload_second, format='json')

    passcode_first = response_create_first.data.get('passcode')
    passcode_second = response_create_second.data.get('passcode')

    code_payload_first = {'phone': '+79995551122', 'passcode': passcode_first}
    code_payload_second = {'phone': '+79995552211', 'passcode': passcode_second}

    first_client.post('/api/accounts/verify', data=code_payload_first, format='json')
    second_client.post('/api/accounts/verify', data=code_payload_second, format='json')

    first_user = User.objects.filter(phone=code_payload_first.get('phone')).first()
    second_user = User.objects.filter(phone=code_payload_second.get('phone')).first()

    invitecode = first_user.referralcode
    invitecode_payload = {"invitecode": invitecode}

    first_client.force_authenticate(user=first_user)
    second_client.force_authenticate(user=second_user)

    response_invitecode = second_client.patch('/api/service/profile', data=invitecode_payload, format='json')
    response_invited_users = first_client.get('/api/service/profile')

    first_user = User.objects.filter(phone=code_payload_first.get('phone')).first()
    second_user = User.objects.filter(phone=code_payload_second.get('phone')).first()

    assert response_invitecode.status_code == 200

    assert first_user.is_inviter is True
    assert second_user.is_invited is True
    assert second_user.invitecode == invitecode

    assert response_invited_users.status_code == 200

    invited_user = response_invited_users.data.get('invited_users')[0]

    assert invited_user.get('phone') == second_user.phone
    assert invited_user.get('created_at') == second_user.created_at
