#!/usr/bin/env python2
import cv2, sys, socket, signal, numpy, hashlib

def signal_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    cv2.namedWindow("preview")

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("127.0.0.1", 5005))
    while True:
        try:
            data, addr = s.recvfrom(8)
            print "DATA SIZE: " + data
            frame, addr = s.recvfrom(int(data))
            m = hashlib.md5()
            m.update(frame)
            print "FRAME HASH: {}".format(m.hexdigest())
            array = numpy.asarray(bytearray(frame), dtype=numpy.uint8)
            decoded_frame = cv2.imdecode(array, cv2.CV_LOAD_IMAGE_UNCHANGED)
            import ipdb; ipdb.set_trace()
            cv2.imshow("preview", decoded_frame)
            cv2.waitKey(1)
        except ValueError:
            continue


    cv2.destroyWindow("preview")

if __name__ == '__main__':
    main()
