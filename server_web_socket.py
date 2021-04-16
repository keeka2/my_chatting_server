import asyncio
# 웹 소켓 모듈을 선언한다.
import json

import websockets

# 클라이언트 접속이 되면 호출된다.
from const import Status
from redis_database import set_client_server, get_send_people_list, update_chat_room, put_message_for_other_server, \
    get_message_to_send, close_connection, get_client_server


class Server:
    def __init__(self, port):
        self.on_server_client = {}
        self.chat_room_user_id_list = {}
        self.all_chatroom = {}
        self.host = "192.168.35.169"
        self.port = port

    def start(self):
        # 서버 데이터 초기화
        start_server = websockets.serve(self.receive_handler, self.host, self.port)
        # 비동기로 서버를 대기한다.
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def register(self, websocket):
        # 연결 설정
        user_id = await websocket.recv()
        # 새로운 유저
        print(f"새로운 유저 {user_id} 접속 축하!")
        self.on_server_client[user_id] = websocket
        set_client_server(user_id, self.host, self.port)
        print(self.on_server_client)

    async def accept(self, websocket, path):
        print("hi")
        await self.register(websocket)
        async for received_data_raw in websocket:
            received_data_json = json.loads(received_data_raw)
            status = received_data_json["status"]
            del received_data_json["status"]
            if status == Status.SEND_MESSAGE:
                await self.handle_received_message(received_data_json)

    async def receive_handler(self, websocket, path):
        await self.register(websocket)
        while True:
            receive_task = asyncio.ensure_future(websocket.recv())
            broadcast_task = asyncio.ensure_future(self.broadcast())
            done, pending = await asyncio.wait(
                [receive_task, broadcast_task],
                return_when=asyncio.FIRST_COMPLETED)
            if receive_task in done:
                received_data_raw = receive_task.result()
                received_data_json = json.loads(received_data_raw)
                status = received_data_json["status"]
                del received_data_json["status"]
                if status == Status.SEND_MESSAGE:
                    await self.handle_received_message(received_data_json)
            else:
                receive_task.cancel()

            if broadcast_task in done:
                message = broadcast_task.result()
            else:
                broadcast_task.cancel()

    async def enter_chat_room(self, received_data_json):
        user_id = received_data_json["user_id"]
        msg = received_data_json["msg"]
        chat_room_id = received_data_json["chat_room_id"]
        print(user_id, msg, chat_room_id)
        update_chat_room(user_id, chat_room_id)

    async def handle_received_message(self, received_data_json):
        received_data_raw = json.dumps(received_data_json)
        await self.enter_chat_room(received_data_json)
        user_id = received_data_json["user_id"]
        msg = received_data_json["msg"]
        chat_room_id = received_data_json["chat_room_id"]
        send_people_list = get_send_people_list(chat_room_id)
        v = {}
        USERS = []
        not_send_list = []
        print(send_people_list)
        for user in send_people_list:
            if user not in v:
                if user in self.on_server_client:
                    v[user] = True
                    ws = self.on_server_client[user]
                    USERS.append(user)
                    await ws.send(received_data_raw)
                else:
                    not_send_list.append(user)
        if not_send_list:
            for user in not_send_list:
                server_url = get_client_server(user)
                data = {
                    "user_id": user,
                    "received_data_raw": received_data_raw,
                }
                put_message_for_other_server(json.dumps(data), server_url)

    async def broadcast(self):
        while True:
            v = {}
            send_other_messages = get_message_to_send(self.host, self.port)
            if send_other_messages:
                futures = []
                for message in send_other_messages:
                    message_json = json.loads(message)
                    user = message_json["user_id"]
                    received_data_raw = message_json["received_data_raw"]
                    if user in self.on_server_client:
                        v[user] = True
                        ws = self.on_server_client[user]
                        futures.append(asyncio.ensure_future(ws.send(received_data_raw)))
                await asyncio.gather(*futures)
                break
            else:
                await asyncio.sleep(1)
        return True


# 비동기로 서버에 시한다.
if __name__ == "__main__":
    while True:
        try:
            port = int(input("server port:"))
            break
        except:
            print("try_again")
    server = Server(port)
    server.start()
