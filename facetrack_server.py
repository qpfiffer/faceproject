#!/usr/bin/env python2
from threading import Thread
import cv2
import signal, sys, socket, hashlib, array
m = hashlib.md5()

def face_detect(frame, face_cascade):
    # Read the image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags = cv2.cv.CV_HAAR_SCALE_IMAGE
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    return frame

class CameraFrenk(object):
    def __init__(self, index):
        self.cap = cv2.VideoCapture(index)
        if self.cap.isOpened() is False:
            raise Exception("Camera does not exist.")

        self.cap.set(cv2.cv.CV_CAP_PROP_FPS, 120)
        self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
        self.rval, self.frame = self.cap.read()

        # Create the haar cascade
        # Get user supplied values
        casc_path = "./haarcascade_frontalface_alt.xml"
        self.face_cascade = cv2.CascadeClassifier(casc_path)


    def start(self):
        self.thread = Thread(target=self.update, args=())
        self._stop = False
        self.thread.start()

    def stop(self):
        self._stop = True

    def read(self):
        return (self.rval, self.frame)

    def update(self):
        while True:
            if self._stop:
                break
            rval, frame = self.cap.read()
            frame = face_detect(frame, self.face_cascade)
            self.rval, self.frame = cv2.imencode(".jpg", frame)

def main():

    capture_threads = []
    for x in range(4):
        try:
            x0 = CameraFrenk(x)
            x0.start()
            capture_threads.append(x0)
        except Exception:
            pass

    def signal_handler(signal, frame):
        for x in capture_threads:
            x.stop()
            sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rval, frame = capture_threads[0].read()
    frame = frame.tostring()
    frame_bytes = array.array("B", frame)
    m.update(frame)
    print "FRAME HASH: {}".format(m.hexdigest())
    frame_size = len(frame)
    data_size = str(frame_size).zfill(8)
    print "DATA SIZE:" + data_size

    while True:
        for capture_thread in capture_threads:
            #rval, frame = capture_thread.read()
            #frame = frame.tostring()

            destination = ('127.0.0.1', 5005)
            packet_size = 4096
            frame_size = len(frame_bytes)
            chunks = range(int(1 + (frame_size - 1) / packet_size))
            data_size = str(frame_size).zfill(8)
            s.sendto(data_size, destination)

            bytes_sent = 0
            for i in chunks:
                minimum = i * packet_size
                maximum = i * packet_size + 4096
                frame_bytes_specific = frame_bytes[minimum:maximum]
                s.sendto(frame_bytes_specific, destination)
                bytes_sent = bytes_sent + 4096
            minimum = bytes_sent
            maximum = frame_size
            frame_bytes_specific = frame_bytes[minimum:maximum]
            s.sendto(frame_bytes_specific, destination)
            bytes_sent = bytes_sent + (maximum - minimum)

if __name__ == '__main__':
    main()
