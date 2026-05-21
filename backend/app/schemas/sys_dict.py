from pydantic import BaseModel, ConfigDict, Field


class SysDictRowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dict_type: str
    code: str
    label: str
    parent_code: str | None = None
    sort_order: int = 0
    enabled: bool = True
    remark: str | None = None


class SysDictCreate(BaseModel):
    dict_type: str = Field(..., max_length=40)
    code: str = Field(..., max_length=60)
    label: str = Field(..., max_length=120)
    parent_code: str | None = Field(default=None, max_length=60)
    sort_order: int = 0
    enabled: bool = True
    remark: str | None = Field(default=None, max_length=255)


class SysDictUpdate(BaseModel):
    label: str | None = Field(default=None, max_length=120)
    parent_code: str | None = Field(default=None, max_length=60)
    sort_order: int | None = None
    enabled: bool | None = None
    remark: str | None = Field(default=None, max_length=255)


class DictTypeMeta(BaseModel):
    type: str
    label: str
    has_parent: bool = False
