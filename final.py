import cv2
import numpy as np
import os
from handtrackingmodule import HandDetector
import pyautogui as py
from pynput.keyboard import Controller
from time import sleep



wScr, hScr =py.size()

pb=""
wCam, hCam = 1280,720

pc=(255, 0, 255)

folderPath="head"
l=os.listdir(folderPath)
imgl= []
for i in l:
    image = cv2.imread(f'{folderPath}/{i}')
    imgl.append(image)


header1=imgl[0]

cap = cv2.VideoCapture(0)
cap.set(3,wCam) 
cap.set(4,hCam)

detector = HandDetector()
xp, yp = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)
r=0
font = cv2.FONT_HERSHEY_SIMPLEX
i=10
currX, currY, prevX, prevY = 0, 0, 0, 0
smoothening=2
frame_red =200

keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]
finalText = ""

keyboard = Controller()


def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, button.text, (x + 20, y + 65),cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
    return img



class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text


buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([100 * j + 50, 100 * i + 200], key))


while True:
    # Import the image
    sc, img = cap.read()
    img = cv2.flip(img, 1)

    # Find the Hand Landmarks 
    lmList, img = detector.lmlist(img)
    #k = cv2.waitKey(33)

    if len(lmList) != 0:
        # tip of index finger
        x1, y1 = lmList[8][1:]
        # tip of  middle finger
        x2, y2 = lmList[12][1:]

        # Find fingers which  are up
        fingers, img = detector.fingersUp(img, lmList, False)
        

        # Selection Mode (index and middle finger are up)
        if fingers[1] and fingers[2]:
            #xp, yp = 0, 0
            if y1<133:
                #mouse
                if 232<x1<450:
                    header1=imgl[1]
                    r=1

                #keyboard
                elif 500<x1<900:
                    header1=imgl[2]
                    r=2

                #voice
                elif 920<x1<1110:
                    header1=imgl[3]
                    r=3

            cv2.rectangle(img, (x1, y1 - 30), (x2, y2+30), pc, cv2.FILLED)

      
        if r==1:
            cv2.putText(img,"mouse mode", (200,200),cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
            if(fingers == [0,1,0,0,0]):

                x1, y1 = lmList[8][1:]
                cv2.rectangle(img, (frame_red, frame_red), (wCam - frame_red, hCam - frame_red), (255, 0, 255), 2)

                cv2.circle(img, (x1,y1), 15, (255,0,255), cv2.FILLED)
                
                posX = np.interp(x1, (frame_red,wCam-frame_red), (0,wScr))
                posY = np.interp(y1, (frame_red,hCam-frame_red), (0,hScr))

                currX = prevX + (posX - prevX)/smoothening
                currY = prevY + (posY - prevY)/smoothening

                py.moveTo(currX,currY)

                prevX = currX
                prevY = currY

            elif(fingers[1] and fingers[2]):
                    distance, img = detector.findDistance(8, 12, img, lmList)
                    #print(distance)
                    if (distance<40):
                        py.click()

            elif(fingers==[1,0,0,0,0]):
                
                posX = np.interp(x1, (frame_red,wCam-frame_red), (0,wScr))
                posY = np.interp(y1, (frame_red,hCam-frame_red), (0,hScr))

                currX = prevX + (posX - prevX)/smoothening
                currY = prevY + (posY - prevY)/smoothening
                prevX = currX
                prevY = currY
                py.dragTo(currX, currY, 1,button='left')




        elif r==2:
            img = drawAll(img, buttonList)
            for button in buttonList:
                x, y = button.pos
                w, h = button.size
                dist=0


                if(fingers == [1,1,0,0,0] or fingers == [0,1,0,0,0]):

                    if x <lmList[8][1] <(x + w) and y <lmList[8][2] <y + h:

                        cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                        cv2.putText(img, button.text, (x + 20, y + 65),cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                        dist, img = detector.findDistance(8, 12, img, lmList)
                        #print(dist)

                        if(pb!=button.text):
                            keyboard.press(button.text)
                            cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                            cv2.putText(img, button.text, (x + 20, y + 65),cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                            finalText += button.text
                            sleep(0.1)
                        pb=button.text
                        

            cv2.rectangle(img, (50, 550), (700, 650), (175, 0, 175), cv2.FILLED)
            cv2.putText(img, finalText, (60, 630),cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

        elif r==3:
            continue
        
        
    img[0:130,0:1280] = header1
    cv2.imshow("Image", img)
    cv2.waitKey(1)
    key = cv2.waitKey(1)
    if(key == 27):
        break