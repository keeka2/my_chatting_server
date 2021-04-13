import asyncio
# 웹 소켓 모듈을 선언한다.
import json

import websockets

from api_server import get_client_init_data
from const import Status
from data_util.client_request_data import get_init_data_request_data, get_send_message_request_data


class Client:
    user_id = None
    cur_chatroom = None
    chat_room_list = []
    chat_room_msg_dict = {}

    def start(self):
        while True:
            try:
                user_id = int(input("my user id(int):"))
                user_id = str(user_id)
                self.user_id = user_id
                break
            except:
                print("wrong input retry")
        # 시작시 사용자 데이터 초기화 - websocket 아닌 api 요청
        self.init_user_data()
        asyncio.get_event_loop().run_until_complete(self.my_connect())

    def init_user_data(self):
        # api 요청
        init_data = get_client_init_data(self.user_id)
        self.chat_room_list = init_data["chat_room_list"]
        self.chat_room_msg_dict = init_data["chat_room_msg_dict"]

    async def my_connect(self):
        # 웹 소켓에 접속을 합니다.
        async with websockets.connect("ws://192.168.35.191:9998") as websocket:
            # 10번을 반복하면서 웹 소켓 서버로 메시지를 전송합니다.
            await websocket.send(self.user_id)
            msg = await websocket.recv()
            print(msg)

            while True:
                if not self.cur_chatroom:
                    await self.set_chatroom()
                await self.my_send(websocket)
                await self.my_received(websocket)

    async def set_chatroom(self):
        while True:
            chat_room_id = input("select or make new chat room(int):")
            try:
                integer_check = int(chat_room_id)
                self.cur_chatroom = chat_room_id
                if self.cur_chatroom in self.chat_room_msg_dict:
                    for chat_data in self.chat_room_msg_dict[self.cur_chatroom]:
                        print(chat_data["user_id"], ":", chat_data["msg"])
                else:
                    self.chat_room_list.append(self.cur_chatroom)
                    self.chat_room_msg_dict[self.cur_chatroom] = []
                break
            except Exception as e:
                print(e)
                print("wrong input retry")
                pass

        print(f"entered {chat_room_id}")
        print(f"if you want to change chat room input *exit* and press enter")

    async def my_send(self, websocket):
        msg = input()
        if msg == "*exit*":
            self.cur_chatroom = None
        elif msg:
            # send data: json 형식의 string format
            send_data = get_send_message_request_data(self.user_id, self.cur_chatroom, msg)
            await websocket.send(send_data)

    async def my_received(self, websocket):
        receive_data = await websocket.recv()
        received_data_json = json.loads(receive_data)
        received_status = received_data_json["status"]
        if received_status == Status.SEND_MESSAGE:
            await self.handle_received_message(received_data_json)
        print(receive_data)

    async def handle_received_message(self, received_data_json):
        user_id = received_data_json["user_id"]
        msg = received_data_json["msg"]
        chat_room_id = received_data_json["chat_room_id"]
        if self.cur_chatroom == chat_room_id:
            print(user_id, ":", msg)
        del received_data_json["status"]
        del received_data_json["chat_room_id"]
        self.chat_room_msg_dict[chat_room_id].append(received_data_json)


# 비동기로 서버에 접속한다.
if __name__ == "__main__":
    client = Client()
    client.start()