#Importing the required libraries 
import cv2
import glob
from joblib import Parallel, delayed
import os, random, argparse 
from PIL import Image ,ImageEnhance,ImageOps, ImageDraw
from resizeimage import resizeimage
import imghdr 
import numpy as np 
from matplotlib import pyplot as plt
  
def saisie_gridsize(target_image):
  tab=[10,22,34,56,74, 112, 130, 168, 224]
  dims=[]
  for i in tab:
    x=(target_image.size[1] // i ,target_image.size[0] // i)
    if x not in dims:
      dims.append(x)
  print("\nchoisie une combinaison parmis ces dimentions:",dims)
  n=int(input("donner premiere dimentionn\n"))
  m=int(input("donner deuxieme dimention\n"))
  print((n,m))
  while (n,m) not in dims:
      print("erreur : donner une dimention valide!!!!")
      m=input("donner premiere dimentionn\n")
      n=input("donner deuxieme dimention\n")
  grid_size = (n,m)
  return grid_size
def getAverageRGBOld(image): 
  """ 
  Given PIL Image, return average value of color as (r, g, b) 
  """
  # no. of pixels in image 
  npixels = image.size[0]*image.size[1] 
  # get colors as [(cnt1, (r1, g1, b1)), ...] 
  cols = image.getcolors(npixels) 
  # get [(c1*r1, c1*g1, c1*g2),...] 
  sumRGB = [(x[0]*x[1][0], x[0]*x[1][1], x[0]*x[1][2]) for x in cols]  
  # calculate (sum(ci*ri)/np, sum(ci*gi)/np, sum(ci*bi)/np) 
  # the zip gives us [(c1*r1, c2*r2, ..), (c1*g1, c1*g2,...)...] 
  avg = tuple([int(sum(x)/npixels) for x in zip(*sumRGB)]) 
  return avg 
  
def getAverageRGB(image): 
  """ 
  Given PIL Image, return average value of color as (r, g, b) 
  """
  # get image as numpy array 
  im = np.array(image) 
  # get shape 
  w,h,d = im.shape 
  # get average 
  return tuple(np.average(im.reshape(w*h, d), axis=0)) 
  
def splitImage(image, size): 
  """ 
  Given Image and dims (rows, cols) returns an m*n list of Images  
  """
  W, H = image.size[0], image.size[1] 
  m, n = size 
  w, h = int(W/n), int(H/m) 
  # image list 
  imgs = [] 
  # generate list of dimensions 
  for j in range(m): 
    for i in range(n): 
      # append cropped image 
      imgs.append(image.crop((i*w, j*h, (i+1)*w, (j+1)*h))) 
  return imgs 
  
def getImages(imageDir): 
  """ 
  given a directory of images, return a list of Images 
  """
  files = os.listdir(imageDir) 
  images = [] 
  for file in files: 
    filePath = os.path.abspath(os.path.join(imageDir, file)) 
    try: 
      # explicit load so we don't run into resource crunch 
      fp = open(filePath, "rb") 
      im = Image.open(fp) 
      images.append(im) 
      # force loading image data from file 
      im.load()  
      # close the file 
      fp.close()  
    except: 
      # skip 
      print("Invalid image: %s" % (filePath,)) 
  return images 
  
def getImageFilenames(imageDir): 
  """ 
  given a directory of images, return a list of Image file names 
  """
  files = os.listdir(imageDir) 
  filenames = [] 
  for file in files: 
    filePath = os.path.abspath(os.path.join(imageDir, file)) 
    try: 
      imgType = imghdr.what(filePath)  
      if imgType: 
        filenames.append(filePath) 
    except: 
      # skip 
      print("Invalid image: %s" % (filePath,)) 
  return filenames 
  
def getBestMatchIndex(input_avg, avgs): 
  """ 
  return index of best Image match based on RGB value distance 
  """
  
  # input image average 
  avg = input_avg 
    
  # get the closest RGB value to input, based on x/y/z distance 
  index = 0
  min_index = 0
  min_dist = float("inf") 
  for val in avgs: 
    dist = ((val[0] - avg[0])*(val[0] - avg[0]) +
            (val[1] - avg[1])*(val[1] - avg[1]) +
            (val[2] - avg[2])*(val[2] - avg[2])) 
    if dist < min_dist: 
      min_dist = dist 
      min_index = index 
    index += 1
  val2=avgs[min_index]
  l=[]
  i=0
  for val in avgs: 
    dist = ((val[0] - val2[0])*(val[0] - val2[0]) +
            (val[1] - val2[1])*(val[1] - val2[1]) +
            (val[2] - val2[2])*(val[2] - val2[2]))
    if dist <= 400: 
      l.append(i)
    i+=1  
  
  return l[random.randint(0,len(l)-1)]
        
  
  
def createImageGrid(images, dims): 
  """ 
  Given a list of images and a grid size (m, n), create  
  a grid of images.  
  """
  m, n = dims 
  
  # sanity check 
  assert m*n == len(images) 
  
  # get max height and width of images 
  # ie, not assuming they are all equal 
  width = max([img.size[0] for img in images]) 
  height = max([img.size[1] for img in images]) 
  
  # create output image 
  grid_img = Image.new('RGB', (n*width, m*height)) 
    
  # paste images 
  for index in range(len(images)): 
    row = int(index/n) 
    col = index - n*row 
    grid_img.paste(images[index], (col*width, row*height)) 
      
  return grid_img 
  
  
def createPhotomosaic(target_image, input_images, grid_size, 
                      reuse_images=True): 
  """ 
  Creates photomosaic given target and input images. 
  """
  
  print('splitting input image...') 
  # split target image  
  target_images = splitImage(target_image, grid_size) 
  
  print('finding image matches...') 
  # for each target image, pick one from input 
  output_images = [] 
  # for user feedback 
  count = 0
  batch_size = int(len(target_images)/10) 
  
  # calculate input image averages 
  avgs = [] 
  for img in input_images: 
    avgs.append(getAverageRGB(img)) 
  
  for img in target_images: 
    # target sub-image average 
    avg = getAverageRGB(img) 
    # find match index 
    match_index = getBestMatchIndex(avg, avgs) 
    res=crop(input_images[match_index])
    img = img.resize((120, 120))
    img.paste(res,(0,0),res)
    output_images.append(img) 
    # user feedback 
    if count > 0 and batch_size > 10 and count % batch_size is 0: 
      print('processed %d of %d...' %(count, len(target_images))) 
    count += 1
    # remove selected image from input if flag set 
    if not reuse_images: 
      input_images.remove(match) 
  
  print('creating mosaic...') 
  # draw mosaic to image 
  mosaic_image = createImageGrid(output_images, grid_size) 
  
  # return mosaic 
  return mosaic_image 

def crop(im):

    im = im.resize((120, 120))
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask) 
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)

    output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output  

