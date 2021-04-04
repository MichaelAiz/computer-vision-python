import cv2
import numpy as np
from boxDetection.detect import Detection
from qrScan.scan import scan as scan_qr
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)


class Taxi:
    """
    Performs cardboard box detection on a given video frame

    Attributes
    ----------
    state : string
        state of object recognition ("BOX", "QR", ...)
    bbox : list<tuple<tuple, tuple>>
        a list of ((x1, y1), (x2, y2)) coordinates for (top left, bottom right) of bounding boxes; one per box
    frame : np.ndarray
        the current video frame
    yolo : Detection object
        the YOLOv5 detector
    tracker : TrackerKCF object
        the cv2 KCF bounding box tracker
    nextUncheckedID : int
        the ID of the next box to scan
    expectedCount : int
        the number of boxes it needs to detect to go into tracking state
    expectedQR : string
        QR code on the correct box
    numStableFrames : int
        the number of consecutive frames with all <expectedCount> number of boxes in view before switching to TRACK
    distanceFromBox : int
        the plane's current distance from the target box
    minDistanceFromBox : int
        the minimum distance the plane can be from the box until it's considered too close
    moveWaitTarget : int
        the number of frames to wait before issuing another move or turn command

    Methods
    -------
    __init__()
        Initialize class variables
    find_overlapped_bbox()
        Find which new YOLO bbox overlaps the previously tracked bbox
    calculate_distance()
        Calculate approximate distance between box and drone
    set_state(state: string)
        Prepare variables for box detection, qr decoding, etc.
    main()
        Main operations: getting camera input and passing the image to appropriate methods
    """

    def __init__(self, state="BOX", bbox=[((0, 0), (0, 0))], frame=[], nextUncheckedID=0, 
                 expectedCount=5, expectedQR="abcde12345", numStableFrames=20, distanceFromBox=0, 
                 minDistanceFromBox=30, moveWaitTarget=10, recalibrate=False, lastBbox=[]):
        """
        Initializes variables
        """
        self.state = state
        self.bbox = bbox
        self.frame = frame
        self.yolo = Detection()
        self.tracker = None
        self.nextUncheckedID = nextUncheckedID
        self.expectedCount = expectedCount
        self.expectedQR = expectedQR
        self.numStableFrames = stableFrames
        self.distanceFromBox = distance
        self.minDistanceFromBox = minDistanceFromBox
        self.moveWaitTarget = moveWaitTarget
        self.recalibrate = recalibrate
        self.lastBbox = self.lastBbox

    def find_overlapped_bbox(self):
        """
        Find which new YOLO bbox overlaps the previously tracked bbox
        """
        # TODO: given self.lastBbox and self.bbox, return the one bbox from self.bbox which overlaps/covers self.lastBbox by a significant amount
        # The new bbox must belong to the same box as the last one
        # This function helps recalibrate the bounding box to fit the actual box better, so distance calculation is more accurate
        # If self.bbox is empty or no new bbox overlaps the old one by a significant amount, return None
        return bbox

    def calculate_distance(pts):
        """
        Calculate approximate distance between box and drone
        """

        # For temporary storage of distances
        tempDistancesList = []

        # (Known) focal length of the camera in mm
        focalLength = 1

        # (Known) real Height of the box in mm
        realHeight = 101.6

        # (Known) height of the image in pixels
        imageHeight = 1

        # (Known) height of the sensor in mm
        sensorHeight = 1

        # Calculating object height in pixels by extracting y coordinates from each tuple 'pts'
        objectHeight = pts[0][1] - \
            pts[1][1] if (pts[0][1] > pts[1][1]) else pts[1][1] - pts[0][1]

        # Calculate distance
        distance = (focalLength * realHeight * imageHeight) / \
            (objectHeight * sensorHeight)

        return distance

    def set_state(self, state):
        """
        Prepare variables for box detection, qr decoding, etc.

        Parameters
        ----------
        state: string
            state of object recognition ("BOX", "QR", ...)
        """
        if state == "BOX" or state == 0:
            self.state = "BOX"

        elif state == "TRACK" or state == 1:
            self.state = "TRACK"

            # If switching to track from box for the first time, use the box ID
            if not self.recalibrate:
                bbox = self.bbox[self.nextUncheckedID]
            # Else update distance with recalibrated bbox
            else:
                bbox = find_overlapped_bbox()

            # If recalibration failed to find the new box, attempt QR read
            if bbox == None:
                self.set_state("QR")
                
            # If recalibration found the new box, recalculate distance and carry on moving
            else:
                bboxReformat = (bbox[0][0], bbox[0][1],
                                bbox[1][0] - bbox[0][0], bbox[1][1] - bbox[0][1])
                # Note: must create the tracker here instead of __init__, else can't switch freely between track & box
                self.tracker = cv2.TrackerKCF_create()
                # Initialize tracker with first frame and bounding box
                self.tracker.init(self.frame, bboxReformat)
                # Calculate distance from tracked bbox
                self.distanceFromBox = self.calculate_distance(bbox)

        elif state == "QR" or state == 2:
            self.state = "QR"

        else:
            print("Error: invalid state selected")

    def main(self):
        """
        Main operations: getting camera input and passing the image to appropriate methods
        """
        cap = cv2.VideoCapture(0)

        # The number of consecutive frames where all <expectedCount> boxes are in view
        frameCount = 0

        # Wait for a certain number of detections before issuing the next movement command
        moveWaitCount = 0

        # Tracks whether the plane has moved by the calculated distance
        # In which case it needs to recalibrate the bounding box and calculate a new distance
        distanceCount = 0

        while True:
            ret, self.frame = cap.read()

            if self.state == "BOX":
                self.bbox = self.yolo.detect_boxes(self.frame)
                for (topLeft, botRight) in self.bbox:
                    cv2.rectangle(self.frame, topLeft,
                                  botRight, (0, 0, 255), 2)

                # If initial run, expect 5 boxes
                # If recalibrating, expect at least 1 box (less accurate but there's no other way)
                if not self.recalibrate:
                    expCount = self.expectedCount
                else:
                    expCount = 1

                # YOLO can't move on until all 5 boxes stay in frame consistently/continuously for more than frameCount frames
                if len(self.bbox) == expCount:
                    frameCount += 1
                else:
                    frameCount = 0

                if frameCount == self.numStableFrames:
                    self.set_state("TRACK")
                    frameCount = 0

            # Switch to track when all 5 boxes are in view
            if self.state == "TRACK":
                found, bbox = self.tracker.update(self.frame)

                # Tracking succeeds and plane isn't already close enough
                if found and self.distanceFromBox > self.minDistanceFromBox:
                    p1 = (int(bbox[0]), int(bbox[1]))
                    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                    self.bbox = [(p1, p2)]
                    cv2.rectangle(self.frame, p1, p2, (255, 0, 0), 2, 1)

                    # While not at half the distance from the box, keep moving forward
                    if distanceCount < self.distanceFromBox // 2:
                        # Issue the next movement command every couple of frames
                        if moveWaitCount < self.moveWaitTarget:
                            moveWaitCount += 1
                        else:
                            # Don't need to turn if the bbox midpoint is within the center margin
                            # If center to left past margin, turn right by 1 degree
                            # If center to right past margin, turn left by 1 degree
                            margin = 50
                            turn = 0
                            forward = 0
                            if (p1[0] + p2[0])/2 < self.frame.shape[0]/2 - margin:
                                turn = 1
                            elif (p1[0] + p2[0])/2 > self.frame.shape[0]/2 + margin:
                                turn = -1
                            else:
                                forward = 5
                                distanceCount += forward
                            print(
                                f"Turn {turn} degree(s) and move forward by {forward}")

                            # TODO: fix self.frame.shape not matching cv.imshow video shape
                            cv2.rectangle(self.frame, (240, 0),
                                          (240, 640), (255, 0, 255), 2, 1)

                            moveWaitCount = 0

                    # At the halfway point, do YOLO again to reset the size of the bounding box
                    # KCF and most other tracking algos have constant bbox size even when getting closer, which is a problem for distance calculation
                    else:
                        self.recalibrate = True
                        self.lastBbox = self.bbox
                        self.set_state("BOX")

                # Tracking fails or plane is already close enough
                else:
                    # Assuming the plane is facing the right box, tracking fails either due to algo error or the plane got too close to object
                    # In the latter case, try scanning the QR code
                    # If scanned, great!
                    # Else, switch to human control to drive the plane to the right spot
                    self.set_state("QR")

            if self.state == "QR":
                message = scan_qr(self.frame)
                # print(message)
                if message != None:
                    if message == self.expectedQR:
                        print("QR found and matches. Pick up the box")
                    else:
                        print("QR found but does not match. Turn around and try again")
                else:
                    print("No QR code found. Switch to human control")

            cv2.imshow('Image', self.frame)

            # Temporary manual box selection
            key = cv2.waitKey(10)
            if key == ord('b') and self.state != "BOX":
                self.set_state("BOX")
                print("switch to box state")

            # Temporary manual tracking selection
            if key == ord('t') and self.state != "TRACK":
                self.set_state("TRACK")
                print("switch to tracking state")

            # Temporary manual QR code selection
            if key == ord('r') and self.state != "QR":
                self.set_state("QR")
                print("switch to QR state")

            if key == ord('q'):
                break


# Instantiate the Taxi object and run operations
if __name__ == '__main__':
    testTaxi = Taxi(expectedQR="abcde12345")
    testTaxi.main()