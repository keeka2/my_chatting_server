from const import Status
from data_util.data import get_my_chatroom_list, get_my_chatroom_msg_list, get_all_chatroom, get_people_in_chatroom, \
    get_all_user


def put_init_data_response_data(user_id):
    response_data = {
        "status": Status.INIT_DATA_REQUEST,
        "user_id": user_id,
        "chat_room_list": get_my_chatroom_list(user_id),
        "chat_room_msg_dict": get_my_chatroom_msg_list(user_id)
    }
    return response_data


def get_server_init_data():
    all_user = get_all_user()
    on_server_client = {}
    for user in all_user:
        on_server_client[user] = False
    all_chatroom = get_all_chatroom()
    chat_room_user_id_list = {}
    for chatroom in all_chatroom:
        chat_room_user_id_list[chatroom] = get_people_in_chatroom(chatroom)
    response_data = {
        "on_server_client": on_server_client,
        "all_chatroom": all_chatroom,
        "chat_room_user_id_list": chat_room_user_id_list,
    }
    return response_data


def put_change_chat_room_response_data(user_id, chat_room_id):
    response_data = {
        "status": Status.CHANGE_CHAT_ROOM,
        "user_id": user_id,
        "msg": f"====entered {chat_room_id}====="
    }
    return response_data


def put_send_message_response_data(received_data_json):
    response_data = {
        "status": Status.SEND_MESSAGE,
        "user_id": received_data_json["user_id"],
        "msg": received_data_json["msg"],
        "chat_room_id": received_data_json["chat_room_id"],
    }
    return response_data
