import pickle

from redis_util import RedisClient


def get_all_chatroom():
    client = RedisClient()
    chatroom_list = client.conn.lrange("all_chatroom_list", 0, -1)
    if chatroom_list:
        return list(map(bytes.decode, chatroom_list))
    else:
        return []


def add_chatroom(chat_room_id):
    client = RedisClient()
    client.conn.rpush("all_chatroom_list", chat_room_id)


def get_my_chatroom_list(user_id):
    client = RedisClient()
    chatroom_list = client.conn.lrange(f"{user_id}_chatroom_list", 0, -1)
    if chatroom_list:
        return list(map(bytes.decode, chatroom_list))
    else:
        return []


def get_people_in_chatroom(chat_room_id):
    client = RedisClient()
    people_list = client.conn.lrange(f"{chat_room_id}_people_list", 0, -1)
    return list(map(bytes.decode, people_list))


def get_my_chatroom_msg_list(chat_room_list):
    client = RedisClient()
    chat_room_msg_list = {}
    for chat_room in chat_room_list:
        msg_list = client.conn.lrange(f"{chat_room}_chatroom_msg", 0, -1)
        chat_room_msg_list[chat_room] = list(map(pickle.loads, msg_list))
    return chat_room_msg_list


def add_to_my_chatroom_list(user_id, chat_room_id):
    client = RedisClient()
    client.conn.rpush(f"{user_id}_chatroom_list", chat_room_id)
    client.conn.rpush(f"{chat_room_id}_people_list", user_id)


def add_msg_in_chatroom(data):
    client = RedisClient()
    chat_room_id = data["chat_room_id"]
    del data["chat_room_id"]
    client.conn.rpush(f"{chat_room_id}_chatroom_msg", pickle.dumps(data))
