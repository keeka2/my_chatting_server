import pickle

from redis_util import RedisClient

client = RedisClient()


def add_server(host, port):
    key = "server_list"
    value = f"{host}:{port}"
    client.conn.rpush(key, value)


def get_server_list():
    key = "server_list"
    value = client.conn.lrange(key, 0, -1)
    return list(map(bytes.decode, value))


def set_client_server(user_id, host, port):
    set_key = f"{user_id}_server"
    set_value = f"{host}:{port}"
    client.conn.set(set_key, set_value)


def get_client_server(user_id):
    key = f"{user_id}_server"
    value = client.conn.get(key)
    return value.decode()


def update_chat_room(user_id, chat_room_id):
    key = f"{user_id}_cur_chat_room"
    old = client.conn.get(key)
    if not old or old.decode() != chat_room_id:
        chat_room_key = f"{old}_chat_room_user_list"
        client.conn.lrem(chat_room_key, 1, user_id)
        chat_room_key = f"{chat_room_id}_chat_room_user_list"
        client.conn.rpush(chat_room_key, user_id)
        client.conn.set(key, chat_room_id)


def get_send_people_list(chat_room_id):
    key = f"{chat_room_id}_chat_room_user_list"
    value = client.conn.lrange(key, 0, -1)
    return list(map(bytes.decode, value))


def put_message_for_other_server(data, server_url):
    key = f"{server_url}_messages"
    client.conn.rpush(key, data)


def get_message_to_send(host, port):
    key = f"{host}:{port}_messages"
    value = client.conn.lrange(key, 0, -1)
    client.conn.delete(key)
    return list(map(bytes.decode, value))


def close_connection(user_id, chat_room_id):
    server_key = f"{user_id}_server"
    client.conn.delete(server_key)
    if chat_room_id:
        chat_room_key = f"{chat_room_id}_chat_room_user_list"
        client.conn.lrem(chat_room_key, 1, user_id)
    cur_chat_room_key = f"{user_id}_cur_chat_room"
    if client.conn.get(cur_chat_room_key):
        client.conn.delete(cur_chat_room_key)


if __name__ == "__main__":
    client.conn.rpush("12_chat_room_user_list", "1")
    client.conn.lrem("12_chat_room_user_list", 1, "1")
    a = client.conn.lrange("12_chat_room_user_list", 0, -1)
    print(list(map(bytes.decode, a)))
