from fastapi import APIRouter

router = APIRouter()

@router.post("/test/callback")
async def test_callback(payload: dict):
    task_id = payload.get("track_id")
    status = payload.get("status")

    print(f"Received callback for task {task_id} with status {status}")

    # save the result in the payload as a JSON file or database as needed
    # For demonstration, we'll just print the payload
    print(f"Callback payload: {payload}")

    return {"message": "Callback received successfully"}