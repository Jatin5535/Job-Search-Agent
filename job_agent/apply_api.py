from fastapi import APIRouter, HTTPException
from .apply_copilot import build_apply_pack, mark_applied
from .copilot import load_profile

router=APIRouter(prefix='/apply', tags=['application'])

@router.get('/{job_id}/pack')
def apply_pack(job_id: str):
    try:
        return build_apply_pack(job_id, load_profile())
    except KeyError:
        raise HTTPException(status_code=404, detail='Job not found')

@router.post('/{job_id}/mark-applied')
def applied(job_id: str):
    return mark_applied(job_id)
