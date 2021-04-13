import json
import socket
import threading
import requests

from const import Status
from data_util.client_request_data import get_change_chat_room_request_data, get_send_message_request_data, \
    get_init_data_request_data


class Client:
    # server ip
    host = "127.0.0.1"
    socket_port = 9000
    cur_chatroom = None
    chat_room_list = []
    chat_room_msg_dict = {}

    def __init__(self, user_id):
        self.user_id = user_id
        self.client_sock = socket.socket()
        self.client_sock.connect((self.host, self.socket_port))
        print('Connecting to ', self.host, self.socket_port)

    def start(self):
        self.request_init_data()
        # Client의 메시지를 보낼 쓰레드
        thread1 = threading.Thread(target=self.send, args=())
        thread1.start()

        # Server로 부터 다른 클라이언트의 메시지를 받을 쓰레드
        thread2 = threading.Thread(target=self.receive, args=())
        thread2.start()

    def send_data(self, request_data):
        encoded_request_data = bytes(json.dumps(request_data).encode())
        self.client_sock.send(encoded_request_data)  # Client -> Server 데이터 통신

    def request_init_data(self):
        request_data = get_init_data_request_data(self.user_id)
        self.send_data(request_data)

    def change_chat_room(self, chat_room_id):
        request_data = get_change_chat_room_request_data(self.user_id, chat_room_id)
        self.send_data(request_data)

    def send_message(self, msg):
        request_data = get_send_message_request_data(self.user_id, self.cur_chatroom, msg)
        self.send_data(request_data)
        del request_data["chat_room_id"]
        self.chat_room_msg_dict[self.cur_chatroom].append(request_data)

    def send(self):
        while True:
            print("my chat room list:", self.chat_room_list)
            if not self.cur_chatroom:
                chat_room_id = input("select or make new chat room(int):")
                try:
                    integer_check = int(chat_room_id)
                    self.cur_chatroom = chat_room_id
                    self.change_chat_room(chat_room_id)

                    print(f"entered {chat_room_id}")
                    print(f"if you want to change chat room input *exit* and press enter")
                    if self.cur_chatroom in self.chat_room_msg_dict:
                        for chat_data in self.chat_room_msg_dict[self.cur_chatroom]:
                            print(chat_data["user_id"], ":", chat_data["msg"])
                    else:
                        self.chat_room_list.append(self.cur_chatroom)
                        self.chat_room_msg_dict[self.cur_chatroom] = []
                except:
                    print("wrong input retry")
                    continue

            while True:
                msg = input()
                if msg == "*exit*":
                    self.cur_chatroom = None
                    break
                self.send_message(msg)
                print(self.user_id, ":", msg)

    def receive(self):
        while True:
            received_data = self.client_sock.recv(1024).decode()  # Server -> Client 데이터 수신
            received_data_json = json.loads(received_data.split(";")[0])
            status = received_data_json["status"]
            if status == Status.INIT_DATA_REQUEST:
                self.chat_room_list = received_data_json["chat_room_list"]
                self.chat_room_msg_dict = received_data_json["chat_room_msg_dict"]
            elif status == Status.ADD_CHAT_ROOM:
                self.chat_room_msg_dict["chat_room_id"] = []
            elif status == Status.SEND_MESSAGE:
                chat_room_id = received_data_json["chat_room_id"]
                if self.cur_chatroom == chat_room_id:
                    opponent_id = received_data_json["user_id"]
                    msg = received_data_json["msg"]
                    print(opponent_id, ":", msg)
                del received_data_json["chat_room_id"]
                self.chat_room_msg_dict[chat_room_id].append(received_data_json)


if __name__ == "__main__":
    my_id = input("my user id(int):")
    me = Client(my_id)
    try:
        me.start()
    except Exception as e:
        print(e)
        me.client_sock.close()
