from datetime import datetime

from pydantic import BaseModel, UUID4, computed_field


class HasID(BaseModel):
    id: UUID4


class HasEventID(BaseModel):
    event_id: UUID4


class HasCreatedAt(BaseModel):
    created_at: datetime

    @computed_field
    @property
    def created_date(self) -> str:
        return self.created_at.date().isoformat()

    @computed_field
    @property
    def created_time(self) -> str:
        return self.created_at.time().strftime('%H:%M:%S')


class HasUpdatedAt(BaseModel):
    updated_at: datetime

    @computed_field
    @property
    def updated_date(self) -> str:
        return self.updated_at.date().isoformat()

    @computed_field
    @property
    def updated_time(self) -> str:
        return self.updated_at.time().strftime('%H:%M:%S')
