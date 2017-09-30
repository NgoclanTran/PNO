#!/usr/bin/env python

# Initial Date: Oktober 22, 2014
# Last Updated: April 24, 2014
# Team Ijzer 

# import the necessary packages
import numpy as np
import cv2
import cv2.cv as cv

class ImRec:
    '''Image recognition class, using methods from OpenCV.
    Possible improvements:
    - self.boundaries
    - if (area < 1000): #or (area > 12000):
        continue
        in detectShape()
    - ...
    '''

    def __init__(self):

        # Normally, one set of boundaries for every color should suffice
        self.colors = ['red','blue','green','purple']
        #self.colors = ['red','red','blue','blue','green','purple']
        
        #self.colorWeights = len(self.colors)*[1.0]
        
        self.shapes = ['circle','square','triangle','star']
        
        #self.shapeWeights = len(self.shapes)*[1.0]

        self.boundaries = [([0, 78, 204], [5, 255, 255]),
                           ([175, 128, 178], [180, 255, 255]),
                           ([30, 78, 150], [75, 255, 255]),
                           ([125, 78, 78], [175, 255, 255])]

        # Used for calibration
        self.boundDict = {
            
            'red': [([0, 78, 204], [5, 255, 255]),
                    ([175, 128, 178], [180, 255, 255])],
            
            'blue': [([175, 128, 178], [180, 255, 255]),
                     ([95, 78, 102], [125, 255, 255])],

            'green': [([30, 78, 150], [75, 255, 255])],

            'yellow': [([27, 78, 178], [30, 255, 255]),
                       ([22, 178, 178], [27, 255, 255])],

            'puprle': [([125, 78, 78], [175, 255, 255])]

            }

##    def setWeights(self,weights):
##        
##        self.colorWeights = len(self.colors)*[1.0]        
##        self.shapeWeights = len(self.shapes)*[1.0]        
##        
##        for k in weights.keys():
##            if k in self.colors:
##                for i in len(self.colors):
##                    if self.colors(i) == k:
##                        self.colorWeights[i] = weights.get(k)
##            
##            elif k in self.shapes:
##                i = self.shapes.index(k)
##                self.shapeWeights[i] = weights.get(k)

    def calibrate(self,color,testCases):
        '''color is a string specifying the name of the color to calibrate,
        testCases is a range of integers X specifying the test cases testX.jpg available'''

        'Starting calibration for ' + color + '...'

        # Save current settings
        colors = self.colors
        boundaires = self.boundaries

        # Get info for this color
        colorIndex = self.colors.index(color)
        colorBoundaries = self.boundDict[color]

        # Do calibration
        self.colors = [color]
        results = list()
        for b in colorBoundaries:
            
            print 'Trying ' + str(b) + '...'
            
            self.boundaries = [b]
            nbSuccess = 0
            for k in testCases:
                res = self.detectImage('test'+str(k)+'.jpg')
                if res:
                    nbSuccess += 1
            result.append(nbSucces)

            print str(nbSuccess) + ' of ' + len(testCases) + ' recognised.'

        bestResult = np.argmax(result)

        # Update attributes after calibration
        self.colors = colors
        self.boundaries = boundaries
        boundaries[colorIndex] = colorBoundaries[bestResult]

        print 'Calibration finished.'
        
        return

    def detectImage(self,filename):

        # load the image
        image = cv2.imread(filename)
        
        # resize the image
        img = self.resize(image)
        
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
            
        # draw the found contour; debug reasons
        #cv2.drawContours(img, contour,-1,[255, 0, 0],2)
        #cv2.imshow('img',img)
        #cv2.imwrite('star6.jpg',img)
        #cv2.waitKey(0)

        # color constancy algorithm
        img = self.max_white(orig_img)                   
        
        # build a mask from contour
        (mask,maskLength) = self.buildMask(contour,img)
        if (maskLength == 0):
            return 0
        
        img = cv2.bitwise_and(img,img,mask=mask)        
        
        #cv2.imshow('img',img)
        #cv2.imwrite('star7.jpg',img) 
        #cv2.waitKey(0)        
        
        # detect color
        color = self.detectColor(img,maskLength)
        
        if len(color) == 0:
            return 0
        
        print 'ImRec.py: ',color+'_'+shape+'.png'
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
        
        # Find corners
        corners = cv2.goodFeaturesToTrack(edges,20,0.01,5)
        
