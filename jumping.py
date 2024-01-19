import socket
import cv2
import numpy as np
import base64
import pyrealsense2 as rs
import threading
import json
import os
import time # Import the time module

# Configure RealSense pipeline


# Set up the socket server
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind(('localhost', 5002))  # Bind to localhost and port 12345
# server_socket.listen(1)  # Listen for connections (1 client)

# print("Waiting for a connection...")
# conn, addr = server_socket.accept()
# print(f"Connected to {addr}")

is_streaming = False
save_commands = {"front": False, "back": False, "side": False, 
                 "rom_ha_left": False, "rom_ha_right": False, 
                 "rom_hf_left": False, "rom_hf_right": False, 
                 "rom_sa_left": False, "rom_sa_right": False, 
                 "rom_sf_left": False, "rom_sf_right": False, 
                 "start-stream": False, "stop-stream": False  }

#body
save_count_front = 0
duration_front = 2
max_saves_front = 6
waiting_front = 5

save_count_back = 0
duration_back = 2
max_saves_back = 7
waiting_back = 5


save_count_side = 0
duration_side = 2
max_saves_side = 6
waiting_side = 5


#foot
#left foot to side start:10s duration: 8s 
save_count_rom_ha_left = 0
max_saves_rom_ha_left = 31
duration_rom_ha_left = 8
waiting_rom_ha_left = 10


#right foot to side start:10s duration: 8s 
save_count_rom_ha_right = 0
max_saves_rom_ha_right = 50
duration_rom_ha_right = 8
waiting_rom_ha_right = 8


#left foot to front start:10s duration: 8s 
save_count_rom_hf_left = 0
max_saves_rom_hf_left = 36
duration_rom_hf_left = 8
waiting_rom_hf_left = 10


#right foot to front start:10s duration: 8s 
save_count_rom_hf_right = 0
max_saves_rom_hf_right = 51
duration_rom_hf_right = 8
waiting_rom_hf_right = 8

#hand
# left hand to side start:10s duration: 10s 
save_count_rom_sa_left = 0
max_saves_rom_sa_left = 85
duration_rom_sa_left = 10
waiting_rom_sa_left = 10


# right hand to side start:10s duration: 10s 
save_count_rom_sa_right = 0
max_saves_rom_sa_right = 86
duration_rom_sa_right = 10
waiting_rom_sa_right = 10

# left hand to front start:10s duration: 10s 
save_count_rom_sf_left = 0 
max_saves_rom_sf_left = 81
duration_rom_sf_left = 10
waiting_rom_sf_left = 10

# right hand to front start:10s duration: 10s
save_count_rom_sf_right = 0
max_saves_rom_sf_right = 91
duration_rom_sf_right = 10
waiting_rom_sf_right = 10

command_received_time = {cmd: None for cmd in save_commands}
capture_counters = {cmd: 0 for cmd in save_commands}

def crop_vertical(img):
    # Original dimensions
    original_height, original_width = img.shape[:2]

    # New width for the crop
    new_width = 405

    # Calculate the starting x coordinate for cropping
    startx = original_width // 2 - new_width // 2 

    # Crop the image to 405 (width) x 720 (height)
    cropped_img = img[0:720, startx:startx + new_width]

    return cropped_img


def saving_image(command, color_image, depth_image, duration, waiting_time):
    global save_commands, command_received_time, capture_counters

    current_time = time.time()
    if save_commands[command] and command_received_time[command] is not None:
        time_since_command_received = current_time - command_received_time[command]

        # Check if waiting time has elapsed
        if time_since_command_received >= waiting_time:
            elapsed_time = time_since_command_received - waiting_time
            if elapsed_time <= duration:
                deep_folder = 'temp/' + command
                os.makedirs(deep_folder, exist_ok=True)
                counter = capture_counters[command]

                # timestamp = int(elapsed_time * 1000)  # Convert to milliseconds
                filename = os.path.join(deep_folder, f'rgb-{counter:06}.png')
                cropped_color_image = crop_vertical(color_image)
                #resized_color_image = cv2.resize(color_image, (720, 1280))
                cv2.imwrite(filename, cropped_color_image)

                filename = os.path.join(deep_folder, f'depth-{counter:06}.png')
                cropped_depth_image = crop_vertical(depth_image)
                #resized_depth_image = cv2.resize(depth_image, (720, 1280))
                cv2.imwrite(filename, cropped_depth_image)

                capture_counters[command] += 1 
            else:
                # End of the duration
                save_commands[command] = False
                command_received_time[command] = None
                capture_counters[command] = 0  # Reset the counter
    return  save_commands[command]




def handle_client_connection(client_socket):
    global is_streaming, save_commands

    

    try:
        while True:
            try:
                client_socket.settimeout(0.1)  # Set timeout for non-blocking recv
                command = client_socket.recv(1024).decode().strip()

                if command == "start-stream":
                    is_streaming = True
                    print("Streaming started.")

                elif command == "stop-stream":
                    is_streaming = False
                    print("Streaming stopped.")

                elif command in save_commands:
                    save_commands[command] = True
                    command_received_time[command] = time.time()

            except socket.timeout:
                # Handle timeout, which means no command was received
                pass

            # Stream and/or save frames if applicable
            if is_streaming or any(save_commands.values()):
                pipeline = rs.pipeline()
                config = rs.config()
                config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
                config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

                # Start streaming
                pipeline.start(config)
                frames = pipeline.wait_for_frames()
                color_frame = frames.get_color_frame()
                depth_frame = frames.get_depth_frame()

                if not color_frame or not depth_frame:
                    continue

                color_image = np.asanyarray(color_frame.get_data())
                depth_image = np.asanyarray(depth_frame.get_data())

                # Saving images based on commands
                for cmd in save_commands:
                    if save_commands[cmd]:
                        duration = globals()[f"duration_{cmd}"]
                        waiting_time = globals()[f"waiting_{cmd}"]
                        save_commands[cmd] = saving_image(cmd, color_image, depth_image, duration, waiting_time)

                # Stream if streaming is active
                if is_streaming:
                    _, color_buffer = cv2.imencode('.jpg', crop_vertical(color_image),  [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                    _, depth_buffer = cv2.imencode('.jpg', crop_vertical(depth_image),  [int(cv2.IMWRITE_JPEG_QUALITY), 70])

                    jpeg_color = base64.b64encode(color_buffer).decode('utf-8')
                    jpeg_depth = base64.b64encode(depth_buffer).decode('utf-8')

                    frame_data = json.dumps({'rgb': jpeg_color, 'depth': jpeg_depth})
                    client_socket.sendall((frame_data + "\n").encode())

    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        client_socket.close()
        client_socket.close()
        pipeline.stop()


def accept_connections():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 5002))
    server_socket.listen(5)
    print("Server is listening on localhost:5002")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connected to {addr}")
        client_thread = threading.Thread(target=handle_client_connection, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    accept_connections()
