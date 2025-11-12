from dotenv import load_dotenv
load_dotenv(".env.dev")


import uvicorn

from app.v1 import *

service = NotificationService.factory()


if __name__ == "__main__":
    uvicorn.run("main:NotificationService.factory",
                host=os.environ["SERVICE_HOST"],
                port=int(os.environ["SERVICE_PORT"]),
                reload=True,
                factory=True,
                log_level="debug",
                lifespan="on")
