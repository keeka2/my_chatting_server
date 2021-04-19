import json
import requests
import websocket
from const import Status, MyServer
from redis_database import get_server_list

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
                    request_data = {
                        "status": Status.CHANGE_CHAT_ROOM,
                        "user_id": user_id,
                        "chat_room_id": cur_chatroom,
                        "msg": f"{user_id} entered {cur_chatroom}",
                    }
                    send_data = json.dumps(request_data)
                    ws.send(send_data)
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
                elif msg =="stress_test":
                    for i in range(1000):
                        request_data = {
                            "status": Status.SEND_MESSAGE,
                            "user_id": user_id,
                            "chat_room_id": cur_chatroom,
                            "msg": f"{msg}_{i}",
                        }
                        send_data = json.dumps(request_data)
                        ws.send(send_data)
                elif msg:
                    request_data = {
                        "status": Status.SEND_MESSAGE,
                        "user_id": user_id,
                        "chat_room_id": cur_chatroom,
                        "msg": msg,
                    }
                    send_data = json.dumps(request_data)
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
    print(f"http://{MyServer.HOST}/get/server_list")
    resp = requests.get(f"http://{MyServer.HOST}/get/server_list")
    if resp:
        server_list = resp.json()["server_list"]
        print(server_list)
        for idx in range(len(server_list)):
            print(idx + 1, ":", server_list[idx])
        while True:
            try:
                server_idx = int(input("select server: "))
                if 0 <= server_idx - 1 < len(server_list):
                    server = server_list[server_idx - 1]
                    websocket_url = f"ws://{server}"
                    print(f"connected to {websocket_url}")
                    break
            except:
                print("wrong input try again")

        uid = input("my user id:")
        user_id = uid
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(websocket_url,
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)

        ws.run_forever()
    else:
        print("api server error")

