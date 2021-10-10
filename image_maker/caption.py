import cv2
from resizeimage import resizeimage
import glob
from PIL import Image 

# Opens the Video file
k=15
"""
cap= cv2.VideoCapture('video2.mp4')

i=0
while(cap.isOpened()):
    frameId = cap.get(1) #current frame number
    ret, frame = cap.read()
    if (ret != True):
        break
    if (i % k == 0):
        filename = "captions\%s.jpg"%(i,)
        cv2.imwrite(filename, frame)
    i+=1
"""
filenames = []

for filename in glob.glob('mosaic_pictures/*.jpg'):
    
    #img = cv2.imread(filename)
    filenames.append(filename)




out=cv2.VideoWriter('mosaic_video.avi',0,8,(1000,600))
i=0
while True:
    bol=False 
    ch="mosaic_pictures\%s.jpg"%(i,)
    print ch
    for filename in filenames:
        
        if (filename == ch):
           
            img = Image.open(filename).resize((1000,600))
            img.save('mosaic.jpg')
            img2=cv2.imread('mosaic.jpg')
            out.write(img2)
            bol=True
            print"done"
    if (bol==False):
        break
    i+=k        
out.release()    

print "TERMINER!"


