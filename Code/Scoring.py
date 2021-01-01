#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Scoring.py: Scoring a Firing Range.'''

# import standard libraries
from skimage.measure import compare_ssim
import cv2
import numpy as np
import math

def calculateScore(rings, circles):
    """ Funtion to calculate the score a bullet mark on the firing board taeget
    
    Parameters:
    argument1 (): array of centre coordinates of the firing board rings
    argument2 (): array of centre coordinates and the radius of the bullet marks
    
    Returns:
    int: score of the bullet mark
    float: score of the bullet mark in sub-decimal form
    
    """
    # calculate the Eucledian distabce between the bullet mark and the centre 
    # of the rings  
    x = int(circles[0]) - int(rings[0][0])
    y = int(circles[1]) - int(rings[0][1])
    d = int(math.sqrt((x)**2 + (y)**2) - circles[2])
    
    prevring = 0
    index = 0
    for curring in rings:
        if d < curring[2]:
            break
        else:
            prevring = curring[2]
        index += 1
        
    # claculate sub-decimal precision score
    sub = 0
    
    delta = (curring[2] - prevring)/10
    if index > 0:
        for i in range(9):
            if d < (prevring + i*delta):
                break
        sub = 10-index - 1 + (10 - i + 1)/10
    else:
        sub = 10-index
    return (10-index), round(sub, 1)