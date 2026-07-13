from datetime import datetime, timedelta

from jose import jwt

from labelu.internal.common.config import settings
from labelu.internal.common.security import AccessToken
from labelu.internal.common.security import create_access_token


def test_create_access_token_successful():
    # prepare data
    user_id = 1
    username = "labelu@example.com"
    token = AccessToken(id=user_id, username=username)

    # run
    access_token = create_access_token(token=token)

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


def test_access_token_no_exp_time():
    # prepare data - create a token with no expiration set initially
    token = AccessToken(id=1, username="user@example.com")
    encoded = jwt.encode(
        token.dict(),
        settings.PASSWORD_SECRET_KEY,
        algorithm=settings.TOKEN_GENERATE_ALGORITHM,
    )

    # check
    payload = jwt.decode(
        encoded,
        settings.PASSWORD_SECRET_KEY,
        algorithms=[settings.TOKEN_GENERATE_ALGORITHM],
        options={"verify_exp": False},
    )
    assert payload
    assert payload["id"] == 1
    assert payload["username"] == "user@example.com"
