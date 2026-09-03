from fastapi import APIRouter, HTTPException
from .workspace import build_workspace
from .db import connect, set_status

router = APIRouter(prefix='/workspace', tags=['workspace'])

@router.get('/{job_id}')
def workspace(job_id: str):
    try:
        return build_workspace(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail='Job not found')

@router.post('/{job_id}/status')
def status(job_id: str, payload: dict):
    value = payload.get('status')
    try:
        set_status(job_id, value)
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid status')
    return {'ok': True, 'job_id': job_id, 'status': value}
