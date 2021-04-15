import asyncio
# 웹 소켓 모듈을 선언한다.
import json
import threading

import websockets
from queue import Queue
# 클라이언트 접속이 되면 호출된다.
from const import Status
from data_util.data import add_chatroom, add_to_my_chatroom_list, add_user, add_msg_in_chatroom
from data_util.server_response_data import get_server_init_data


class Server:
    on_server_client = {}
    chat_room_user_id_list = {}
    all_chatroom = {}
    send_queue = Queue()

    def start(self):
        # 서버 데이터 초기화
        start_server = websockets.serve(self.accept, "192.168.35.252", 9998)
        # 비동기로 서버를 대기한다.
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def init_server_data(self):
        init_data = get_server_init_data()
        self.on_server_client = init_data["on_server_client"]
        self.chat_room_user_id_list = init_data["chat_room_user_id_list"]
        all_chatroom_list = init_data["all_chatroom"]
        for chat_room in all_chatroom_list:
            self.all_chatroom[chat_room] = True

    async def register(self, websocket):
        # 연결 설정
        await self.init_server_data()
        user_id = await websocket.recv()
        # 새로운 유저
        if user_id not in self.on_server_client:
            print(f"새로운 유저 {user_id} 접속 축하!")
            self.on_server_client[user_id] = websocket
            add_user(user_id)
            await websocket.send(f"새로운 유저 {user_id} 접속 축하!")
        elif not self.on_server_client[user_id]:
            print(f"유저 {user_id}님 돌아온걸 환영해요!")
            self.on_server_client[user_id] = websocket
            await websocket.send(f"유저 {user_id}님 돌아온걸 환영해요!")

        print(self.on_server_client)

    async def accept(self, websocket, path):
        await self.register(websocket)
        print("접속 완료")
        while True:
            # 클라이언트로부터 메시지를 대기한다.
            received_data_raw = await websocket.recv()
            print(received_data_raw)
            await self.handle_received_message(received_data_raw)

    async def handle_received_message(self, received_data_raw):
        received_data_json = json.loads(received_data_raw)
        user_id = received_data_json["user_id"]
        msg = received_data_json["msg"]
        chat_room_id = received_data_json["chat_room_id"]
        print(user_id, msg, chat_room_id)

        # 아예 새로 만든 채팅방
        if chat_room_id not in self.all_chatroom:
            add_chatroom(chat_room_id)
            add_to_my_chatroom_list(user_id, chat_room_id)
            self.chat_room_user_id_list[chat_room_id] = [user_id]
            self.all_chatroom[chat_room_id] = True
            print(user_id, "made new chat room :", chat_room_id)
            print("all_chat_room : ", self.all_chatroom.keys())
        # 처음 참가하는 채팅방
        elif user_id not in self.chat_room_user_id_list[chat_room_id]:
            self.chat_room_user_id_list[chat_room_id].append(user_id)
            add_to_my_chatroom_list(user_id, chat_room_id)
            print("new user (", user_id, ") entered chat room :", chat_room_id)

        send_people_list = self.chat_room_user_id_list[chat_room_id]
        send_data_raw = json.dumps(received_data_raw)
        add_msg_in_chatroom(received_data_json)
        v = {}
        for user in send_people_list:
            if user in self.on_server_client and self.on_server_client[user] and user not in v:
                v[user] = True
                ws = self.on_server_client[user]
                print("sending...user ",send_data_raw)
                await ws.send(send_data_raw)
        print("finish sending", send_data_raw)


# 비동기로 서버에 시한다.
if __name__ == "__main__":
    server = Server()
    server.start()
