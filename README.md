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

# server - 채팅 서버 시작
docker run -p [port]:10000 -it --rm chatting /bin/bash -c "poetry run python server_web_socket.py port=[port]" 
ex] docker run -p 10002:10000 -it --rm chatting /bin/bash -c "poetry run python server_web_socket.py port=10002"

# api server 시작
docker run -p 80:80 -it --rm chatting /bin/bash -c "python api_server.py"

#client
docker run -it --rm chatting /bin/bash -c "poetry run python client_web_socket.py"
</pre>
