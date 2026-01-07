import os
from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

def shorten_url(url):
    if not url: return url
    try:
        res = requests.post(
            "https://freelyshrink.com/shorten.php",
            headers={"User-Agent": "Mozilla/5.0"},
            data={"long_url": url},
            timeout=5
        )
        match = re.search(r'code=([a-zA-Z0-9]+)', res.url) or re.search(r'code=([a-zA-Z0-9]+)', res.text)
        if match:
            return f"https://hosturl.link/{match.group(1)}"
    except:
        pass
    return url

@app.route("/api/yt", methods=["GET"])
def yt_api():
    video_link = request.args.get("link")
    if not video_link:
        return jsonify({"status": 0, "error": "No link provided"}), 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
        "Content-Type": "application/json",
        "Origin": "https://vidssave.com",
        "Referer": "https://vidssave.com/yt"
    }

    try:
        session = requests.Session()
        session.get("https://vidssave.com/yt", headers=headers, timeout=5)
        
        payload = {
            "url": "/media/parse",
            "data": {"origin": "source", "link": video_link},
            "token": ""
        }
        
        response = session.post("https://vidssave.com/api/proxy", headers=headers, json=payload, timeout=10)
        data = response.json()

        if data.get("status") != 1:
            return jsonify({"status": 0, "error": "Invalid response"}), 500

        source = data["data"]
        results = []

        for item in source.get("resources", []):
            if item.get("download_mode") == "check_download":
                results.append({
                    "quality": item.get("quality"),
                    "format": item.get("format"),
                    "size": item.get("size"),
                    "download": shorten_url(item.get("download_url"))
                })

        return jsonify({
            "status": 1,
            "title": source.get("title"),
            "duration": source.get("duration"),
            "thumbnail": shorten_url(source.get("thumbnail")),
            "data": results
        })

    except Exception as e:
        return jsonify({"status": 0, "error": "System Busy"}), 500

if __name__ == "__main__":
    # Render hamesha PORT environment variable bhejta hai
    port = int(os.environ.get("PORT", 10000)) 
    app.run(host="0.0.0.0", port=port)
