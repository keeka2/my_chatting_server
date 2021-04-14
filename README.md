# Docker 예제
### Installation
<pre>
cd /home
git clone https://github.com/keeka2/Docker-Practice.git
cd Docker-Practice
</pre>
### Run
<pre>
# Login For Private Docker Repository
docker build -t chatting .
# server
docker run --rm -p 8081:8081 --name chatting_server chatting poetry run python -m server

#client
docker run --rm -p 8081:8081 --name chatting_server chatting poetry run python -m server
</pre>