# Gather our code in a main() function 
def main(img,input_images): 
  # Command line args are in sys.argv[1], sys.argv[2] .. 
  # sys.argv[0] is the script name itself and can be ignored 
  
 
  
  # target image 
  frame, i= img
  cv2.imwrite("frame%s.jpg" %(i,), frame)
  target_image = Image.open("frame%s.jpg" %(i,)) 
  # size of grid 
  #grid_size = (49, 87)
  grid_size =(31, 56)
  #grid_size = saisie_gridsize(target_image)
  
  
  # shuffle list - to get a more varied output? 
  input_images=input_images1
  random.shuffle(input_images) 
  
  
   
  
  # output 
  output_filename = "mosaic%s.jpg" %(i,)

    
  # re-use any image in input 
  reuse_images = True
  
  # resize the input to fit original image size? 
  resize_input = True
  
  ##### END INPUTS ##### 
  
  print('starting photomosaic creation...') 
    
  # if images can't be reused, ensure m*n <= num_of_images  
  if not reuse_images: 
    if grid_size[0]*grid_size[1] > len(input_images): 
      print('grid size less than number of images') 
      exit() 
    
  # resizing input  
  if resize_input: 
    print('resizing images...') 
    # for given grid size, compute max dims w,h of tiles 
    dims = (int(target_image.size[0]/grid_size[1]),  
            int(target_image.size[1]/grid_size[0]))  
    print("max tile dims: %s" % (dims,)) 
    # resize 
    for img in input_images: 
      img.thumbnail(dims) 
      
  
  # create photomosaic 
  mosaic_image = createPhotomosaic(target_image, input_images, grid_size, reuse_images) 
  im3 = Image.open("frame%s.jpg" %(i,)).resize(mosaic_image.size)
  

  mask = Image.new("L", mosaic_image.size, 80)
  im = Image.composite(im3 ,mosaic_image, mask)
  im.save(output_filename, 'PNG') 


  im2 = cv2.imread("frame%s.jpg" %(i,))
  mask_blur = cv2.GaussianBlur(im2, (3, 3), 0)
  edges = cv2.Canny(mask_blur, 21,21)
  cv2.imwrite("frame%s.jpg" %(i,), edges)

  im21 = Image.open(output_filename)
  edges2=Image.open("frame%s.jpg" %(i,)).resize(im21.size)
  im4 = Image.composite(im3, im21, edges2)


  im4.save(output_filename, 'PNG') 
  

  print("saved output to %s" % (output_filename,)) 
  print('done.') 
  
