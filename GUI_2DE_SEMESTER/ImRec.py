#!/usr/bin/env python

# Initial Date: Oktober 22, 2014
# Last Updated: April 24, 2015
# Team Ijzer 

# import the necessary packages
import numpy as np
import cv2
import csv

class ImRec:
    '''Image recognition class, using methods from OpenCV.'''

    def __init__(self, colorFile='colors.csv'):

        # Normally, one set of boundaries for every color should suffice
        self.colors = ['red','blue','green','purple']
        self.shapes = ['circle','square','triangle','star']

        # Color boundaries
        self.colorList = list()
        self.colorTree = []
        self.importColors(colorFile)
        #self.boundaries = [([0, 78, 204], [5, 255, 255]),
#                            ([175, 128, 178], [180, 255, 255]),
#                            ([30, 78, 150], [75, 255, 255]),
#                            ([125, 78, 78], [175, 255, 255])]

    def importColors(self,colorFile):
        '''Import colors obtained from test images as [H,S,V]'''
        with open(colorFile, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in spamreader:
                color = row[0]
                row = row[1]
                row = row.split(",")
                self.colorList.append(color)
                hsv = [int(row[0][1:]),int(row[1]),int(row[2][:-1])]
                self.colorTree.append(hsv)
    
    

    def detectImage(self,filename):

        # load the image
        image = cv2.imread(filename)
        
        # resize the image
        img = self.resize(image)
        randNumb = np.random.randint(1,1000)
        #cv2.imshow('img',img)
        cv2.imwrite('img'+str(randNumb)+'.jpg',img)
        #cv2.waitKey(0)
        
        # apply bilateral filtering
        img = self.bilateral(img)
        orig_img = img.copy()
        
        #cv2.imshow('img',img)
        #cv2.imwrite('star1.jpg',img)
        #cv2.waitKey(0)
        
        # add black borders
        # img = self.addBorders(img)                   
        
        # compute laplacian
        laplacian = cv2.Laplacian(img,-1)
        
        #cv2.imshow('img',laplacian)
        #cv2.imwrite('star2.jpg',laplacian)
        #cv2.waitKey(0)        
        
        # convert to grayscale
        im = self.toGrayScale(laplacian) # alternative: img              

        # convert to binary
        (ret,thresh) = self.otsuBin(im)        
        
        # edge detection
        edges = self.findEdges(im,ret)                
        
        #cv2.imshow('img',edges)
        #cv2.imwrite('star3.jpg',edges)
        #cv2.waitKey(0)   
        
        # dilate and erode
        edges = self.dilateAndErode(edges)

        #cv2.imshow('img',edges)
        #cv2.imwrite('star4.jpg',edges)
        #cv2.waitKey(0)        
        
        # detect shape
        (shape,contour) = self.detectShape(edges,img)
        
        # if no shape was found
        if len(shape) == 0:
            return 0
        print 'ImRec.py: shape = '+shape
            
        # draw the found contour; debug reasons
        cv2.drawContours(img, contour,-1,[255, 0, 0],2)
        #cv2.imshow('img',img)
        #cv2.imwrite('star6.jpg',img)
        #cv2.waitKey(0)

        # color constancy algorithm
        img = self.max_white(orig_img)                   
        #cv2.imshow('img',img)
        #cv2.imwrite('red.jpg',img)
        #cv2.waitKey(0)
        
        # build a mask from contour
        (mask,maskLength) = self.buildMask(contour,img)
        if (maskLength == 0):
            return 0
        
        img = cv2.bitwise_and(img,img,mask=mask)        
        
        #cv2.imshow('img',img)
        #cv2.imwrite('star7.jpg',img) 
        #cv2.waitKey(0)        
        
        # detect color
        color = self.detectColor(img,mask)
        if len(color) == 0:
            return 0
        print 'ImRec.py: color = '+color
        if color == "brown":
            return 0
        return color+'_'+shape+'.png'
    
        
    def resize(self,image):
        size = np.shape(image)
        fx = 512.0/size[0]
        im = cv2.resize(image,dsize=(0,0),fx=fx,fy=fx,interpolation=cv2.INTER_AREA)
        return im
        
    def bilateral(self,img):
        for i in range(30): # 3
            #img = cv2.bilateralFilter(img,15,7,9)
            img = cv2.bilateralFilter(img,7,9,7)
        return img
        
    def toGrayScale(self,image):
        return cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        
    def otsuBin(self,image):
        # Otsu's binarization
        # http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html#thresholding
        ret,thresh = cv2.threshold(image,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return (ret,thresh)
    
    def findEdges(self,image,ret):
        return cv2.Canny(image,ret,ret/2,L2gradient=1)
        
    def dilateAndErode(self,image):
        kernel = np.ones((7,7),np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        
    def addBorders(self,image):
        return cv2.copyMakeBorder(image, 2,2,2,2, cv2.BORDER_CONSTANT)
        
    def detectShape(self,edges,img):
        
        # Find contours
        edges2 = edges.copy()
        #http://docs.opencv.org/modules/imgproc/doc/structural_analysis_and_shape_descriptors.html#double matchShapes(InputArray contour1, InputArray contour2, int method, double parameter)
        contours, hierarchy = cv2.findContours(edges2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        
        # Load shape contours
        shapes = []
        shapeNames = self.shapes
    
        for i in range(4):
            filename = str(i) + '.jpg'
            pattern = cv2.imread(filename,0)
            ret, threshPattern = cv2.threshold(pattern, 127, 255,0)
            contoursPattern, hierarchyPattern = cv2.findContours(threshPattern,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
            #contoursPattern = cv2.approxPolyDP(contoursPattern[0],0.001*cv2.arcLength(contoursPattern[0],1),1)            
            shapes += [contoursPattern[0]]
            
        Min = 1 # experimental threshold
        shape = []
        contour = []
        
        for i in range(np.shape(hierarchy)[1]):
        
            cnt = contours[i]
            area = cv2.contourArea(cnt) 
        
            if (area < 2000): #or (area > 12000):
                continue
            
            moments = cv2.moments(cnt)
            #x = moments['m10']/moments['m00']
            y = moments['m01']/moments['m00']
            
            if y < 100:
                continue        
        
            row = []
            for sh in shapes:
                row += [cv2.matchShapes(sh,cnt,1,0.0)]
            
            #row = np.array(row)
            #weights = np.array(self.shapeWeights)
            #row = np.multiply(row,weights)
            #print row            
            
            #cv2.drawContours(img, cnt, -1, [0, 0, 0],0)
            #cv2.imshow('img',img)
            #cv2.waitKey(0)        
        
            bestMatchIdx = np.argmin(row)        
        
            if row[bestMatchIdx] < Min:
                Min = row[bestMatchIdx]
                shape = shapeNames[bestMatchIdx]
                contour = cnt
            
        #print 'min: ',Min
        return (shape,contour)
    
    def max_white(self,nimg):
        if nimg.dtype==np.uint8:
            brightest=float(2**8)
        elif nimg.dtype==np.uint16:
            brightest=float(2**16)
        elif nimg.dtype==np.uint32:
            brightest=float(2**32)
        else:
            brightest=float(2**8)
        nimg = nimg.transpose(2, 0, 1)
        nimg = nimg.astype(np.int32)
        if (nimg[0].max()==0) or (nimg[1].max()==0) or (nimg[2].max()==0):
            return nimg
            
        nimg[0] = np.minimum(nimg[0] * (brightest/float(nimg[0].max())),255)
        nimg[1] = np.minimum(nimg[1] * (brightest/float(nimg[1].max())),255)
        nimg[2] = np.minimum(nimg[2] * (brightest/float(nimg[2].max())),255)
        return nimg.transpose(1, 2, 0).astype(np.uint8)
    
    def buildMask(self,contour,img):
        h, w = img.shape[:2]
        maskLength = 0
        
        mask = np.zeros((h,w,1),dtype=np.uint8)     
    
        for i in range(h):
            row = [cnt for cnt in contour if cnt[0][0] == i]
            if len(row) > 0:
                begin = row[0][0][1]
                end = row[-1][0][1]
                Min = min(begin,end)
                Max = max(begin,end)
                for j in range(Min,Max+1):
                    mask[j,i] = 255
                    maskLength += 1
    
        return (mask,maskLength)

    def detectColor(self,image,mask):

        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Extract dominant hue, saturation and value
        hsv = [0,0,0]
        for i in range(3):
            histr = cv2.calcHist([image],[i],mask,[256],[0,256])
            hsv[i] = np.argmax(histr)

        distance, index = self.query(hsv)
        print 'ImRec.py: distance to NN = ' + str(distance)

        return self.colorList[index]


    def query(self,point):
        i = -1
        Min = 9999999999
        point = np.array(point)
        
        for j in range(len(self.colorTree)):
            dist = np.linalg.norm(np.array(self.colorTree[j])-point)
            if dist < Min:
                i = j
                Min = dist
                
        return (Min,i)
        
#     def detectColor(self,image,maskLength):
# 
#         image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)        
#         
# 
#         #Define a list of colors and boundaries
#         colors = self.colors
#     
#         boundaries = self.boundaries
#     
#         # amount of color in image for every color
#         amountColor = []
#     
#         for k in range(len(colors)):
#     
#             (lower,upper) = boundaries[k]
#             
#             # Define the boundaries
#             lower = np.array(lower, dtype = "uint8")
#             upper = np.array(upper, dtype = "uint8")
#             
#             colorMask = cv2.inRange(image, lower, upper)       
#             res = np.count_nonzero(colorMask)
#             amountColor += [(float( res ) / float( maskLength ))]
#     
#         #print 'amountColor: ', amountColor
#         #amountColor = np.array(amountColor)
#         #weights = np.array(self.colorWeights)
#         #amountColor = np.multiply(amountColor,weights)
#         
#         if(np.count_nonzero(amountColor)):
#             colorindex = np.argmax(amountColor)
#             color = colors[colorindex]
#             return color
#         
#         else:
#             return ''

##            if amountColor[colorindex] > 0.02:
##                return (colorindex, colors[colorindex],colorMask[colorindex])

# i = ImRec()
# #print i.detectImage('image.jpg')
# for k in range(3,10):
#     result = i.detectImage('im'+str(k)+'.jpg')
#      
#     print result
