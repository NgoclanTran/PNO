#!/usr/bin/env python

# Initial Date: Oktober 22, 2014
# Last Updated: Oktober 22, 2014
# Team Ijzer 

# import the necessary packages
import numpy as np
import cv2
import cv2.cv as cv

class ImRec:
    'Image recognition class class, using methods from OpenCV.'

    def detectImage(self,filename):

        # load the image
        image = cv2.imread(filename)

        #resize the image
        smallImg = self.resize(image)

        # filter out noise
        im = cv2.medianBlur(smallImg,11)

        # convert to HSV color space
        img = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        
        (colors,colorMask) = self.detectColor(img)
        
        nbColors = len(colors)
        
        # If no color was found ...
        if nbColors == 0: 
            return 0
        
        print 'colors: ',colors
        
        shapes = []
        matches = []
        
        for i in range(nbColors):
            
            dst = self.filterColor(img,colorMask[i])
            
#            cv2.imshow('dst',dst)
#            cv2.waitKey(0)
#            cv2.destroyAllWindows()
            
            imGray = self.grayScale(dst)
            thresh = self.otsuBin(imGray)
            
            (shape, match) = self.detectShape(thresh)
            if len(match) == 0:
                colors.pop(i)
            else:
                matches += match
                shapes += shape
            
        print 'matches: ', matches
        print 'shapes: ', shapes
        
        # If no shapes were found ...
        if len(matches) == 0:
            return 0
            
        bestMatchIndex = np.argmin(matches)
        
        print bestMatchIndex
        
        if matches[bestMatchIndex] > 0.06:
            return 0 # erroneous star detection
        else:
            return colors[bestMatchIndex] +'_'+ shapes[bestMatchIndex] + '.jpeg'
        

    def resize(self,image):
        size = np.shape(image)
        fx = 250.0/size[0]
        return cv2.resize(image,dsize=(0,0),fx=fx,fy=fx,interpolation = cv2.INTER_AREA)
        
        
##    def filterBrown(self,im,boundaries):
##        
##        # create NumPy arrays from the boundaries
##        lower = np.array(boundaries[0], dtype = "uint8")
##        upper = np.array(boundaries[1], dtype = "uint8")
## 
##        # find the colors within the specified boundaries and apply
##        # the mask
##        mask = cv2.inRange(im, lower, upper)
##        mask = cv2.bitwise_not(mask)
##        dst = cv2.bitwise_and(im,im,mask=mask)
##        return dst

    def filterColor(self,im,colorMask):

        dst = cv2.bitwise_and(im,im,mask=colorMask)
        return dst

    def grayScale(self,image):

        return cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    def otsuBin(self,image):
        
        # Otsu's binarization
        # http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html#thresholding
        ret,thresh = cv2.threshold(image,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return thresh
    
    def detectColor(self,image):

        size = np.shape(image)
        m = size[0]
        n = size[1]
        newSize = m*n

        #Define a list of colors and boundaries
        colors = ['red','blue','green','yellow','purple']    # second blue is bluegray

        boundaries = [([0, 127, 178], [8, 178, 255]),
                      ([95, 89, 127], [105, 255, 255]),
                      #([17, 51, 127], [25, 153, 255]),
                      ([25, 150, 120], [35, 235, 255]),
                      ([19, 120, 190], [27, 255, 255]),
                      ([135, 80, 51], [160, 178, 255])]

        amountColor = []
        colorMask = []

        for k in range(len(colors)):

            (lower,upper) = boundaries[k]
            
            # Define the boundaries
            lower = np.array(lower, dtype = "uint8")
            upper = np.array(upper, dtype = "uint8")
            
            colorMask += [cv2.inRange(image, lower, upper)]       
            
            res = np.count_nonzero(colorMask[k])

            amountColor += [(float( res ) / float( newSize ))]

        print 'amountColor: ', amountColor
        if(np.count_nonzero(amountColor)):
            colorindex = [i for i in range(len(amountColor)) if amountColor[i] > 0]
            print 'colorindex: ', colorindex
            mask = [colorMask[i] for i in colorindex]
            color = [colors[i] for i in colorindex]
            return (color, mask)
        
        else:
            return ([],[])

##            if amountColor[colorindex] > 0.02:
##                return (colorindex, colors[colorindex],colorMask[colorindex])


    def detectShape(self, thresh):
        #Find contours
        thresh2 = thresh.copy()
        #http://docs.opencv.org/modules/imgproc/doc/structural_analysis_and_shape_descriptors.html#double matchShapes(InputArray contour1, InputArray contour2, int method, double parameter)
        contours, hierarchy = cv2.findContours(thresh2,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

        # Match Shapes
        shapes = []
        shapeNames = ['circle','square','triangle','star']
        
        for i in range(4):
            filename = str(i) + '.jpg'
            pattern = cv2.imread(filename,0)
            ret, threshFigure = cv2.threshold(pattern, 127, 255,0)
            contoursFigure,hierarchy = cv2.findContours(threshFigure,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
            shapes += [contoursFigure[0]]

        matrix = []
        
        for cnt in contours:
            
            print 'area: ', cv2.contourArea(cnt)            
            
            if cv2.contourArea(cnt) < 1000:
                continue
            
            row = []
            
            for sh in shapes:
                row += [cv2.matchShapes(sh,cnt,3,0.0)]
            
            matrix.append(row)
            
        print 'matrix: ',matrix
        
        if len(matrix) > 0:
            bestMatch = np.argwhere(matrix == np.amin(matrix))
        
            shape = shapeNames[bestMatch[0][1]]
            return ([shape],[matrix[bestMatch[0][0]][bestMatch[0][1]]])
        
        else:
            return ([],[])



##TEST##
#a = ImRec()
#print a.detectImage('brownwall.jpg')
    
