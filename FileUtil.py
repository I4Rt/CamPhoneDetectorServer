import base64
import cv2
from numpy import *

def convertImageToBytes(img, imgType = '.png') -> str:
        _, encriptedImg = cv2.imencode(imgType, img)
        imgAsStr = encriptedImg.tostring()
        imgByteStr = base64.b64encode(imgAsStr).decode("utf-8")
        return imgByteStr
    
def convertBytesToImg(encImg: str):
        readImgBytes = base64.b64decode(encImg)
        npImg = frombuffer(readImgBytes, uint8) 
        decImg = cv2.imdecode(npImg, -1)
        return decImg