import cv2 as cv
import time

CAMERA_INDEX = "1900-151662242_tiny.mp4"  # 0--> webcam and 1--> external camera

cap = cv.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    print("[ERROR] Cannot open camera")
    exit()

tracker = cv.TrackerCSRT_create()
BB = None

total_time = 0
frame_count = 0
tracking_active = False
start_time = 0

def track(frame):
    global total_time, frame_count
    start = time.time()
    success, box = tracker.update(frame)
    end = time.time()
    
    elapsed = end - start
    total_time += elapsed
    frame_count += 1
    print(f"[INFO] Frame {frame_count}, Time: {elapsed:.6f}s") #each frame time count

    if success:
        (x, y, w, h) = [int(v) for v in box]
        cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    return success, frame

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Frame capture failed.")
        break

    if BB is not None:
        if not tracking_active:
            start_time = time.time()
            tracking_active = True
        success, frame = track(frame)

    cv.imshow("Frame", frame)
    key = cv.waitKey(1) & 0xFF

    if key == ord("s"):
        BB = cv.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
        tracker.init(frame, BB)

    elif key == ord("q"):
        break

cap.release()
cv.destroyAllWindows()

# Print summary stats
if tracking_active:
    total_tracking_time = time.time() - start_time
    print(f"\n[SUMMARY]")
    print(f"Total frames tracked: {frame_count}")
    print(f"Total tracking execution time: {total_time:.4f} seconds")
    print(f"Average tracker.update() time: {total_time / frame_count:.6f} seconds")
    print(f"Total real time spent (including display, etc.): {total_tracking_time:.4f} seconds")
