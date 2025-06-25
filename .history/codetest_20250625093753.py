import requests

code = {"code": "print('Local test successful')"}
res = requests.post("http://127.0.0.1:5000/run", json=code)
print(res.json())