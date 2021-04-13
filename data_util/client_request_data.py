import json

from const import Status


def get_init_data_request_data(user_id):
    request_data = {
        "status": Status.INIT_DATA_REQUEST,
        "user_id": user_id,
    }
    return request_data


def get_change_chat_room_request_data(user_id, chat_room_id):
    request_data = {
        "status": Status.CHANGE_CHAT_ROOM,
        "user_id": user_id,
        "chat_room_id": chat_room_id,
    }
    return request_data


def get_send_message_request_data(user_id, cur_chatroom, msg):
    request_data = {
        "status": Status.SEND_MESSAGE,
        "user_id": user_id,
        "chat_room_id": cur_chatroom,
        "msg": msg,
    }
    return json.dumps(request_data)
