#!/usr/bin/env python2
import cv2, sys, socket, signal, numpy, hashlib

def signal_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    cv2.namedWindow("preview")

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("127.0.0.1", 5005))
    old_frame = None
    while True:
        try:
            data, addr = s.recvfrom(8)
            frame_size = int(data)
            bytes_recieved = 0
            full_frame = ""
            while bytes_recieved < frame_size:
                if frame_size - bytes_recieved > 4096:
                    frame, _ = s.recvfrom(4096)
                else:
                    bytes_left = frame_size - bytes_recieved
                    frame, _ = s.recvfrom(bytes_left)
                full_frame = full_frame + frame
                bytes_recieved = bytes_recieved + len(frame)
        except ValueError:
            continue

        array = numpy.asarray(bytearray(full_frame), dtype=numpy.uint8)
        decoded_frame = cv2.imdecode(array, cv2.CV_LOAD_IMAGE_UNCHANGED)
        if decoded_frame is None:
            continue
        old_frame = decoded_frame
        cv2.imshow("preview", old_frame)
        cv2.waitKey(1)


    cv2.destroyWindow("preview")

if __name__ == '__main__':
    main()
