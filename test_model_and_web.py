"""
Test script to generate sample test images and perform full model inference testing.
"""
import io
import os
import numpy as np
from PIL import Image

os.makedirs("tests", exist_ok=True)

# 1. Create a synthetic test image (colorful gradient)
img_ai = Image.new("RGB", (300, 300), color=(120, 200, 240))
# add some pattern
pixels = img_ai.load()
for i in range(300):
    for j in range(300):
        pixels[i, j] = (int((i/300)*255), int((j/300)*200), 220)
img_ai.save("tests/sample_ai.jpg")
print("Saved tests/sample_ai.jpg")

# 2. Create a realistic photo-like test image
img_real = Image.new("RGB", (400, 300), color=(80, 120, 70))
np.random.seed(42)
arr = np.random.randint(50, 150, (300, 400, 3), dtype=np.uint8)
img_real = Image.fromarray(arr)
img_real.save("tests/sample_real.jpg")
print("Saved tests/sample_real.jpg")

# 3. Test standalone inference module
print("\n--- Testing app.inference.predict directly ---")
from app.inference import predict

with open("tests/sample_ai.jpg", "rb") as f:
    ai_bytes = f.read()
res_ai = predict(ai_bytes)
print("sample_ai.jpg result:", res_ai)

with open("tests/sample_real.jpg", "rb") as f:
    real_bytes = f.read()
res_real = predict(real_bytes)
print("sample_real.jpg result:", res_real)

# 4. Test Flask test client routes (upload, predict, history, health)
print("\n--- Testing Flask App Routes ---")
from app.app import app

client = app.test_client()

# GET /health
resp_health = client.get("/health")
print("GET /health ->", resp_health.status_code, resp_health.get_json())

# POST /predict with sample_ai.jpg
data = {
    "file": (io.BytesIO(ai_bytes), "sample_ai.jpg")
}
resp_pred = client.post("/predict", data=data, content_type="multipart/form-data")
print("POST /predict (sample_ai.jpg) ->", resp_pred.status_code)
assert resp_pred.status_code == 200

# POST /predict with sample_real.jpg
data2 = {
    "file": (io.BytesIO(real_bytes), "sample_real.jpg")
}
resp_pred2 = client.post("/predict", data=data2, content_type="multipart/form-data")
print("POST /predict (sample_real.jpg) ->", resp_pred2.status_code)
assert resp_pred2.status_code == 200

# POST /api/predict (JSON endpoint)
data3 = {
    "file": (io.BytesIO(ai_bytes), "api_test.jpg")
}
resp_api = client.post("/api/predict", data=data3, content_type="multipart/form-data")
print("POST /api/predict (JSON) ->", resp_api.status_code, resp_api.get_json())
assert resp_api.status_code == 200

# GET /history
resp_hist = client.get("/history")
print("GET /history ->", resp_hist.status_code)
assert resp_hist.status_code == 200

print("\n>>> ALL MODEL AND WEBSITE TESTS PASSED SUCCESSFULLY! <<<")
