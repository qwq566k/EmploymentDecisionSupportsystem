from typing import List, Union

from pydantic import BaseModel, model_validator

from .verify_model import BossZhipinModel, ZhiLianModel


class ResponseModel(BaseModel):
    code: int = 0
    message: str = "success"
    data: Union[dict, list] = []


class UpdateTaskModel(BaseModel):
    task_id: int
    status: int


class ResultModel(BaseModel):
    task_id: int
    platform: int
    data: List[dict]

    @model_validator(mode="after")
    def check_data(self):
        if self.platform == 1:
            self.data =  [ZhiLianModel.model_validate(item) for item in self.data]
            return self
        elif self.platform == 2:
            self.data =  [BossZhipinModel.model_validate(item) for item in self.data]
            return self
        else:
            raise ValueError('Invalid platform value')
