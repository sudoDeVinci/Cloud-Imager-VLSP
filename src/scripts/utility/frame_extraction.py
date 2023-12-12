"""
This script takes in a video stream (via a passed in path), then saves every Nth frame as a png.
"""

from multiprocessing import Queue, Process
from time import perf_counter
from os import get_terminal_size, system
from platform import platform
from time import sleep
from cv2 import COLOR_BGR2GRAY, VideoCapture, cvtColor, resize, CAP_PROP_FPS, CAP_PROP_FRAME_COUNT


def queue_frames(video_path: str, dsize: tuple[int, int], queue: Queue, N:int) -> None:
    try:
        stream = VideoCapture(video_path)
        grabbed, frame = stream.read()
    except Exception:
        print("Exception reading video stream")
        queue.put(None)
        return None
    
    # If the first frame isn't grabbed but the video exists
    if not grabbed:
        queue.put(None)
        return None

    # Firstly, get the length of the video.
    frame_count = stream.get(CAP_PROP_FRAME_COUNT)
    print(f"Video length: {frame_count} frames")

    # Read the frame, resize it to standard size, then add it to the queue.
    grabbed, frame = stream.read()
    while grabbed:
        frame = resize(frame, dsize)
        queue.put(frame)
        for _ in range(N):
           grabbed, frame = stream.read() 
    
    stream.release()
    
    queue.put(None)
    return None

# Read frames from queue.
# Read every other frame from the queue
def save_frames(queue: Queue, folder: str):
    while True:
        frame = queue.get()
        if frame is None:
            pass