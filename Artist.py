import cv2
import os
import numpy as np
import AI
import Slides

debug = False

#Slides.open_presentation()

# Function to crop the given image
def cropImage(image):
    white_pixels = cv2.findNonZero(image)

    # Find the bounding rectangle
    x, y, w, h = cv2.boundingRect(white_pixels)

    # Crop the image to the bounding rectangle
    cropped_image = image[y:y+h, x:x+w]
    return cropped_image

# Path to the folder containing images
folder_path = 'pics/traces'
# Create the folder if it doesn't exist
os.makedirs(folder_path, exist_ok=True)

# Remove existing PNG files from the folder
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path) and filename.lower().endswith(('.png')):
        os.remove(file_path)

# Parameters for blob detection
params = cv2.SimpleBlobDetector_Params()
params.minThreshold = 10
params.maxThreshold = 200
params.filterByArea = True
params.minArea = 20
params.filterByCircularity = True
params.minCircularity = 0.8
params.filterByConvexity = True
params.minConvexity = 0.7
params.filterByInertia = False
#params.minInertiaRatio = 0.01
params.filterByColor = True
params.blobColor = 255

# Create a blob detector with the specified parameters
detector = cv2.SimpleBlobDetector_create(params)

# Initialize background subtractor
bg_subtractor = cv2.createBackgroundSubtractorMOG2()

# Start capturing video from the default camera
cap = cv2.VideoCapture(0)

# Initialize variables
blob_path = []
trace_image = None
imageCount = 0

# Contrast control (1.0-3.0)
alpha = 0.4
# Brightness control (0-100)
beta = -50
threshold = 50

# Threshold for detecting movement
movingThreshold = 1
idleCount = 0
idleCountTolerance = 3
moving = False
movingCount = 0
cycleCount = 0

backgroundRemoved = False
fg_removed = None

ret, init_frame = cap.read()
cv2.imshow("Keypoints", np.zeros((init_frame.shape[0], init_frame.shape[1], 3), dtype=np.uint8))

# Main loop
while True:
    # Increment cycle count
    cycleCount += 1

    # Read a frame from the video capture
    ret, frame = cap.read()
    # Flip the frame horizontally
    frame_flipped = cv2.flip(frame, 1)
    if not ret:
        break

    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2GRAY)
    frame_flipped = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2GRAY)
    # Adjust contrast and brightness
    gray_frame = cv2.convertScaleAbs(gray_frame, alpha=alpha, beta=beta)
    # Apply binary thresholding
    ret, gray_frame = cv2.threshold(gray_frame, threshold, 255, cv2.THRESH_BINARY)

    # Detect blobs in the frame
    keypoints = detector.detect(gray_frame)
    points = cv2.KeyPoint_convert(keypoints)

    # Check if a blob is present
    blobPresent = False
    if len(points) > 0:
        blobPresent = True

    point = [0, 0]
    moving = False
    fg_removed = gray_frame.copy()
    if blobPresent:
        point = points[0]
        blobBorn = False
        if len(blob_path) == 0:
            blobBorn = True
            moving = True

        if len(blob_path) > 0:
            backgroundRemoved = True
            if backgroundRemoved:
                # Create the mask
                mask = np.zeros_like(frame_flipped, dtype=np.uint8)
                if len(blob_path) > 0:
                    for i in range(1, len(blob_path)):
                        cv2.line(mask, tuple(np.intp(blob_path[i - 1])), tuple(np.intp(blob_path[i])), (255, 255, 255),
                                 15)

                # Apply the mask to and remove the background using bitwise and
                im_with_keypoints = cv2.bitwise_and(frame_flipped, frame_flipped, mask=mask)

                cv2.imshow("Keypoints", im_with_keypoints)
            delta = abs(blob_path[-1] - point)
            dx, dy = delta
            if (dx > movingThreshold and dy > movingThreshold) or blobBorn:
                moving = True
            else:
                moving = False
        delta = None
    else:
        pass
        #im_with_keypoints = cv2.drawKeypoints(frame_flipped, keypoints, np.array([]), (0, 0, 255),
           #                                   cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        #cv2.imshow("Keypoints", im_with_keypoints)
        #fg_removed = gray_frame.copy()


    # Update state based on movement detection
    if moving:
        idleCount = 0
        movingCount += 1
    else:
        idleCount += 1

    if moving:
        blob_path.append(point)

    # Draw traced path on the frame
    if len(blob_path) > 0:
        for i in range(1, len(blob_path)):
            cv2.line(frame_flipped, tuple(np.intp(blob_path[i-1])), tuple(np.intp(blob_path[i])), (0, 255, 0), 15)
            cv2.line(gray_frame, tuple(np.intp(blob_path[i-1])), tuple(np.intp(blob_path[i])), (255, 255, 255), 15)

    # Check if the blob has been idle for a certain duration
    if idleCount > idleCountTolerance:
        if len(blob_path) > 20:
            imageCount += 1

            # Create and save traced image
            trace_image = np.zeros_like(frame_flipped)
            prevPoint = [0,0]
            for i in range(1, len(blob_path)):
                cv2.line(trace_image, tuple(np.intp(blob_path[i-1])), tuple(np.intp(blob_path[i])), (0, 255, 0), 15)

            imagePath = f'pics/traces/{imageCount}_trace_image.png'
            croppedImage = cropImage(gray_frame)
            cv2.imwrite(imagePath, croppedImage)

            # AI.feed(imagePath)

            cv2.imwrite(imagePath, gray_frame)
            AI.feed(imagePath)
            trace_image = None
            blob_path = []
            idleCount = 0

    # Draw keypoints on the frame
    im_with_keypoints = cv2.drawKeypoints(frame_flipped, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    gray_frame = cv2.drawKeypoints(gray_frame, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imshow("Processed", gray_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close windows
cap.release()
cv2.destroyAllWindows()

