"""
run in terminal:
export DJANGO_SETTINGS_MODULE=referral_service.settings

then use one of the options:
pytest --ignore=volumes/db/  # to avoid Permission denied
pytest accounts/tests/test_verify_code.py -s  # it will trigger logger
python3 -m pytest accounts/tests/test_verify_code.py -s  # it will trigger logger
"""

import pytest
from rest_framework.test import APIClient

from accounts.models import User


client = APIClient()


@pytest.mark.django_db
def test_code_verification() -> None:
    """
    Тестируем валидность введенного кода и создание User
    :return:
    """
    phone_payload = {'phone': '+79995551122'}

    response_create = client.post('/api/accounts/code', data=phone_payload, format='json')

    passcode = response_create.data.get('passcode')

    code_payload = {'phone': '+79995551122', 'passcode': passcode}

    response_verify = client.post('/api/accounts/verify', data=code_payload, format='json')

    user = User.objects.filter(phone=code_payload.get('phone')).first()

    assert response_verify.status_code == 201

    assert user is not None
