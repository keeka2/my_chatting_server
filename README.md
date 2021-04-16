### Installation
<pre>
git clone 
cd my_chatting_server
</pre>
### Run
<pre>
# build docker
docker build -t chatting .

# 공통
서버로 사용할 ip 변경, redis_util에서 redis 주소 변경

# server
docker run -it --rm chatting /bin/bash -c "poetry run python server_web_socket.py"
사용할 포트 입력

#client
docker run -it --rm chatting /bin/bash -c "poetry run python client_web_socket.py"
사용할 서버주소의 포트 입력
</pre>
