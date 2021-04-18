import uvicorn
from fastapi import FastAPI

from redis_database import get_server_list

app = FastAPI()


@app.get("/get/server_list/")
def get_server():
    resp = {"server_list": get_server_list()}
    return resp


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=80)
