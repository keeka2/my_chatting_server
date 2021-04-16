### Installation
<pre>
git clone 
cd my_chatting_server
</pre>
### Run
<pre>
# build docker
docker build -t chatting .

# server
docker run --rm -p 8081:8081 --name chatting_server chatting poetry run python -m server_web_socket

#client
docker run --rm -p 8081:8081 --name chatting_server chatting poetry run python -m client_web_socket
</pre>
