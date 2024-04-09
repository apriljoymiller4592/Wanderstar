import cv2
import os
import numpy as np
import AI
import Slides
debug = False


Slides.open_presentation()

def cropImage(image):
    white_pixels = cv2.findNonZero(image)

    # Find the bounding rectangle
    x, y, w, h = cv2.boundingRect(white_pixels)

    # Crop the image to the bounding rectangle
    cropped_image = image[y:y+h, x:x+w]
    return cropped_image

folder_path = 'pics/traces'
os.makedirs(folder_path, exist_ok=True)
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)

    if os.path.isfile(file_path) and filename.lower().endswith(('.png')):
        os.remove(file_path)

params = cv2.SimpleBlobDetector_Params()
params.minThreshold = 10
params.maxThreshold = 200
params.filterByArea = True
params.minArea = 500
params.filterByCircularity = True
params.minCircularity = 0.001
params.filterByConvexity = True
params.minConvexity = 0.1
params.filterByInertia = True
params.minInertiaRatio = 0.01
params.filterByColor = True
params.blobColor = 255

detector = cv2.SimpleBlobDetector_create(params)
cap = cv2.VideoCapture(0)

blob_path = []
trace_image = None
imageCount = 0

alpha = 0.4  # Contrast control (1.0-3.0)
beta = -50 # Brightness control (0-100)
threshold = 50

delta = None
movingThreshold = 1
idleCount = 0
idleCountTolerance = 5
moving = False
movingCount = 0
cycleCount = 0

while True:
    if debug:
        print(f"===Cycle {cycleCount}")
    cycleCount += 1
    ret, frame = cap.read()
    frame_flipped = cv2.flip(frame, 1)
    if not ret:
        break

    gray_frame = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.convertScaleAbs(gray_frame, alpha=alpha, beta=beta)
    gray_frame = cv2.flip(gray_frame, 1)#flipp frame
    ret, gray_frame = cv2.threshold(gray_frame, threshold, 255, cv2.THRESH_BINARY)#127 is highest threshhold

    keypoints = detector.detect(gray_frame)
    points = cv2.KeyPoint_convert(keypoints)

    blobPresent = False
    if len(points) > 0:
        blobPresent = True

    point = [0,0]
    moving = False
    if blobPresent:
        if debug:
            print("blob present")
        point = points[0]
        blobBorn = False
        if len(blob_path) == 0:
            blobBorn = True
            if debug:
                print("blob born")
            moving = True

        if len(blob_path) > 0:
            delta = abs(blob_path[-1] - point)
            dx,dy = delta
            if debug:
                print (delta)
            if (dx > movingThreshold and dy > movingThreshold) or blobBorn:
                moving = True
            else:
                moving = False
        delta = None
    else:
        if debug:
            print("empty")

    if moving:
        idleCount = 0
        movingCount += 1
        if debug:
            print("moving->" + f" {movingCount}")
    else:
        idleCount += 1
        if blobPresent:
            if debug:
                print("idleing...")
                print(f"idleCount: {idleCount}")

    if moving:
        if debug:
            print('Tracing []')
        blob_path.append(point)

    if len(blob_path) > 0:
        for i in range(1, len(blob_path)):
            cv2.line(frame_flipped, tuple(np.intp(blob_path[i-1])), tuple(np.intp(blob_path[i])), (0, 255, 0), 15)
            cv2.line(gray_frame, tuple(np.intp(blob_path[i-1])), tuple(np.intp(blob_path[i])), (255, 255, 255), 15)

    if idleCount > idleCountTolerance :

        if len (blob_path) > 20:
            if debug:
                print('TRACED')
            imageCount += 1

            trace_image = np.zeros_like(frame_flipped)
            prevPoint = [0,0]
            for i in range(1, len(blob_path)):
                cv2.line(trace_image, tuple(np.intp(blob_path[i-1])), tuple(np.intp(blob_path[i])), (0, 255, 0), 15)
                #print(f"{blob_path[i]} delta: {abs(blob_path[i]-prevPoint)}")
                prevPoint = blob_path[i]

            imagePath = f'pics/traces/{imageCount}_trace_image.png'
            croppedImage = cropImage(gray_frame)
            cv2.imwrite(imagePath, croppedImage)
            AI.feed(imagePath)

            cv2.imwrite(imagePath, gray_frame)
            AI.feed(imagePath)
            trace_image = None
            blob_path = []
            idleCount = 0

    im_with_keypoints = cv2.drawKeypoints(frame_flipped, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    gray_frame = cv2.drawKeypoints(gray_frame, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imshow("Keypoints", im_with_keypoints)
    cv2.imshow("Proccesed", gray_frame)

    if cv2.waitKey(1) &  0xFF == ord('q'):
        for point in points:
            print(point)
        break
    

cap.release()
cv2.destroyAllWindows()
