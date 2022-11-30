from typing import Union

from pydantic import BaseModel
from typing import Generic, TypeVar
from typing import Generic, TypeVar
from pydantic.generics import GenericModel

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


class OkResp(GenericModel, Generic[DataT]):
    data: DataT


class OkRespWithMeta(GenericModel, Generic[DataT]):
    meta_data: Union[MetaData, None] = None
    data: DataT
