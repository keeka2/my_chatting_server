import asyncio
# 웹 소켓 모듈을 선언한다.
import sys
import json
import socket
import websockets
from const import Status, MyServer
from redis_database import set_client_server, get_send_people_list, update_chat_room, put_message_for_other_server, \
    get_message_to_send, close_connection, get_client_server, add_server


class Server:
    def __init__(self, host, port=10000):
        self.on_server_client = {}
        self.chat_room_user_id_list = {}
        self.all_chatroom = {}
        self.host = host
        self.container_port = 10000
        self.port = port

        # 서버가 실행되면 서버 주소 저장(클라이언트 접속시 서버 선택 가능)
        add_server(MyServer.HOST, port)

    def start(self):
        start_server = websockets.serve(self.receive_handler, self.host, self.container_port)
        # async로 선언되지 않은 일반 동기 함수 내에서 비동기 함수를 호출
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
                if status == Status.CHANGE_CHAT_ROOM:
                    await self.enter_chat_room(received_data_json)
                    await self.handle_received_message(received_data_json)
                elif status == Status.SEND_MESSAGE:
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
        chat_room_id = received_data_json["chat_room_id"]
        send_people_list = get_send_people_list(chat_room_id)
        v = {}
        # 퓨처(asyncio.Future)는 미래에 할 일을 표현하는 클래스인데 할 일을 취소하거나 상태 확인, 완료 및 결과 설정에 사용
        futures = []
        print(send_people_list)
        for user in send_people_list:
            if user not in v and user in self.on_server_client:
                v[user] = True
                ws = self.on_server_client[user]
                futures.append(asyncio.ensure_future(ws.send(received_data_raw)))
            else:
                server_url = get_client_server(user)
                data = {
                    "user_id": user,
                    "received_data_raw": received_data_raw,
                }
                put_message_for_other_server(json.dumps(data), server_url)
        await asyncio.gather(*futures)

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


if __name__ == "__main__":
    try:
        if len(sys.argv) == 2:
            port = sys.argv[1].split("=")[1]
            port = int(port)

            # 컨테이너의 ip 받아와서 host 설정
            host = socket.gethostbyname(socket.getfqdn())
            print(host, port)
            server = Server(host, port)
            server.start()
        else:
            print('start again ex)')
            print(
                'docker run -p [my_port]:10000 -it --rm chatting /bin/bash -c "poetry run python server_web_socket.py port=[my_port]"')
    except Exception as e:
        print(e)
        pass
