# playgui.py
# Source: https://github.com/DrGFreeman/rps-cv
#
# MIT License
#
# Copyright (c) 2017 Julien de la Bruere-Terreault <drgfreeman@tuta.io>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# This file is the main program to run to play the Rock-Paper-Scissors game
# with the pygame graphical user interface (GUI).

import pickle
import random
import sys
import time

import pygame as pg
import pygame.locals

import numpy as np
import cv2

import rpsutil as rps
import rpsimgproc as imp
import rpsgui

def saveImage(img, gesture, notify=False):

    # Define image path and filename
    folder = rps.imgPathsRaw[gesture]
    name = rps.gestureTxt[gesture] + '-' + time.strftime('%Y%m%d-%H%M%S')
    extension = '.png'

    if notify:
        print('Saving {}'.format(folder + name + extension))

    # Save image
    cv2.imwrite(folder + name + extension, img)

def getResult(cam):

    # Initialize game mode variables
    privacy = False
    loop = False

    # Read command line arguments
    argv = sys.argv
    argv.pop(0)

    if len(sys.argv) > 0:
        for arg in argv:
            if arg == 'privacy':
                privacy = True
            elif arg == 'loop':
                loop = True
            else:
                print('{} is not a recognized argument'.format(arg))

    # Load classifier from pickle file
    filename = 'clf.pkl'
    with open(filename, 'rb') as f:
        clf = pickle.load(f)

    # Initialize last gesture value
    lastGesture = -1

    while True:

        # Get image from camera
        img = imp.crop(cam)

        # Convert image to RGB (from BGR)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Set player image to imgRGB
        gui.setPlImg(imgRGB)

        # Get grayscale image
        gray = imp.getGray(imgRGB, threshold=17)

        # Count non-background pixels
        nonZero = np.count_nonzero(gray)
        #print(nonZero)

        # Define waiting time
        waitTime = 0

        # Parameters for saving new images
        gesture = None
        notify = False

        #time.sleep(2)
        # Check if player hand is present
        # Predict gesture
        predGesture = clf.predict([gray])[0]
        if predGesture == lastGesture:
            successive += 1
        else:
            successive = 0
        if successive == 2:
            print('Player: {}'.format(rps.gestureTxt[predGesture]))
            waitTime = 3000
            gesture = predGesture

            # Computer gesture
            computerGesture = random.randint(0,2)
            print('Computer: {}'.format(rps.gestureTxt[computerGesture]))

            # Set computer image to computer gesture
            gui.setCoImg(coImgs[computerGesture])

            diff = computerGesture - predGesture
            if diff in [-2, 1]:
                return [1, predGesture, computerGesture]
            elif diff in [-1, 2]:
                return [2, predGesture, computerGesture]
            else:
                return [0, predGesture, computerGesture]

            lastGesture = predGesture

        else:
            lastGesture = -1

        # Wait
        pg.time.wait(waitTime)

        if gesture is not None:
            # Save new image
            saveImage(img, gesture, notify)
