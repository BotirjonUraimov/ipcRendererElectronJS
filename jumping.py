import cv2
import numpy as np
import pyrealsense2 as rs
import json
import sys
import os

# Configure RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

# Start streaming
pipeline.start(config)

# Create a directory to save images
output_dir = 'output_images'
os.makedirs(output_dir, exist_ok=True)

# Set the frame rate for saving images (frames per second)
save_frame_rate = 20
frame_interval = int(30 / save_frame_rate)
frame_count = 0

try:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if depth_frame and color_frame:
            # Convert frames to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Save color image every frame_interval frames
            if frame_count % frame_interval == 0:
                image_filename = os.path.join(output_dir, f'frame_{frame_count // frame_interval}.png')
                cv2.imwrite(image_filename, color_image)
                #print(f"Saved {image_filename}")

                # Send the image path to Electron.js
                sys.stdout.flush()

            frame_count += 1

            # Send the JSON-formatted frames data to Electron.js
            frames_data = {
                'id': 1,
                'frame_path': image_filename.replace(os.path.sep, '/'),
            }
            print(json.dumps(frames_data))
            sys.stdout.flush()

finally:
    # Stop streaming
    pipeline.stop()
    cv2.destroyAllWindows()
