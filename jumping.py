import socket
import cv2
import numpy as np
import base64
import pyrealsense2 as rs
import json
import os
import time # Import the time module

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


save_commands = {"front": False, "back": False, "side": False, 
                 "rom_ha_left": False, "rom_ha_right": False, 
                 "rom_hf_left": False, "rom_hf_right": False, 
                 "rom_sa_left": False, "rom_sa_right": False, 
                 "rom_sf_left": False, "rom_sf_right": False  }

#body
save_count_front = 0
max_saves_front = 6

save_count_back = 0
max_saves_back = 7

save_count_side = 0
max_saves_side = 6

#foot
save_count_rom_ha_left = 0
max_saves_rom_ha_left = 31

save_count_rom_ha_right = 0
max_saves_rom_ha_right = 50

save_count_rom_hf_left = 0
max_saves_rom_hf_left = 36

save_count_rom_hf_right = 0
max_saves_rom_hf_right = 51

#hand
save_count_rom_sa_left = 0
max_saves_rom_sa_left = 85

save_count_rom_sa_right = 0
max_saves_rom_sa_right = 86

save_count_rom_sf_left = 0
max_saves_rom_sf_left = 81

save_count_rom_sf_right = 0
max_saves_rom_sf_right = 91

save_count = 0
max_saves = 6  # Maximum number of saves
command_received_time = None

# Create a new directory for saved images
save_folder = "temp"
os.makedirs(save_folder, exist_ok=True)


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
                command_received_time = time.time()
        except socket.timeout:
            pass

           # Check if save command is received and save_count is less than max_saves
         # Check if save command is received and if 5 seconds have passed
        current_time = time.time()
        if (save_commands["front"]):
            if current_time - command_received_time >= 5:
                deep_folder = 'temp/front'
                os.makedirs(deep_folder, exist_ok=True)
                while save_count_front<max_saves_front:
                    cv2.imwrite(os.path.join(deep_folder, f'rgb_{save_count_front:06}.png'), color_image)
                    cv2.imwrite(os.path.join(deep_folder, f'depth_{save_count_front:06}.png'), depth_image)
                    save_count_front += 1
                    save_commands["front"] = False
                    command_received_time = None
                    if save_count_front >= max_saves_front:
                        print("Max number of saves reached.")
                    #break # Optional: Break the loop if max saves reached
                        
        #capturing back                
        elif(save_commands["back"]):
            if current_time - command_received_time >= 5:
                deep_folder = 'temp/back'
                os.makedirs(deep_folder, exist_ok=True)
                while save_count_back<max_saves_back:
                    cv2.imwrite(os.path.join(deep_folder, f'rgb_{save_count_back:06}.png'), color_image)
                    cv2.imwrite(os.path.join(deep_folder, f'depth_{save_count_back:06}.png'), depth_image)
                    save_count_back += 1
                    save_commands["back"] = False
                    command_received_time = None
                    if save_count_back >= max_saves_back:
                        print("Max number of saves reached.")
                    #break # Optional: Break the loop if max saves reached

finally:
    pipeline.stop()
    conn.close()
    #server_socket.close()
    print("Server closed")
