import socket
import cv2
import numpy as np
import base64
import pyrealsense2 as rs
import json
import os

# Configure RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

# Start streaming
pipeline.start(config)

# Set up the socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 5002))  # Bind to localhost and port 12345
server_socket.listen(1)  # Listen for connections (1 client)

print("Waiting for a connection...")
conn, addr = server_socket.accept()
print(f"Connected to {addr}")


save_commands = {"save_rgb": False, "save_depth": False}


try:
    while True:
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if not depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Example: Convert an image to JPEG format and base64 encode
        _, buffer = cv2.imencode('.jpg', color_image)  # Assuming color_image is a numpy array
        jpeg_encoded = base64.b64encode(buffer).decode('utf-8')
        
        
        _, buffer2 = cv2.imencode('.jpg', depth_image)  # Assuming color_image is a numpy array
        jpeg_encoded2 = base64.b64encode(buffer2).decode('utf-8')

        # Check if save command is received
        if save_commands["save_rgb"]:
            cv2.imwrite('rgb-image.png', color_image)
            save_commands["save_rgb"] = False

        if save_commands["save_depth"]:
            cv2.imwrite('depth-image.png', depth_image)
            save_commands["save_depth"] = False

   

        # Serialize and send the frame data
        try:
            frame_data = json.dumps({'rgb': jpeg_encoded, 'depth': jpeg_encoded2})
            message = frame_data + "\n"  # Add the delimiter
            # frame_data = {'rgb': color_image.tolist(), 'depth': depth_image.tolist()}
            # message = json.dumps(frame_data).encode()
            conn.sendall(message.encode())
        except Exception as e:
            print(f"Error sending data: {e}")
            break
        
        # Listen for commands from Electron app
        try:
            conn.settimeout(0.1)  # Non-blocking
            command = conn.recv(1024).decode().strip()
            if command:
                save_commands[command] = True
        except socket.timeout:
            pass
finally:
    pipeline.stop()
    conn.close()
    #server_socket.close()
    print("Server closed")
