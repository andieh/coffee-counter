import cv2
import numpy as np
import os

CACHE_FOLDER = "/home/andieh/src/coffee-counter/server/tmp/"

class Numbers:
    def __init__(self, height=60, pos=(0,0)):
        self.pos = pos
        self.height = height

    def draw(self, number):
        if number <= 0:
            return None

        step = int(self.height / 5)
        exp_w = (int(number / 5)+1)*step*5
        img = np.ones((self.height, exp_w, 1), np.uint8)*255

        for i in range(1, number+1):
            init = self.pos
            if i % 5 == 0:
                x_start = init[0] + ((i-5)*step )
                x_end = init[0] + (i*step)
            else:
                x_start = init[0] + (i*step)
                x_end = x_start
            
            cv2.line(img, (x_start, init[1]), (x_end, init[1] + self.height), 0, 2)

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
        
        if os.path.exists(fn):
            return fn 

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
