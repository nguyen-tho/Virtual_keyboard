import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import numpy as np
import cvzone
from pynput.keyboard import Controller
from pynput.keyboard import Key
from math import hypot
import os
# Start Notepad
os.system("start notepad.exe")

# Webcam settings
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
# Set the resolution to 1280x720
# Hand Detector
detector = HandDetector(detectionCon=0.8)
caps_on = False  # Global state for CAPS
fn_on = False  # Global state for Fn

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
    def __init__(self, pos, text, size=[60, 60]):
        self.pos = pos
        self.size = size
        self.text = text

# Create button list with variable sizes
# based on key type
# Horizontal offset between keys
# Vertical offset between rows
def keyboardLayout(keys):
    buttonList = []
    startY = 10

    for i in range(len(keys)):
        startX = 10
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
    
    return buttonList

# Create button list
buttonList = keyboardLayout(keys)
# Function to check if special key is pressed
# This function checks if a special key is pressed and returns the button color

def special_key_pressed(button, special_key, key_status):  
    if button.text == special_key and key_status:
        button_color = (0, 255, 0)  # Green if special key status is active
    else:
        button_color = (255, 0, 255)  # Regular purple when not pressed
    return button_color
    

# Draw all buttons
def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size

        # Default color
        button_color = (255, 0, 255)

        # Check CAPS status
        if special_key_pressed(button, "CAPS", caps_on) == (0, 255, 0):
            button_color = (0, 255, 0)

        # Check Fn status
        if special_key_pressed(button, "Fn", fn_on) == (0, 255, 0):
            button_color = (0, 255, 0)
        
        # Draw button box
        cvzone.cornerRect(img, (x, y, w, h), 20, rt=0)
        cv2.rectangle(img, button.pos, (x + w, y + h), button_color, cv2.FILLED)

        # Set font properties
        font = cv2.FONT_HERSHEY_PLAIN
        font_scale = 1.8
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


    
"""
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
                        finalText += key_pressed.lower()
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
"""

type_action = False  # To avoid double triggering
# use global variable for caps_on to keep track of the state

# Function to handle special keys
# This function handles the special keys like SPACE, ENTER, TAB, DEL, ESC, and CAPS
def handle_special_key(key_pressed, keyboard, finalText, caps_on, fn_on):
    # Define functions for each special key
    def press_space():
        keyboard.press(Key.space)
        print("SPACE pressed")
        return finalText + " ", caps_on, fn_on

    def press_enter():
        keyboard.press(Key.enter)
        print("ENTER pressed")
        return finalText + "\n", caps_on, fn_on

    def press_tab():
        keyboard.press(Key.tab)
        print("TAB pressed")
        return finalText + "    ", caps_on, fn_on
    def press_del():
        keyboard.press(Key.backspace)
        print("DEL pressed")
        return finalText[:-1], caps_on, fn_on

    def press_esc():
        keyboard.press(Key.esc)
        return finalText, caps_on, fn_on

    def toggle_caps():
        new_caps = not caps_on
        print(f"CAPS {'ON' if new_caps else 'OFF'}")
        sleep(0.4)
        return finalText, new_caps, fn_on
    
    def toggle_fn():
        new_fn = not fn_on
        print(f"Fn {'ON' if new_fn else 'OFF'}")
        sleep(0.4)
        return finalText,caps_on, new_fn

    # Map key text to their actions
    special_key_actions = {
        "SPACE": press_space,
        "ENTER": press_enter,
        "TAB": press_tab,
        "DEL": press_del,
        "ESC": press_esc,
        "CAPS": toggle_caps,
        "Fn": toggle_fn
    }

    # Execute if key_pressed is in special keys
    if key_pressed in special_key_actions:
        return special_key_actions[key_pressed]()
    
    # If not a special key, return unchanged values
    return finalText, caps_on, fn_on

# Function to process hand input
# This function processes the hand input and checks if the index finger is hovering over a button
def process_hand_input(hands, canvas, buttonList, keyboard, caps_on, fn_on, type_action, finalText, distance_comp=40):
    if hands:
        hand = hands[0]
        lmList = hand["lmList"]

        # Get fingertip positions
        x1, y1 = lmList[8][0], lmList[8][1]  # Index fingertip
        x2, y2 = lmList[12][0], lmList[12][1]  # Middle fingertip

        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            # Check if index fingertip is hovering over button
            if x < x1 < x + w and y < y1 < y + h:
                # Highlight key on hover
                cv2.rectangle(canvas, (x - 5, y - 5), (x + w + 5, y + h + 5),
                              (175, 0, 175), cv2.FILLED)
                cv2.putText(canvas, button.text, (x + 15, y + 60),
                            cv2.FONT_HERSHEY_PLAIN, 2.5, (255, 255, 255), 3)

                # Draw touch point
                cv2.circle(canvas, (x1, y1), 20, (0, 255, 0), cv2.FILLED)

                # Check for tap gesture (index and middle finger close together)
                distance = hypot(x2 - x1, y2 - y1)

                if distance < distance_comp and not type_action:
                    key_pressed = button.text

                    # Handle special keys
                    if key_pressed in ["SPACE", "ENTER", "TAB", "DEL", "ESC", "CAPS", "Fn"]:
                        finalText, caps_on, fn_on = handle_special_key(key_pressed, keyboard, finalText, caps_on, fn_on)
                    else:
                        if len(key_pressed) == 1:
                            char_to_type = key_pressed
                            if char_to_type.isalpha():
                                char_to_type = char_to_type.upper() if caps_on else char_to_type.lower()
                            keyboard.press(char_to_type)
                            finalText += char_to_type
                            print(f"Typed: {char_to_type}")

                    type_action = True

                elif distance >= distance_comp:
                    type_action = False
                    # Draw button green when pressed
                    cv2.rectangle(canvas, button.pos, (x + w, y + h),
                                  (0, 255, 0), cv2.FILLED)
                    cv2.putText(canvas, button.text, (x + 15, y + 60),
                                cv2.FONT_HERSHEY_PLAIN, 2.5, (255, 255, 255), 3)

                    sleep(0.4)
    return canvas, caps_on, fn_on, type_action, finalText

# Main loop

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    
    # Create bigger canvas
    canvas = np.zeros((1080, 1920, 3), dtype=np.uint8)

# Paste camera frame into canvas
    canvas[0:img.shape[0], 0:img.shape[1]] = img

# Draw your keyboard on canvas now
    hands, canvas = detector.findHands(img)
    # Draw all buttons
    canvas = drawAll(canvas, buttonList)

    canvas, caps_on, fn_on, type_action, finalText = process_hand_input(hands, canvas, buttonList, 
                                                                        keyboard, caps_on, fn_on, type_action, finalText)

    # Draw text box for typed characters
    #cv2.rectangle(canvas, (50, 650), (1280, 720), (175, 0, 175), cv2.FILLED)
    #cv2.putText(canvas, finalText, (60, 700),
    #           cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

    cv2.imshow("Virtual Keyboard", canvas)
    if cv2.waitKey(1) & 0xFF == ord('q'): # Press 'q' to exit
        break

cap.release()
os.system("taskkill /im notepad.exe /f") # Close Notepad
# Close all OpenCV windows
cv2.destroyAllWindows()
