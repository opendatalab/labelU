from typing import Union

from pydantic import BaseModel
from typing import Generic, TypeVar

DataT = TypeVar("DataT", bound=BaseModel)


class UserResp(BaseModel):
    id: Union[int, None]
    username: Union[str, None]


class CommonDataResp(BaseModel):
    ok: bool


class MetaData(BaseModel):
    total: int
    page: Union[int, None]
    size: int


class OkResp(BaseModel, Generic[DataT]):
    data: DataT


class OkRespWithMeta(BaseModel, Generic[DataT]):
    meta_data: Union[MetaData, None] = None
    data: DataT

