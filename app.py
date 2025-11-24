from flask import Flask, request
import requests
from datetime import datetime

app = Flask(__name__)

def get_client_ip(request):
    if request.headers.get("CF-Connecting-IP"):
        return request.headers.get("CF-Connecting-IP")

    if request.headers.get("X-Real-IP"):
        return request.headers.get("X-Real-IP")

    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()

    return request.remote_addr


def get_geo(ip):
    try:
        r = requests.get(f"https://ipapi.co/{ip}/json/")
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {}
    

@app.route("/")
def home():
    ip = get_client_ip(request)
    ua = request.headers.get("User-Agent")

    geo = get_geo(ip)

    data = {
        "ip": ip,
        "city": geo.get("city"),
        "region": geo.get("region"),
        "country": geo.get("country_name"),
        "isp": geo.get("org"),
        "browser": request.user_agent.browser,
        "platform": request.user_agent.platform,
        "device": ua,
        "access_time": str(datetime.now())
    }

    print(data)
    return data
