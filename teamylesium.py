## 3차원 자세 추정 API

import requests
import cv2
import json
import io
import struct
##import matplotlib.pyplot as plt
import numpy as np
import time

base_url = "http://127.0.0.1:5000"

## 3차원 자세 분석 API / 정면
url = f"{base_url}/pose_analysis/front"

data = {'info': json.dumps({
                    'colorImageInfo': {
                        'height':1280 ,
                        'width':720
                    },
                    'depthImageInfo': {
                        'height': 1280,
                        'width': 720
                    },
                 
                })}

##print("Python script started")
def get_color_fp(rgb_sample_filename):
    rgb_fp = io.BytesIO()
    rgb = cv2. imread(rgb_sample_filename)[:, :, [2, 1, 0]]
#     rgb = cv2.flip(cv2. imread(rgb_sample_filename), 1)[:, :, [2, 1, 0]]
    rgb_fp.write(rgb.tobytes())
    rgb_fp.seek(0)
    
    return rgb_fp

def get_depth_fp(depth_sample_filename):

    depth_fp = io.BytesIO()
    depth = cv2. imread(depth_sample_filename, -1).astype(np.uint16)
#     depth = cv2.flip(cv2. imread(depth_sample_filename, -1), 1).astype(np.uint16)
    depth_fp.write(depth.tobytes())
    depth_fp.seek(0)
    return depth_fp

files = []
for imgi in range(38, 44):
    
    rgb_sample_filename = f'front/rgb_{imgi:06}.png'
    depth_sample_filename = f'front/depth_{imgi:06}.png'
    rgb_fp = get_color_fp(rgb_sample_filename)
    depth_fp = get_depth_fp(depth_sample_filename)
    files += [('colorBuffer[]', rgb_fp),('depthBuffer[]', depth_fp)]

## API 호출    
start_time = time.time()
response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    try:
        # Try to parse the JSON response
        data = json.loads(response.text)
        print(json.dumps(data))  # Convert to JSON string with double quotes
    except json.JSONDecodeError:
        print("Error: Invalid JSON in the response")
else:
    print(f"Error: Server returned status code {response.status_code}")


##print(json.dumps(json.loads(response.text)))  # Convert to JSON string with double quotes
##print(json.loads(response.text))

##json.loads(response.text)


# 각도는 오른쪽 관절 기준
# +일 경우 위로/앞으로 기울어짐.
# -일 경우 아래로/뒤로 기울어짐.