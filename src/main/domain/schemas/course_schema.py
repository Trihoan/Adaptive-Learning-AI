from pydantic import BaseModel

class CourseResponse(BaseModel):
    id: str
    title: str
    description: str