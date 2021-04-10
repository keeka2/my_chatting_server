import redis


class Singleton(type):
    """
    An metaclass for singleton purpose. Every singleton class should inherit from this class by 'metaclass=Singleton'.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RedisClient(metaclass=Singleton):
    HOST = "127.0.0.1"
    PORT = 6379

    def __init__(self):
        self.pool = redis.ConnectionPool(
            host=self.HOST, port=self.PORT
        )

    @property
    def conn(self):
        if not hasattr(self, "_conn"):
            self.get_connection()
        return self._conn

    def get_connection(self):
        self._conn = redis.Redis(connection_pool=self.pool)


if __name__ == "__main__":
    client = RedisClient()
    chatroom_list = client.conn.lrange("all_chatroom_list", 0, -1)
    if chatroom_list:
        print(list(map(bytes.decode, chatroom_list)))
    else:
        print([])

