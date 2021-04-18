### Installation
<pre>
git clone https://github.com/keeka2/my_chatting_server.git
cd my_chatting_server
</pre>
### Run
<pre>
# build docker
docker build -t chatting .

# Setting - const.py
Server.HOST : 실행할 서버의 ip로 변경 (ex: 127.0.0.1)
Server.REDIS_HOST : redis HOST 주소 변경 (ex: 127.0.0.1)

# server
docker run -p [port]:10000 -it --rm chatting /bin/bash -c "poetry run python server_web_socket.py port=[port]" 

ex] docker run -p 10002:10000 -it --rm chatting /bin/bash -c "poetry run python server_web_socket.py port=10002"

#client
docker run -it --rm chatting /bin/bash -c "poetry run python client_web_socket.py"
</pre>
