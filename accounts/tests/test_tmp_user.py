"""
run in terminal:
export DJANGO_SETTINGS_MODULE=referral_service.settings

then use one of the options:
pytest --ignore=volumes/db/  # to avoid Permission denied
pytest accounts/tests/test_tmp_user.py -s  # it will trigger logger
python3 -m pytest accounts/tests/test_tmp_user.py -s  # it will trigger logger
"""

import pytest
from rest_framework.test import APIClient

from accounts.models import TemporaryUser


client = APIClient()


@pytest.mark.django_db
def test_create_tmp_user() -> None:
    """
    Тестируем создание TemporaryUser при первом обращении к сервису
    :return:
    """
    payload = {'phone': '+79995551122'}

    response_create = client.post('/api/accounts/code', data=payload, format='json')

    user = TemporaryUser.objects.filter(phone=payload.get('phone')).first()
    
    assert response_create.status_code == 201

    assert user is not None