# Standard boilerplate to call the main() function to begin 
# the program. 
if __name__ == '__main__': 

  # input images 
  print('reading input folder...') 
    
  input_images1 = getImages("../test-data\set1" ) 
  
  # check if any valid input images found   
  if input_images1 == []: 
      print('No input images found . Exiting.') 
      exit() 
      
  cap= cv2.VideoCapture('../dog.mp4')
  out=cv2.VideoWriter('../mosaic_video.avi',0,10,(1000,600))


  """
  k=10
  i=0
  while(cap.isOpened()):
      frameId = cap.get(1) #current frame number
      ret, frame = cap.read()
      if (ret != True):
          break
      if (i % k == 0):
          print '--------------------------------------------begening nb' ,i ,'photo'
          filename = "captions.jpg"
          cv2.imwrite(filename, frame)
          main(filename,input_images1) 
          img = Image.open('mosaic.jpg').resize((1000,600))
          img.save('mosaic.jpg')
          img2=cv2.imread('mosaic.jpg')
          out.write(img2)
      i+=1
      """
  k=5
  i=0
  total_images=[]
  while(cap.isOpened()):
      frameId = cap.get(1) #current frame number
      ret, frame = cap.read()
      if (ret != True):
          break
      if (i % k == 0):
        total_images.append((frame,i))
      i+=1  
  
  def opt_code(img,input_images1):
    main(img,input_images1) 
    
  nb_proc=15
  i=nb_proc
  j=0
  while True:
      if i< len(total_images):
          l2=total_images[j:i]
          Parallel(n_jobs=len(l2))(delayed(opt_code)(img,input_images1) for img in  l2)

      else:
          l2=total_images[j:]
          Parallel(n_jobs=len(l2))(delayed(opt_code)(img,input_images1) for img in  l2)

          break
      i+=nb_proc
      j+=nb_proc
  
  filenames=[]
  for filename in glob.glob('*.jpg'):
        
      #img = cv2.imread(filename)
      filenames.append(filename)
  out=cv2.VideoWriter('../mosaic_video.avi',0,5,(1000,600))
  i=0
  while True:
      bol=False 
      ch="mosaic%s.jpg"%(i,)
      
      for filename in filenames:
            
          if (filename == ch):
              print ch
              img = Image.open(filename).resize((1000,600))
              img.save(filename)
              img2=cv2.imread(filename)
              out.write(img2)
              bol=True
              
      if (bol==False):
          break
      i+=k 
  for filename in glob.glob('*.jpg') :
    os.remove(filename)  
    print filename,"----> deleted" 
    
  print("programme est terminer")
  

