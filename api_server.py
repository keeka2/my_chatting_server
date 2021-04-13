import uvicorn
from fastapi import FastAPI
from fastapi import Query

from data_util.data import get_my_chatroom_list, add_to_my_chatroom_list, get_my_chatroom_msg_list
from data_util.server_response_data import put_init_data_response_data

app = FastAPI()


@app.get("/", description="message 서버 시작")
def read_root():
    return {"Hello": "This is messaging server"}


@app.get("/client/initdata/", description="채팅방 목록 받아오기")
def get_client_init_data(user_id=Query('', description='유저 id', example='')):
    return put_init_data_response_data(user_id)


@app.get("/get/chatroom/msg/", description="채팅방 대화 내역 받아오기")
def get_chatroom_msg(user_id=Query('', description='유저 id', example='')):
    return get_my_chatroom_msg_list(user_id)


if __name__ == "__main__":
    uvicorn.run(app)
