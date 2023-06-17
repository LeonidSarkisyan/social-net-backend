from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter(
    prefix='/file',
    tags=['file']
)


@router.get('/arrow/friend')
def get_file_arrow_friend():
    return ...
