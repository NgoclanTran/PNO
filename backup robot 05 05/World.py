# -*- coding: utf-8 -*-
"""
Created on Mon Nov  3 17:03:46 2014

@author: Team Ijzer
"""
import re

class World:
    
    def __init__(self,filename='kaart.txt'):
        self.goal = None
        
        # Define the possible tiles in this world
        self.TILES = {'0N':[0,0,0,0],
         '0S':[0,0,0,0],
         '0W':[0,0,0,0],
         '0E':[0,0,0,0],
         '1N':[1,0,0,0],
         '1E':[0,1,0,0],
         '1S':[0,0,1,0],
         '1W':[0,0,0,1],
         '2N':[0,1,0,1],
         '2E':[1,0,1,0],
         '2S':[0,1,0,1],
         '2W':[1,0,1,0],
         '3N':[1,0,0,1],
         '3E':[1,1,0,0],
         '3S':[0,1,1,0],
         '3W':[0,0,1,1],
         '4N':[1,1,0,1],
         '4E':[1,1,1,0],
         '4S':[0,1,1,1],
         '4W':[1,0,1,1],
         '5N':[0,1,0,1],
         '5E':[1,0,1,0],
         '5S':[0,1,0,1],
         '5W':[1,0,1,0],
         '6N':[0,1,0,1],
         '6E':[1,0,1,0],
         '6S':[0,1,0,1],
         '6W':[1,0,1,0],
         '7N':[0,1,0,1],
         '7E':[1,0,1,0],
         '7S':[0,1,0,1],
         '7W':[1,0,1,0]}
        
        # Extract a matrix representing this world's map from the given filename
        self.setupMapFrom(filename)
        

    def setGoal(self, goal):
        # Set up the goal of the world
        self.determineGoal(goal)
        
        # give every element in this world's map an associated heuristic value 
        self.hmap = self.getHeuristicMap(goal)
        
        
    def setupMapFrom(self,filename):
        
        f = open(filename, 'r')
        
        # Strip the newlines
        f = [line.rstrip('\n') for line in f]        
        
        # Create a list to store the file's characters
        temp = list()       
        
        for line in f:
            if not((line == '') or (line[0] == '#')): # Remove empty lines and comments
                temp.extend(line.split())

        # Save this world's dimensions
        self.breadth = int(temp.pop(0))
        self.depth = int(temp.pop(0))
        print "breadth: " + str(self.breadth)
        print "depth: " + str(self.depth)
        
        Map = list()
        
        for i in range(self.depth):
            row = list()
            for j in range(self.breadth):
                row.append(temp.pop(0))
            Map.append(row)

        self.map = Map

        self.images = dict()
        self.unknownimagepositions = list()
        sub = 'images/'
        
        for line in temp:
            i = line.find(sub)
            if i > 0:
                name = line[i+len(sub):]
                posTile = int(line[0:i-1])
                position = (posTile/self.breadth, posTile%self.breadth)
                orientation = line[i-1]
                self.images[name] = [position,orientation]
            else:
                i = line.find('?')
                posTile = int(line[0:i])
                position = (posTile/self.breadth, posTile%self.breadth)
                self.unknownimagepositions.append(position)
                
    def determineGoal(self, goal):
        if (type(goal) is tuple):
            self.goal = goal
        else: 
            self.goal = self.images.get(goal)[0]
        
    def getHeuristicMap(self,goal):
        
        # Use the manhattan distance as a heuristic value for every tile
        hmap = list()
        
        for i in range(self.depth):
            row = list()
            for j in range(self.breadth):
                row.append( abs(i-goal[0]) + abs(j-goal[1]) )
            hmap.append(row)
            
        return hmap

    def getHeuristicForPath(self,path):
        
        # Heuristic value for path is equal to the heuristic value of its last node
        end = path[-1]
        
        return self.hmap[end[0]][end[1]]
        
    def doGreedySearch(self,start,goal):

        Queue = [[start]]
        result = self.goalReached(Queue,goal)
        if (len(result) > 0):
            return result
           
        while (len(Queue) > 0):
            
            firstPath = Queue.pop(0)
            newPaths = self.createPathsToChildrenFrom(firstPath)

            # Look for effective new paths
            if (len(newPaths) > 0):
                # Look for goal node
                result = self.goalReached(newPaths,goal)
                if (len(result) > 0):
                    return result
                else:
                    # Add the new paths and sort the entire queue by heuristic
                    Queue.extend(newPaths)
                    Queue = self.sortQueue(Queue)
            
            '''
            The robot should still move to the first path of the new sorted (or the result) queue before continuing 
            '''
    
    def createPathsToChildrenFrom(self,path):       
        
        # List eventually containing all paths to children
        paths = list()
        
        # End node of the given path
        end = path[-1]
        # Paths appended with new paths to existing neighbours of the end node
        for i in [-1,1]:
            new = ( end[0]+i, end[1])
            if not(new[0] in range(self.depth)):
                continue
            elif self.wallBetween(end,new): # Reject the new paths with walls
                continue
            elif (new in path): # Reject the new paths with loops
                continue
            elif (self.map[new[0]][new[1]][0] == '0') and (not(self.zeroWithWall(new))):
                continue
            else:
                temp = path + [new]
                paths.append(temp)
        
        # Paths appended with new paths to existing neighbours of the end node
        for j in [-1,1]:
            new = ( end[0], end[1]+j)
            if not(new[1] in range(self.breadth)):
                continue
            elif self.wallBetween(end,new): # Reject the new paths with walls
                continue
            elif (new in path): # Reject the new paths with loops
                continue
            elif (self.map[new[0]][new[1]][0] == '0') and (not(self.zeroWithWall(new))):
                continue
            else:
                temp = path + [new]
                paths.append(temp)
        
        return paths

    def zeroWithWall(self,position):
        
        for i in [-1,1]:
            neighbour = ( position[0]+i, position[1] )
            if not(neighbour[0] in range(self.depth)):
                continue
            else:
                n = self.map[neighbour[0]][neighbour[1]]
                if(self.TILES.get(n)[1] or self.TILES.get(n)[3]):
                    return 1
        for j in [-1,1]:
            neighbour = ( position[0], position[1]+j )
            if not(neighbour[1] in range(self.breadth)):
                continue
            else:
                n = self.map[neighbour[0]][neighbour[1]]
                if(self.TILES.get(n)[0] or self.TILES.get(n)[2]):
                    return 1

        return 0

                
    def wallBetween(self,parent,child):
        # Check whether there is a wall between the specified parent and its child
    
        walls = self.TILES.get(self.map[parent[0]][parent[1]])
        
        if (child[0] < parent[0]): # N
            return walls[0]
        elif (child[1] > parent[1]): # E
            return walls[1]
        elif (child[0] > parent[0]): # S
            return walls[2]
        else: # W
            return walls[3]
    
    def sortQueue(self,Queue):
        # We use selection sort for now, this could be speeded up later on

        for i in range(len(Queue)):
            minHeur = self.getHeuristicForPath(Queue[i])
            swap = i
            for j in range(i,len(Queue)):
                newHeur = self.getHeuristicForPath(Queue[j])
                if (newHeur < minHeur):
                    minHeur = newHeur
                    swap = j
            temp = Queue[swap]
            Queue[swap] = Queue[i]
            Queue[i] = temp      
 
        return Queue
        
    def goalReached(self,paths, goal):
        
        for path in paths:
            if goal in path:
                return path
        
        return []

    def checkImagePosition(self, position):
        for imagePosition in self.images.values():
            if (imagePosition[0] == position):
                return imagePosition[1]
        return 0

    def checkCommonWall(self,old,new):
    
        wallsOld = self.TILES.get(self.map[old[0]][old[1]])
        wallsNew = self.TILES.get(self.map[new[0]][new[1]])
        wallList = []

        if (old[0] == new[0]):
            if (wallsOld[0] == wallsNew[0]):
                if (wallsOld[0]):
                    wallList.append('N')
                    #return 'N'
            if (wallsOld[2] == wallsNew[2]):
                if (wallsOld[2]):
                    wallList.append('S')
                    #return 'S'
        if (old[1] == new[1]):
            if (wallsOld[1] == wallsNew[1]):
                if (wallsOld[1]):
                    wallList.append('E')
                    #return 'E'
            if (wallsOld[3] == wallsNew[3]):
                if (wallsOld[3]):
                    wallList.append('W')
                    #return 'W'

        return wallList
    #return 0
    
    def checkTileForImage(self,orientation,position):
        tileType = self.map[position[0]][position[1]]
        orientations = ['N','E','S','W']
        robotOrientation = orientations.index(orientation)
        tileOrientation = orientations.index(tileType[1])
        delta = (tileOrientation - robotOrientation)%4
        
        tileType = tileType[0] + orientations[delta]
        
        return self.TILES.get(tileType)
        

        
    def getTileFromImage(self, image):

        if image in self.images.keys():
            return (image, self.images.get(image))
        else:
            return []
            
