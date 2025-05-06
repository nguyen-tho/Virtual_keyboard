import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import numpy as np
import cvzone
from pynput.keyboard import Controller
from pynput.keyboard import Key


# Webcam settings
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

width = cap.get(3)
height = cap.get(4)
print(f"Actual camera resolution: {width} x {height}")
# Hand Detector
detector = HandDetector(detectionCon=0.8)


# Virtual Keyboard layout (Keychron K6-like)
keys = [
    ["ESC", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "DEL"],
    ["TAB", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"],
    ["CAPS", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "ENTER"],
    ["SHIFT", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/","SHIFT"],
    ["CTRL", "Fn", "ALT", "Win", "SPACE", "CMD", "ALT", "CTRL"]
]

finalText = ""

# Virtual keyboard controller
keyboard = Controller()

# Button class
class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text

# Create button list with variable sizes
# based on key type
# Horizontal offset between keys
# Vertical offset between rows
buttonList = []
startY = 0

for i in range(len(keys)):
    startX = 0
    for key in keys[i]:
        if key == "SPACE":
            size = [250, 60]
        elif key in ["SHIFT", "ENTER", "CAPS", "TAB", "CMD", "CTRL", "ALT", "DEL", "ESC", "Fn", "Win"]:
            size = [90, 60]
        else:
            size = [60, 60]

        buttonList.append(Button([startX, startY], key, size))
        startX += size[0] + 5
    startY += 100

# Get last button’s X pos for arrow keys starting point
lastButtonX = buttonList[-1].pos[0] + buttonList[-1].size[0] + 5
arrowY = startY - 100  # same Y as bottom row

arrow_size = [60, 60]
buttonList.append(Button([lastButtonX, arrowY], "Lt", arrow_size))
buttonList.append(Button([lastButtonX + 65, arrowY - 70], "Up", arrow_size))  # Up button above
buttonList.append(Button([lastButtonX + 65, arrowY], "Dn", arrow_size))
buttonList.append(Button([lastButtonX + 130, arrowY], "Rt", arrow_size))




# Draw all buttons
def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size

        # Draw button box
        cvzone.cornerRect(img, (x, y, w, h), 20, rt=0)
        cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)

        # Set font properties
        font = cv2.FONT_HERSHEY_PLAIN
        font_scale = 1.8  # smaller scale
        thickness = 2

        # Measure text size
        text_size, _ = cv2.getTextSize(button.text, font, font_scale, thickness)
        text_width, text_height = text_size

        # Calculate centered text position
        text_x = x + (w - text_width) // 2
        text_y = y + (h + text_height) // 2 - 5

        # Draw text
        cv2.putText(img, button.text, (text_x, text_y),
                    font, font_scale, (255, 255, 255), thickness)

    return img


# Main loop
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    
    # Create bigger canvas
    canvas = np.zeros((1080, 1920, 3), dtype=np.uint8)

# Paste camera frame into canvas
    canvas[0:img.shape[0], 0:img.shape[1]] = img

# Draw your keyboard on canvas now
    canvas = drawAll(canvas, buttonList)
    hands, canvas = detector.findHands(img)

    canvas = drawAll(canvas, buttonList)

    if hands:
        hand = hands[0]
        lmList = hand["lmList"]

        for button in buttonList:
            x, y = button.pos
            w, h = button.size

        # Check if index fingertip is inside button
            if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
            # Highlight key on hover
                cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5),
                          (175, 0, 175), cv2.FILLED)
                cv2.putText(img, button.text, (x + 15, y + 60),
                        cv2.FONT_HERSHEY_PLAIN, 2.5, (255, 255, 255), 3)

            # Click effect (just touching with index finger triggers press)
                key_pressed = button.text
                cv2.circle(canvas, (lmList[8][0], lmList[8][1]), 20, (0, 255, 0), cv2.FILLED)

            # Handle special keys
                if key_pressed == "SPACE":
                    keyboard.press(Key.space)
                    finalText += " "
                elif key_pressed == "ENTER":
                    keyboard.press(Key.enter)
                elif key_pressed == "TAB":
                    keyboard.press(Key.tab)
                    finalText += "    "
                elif key_pressed == "DEL":
                    keyboard.press(Key.backspace)
                    finalText = finalText[:-1]
                elif key_pressed == "ESC":
                    keyboard.press(Key.esc)
                else:
                    if len(key_pressed) == 1:
                        keyboard.press(key_pressed)
                        finalText += key_pressed
                        print(key_pressed)

            # Draw button green when clicked
                cv2.rectangle(img, button.pos, (x + w, y + h),
                          (0, 255, 0), cv2.FILLED)
                cv2.putText(img, button.text, (x + 15, y + 60),
                        cv2.FONT_HERSHEY_PLAIN, 2.5, (255, 255, 255), 3)
                sleep(1)  # small delay to avoid multiple presses


    # Draw text box for typed characters
    cv2.rectangle(img, (50, 650), (1280, 720), (175, 0, 175), cv2.FILLED)
    cv2.putText(img, finalText, (60, 700),
                cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

    cv2.imshow("Virtual Keyboard", canvas)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
