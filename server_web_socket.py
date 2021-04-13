import asyncio
# 웹 소켓 모듈을 선언한다.
import json

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
    loop = None
    send_queue = Queue()

    def start(self):
        # 서버 데이터 초기화
        self.init_server_data()
        self.loop = asyncio.get_event_loop()
        # self.loop.create_task(self.broadcast())

        # 웹 소켓 서버 생성.호스트는 localhost에 port는 9998로 생성한다.
        start_server = websockets.serve(self.accept, "localhost", 9998)
        # 비동기로 서버를 대기한다.
        self.loop.run_until_complete(start_server)
        self.loop.run_forever()

    def init_server_data(self):
        init_data = get_server_init_data()
        self.on_server_client = init_data["on_server_client"]
        self.chat_room_user_id_list = init_data["chat_room_user_id_list"]
        self.all_chatroom = init_data["all_chatroom"]

    async def accept(self, websocket, path):
        print(path)
        user_id = await websocket.recv()
        # 새로운 유저
        if user_id not in self.on_server_client:
            print(f"새로운 유저 {user_id} 접속 축하!")
            self.on_server_client[user_id] = websocket
            add_user(user_id)
            await websocket.send(f"새로운 유저 {user_id} 접속 축하!")
        elif not self.on_server_client[user_id]:
            print(f"새로운 유저 {user_id} 접속 축하!")
            self.on_server_client[user_id] = websocket
            await websocket.send(f"유저 {user_id}님 돌아온걸 환영해요!")

        while True:
            # 클라이언트로부터 메시지를 대기한다.
            receive_data = await websocket.recv()
            received_data_json = json.loads(receive_data)
            received_status = received_data_json["status"]
            if received_status == Status.SEND_MESSAGE:
                await self.handle_received_message(websocket, received_data_json)
                await self.broadcast()

    async def handle_received_message(self, websocket, received_data_json):
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
        self.send_queue.put(received_data_json)

    async def broadcast(self):
        send_data = self.send_queue.get()
        chat_room_id = send_data["chat_room_id"]
        send_people_list = self.chat_room_user_id_list[chat_room_id]
        send_data_raw = json.dumps(send_data)
        add_msg_in_chatroom(send_data)
        futures = []
        v = {}
        for user in send_people_list:
            if user in self.on_server_client and self.on_server_client[user] and user not in v:
                v[user] = True
                futures.append(asyncio.ensure_future(self.on_server_client[user].send(send_data_raw)))

        print(futures)
        await asyncio.gather(*futures, return_exceptions=False)
        await asyncio.sleep(2)


# 비동기로 서버에 시한다.
if __name__ == "__main__":
    server = Server()
    server.start()
