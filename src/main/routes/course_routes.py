from fastapi import APIRouter

# Phải có dòng này và tên biến phải là 'router'
router = APIRouter()

@router.get("/courses")
async def get_courses():
    return [{"id": 1, "name": "AI Course"}]