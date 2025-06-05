from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str, help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="kcf", help="OpenCV object tracker type")
args = vars(ap.parse_args())

OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "mil": cv2.TrackerMIL_create,
}

tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()

initBB = None
start_time = None
total_update_time = 0.0
frame_count = 0

if not args.get("video", False):
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(1.0)
else:
    vs = cv2.VideoCapture(args["video"])

fps = None

while True:
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame
    if frame is None:
        break
    frame = imutils.resize(frame, width=500)
    (H, W) = frame.shape[:2]

    if initBB is not None:
        # Measure time taken by tracker.update()
        update_start = time.time()
        (success, box) = tracker.update(frame)
        update_end = time.time()
        
        update_duration = update_end - update_start
        total_update_time += update_duration
        frame_count += 1
        
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        fps.update()
        fps.stop()

        info = [
            ("Tracker", args["tracker"]),
            ("Success", "Yes" if success else "No"),
            ("FPS", "{:.2f}".format(fps.fps())),
        ]

        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        initBB = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
        tracker.init(frame, initBB)
        fps = FPS().start()
        start_time = time.time()
        total_update_time = 0.0
        frame_count = 0

    elif key == ord("q"):
        break

if not args.get("video", False):
    vs.stop()
else:
    vs.release()
cv2.destroyAllWindows()

if start_time is not None and frame_count > 0:
    total_tracking_time = time.time() - start_time
    avg_update_time = total_update_time / frame_count
    print("\n[SUMMARY]")
    print(tracker)
    print(f"Total frames tracked: {frame_count}")
    print(f"Total tracker.update() execution time: {total_update_time:.4f} seconds")
    print(f"Average tracker.update() time per frame: {avg_update_time:.6f} seconds")
    print(f"Total real time spent (including display, etc.): {total_tracking_time:.4f} seconds")
else:
    print("\n[INFO] Tracking was not started.")
