import requests
import json

response = requests.get(f"http://localhost:5001/v2/helloworldpython/manifests/latest")
manifest = json.loads(response.content)
# print(json.dumps(manifest))

for layer in manifest["fsLayers"]:
    headers = requests.head(f"http://localhost:5001/v2/helloworldpython/blobs/sha256:a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4").headers
    print(f'{headers["Location"]}')