import uvicorn
from fastapi import FastAPI
from fastapi import Query

from data import get_my_chatroom_list, add_to_my_chatroom_list, get_my_chatroom_msg_list

app = FastAPI()


@app.get("/", description="message 서버 시작")
def read_root():
    return {"Hello": "This is messaging server"}


@app.get("/get/chatroom/", description="채팅방 목록 받아오기")
def get_chatroom_list(user_id=Query('', description='유저 id', example='')):
    return get_my_chatroom_list(user_id)


@app.get("/add/chatroom/", description="채팅방 목록 받아오기")
def add_chatroom(user_id=Query('', description='유저 id', example=''),
                 chat_room_id=Query('', description='채팅방 id', example='')):
    return add_to_my_chatroom_list(user_id, chat_room_id)


@app.get("/get/chatroom/msg/", description="채팅방 대화 내역 받아오기")
def get_chatroom_msg(user_id=Query('', description='유저 id', example='')):
    return get_my_chatroom_msg_list(user_id)


if __name__ == "__main__":
    uvicorn.run(app)
