import uvicorn
from fastapi import FastAPI
from fastapi import Query

app = FastAPI()


@app.get("/", description="message 서버 시작")
def read_root():
    return {"Hello": "This is messaging server"}


@app.get("/send-message/", description="message 전송")
def send_message_to_client(chat_room_id=Query('', description='채팅방 id', example=''),
              user_id=Query('', description='유저 id', example=''),
              message=Query('', description='전송 메시지', example='')
              ):
    return {"Hello": "This is messaging server"}


@app.get("/get-message/", description="message 서버 시작")
def read_root():
    return {"Hello": "This is messaging server"}


@app.get("/", description="message 서버 시작")
def read_root():
    return {"Hello": "This is messaging server"}


if __name__ == "__main__":
    uvicorn.run(app)
