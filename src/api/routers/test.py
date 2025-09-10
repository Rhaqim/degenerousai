from fastapi import APIRouter

router = APIRouter()

@router.get("/test/callback")
async def test_callback(payload: dict):
    task_id = payload.get("track_id")
    status = payload.get("status")

    print(f"Received callback for task {task_id} with status {status}")

    return {"message": "Callback received successfully"}