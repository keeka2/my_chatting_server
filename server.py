import json
import socket
import threading
from queue import Queue

from const import Status
from data import get_my_chatroom_list, get_my_chatroom_msg_list, add_to_my_chatroom_list, add_msg_in_chatroom, \
    get_all_chatroom, get_people_in_chatroom, add_chatroom


class Server:
    host = "127.0.0.1"
    port = 9000
    send_queue = None
    server_sock = None
    on_server_client = {}
    chat_room_user_id_list = {}
    all_chatroom = {}

    def print_all_chat_room(self):
        k = []
        for c in self.chat_room_user_id_list:
            k.append(c)
        print(k)

    def init_start_data(self):
        print("initiating start data")
        all_chatroom = get_all_chatroom()
        for chatroom in all_chatroom:
            self.all_chatroom[chatroom] = True
            self.chat_room_user_id_list[chatroom] = get_people_in_chatroom(chatroom)
        print("all_chat_room : ", all_chatroom)
        for c in self.chat_room_user_id_list:
            print(c, self.chat_room_user_id_list[c])

    def start(self):
        print("start")
        self.init_start_data()
        self.send_queue = Queue()
        self.server_sock = socket.socket()
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(10)

        while True:
            connection, address = self.server_sock.accept()
            thread1 = threading.Thread(target=self.receive, args=(connection,))
            thread1.start()

            thread2 = threading.Thread(target=self.send, args=())
            thread2.start()

    def put_init_data_response(self, received_data_json, connection):
        user_id = received_data_json["user_id"]
        data = {
            "status": Status.INIT_DATA_REQUEST,
            "user_id": user_id,
            "chat_room_list": get_my_chatroom_list(user_id),
            "chat_room_msg_dict": get_my_chatroom_msg_list(user_id)
        }
        self.on_server_client[user_id] = connection
        self.send_queue.put(data)
        print(user_id, "entered", "...", "send init data")

    def put_change_chat_room_response(self, received_data_json):
        user_id = received_data_json["user_id"]
        chat_room_id = received_data_json["chat_room_id"]

        # 아예 새로 만든 채팅방
        if chat_room_id not in self.all_chatroom:
            add_chatroom(chat_room_id)
            add_to_my_chatroom_list(user_id, chat_room_id)
            self.chat_room_user_id_list[chat_room_id] = [user_id]
            self.all_chatroom[chat_room_id] = True
            print(user_id, "made new chat room :", chat_room_id)
            print("all_chat_room : ", self.print_all_chat_room())
        # 처음 참가하는 채팅방
        elif user_id not in self.chat_room_user_id_list[chat_room_id]:
            self.chat_room_user_id_list[chat_room_id].append(user_id)
            add_to_my_chatroom_list(user_id, chat_room_id)
            print("new user (", user_id, ") entered chat room :", chat_room_id)
        else:
            print(user_id, "entered chat room :", chat_room_id)

        data = {
            "status": Status.CHANGE_CHAT_ROOM,
            "user_id": user_id,
            "msg": f"====entered {chat_room_id}====="
        }
        self.send_queue.put(data)

    def put_send_message_response(self, received_data_json):
        user_id = received_data_json["user_id"]
        data = {
            "status": Status.SEND_MESSAGE,
            "user_id": user_id,
            "msg": received_data_json["msg"],
            "chat_room_id": received_data_json["chat_room_id"],
        }
        chat_room_id = received_data_json["chat_room_id"]
        add_msg_in_chatroom(received_data_json)
        self.send_queue.put(data)
        print(f"[room_id:{chat_room_id}/u_id:{user_id}]: {received_data_json['msg']}")

    def receive(self, connection):
        while True:
            received_data = connection.recv(1024).decode()
            received_data_json = json.loads(received_data)

            status = received_data_json["status"]
            print(connection, status)
            if status == Status.INIT_DATA_REQUEST:
                self.put_init_data_response(received_data_json, connection)
            elif status == Status.CHANGE_CHAT_ROOM:
                self.put_change_chat_room_response(received_data_json)
            elif status == Status.SEND_MESSAGE:
                self.put_send_message_response(received_data_json)
            else:
                continue

    def send_init_data(self, send_data):
        user_id = send_data["user_id"]
        connection = self.on_server_client[user_id]
        send_data = json.dumps(send_data) + ";"
        connection.send(bytes(send_data.encode()))
        print(self.on_server_client)

    def send_change_chat_room_data(self, send_data):
        user_id = send_data["user_id"]
        connection = self.on_server_client[user_id]
        send_data = json.dumps(send_data) + ";"
        connection.send(bytes(send_data.encode()))

    def send_message_data(self, send_data):
        chat_room_id = send_data["chat_room_id"]
        send_people_id = self.chat_room_user_id_list[chat_room_id]
        send_data = json.dumps(send_data) + ";"
        print(chat_room_id, send_people_id, send_data)
        for person_id in send_people_id:
            if person_id in self.on_server_client:
                connection = self.on_server_client[person_id]
                connection.send(bytes(send_data.encode()))

    def send(self):
        while True:
            try:
                send_data = self.send_queue.get()
                print("send data:", send_data)
                status = send_data["status"]
                if status == Status.INIT_DATA_REQUEST:
                    self.send_init_data(send_data)
                elif status == Status.CHANGE_CHAT_ROOM:
                    self.send_change_chat_room_data(send_data)
                elif status == Status.SEND_MESSAGE:
                    self.send_message_data(send_data)
                else:
                    pass
            except:
                pass


if __name__ == "__main__":
    server = Server()
    try:
        server.start()
    except Exception as e:
        print(e)
        server.server_sock.close()
