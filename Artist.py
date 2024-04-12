import cv2
import os
import numpy as np
from pylibfreenect2 import Freenect2, SyncMultiFrameListener
from pylibfreenect2 import FrameType, Registration, Frame
from pylibfreenect2 import createConsoleLogger, setGlobalLogger
from pylibfreenect2 import LoggerLevel
from AI import feed as feedAI

debug = True
import sys


try:
    from pylibfreenect2 import OpenGLPacketPipeline
    pipeline = OpenGLPacketPipeline()
except:
    try:
        from pylibfreenect2 import OpenCLPacketPipeline
        pipeline = OpenCLPacketPipeline()
    except:
        from pylibfreenect2 import CpuPacketPipeline
        pipeline = CpuPacketPipeline()
print("Packet pipeline:", type(pipeline).__name__)

# Create and set logger
#logger = createConsoleLogger(LoggerLevel.Debug)
#setGlobalLogger(logger)

fn = Freenect2()
num_devices = fn.enumerateDevices()
if num_devices == 0:
    print("No device connected!")
    sys.exit(1)

serial = fn.getDeviceSerialNumber(0)
device = fn.openDevice(serial, pipeline=pipeline)

listener = SyncMultiFrameListener(
    FrameType.Color | FrameType.Ir | FrameType.Depth)

# Register listeners
device.setColorFrameListener(listener)
device.setIrAndDepthFrameListener(listener)

device.start()

# NOTE: must be called after device.start()
registration = Registration(device.getIrCameraParams(),
                            device.getColorCameraParams())

undistorted = Frame(512, 424, 4)
registered = Frame(512, 424, 4)

# Optinal parameters for registration
# set True if you need
need_bigdepth = False
need_color_depth_map = False

bigdepth = Frame(1920, 1082, 4) if need_bigdepth else None
color_depth_map = np.zeros((424, 512),  np.int32).ravel() \
    if need_color_depth_map else None


# Function to crop the given image
def cropImage(image):
    white_pixels = cv2.findNonZero(image)

    # Find the bounding rectangle
    x, y, w, h = cv2.boundingRect(white_pixels)

    # Crop the image to the bounding rectangle
    cropped_image = image[y:y+h, x:x+w]
    return cropped_image

# Path to the folder containing images
trace_folder_path = 'traces'
# Create the folder if it doesn't exist
os.makedirs(trace_folder_path, exist_ok=True)

# Remove existing PNG files from the folder
for filename in os.listdir(trace_folder_path):
    file_path = os.path.join(trace_folder_path, filename)
    if os.path.isfile(file_path) and filename.lower().endswith(('.png')):
        os.remove(file_path)

# Parameters for blob detection
params = cv2.SimpleBlobDetector_Params()
params.minThreshold = 10
params.maxThreshold = 200
params.filterByArea = True
params.minArea = 20
params.filterByCircularity = True
params.minCircularity = 0.7
params.filterByConvexity = True
params.minConvexity = 0.1
params.filterByInertia = True
params.minInertiaRatio = 0.01
params.filterByColor = True
params.blobColor = 255

# Create a blob detector with the specified parameters
detector = cv2.SimpleBlobDetector_create(params)

cap = cv2.VideoCapture(24)


# Initialize variables
blob_path = []
trace_image = None
imageCount = 0

# Contrast control (1.0-3.0)
alpha = 0.4
# Brightness control (0-100)
beta = -50
threshold = 250

# Threshold for detecting movement
movingThreshold = 10
idleCount = 0
idleCountTolerance = 5
moving = False
movingCount = 0
cycleCount = 0


# Main loop
while True:
    # Increment cycle count
    cycleCount += 1
    if debug:
        print(f"===Cycle {cycleCount}")
    cycleCount += 1
    """
    # Read a frame from the video capture
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally
    frame_flipped = cv2.flip(frame, 1)
    """
    frames = listener.waitForNewFrame()

    ir_frame = frames["ir"]
    print(type(ir_frame))
    #gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    sixteenbit_gray_frame = ir_frame.asarray() * (255.0 / 65535.0)
    eightbit_gray_frame = cv2.convertScaleAbs(sixteenbit_gray_frame)
    gray_frame =eightbit_gray_frame
    print(gray_frame)
    print(type(gray_frame))
    print(gray_frame.shape)
    print(np.max(gray_frame))
    max_in_columns = np.max(gray_frame, axis=0)
    print("Maximum in each column:", max_in_columns)
    # Convert the frame to grayscale
    #gray_frame = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2GRAY)
    # Adjust contrast and brightness
    #gray_frame = cv2.convertScaleAbs(gray_frame, alpha=alpha, beta=beta)
    # Apply binary thresholding
    ret, gray_frame = cv2.threshold(gray_frame, threshold, 255, cv2.THRESH_BINARY)
    #gray_frame = cv2.flip(gray_frame, 1)
    # Detect blobs in the frame
    keypoints = detector.detect(gray_frame)
    points = cv2.KeyPoint_convert(keypoints)

    # Check if a blob is present
    blobPresent = False
    if len(points) > 0:
        blobPresent = True

    point = [0, 0]
    fg_removed = gray_frame.copy()
    if blobPresent:
        point = points[0]
        blobBorn = False
        if len(blob_path) == 0:
            blobBorn = True
            moving = True

        if len(blob_path) > 0:
            delta = abs(blob_path[-1] - point)
            dx, dy = delta
            if (dx > movingThreshold and dy > movingThreshold) or blobBorn:
                moving = True
            else:
                moving = False
        delta = None
    else:
        if debug:
            print("empty")


    # Update state based on movement detection
    if moving:
        idleCount = 0
        movingCount += 1
    else:
        idleCount += 1

    if moving:
        if debug:
            print('Tracing []')
        blob_path.append(point)

    # Draw traced path on the frame
    if len(blob_path) > 0:
        for i in range(1, len(blob_path)):
            #cv2.line(frame, tuple(np.intp(blob_path[i-1])), tuple(np.intp(blob_path[i])), (0, 255, 0), 15)
            cv2.line(gray_frame, tuple(np.intp(blob_path[i-1])), tuple(np.intp(blob_path[i])), 255, 15)

    # Check if the blob has been idle for a certain duration
    if idleCount > idleCountTolerance:
        #make min_trace_points variable
        if len(blob_path) > 1:
            if debug:
                print('TRACED')
            imageCount += 1
            
            black_image = np.zeros_like(gray_frame)
            trace_image = black_image
            prevPoint = [0,0]
            for i in range(1, len(blob_path)):
                cv2.line(trace_image, tuple(np.intp(blob_path[i-1])), tuple(np.intp(blob_path[i])), 255, 15)
                #print(f"{blob_path[i]} delta: {abs(blob_path[i]-prevPoint)}")
                prevPoint = blob_path[i]

            imagePath = f'{trace_folder_path}/{imageCount}_trace_image.png'
            croppedImage = cropImage(trace_image)
            cv2.imwrite(imagePath, croppedImage)

            feedAI(imagePath)

            trace_image = None
            blob_path = []
            idleCount = 0
    gray_frame = cv2.drawKeypoints(gray_frame, keypoints, np.array([]), 255, cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imshow("Processed", gray_frame)
    listener.release(frames)
    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close windows
#cap.release()
device.stop()
device.close()

sys.exit(0)
cv2.destroyAllWindows()