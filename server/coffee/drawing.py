import cv2
import numpy as np
import os
from random import randint
from config import Config

class Numbers:
    def __init__(self, height=60, pos=(0,0)):
        self.pos = pos
        self.height = height

    def _random(self):
        if not Config.RANDOMNESS:
            return 0
        return randint(-2,2)

    def draw(self, number):
        if number < 0:
            return None

        step = int(self.height / 5)
        exp_w = max((int(number / 5)+1)*step*5, 1)
        img = np.ones((self.height, exp_w, 1), np.uint8)*255

        for i in range(1, number+1):
            init = self.pos
            if i % 5 == 0:
                x_start = init[0] + ((i-5)*step) + self._random()
                x_end = init[0] + (i*step) + self._random()
            else:
                x_start = init[0] + (i*step) + self._random()
                x_end = x_start + self._random()
            
            cv2.line(img, (x_start, init[1] + self._random()), (x_end, init[1] + self.height + self._random()), randint(0,50), 2)

        return img

    def cache_number(self, num, folder):
        # check if already processed
        fnp = os.path.join(folder, str(self.height))
        if not os.path.exists(fnp):
            os.mkdir(fnp)

        try:
            num = int(num)
        except:
            return None
        fn = os.path.join(fnp, "num-{:04d}.jpg".format(num))
        
        #if os.path.exists(fn):
        #    return fn 

        img = self.draw(num)
        cv2.imwrite(fn, img)
        return fn

if __name__ == "__main__":
    nr = Numbers(height=40)
    for i in range(255):
        img = nr.draw(i)
        if img is not None:
            cv2.imshow("what", img)
            cv2.waitKey(30)
