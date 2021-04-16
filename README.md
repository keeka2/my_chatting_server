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
docker run -it --rm chatting /bin/bash -c "poetry run python server_web_socket.py"

#client
docker run -it --rm chatting /bin/bash -c "poetry run python client_web_socket.py"
</pre>
