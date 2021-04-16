import json

import websocket
from const import Status

try:
    import thread
except ImportError:
    import _thread as thread
import time

cur_chatroom = None
user_id = None
chat_room_list = []


def on_message(ws, message):
    received_data_json = json.loads(message)
    user_id = received_data_json["user_id"]
    msg = received_data_json["msg"]
    chat_room_id = received_data_json["chat_room_id"]
    if cur_chatroom == chat_room_id:
        print(user_id, ":", msg)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("closed")


def on_open(ws):
    print(user_id, "entered")
    ws.send(user_id)

    def run(*args):
        global cur_chatroom
        while True:
            while True:
                chat_room_id = input("select or make new chat room(int):")
                try:
                    integer_check = int(chat_room_id)
                    cur_chatroom = chat_room_id
                    print(f"entered room: {chat_room_id}")
                    break
                except Exception as e:
                    print(e)
                    print("wrong input retry")
                    pass
            while True:
                msg = input()
                if msg == "*exit*":
                    cur_chatroom = None
                    break
                elif msg:
                    request_data = {
                            "status": Status.SEND_MESSAGE,
                            "user_id": user_id,
                            "chat_room_id": cur_chatroom,
                            "msg": msg,
                        }
                    send_data = json.dumps(request_data)
                    print(send_data)
                    ws.send(send_data)
                else:
                    time.sleep(1)
                    pass
            time.sleep(1)
            ws.close()
            print("thread terminating...")
            break

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    while True:
        try:
            port = int(input("server port:"))
            break
        except:
            print("try_again")

    uid = input("my user id:")
    user_id = uid
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f"ws://192.168.35.169:{port}",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.run_forever()