##    def getTileFromImageTrav(self, image, position):
##        
##        images = list()
##        # First, check all the images at the given position.
##        for im, pos in self.images.items():
##            
##            if pos[0] == position:
##                images.append(im)
##                
##        resultForNow = self.checkSimilar(images, image)
##
##        return resultForNow
##            
##

    def checkSimilar(self, images, image):

        if image in images:
            
            return (image, self.images.get(image))

        else:

            imageSplit = image.split("_")
            color = imageSplit[0]
            figure = imageSplit[1]
            
            for i in images:
                iSplit = i.split("_")
                iColor = iSplit[0]
                iFigure = iSplit[1]

                print color, figure, iFigure

                if iFigure == figure:

                    if color == 'blue' and iColor == 'purple':
                        return (i, self.images.get(i))
                    elif color == 'purple' and iColor == 'blue':
                        return (i, self.images.get(i))
                    
            for i in images:
                iSplit = i.split("_")
                iColor = iSplit[0]
                iFigure = iSplit[1]
                
                if iColor == color:

                    if figure == 'square.jpeg' and iFigure == 'triangle.jpeg':
                        return (i, self.images.get(i))
                    if figure == 'star.jpeg' and iFigure == 'triangle.jpeg':
                        return (i, self.images.get(i))

            return []

