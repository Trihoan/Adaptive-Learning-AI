from pydantic import BaseModel

class CourseResponse(BaseModel):
    id: int
    maMonHoc: str
    tenMonHoc: str
    moTa: str

    class Config:
        from_attributes = True