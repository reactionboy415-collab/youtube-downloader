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
def yt_downloader():
    video_url = request.args.get("link")
    if not video_url:
        return jsonify({"status": 0, "error": "No link provided"}), 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
        "Content-Type": "application/json",
        "Origin: https://vidssave.com",
        "Referer: https://vidssave.com/yt"
    }

    try:
        session = requests.Session()
        session.get("https://vidssave.com/yt", headers=headers, timeout=5)
        
        payload = {
            "url": "/media/parse",
            "data": {"origin": "source", "link": video_url},
            "token": ""
        }

        response = session.post("https://vidssave.com/api/proxy", headers=headers, json=payload, timeout=10)
        data = response.json()

        if data.get("status") != 1:
            return jsonify({"status": 0, "error": "Source Error"}), 500

        info = data["data"]
        results = []

        thumbnail = shorten_url(info.get("thumbnail"))

        for item in info.get("resources", []):
            if item.get("download_mode") == "check_download":
                results.append({
                    "quality": item.get("quality"),
                    "format": item.get("format"),
                    "size": item.get("size"),
                    "url": shorten_url(item.get("download_url"))
                })

        return jsonify({
            "status": 1,
            "title": info.get("title"),
            "duration": info.get("duration"),
            "thumbnail": thumbnail,
            "links": results
        })

    except Exception as e:
        return jsonify({"status": 0, "error": "Server Busy"}), 500

# Render ke liye ye zaroori nahi hai par local testing ke liye rehne de sakte ho
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
