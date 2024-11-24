from pydantic import BaseModel, Field, field_validator
from typing import List


class SummaryResult(BaseModel):
    """
    Форма для вывода суммаризированной информации о компании
    """
    name: str = Field(description='Название компании')
    description: str = Field(
        description='Презентация продукта компании, подробное продающее описание продукта, которое заставит клиента приобрести этот товар'
    )
    proof_points: List[str] = Field(
        description='Список из 5 строк. Описание ценностного предложения. Конкретные пункты с преимуществами продукта, которые позволят продать его'
    )
    pain_points: List[str] = Field(
        description='Список из 5 строк. Описание проблем клиентов, которые может решить продукт компании'
    )

    @classmethod
    @field_validator('proof_points', 'pain_points')
    def length_validation(cls, field):
        if len(field) != 5:
            raise ValueError(f'length of filed {field} != 5')

        return field


class SummaryResultResponse(SummaryResult):
    full_summary: str = Field(description='Объединение всех полей в строку')