##    def getWeightsForImageFrom(self,position):
##
##        paths = list()
##        pathsToChildren = self.createPathsToChildrenFrom(position)
##        position = position[0] # we don't need the given position as a list anymore
##
##        for path in pathsToChildren:
##            paths.append(path[-1])
##        
##        print paths     
##        
##        weights = dict()
##        
##        for im, pos in self.images.items():
##            print pos[0]
##            
##            if pos[0] == position:
##                print "yes"
##                (color,shape) = self.extractFromImage(im)
##                print color,shape
##                if color in weights.keys():
##                    weights[color] += 5.0
##                else:
##                    weights[color] = 5.0
##                if shape in weights.keys():
##                    weights[shape] *= 0.1
##                else:
##                    weights[shape] = 0.1
##            
##            elif pos[0] in paths:
##                (color,shape) = self.extractFromImage(im)
##                if color in weigths.keys():
##                    weights[color] += 2.0
##                else:
##                    weights[color] = 2.0
##                if shape in weights.keys():
##                    weights[shape] *= 0.5
##                else:
##                    weights[shape] = 0.5
##        
##        return weights
##        
##        
##    def extractFromImage(self,image):
##        split = image.split("_")
##        color = split[0]
##        shape = split[1]
##        shape = shape.split(".")
##        shape = shape[0]
##        return (color,shape)

    def getUnknownImagePositions(self):
        return self.unknownimagepositions[:]
    
    # pos is je eigen huidige positie, positionList is de volledige string die
    # de server doorstuurt.
    def determineNearestGoal(self, pos, positionList):
        print "DNG, positionList: " + str(positionList)
        paths = []
        xMax = self.breadth
        if (len(self.getUnknownImagePositions()) == 1):
            return self.doGreedySearch(pos,self.getUnknownImagePositions())
        elif (len(self.getUnknownImagePositions()) == 0):
            return []
        else:
            paths = self.calculatePaths(pos)
            gesplitsteLijst = positionList.split()
            
            for i in range(0,len(paths)):
                print paths[i]
                shortestPath = True
                destinationPos = paths[i][-1]
                k = 0
                while (k < len(gesplitsteLijst)):
                    team = gesplitsteLijst[k]
                    if (team != "ijzer"):
                        tegelNr = int(gesplitsteLijst[k+1][:-1])
                        x = (tegelNr/xMax)
                        y = (tegelNr%xMax)
                        posOther = (x,y)
                        print posOther
                        print self.getPathLength(posOther,destinationPos)
                        if (len(paths[i]) > self.getPathLength(posOther, destinationPos)):
                            shortestPath = False
                            break
                    k += 2
                    
                if shortestPath:

                    self.goal = paths[i][-1]
                    return paths[i]

            self.goal = paths[i][-1]
            return paths[i]


    def checkPathForEnemies(self,path,positionsList):
        xMax = self.breadth
        print "CPFE, positionslist: " + str(positionsList)
        gesplitsteLijst = positionsList.split()
        destinationPos = path[-1]
        if not(destinationPos in self.unknownimagepositions):
            return False
        
        k = 0
        while (k < len(gesplitsteLijst)):
            team = gesplitsteLijst[k]
            if (team != "ijzer"):
                tegelNr = int(gesplitsteLijst[k+1][:-1])
                x = (tegelNr/xMax)
                y = (tegelNr%xMax)
                posOther = (x,y)
                
                if (len(path) > self.getPathLength(posOther, destinationPos)):
                    return False
            k += 2
            
        return True
      
      
    def updateSymbols(self, discoveredSymbols):
        symbolList = discoveredSymbols
        updatedSymbols = str()
        
        r = re.compile("([A-Z0-9]+)([a-z_]+)")
        print 'symbolList', symbolList

        for i in symbolList:
            m = r.match(i)
            posOr = m.group(1) 
            image = m.group(2) + ".png"
            print 'discovered image: ',image
            print 'images keys: ' + str(self.images.keys())
            print 'unknownimagepositions: '+ str(self.unknownimagepositions)
            if image in self.images.keys(): # Updated earlier 
                pass
            else:
                pos = int(posOr[0:len(posOr)-1])
                xPosition = pos/self.breadth
                yPosition = pos%self.breadth
                orientation = posOr[-1]
                print 'orientationOfDiscoveredImage', orientation
                position = (xPosition,yPosition)
                
                self.images[image] = [position,orientation]
                print 'imagesAfterUpdate: '
                print self.images
                updatedSymbols += (posOr + ' ' + image + ' ')

                if position in self.unknownimagepositions:
                    self.unknownimagepositions.remove(position)

        return updatedSymbols

                
    def removeFromUnknownImagePositions(self, position):
        self.unknownimagepositions.remove(position)    
                 
        
    def getPathLength(self, pos, destinationPos):
        self.setTempGoal(destinationPos)
        temp = self.doGreedySearch(pos, self.tempGoal)
        return len(temp)-1
        
    
    def calculatePaths(self, pos):
        paths = []
        for i in self.getUnknownImagePositions():
            self.setTempGoal(i)
            temp = self.doGreedySearch(pos, self.tempGoal)
            paths.append(temp)
        paths.sort(key = lambda s: len(s))
        return paths
    
    
    def setTempGoal(self, goal):
        self.tempGoal = goal
        
        # give every element in this world's map an associated heuristic value 
        self.hmap = self.getHeuristicMap(goal)

    def getImageFromTile(self, tile):
        for im, pos in self.images.items():
            if pos == tile:
                return im
        return 'NO IMAGE ON THIS TILE'
    
#world = World('kaart.txt','blue_circle.jpeg')
#print world.images
#result = world.getWeightsForImageFrom([(0,1)])
#print result

world = World('kaart.txt')
world.setGoal((5,4))
print world.doGreedySearch((5,4),(1,1))

        
        
        
        
        
