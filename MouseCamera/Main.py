import cv2
import mediapipe as mp
import pyautogui
import threading
from win32api import GetSystemMetrics

if __name__ != "__main__":
    exit()

pyautogui.FAILSAFE = False

SCREEN_WIDTH = GetSystemMetrics(0)
SCREEN_HEIGHT = GetSystemMetrics(1)

mpDrawing = mp.solutions.drawing_utils
mpDrawingStyles = mp.solutions.drawing_styles
mpHands = mp.solutions.hands
capture = cv2.VideoCapture(0)
pressed = False
wristPositionX = 0
wristPositionY = 0

def MouseThread():
    global capture
    global pressed
    global wristPositionX
    global wristPositionY

    while capture.isOpened():
        wristPositionX = min(wristPositionX, SCREEN_WIDTH)
        wristPositionY = min(wristPositionY, SCREEN_HEIGHT)
        wristPositionX = max(wristPositionX, 0)
        wristPositionY = max(wristPositionY, 0)

        if pressed:
            pyautogui.click()

        pyautogui.moveTo(wristPositionX * 50, -wristPositionY * 10, 1)

mouseThread = threading.Thread(target = MouseThread)

mouseThread.start()

with mpHands.Hands(model_complexity = 0,
                   min_detection_confidence = 0.5,
                   min_tracking_confidence = 0.5,
                   max_num_hands = 1) as hands:
    while capture.isOpened():
        success, image = capture.read()

        if not success:
            print("Camera Not Found.")

            continue

        # For performance reasons, disable an image writing.
        image.flags.writeable = False

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        image.flags.writeable = True

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Draw hand annotations on the image.
        if results.multi_hand_landmarks:
            for handLandmarks in results.multi_hand_landmarks:
                wristPositionX = int(handLandmarks.landmark[0].x * 100)
                wristPositionY = int(handLandmarks.landmark[0].y * 100)
                indexFingerTipPositionX = int(handLandmarks.landmark[8].x * 100)
                indexFingerTipPositionY = int(handLandmarks.landmark[8].y * 100)
                pressed = indexFingerTipPositionY <= 61

                cv2.putText(image,
                            text = "Position=[%d, %d] Pressed=%d" %(indexFingerTipPositionX, indexFingerTipPositionY, pressed),
                            org = (15, 30),
                            fontFace = cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale = 1,
                            color = 172,
                            thickness = 5)
                
                mpDrawing.draw_landmarks(image, handLandmarks,
                                         mpHands.HAND_CONNECTIONS,
                                         mpDrawingStyles.get_default_hand_landmarks_style(),
                                         mpDrawingStyles.get_default_hand_connections_style())

        # Flip the image left and right for easier viewing.
        cv2.imshow("Mouse Camera", image)

        if cv2.waitKey(5) & 0xff == 27:
            break

capture.release()