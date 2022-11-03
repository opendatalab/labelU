from datetime import datetime, timedelta

from jose import jwt

from labelu.internal.common.config import settings
from labelu.internal.common.security import create_access_token


def test_create_access_token_successful():

    # run
    access_token = create_access_token(data={"sub": "labelu@example.com"})

    # check
    payload = jwt.decode(
        access_token,
        settings.PASSWORD_SECRET_KEY,
        algorithms=[settings.TOKEN_GENERATE_ALGORITHM],
    )
    assert (
        (datetime.now() + timedelta(minutes=14, seconds=59)).timestamp()
        < payload["exp"]
        <= (datetime.now() + timedelta(minutes=15, seconds=1)).timestamp()
    )
