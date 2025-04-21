import requests

with open("shrimp.jpeg", "rb") as f:
    res = requests.post("http://127.0.0.1:5000/analyze", files={"file": f})
    print("Status Code:", res.status_code)
    print("Response Text:", res.text)