#        # Add polygonal approximation for convex contours
#        for i in range(np.shape(hierarchy)[1]):
#            cnt = contours[i]
#            
#            #cv2.drawContours(img, cnt, -1, [0, 0, 255],1)
#            #cv2.imshow('img',img)
#            #cv2.waitKey(0)             
#            
#            #if hierarchy[0,i,3] == -1:
#            #    continue       
#        
#            self.addApprox(cnt,corners,edges,img)
#            #self.addConvexHull(cnt,corners,edges,img)
#            #cv2.imshow('img',edges)
#            #cv2.waitKey(0)
#        
#        cv2.imshow('img',edges)
#        cv2.waitKey(0)        
#        
#        # Find contours again now
#        edges2 = edges.copy()
#        #http://docs.opencv.org/modules/imgproc/doc/structural_analysis_and_shape_descriptors.html#double matchShapes(InputArray contour1, InputArray contour2, int method, double parameter)
#        contours, hierarchy = cv2.findContours(edges2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        
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
            #cnt = cv2.approxPolyDP(cnt,0.001*cv2.arcLength(cnt,1),1)
            area = cv2.contourArea(cnt) 
        
            #if hierarchy[0,i,3] == -1:
            #    continue

            if (area < 1000): #or (area > 12000):
                continue        
        
            row = []
            for sh in shapes:
                row += [cv2.matchShapes(sh,cnt,1,0.0)]
            
            #row = np.array(row)
            #weights = np.array(self.shapeWeights)
            #row = np.multiply(row,weights)
            print row            
            
            cv2.drawContours(img, cnt, -1, [0, 0, 0],0)
            cv2.imshow('img',img)
            cv2.waitKey(0)        
        
            bestMatchIdx = np.argmin(row)        
        
            if row[bestMatchIdx] < Min:
                Min = row[bestMatchIdx]
                shape = shapeNames[bestMatchIdx]
                contour = cnt
            
        print 'min: ',Min
        return (shape,contour)
        
    def addConvexHull(self,cnt,corners,dst,img):        
        
        cornersForThisContour = []     
        
        for corner in corners:
            if (abs(cv2.pointPolygonTest(cnt, (int(corner[0][0]),int(corner[0][1])), 1)) < 5):
                cornersForThisContour.append([[int(corner[0][0]),int(corner[0][1])]])
                img[int(corner[0][1]),int(corner[0][0])]=[0,0,0]
    
        cornersForThisContour = np.array(cornersForThisContour)

        if True: #cv2.isContourConvex(cornersForThisContour):
            print 'convex'
            #poly = cv2.approxPolyDP(cornersForThisContour,5,0)
            hull = cv2.convexHull(cornersForThisContour, returnPoints = False)
            defects = cv2.convexityDefects(cnt,hull)
            print defects
            hull = cv2.convexHull(cornersForThisContour, 1)
    
            #for corner in poly:
            for i in range(-1,np.shape(hull)[0]-1):
                x0 = hull[i][0][0]
                y0 = hull[i][0][1]
                x1 = hull[i+1][0][0]
                y1 = hull[i+1][0][1]
                cv2.line(dst,(x1,y1),(x0,y0),255,1)
        
        #cv2.imshow('img',dst)
        #cv2.waitKey(0) 
        
    def addApprox(self,cnt,corners,dst,img):        
        
        cornersForThisContour = []     
        
        for corner in corners:
            if (abs(cv2.pointPolygonTest(cnt, (int(corner[0][0]),int(corner[0][1])), 1)) < 5):
                cornersForThisContour.append([[int(corner[0][0]),int(corner[0][1])]])
                img[int(corner[0][1]),int(corner[0][0])]=[0,0,0]
                
        #cv2.imshow('img',img)
        #cv2.waitKey(0)       
        
        cornersForThisContour = np.array(cornersForThisContour)

                
        if len(cornersForThisContour) <= 0:
            return
        
        poly = cv2.approxPolyDP(cornersForThisContour,5,1)
        
        poly = self.sortContour(poly)        
        
        x0 = poly[0][0][0]
        X0 = x0
        y0 = poly[0][0][1]
        Y0 = y0
        poly = np.delete(poly,0,0)
        
        while np.shape(poly)[0] > 0:
            x1 = poly[0][0][0]
            y1 = poly[0][0][1]
            cv2.line(dst,(x1,y1),(x0,y0),255,2)
            (x0,y0) = (x1,y1)
            poly = np.delete(poly,0,0)
            #cv2.imshow('img',dst)
            #cv2.waitKey(0)
        
        cv2.line(dst,(X0,Y0),(x0,y0),255,2)
      
    def sortContour(self,contour):
        
        for i in range(np.shape(contour)[0]-1):
            
            x0 = contour[i][0][0]
            y0 = contour[i][0][1]

            x1 = contour[i+1][0][0]
            y1 = contour[i+1][0][1]
            
            minDist = self.EuclideanDist((x0,y0),(x1,y1))            
            
            swap = i+1
            
            for j in range(i+2,np.shape(contour)[0]):

                x1 = contour[j][0][0]
                y1 = contour[j][0][1]                
                
                newDist = self.EuclideanDist((x0,y0),(x1,y1))
                
                if (newDist < minDist):
                    minDist = newDist
                    swap = j         
            
            temp = contour[swap][0].copy()
            contour[swap][0] = contour[i+1][0].copy()
            contour[i+1][0] = temp  
 
        return contour       
    
    def EuclideanDist(self,start,end):
        return np.sqrt(np.square(end[0]-start[0])+np.square(end[1]-start[1]))
    
    def max_white(self,nimg):
        if nimg.dtype==np.uint8:
            brightest=float(2**8)
        elif nimg.dtype==np.uint16:
            brightest=float(2**16)
        elif nimg.dtype==np.uint32:
            brightest=float(2**32)
        else:
            brightest==float(2**8)
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
        
    def detectColor(self,image,maskLength):

        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)        
        
        m, n = np.shape(image)[:2]

        #Define a list of colors and boundaries
        colors = self.colors
    
        boundaries = self.boundaries
    
        # amount of color in image for every color
        amountColor = []
    
        for k in range(len(colors)):
    
            (lower,upper) = boundaries[k]
            
            # Define the boundaries
            lower = np.array(lower, dtype = "uint8")
            upper = np.array(upper, dtype = "uint8")
            
            colorMask = cv2.inRange(image, lower, upper)       
            res = np.count_nonzero(colorMask)
            amountColor += [(float( res ) / float( maskLength ))]
    
        print 'amountColor: ', amountColor
        #amountColor = np.array(amountColor)
        #weights = np.array(self.colorWeights)
        #amountColor = np.multiply(amountColor,weights)
        
        if(np.count_nonzero(amountColor)):
            colorindex = np.argmax(amountColor)
            color = colors[colorindex]
            return color
        
        else:
            return ''

##            if amountColor[colorindex] > 0.02:
##                return (colorindex, colors[colorindex],colorMask[colorindex])

##i = ImRec()
###print i.detectImage('image.jpg')
##for k in range(58,60):
##    result = i.detectImage('IMG'+str(k)+'.jpg')
    
    #print result
