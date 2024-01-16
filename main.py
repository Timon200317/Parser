import uvicorn
import asyncio
from common.config import fastapi_settings

if __name__ == "__main__":
    uvicorn.run(
        "app:app", host=fastapi_settings.host, port=fastapi_settings.port, reload=True
    )
