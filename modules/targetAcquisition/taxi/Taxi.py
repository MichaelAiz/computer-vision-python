import cv2
import numpy as np
from boxDetection.detect import detect as detect_boxes
from qrScan.scan import scan as scan_qr

class Taxi:
    """
    Performs cardboard box detection on a given video frame

    Attributes
    ----------
    state : string
        state of object recognition ("BOX", "QR", ...)

    Methods
    -------
    __init__()
        Initialize class variables
    set_state(state: string)
        Prepare variables for box detection, qr decoding, etc.
    main()
        Main operations: getting camera input and passing the image to appropriate methods
    """
    
    def __init__(self):
        """
        Initializes variables
        """
        self.state = None

    def set_state(self, state):
        """
        Prepare variables for box detection, qr decoding, etc.

        Parameters
        ----------
        state: string
            state of object recognition ("BOX", "QR", ...)
        """
        if state == "BOX":
            # TODO: set other variables here if necessary
            self.state = "BOX"

        elif state == "QR":
            # TODO: set other variables here if necessary
            self.state = "QR"

        else:
            print("Error: invalid state selected")

    def main(self):
        """
        Main operations: getting camera input and passing the image to appropriate methods
        """
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            cv2.imshow('Image', frame)

            # TODO: wrap this step in a preprocessing function
            if self.state == "BOX":
                boundingBoxes = detect_boxes(img = frame)
                print(boundingBoxes)

            # TODO: wrap this step in a preprocessing function
            if self.state == "QR":
                message = scan_qr(img = frame)
                print(message)

            if cv2.waitKey(10) == ord('q'):
                break

# Instantiate the Taxi object and run operations
if __name__ == '__main__':
    testTaxi = Taxi()
    testTaxi.set_state(state = "BOX")
    testTaxi.main()