import uvicorn
import asyncio
from common.config import fast_api_settings

if __name__ == "__main__":
    uvicorn.run(
        "app:app", host=fast_api_settings.host, port=fast_api_settings.port, reload=True
    )
