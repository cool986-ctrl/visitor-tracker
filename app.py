from flask import Flask, request, jsonify, render_template_string
import requests, os
from datetime import datetime

app = Flask(__name__, static_folder="static", template_folder="static")

# Use IP lookup service (ipapi.co). Optionally set IPAPI_TOKEN as an env var for higher quota.
IPAPI_TOKEN = os.environ.get("IPAPI_TOKEN")

def get_client_ip(req):
    # prefer headers that proxies/CDN set
    for h in ("CF-Connecting-IP", "X-Real-IP", "X-Forwarded-For"):
        v = req.headers.get(h)
        if v:
            return v.split(",")[0].strip()
    return req.remote_addr

def lookup_ip_info(ip):
    try:
        token_suffix = f"?token={IPAPI_TOKEN}" if IPAPI_TOKEN else ""
        r = requests.get(f"https://ipapi.co/{ip}/json/{token_suffix}", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}

@app.route("/", methods=["GET"])
def homepage():
    # Serve the tracker page (index.html in static folder)
    return app.send_static_file("index.html")

@app.route("/report", methods=["POST"])
def report():
    payload = request.get_json(force=True, silent=True) or {}
    # GPS from client (may be None if denied)
    gps = payload.get("gps")  # should be dict with lat, lon, accuracy
    extra = payload.get("extra", {})

    ip = get_client_ip(request)
    ip_info = lookup_ip_info(ip)

    ua = request.headers.get("User-Agent", "")
    # browser/platform from Flask user_agent (may be limited)
    browser = request.user_agent.browser
    platform = request.user_agent.platform

    record = {
        "ip": ip,
        "ip_org": ip_info.get("org"),
        "ip_city": ip_info.get("city"),
        "ip_region": ip_info.get("region"),
        "ip_country": ip_info.get("country_name"),
        "gps_lat": gps.get("lat") if isinstance(gps, dict) else None,
        "gps_lon": gps.get("lon") if isinstance(gps, dict) else None,
        "gps_accuracy_m": gps.get("accuracy") if isinstance(gps, dict) else None,
        "browser": browser,
        "platform": platform,
        "user_agent": ua,
        "extra": extra,
        "access_time": str(datetime.utcnow())
    }

    # Print to Render logs (visible in Render Dashboard → Logs)
    print(record, flush=True)

    # Optionally persist to a file (safe for small tests)
    try:
        with open("visitors.log", "a") as f:
            f.write(str(record) + "\n")
    except Exception:
        pass

    return jsonify({"status": "ok", "received": record}), 200
