from fastapi import FastAPI, HTTPException
from tasks import fetch_store_data_task

app = FastAPI()

@app.get("/fetch_store_data")
async def fetch_data(country: str):
    try:
        fetch_store_data_task.delay(country)
        return {"message": "Task to fetch and store data has been initiated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
