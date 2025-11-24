from flask import Flask, request, jsonify
import requests
import datetime

app = Flask(__name__)

@app.route("/")
def track():
    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    # Lookup IP info from ipapi.co
    ip_info = requests.get(f"https://ipapi.co/{visitor_ip}/json/").json()

    data = {
        "ip": visitor_ip,
        "city": ip_info.get("city"),
        "region": ip_info.get("region"),
        "country": ip_info.get("country_name"),
        "isp": ip_info.get("org"),
        "browser": request.user_agent.browser,
        "platform": request.user_agent.platform,
        "device": request.user_agent.string,
        "access_time": str(datetime.datetime.now())
    }

    print(data)  # prints to Render logs
    return "Visitor tracked successfully!"
