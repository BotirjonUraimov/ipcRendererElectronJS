import cv2
import numpy as np
import pyrealsense2 as rs
import json
import sys
import time
import base64

# Configure RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 720, 1280, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 720, 1280, rs.format.z16, 30)

# Start streaming
pipeline.start(config)
frame_id = 0  # Initialize frame ID

try:


    # Wait for a coherent pair of frames: depth and color
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()

    if depth_frame and color_frame:
        # Convert frames to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        rgb_base64 = base64.b64encode(color_image.tobytes()).decode('utf-8')
        depth_base64 = base64.b64encode(depth_image.tobytes()).decode('utf-8')

        # Send frames to Electron.js
        frames_data = {
            'rgb': rgb_base64,
            'depth': depth_base64
        }
        # frames_data = {
        #     'rgb': color_image.tolist(),
        #     'depth': depth_image.tolist()
        # }
        print(json.dumps(frames_data))
        sys.stdout.flush()

         # Add a delay (in seconds) to allow Electron to receive the data
        time.sleep(0.5)  # Adjust the delay as needed




    # while True:
    #     # Wait for a coherent pair of frames: depth and color
    #     frames = pipeline.wait_for_frames()
    #     depth_frame = frames.get_depth_frame()
    #     color_frame = frames.get_color_frame()

    #     if not depth_frame or not color_frame:
    #         continue

    #     # Convert frames to numpy arrays
    #     depth_image = np.asanyarray(depth_frame.get_data())
    #     color_image = np.asanyarray(color_frame.get_data())

    #     frame_id += 1

    #      # Send frames to Electron.js
    #     frames_data = {
    #         'id': frame_id,
    #         'rgb': color_image.tolist(),
    #         'depth': depth_image.tolist()
    #     }
    #     print(json.dumps(frames_data))
    #     sys.stdout.flush()

        # Display RGB image
        #cv2.imshow("RGB Image", color_image)

        # Display Depth image
        #depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        #cv2.imshow("Depth Image", depth_colormap)

        # Save RGB and Depth images
        #cv2.imwrite("rgb_image.jpg", color_image)
        #cv2.imwrite("depth_image.jpg", depth_colormap)

        # Break the loop by pressing 'q'
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break

finally:
    # Stop streaming
    pipeline.stop()
    cv2.destroyAllWindows()