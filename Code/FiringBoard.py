#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''FiringBoard.py: Realtime Identification and Scoring of a Firing Range.'''

# import standard libraries
from skimage.measure import compare_ssim
import cv2
import numpy as np
import math
import Scoring


# HoughCircle parameters for identofying the firing board rings 
params = [[56, 20, 5, 15], [56, 30, 45, 52], [83, 30, 78, 81], [45, 50, 90, 120], [45, 60, 110, 140], [45, 80, 149, 170], 
          [45, 80, 181, 201], [45, 100, 202, 235], [45, 120, 232, 263], [45, 140, 270, 295]]


boardRings = []

# load the firing range video file
video = cv2.VideoCapture('./../InputFiles/Firing.mp4')
ret, curframe = video.read()

gray = cv2.cvtColor(curframe, cv2.COLOR_BGR2GRAY)

cv2.imshow('Realtime Scoring of Firing Board', gray)

img = curframe.copy()
# open a file to write the target rings coordinates and radius 
boardringsFile = open('./../Reports/TargetRingsIdentified.csv', 'w')
boardringsFile.write('Ring,X-Coordinate,Y-Coorindate,Radius\n')

# Identify the firing board rings
ring = 0    
for param in params:
    # Attempt to detect circles in the grayscale image.
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1 = param[0],
                                param2 = param[1], minRadius = param[2], maxRadius = param[3])
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        boardRings.append(circles[0][0])
        
        for i in circles[0,:]:
            # Draw the outer circle
            cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
            # Draw the center of the circle
            cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)
            # write the board ring coordinates and radius to a text file
            boardringsFile.write(str(10 - ring) + ',' + str(i[0]) + ',' + str(i[1]) + ',' + str(i[2]) + '\n')

    # save the identified board rings image
    cv2.imshow('Realtime Scoring of Firing Board', img)
    cv2.imwrite('./../OutputFiles/TargetRingsIdentified.jpg', img)
    
    ring += 1    
    # close the app if q key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break

# close the boardringsFile
boardringsFile.close()

cumulativeScore = 0
subcumulativeScore = 0.0
bullet = 0

ret, curframe = video.read()
# convert the frame to grey scale
curframe = cv2.cvtColor(curframe, cv2.COLOR_BGR2GRAY)
prevframe = curframe

ret, curframe = video.read()

# open a text file to wrote the score details
scoreFile = open('./../Reports/Score.csv', 'w')
scoreFile.write('Bullet,X-Coorindate,Y-Coorindate,Radius,Bullet Score,Cumulative Score,Sub-decimal Bullet Score,Sub-decimal Cumulative Score\n')

while ret == True:
    # convert the frame to grey scale
    gray = cv2.cvtColor(curframe, cv2.COLOR_BGR2GRAY)    
    
    cv2.imshow('Realtime Scoring of Firing Board', curframe)
    
    # find the difference in the prev and cur frame to identify the bullet mark
    diff = cv2.subtract(gray, prevframe)
    
    img = cv2.GaussianBlur(diff, (99,99), 1, 1)
    
    # HoughCircle parameters to identofy the bullet marks
    param1 = 8
    param2 = 15
    minRadius = 3
    maxRadius = 20 
    
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 10, param1 = param1,
                                        param2 = param2, minRadius = minRadius, maxRadius = maxRadius)
    bulletimg = diff.copy() 
    if circles is not None:
        circles = np.uint16(np.around(circles))
        bullet += 1
        # identify the bullter mark 
        for i in circles[0,:]:
            # Draw the outer circle
            cv2.circle(bulletimg,(i[0],i[1]),i[2],(0,255,0),2)
            # Draw the center of the circle
            cv2.circle(bulletimg,(i[0],i[1]),2,(0,0,255),3)
            
        # save the image of the identified bullet mark
        cv2.imwrite('./../OutputFiles/Bullet' + str(bullet)  + '.jpg', bulletimg)
        
        # for circle in circles[0,:]:
        print(circles[0][0])
        
        score, sub = calculateScore(boardRings, circles[0][0])    
        cumulativeScore += score 
        subcumulativeScore += sub
        print('score: ' + str(score) + '\t' + str(sub))
        print('cum score: ' + str(cumulativeScore) + '\t' + str(round(subcumulativeScore, 1)))
        # write the score to the score file.
        scoreFile.write(str(bullet) + ',' + str(circles[0][0][0]) + ',' + str(circles[0][0][1]) + ',' + str(circles[0][0][2]) + ',' + str(score) + ',' + str(cumulativeScore) + ',' + str(sub) + ',' + str(round(subcumulativeScore, 1)) + '\n')
        
        prevframe = gray
        #prevframe = curframe
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    ret, curframe = video.read()

scoreFile.close()

video.release()
cv2.destroyAllWindows()