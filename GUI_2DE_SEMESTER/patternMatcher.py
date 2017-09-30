import makeMapV2
from Tile import Tile
## input van ROBOT :
## lijst van tuppels (Movement, TileType en Orientation)
## example: [(F,1E),(B,2E)]
## movement kan B,F,L,R
class patternMatcher():
    global nmbMoves
    nmbMoves = 0
    global mapMatrix
    global possiblePositions
    global possibleSolutions
    possibleSolutions = []
    possiblePositions = []
    mapMatrix = makeMapV2.getListOfMapItems()
    global tiles
    tiles = {'0N':[0,0,0,0],
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
    def printTiles(self, tile ):
        print tiles.get(tile)

    def addTile(self, tileType, orientation, move = ""):
        global nmbMoves
        global possibleSolutions
        
        
        #FIND POSITION IN MATRIX
        #position = ...
        if (len(possibleSolutions) == 0):
            self.getAllTilesWithType(tileType,orientation)
        elif(nmbMoves == 1):
            possibleNewSolutions = []
            ## tmp list for new path
            for x in possibleSolutions:
                #print x.getPosition()
                #print x.getAngle()
                #print x.getTileType()
                #print x.getOrientation()
                angle = x.getAngle()
                absoluteOrientation = self.determineOrientation(orientation, angle)
                #print absoluteOrientation
                possibleNewSolutions.extend(self.calculateNewPaths1(x, tileType, absoluteOrientation))
                #print possibleNewSolutions
                ## calculate possible new paths, taking in account -> example: type 2-> N or S same
                ## add in tmp list for new path

            # possibleSolutions = tmpList
            possibleSolutions = possibleNewSolutions
            #print nmbMoves
        else:
            possibleNewSolutions = []
            for x in possibleSolutions:
                angle = x.getAngle()
                absoluteOrientation = self.determineOrientation(orientation, angle)
                possibleNewSolutions.extend(self.calculateNewPaths2(x, tileType, absoluteOrientation, move))
            
            possibleSolutions = possibleNewSolutions
            
        nmbMoves += 1
##        for x in possibleSolutions:
##            if(not(x.getPrevious() == None)):
##                print x.getPosition()
##                print x.getPrevious().getPosition()
##                print "-----------------------"
        for x in possibleSolutions:
            print x.getPosition()
            print x.getTileType()
            print x.getOrientation()
        if(len(possibleSolutions) == 1):
            lastTile = possibleSolutions[0]
            while(True):
                if(not(lastTile.getPrevious == None)):
                    if(lastTile.getPrevious().getPrevious() == None):
                        neededOrientation = self.calculateOrientation(lastTile)
                        oplossingsPositie = possibleSolutions[0].getPosition()
                        oplossingsOrientatie = neededOrientation
                        self.resetPatternMatcher()
                        return(oplossingsPositie, oplossingsOrientatie)
                    else:
                        lastTile = lastTile.getPrevious()
                else:
                    return (possibleSolutions[0].getPosition(),"")
        elif (len(possibleSolutions) == 0):
            self.resetPatternMatcher()
            return (False, "RESET")
        
        else:
            return (False,"")

        if (len(possibleSolutions) == 0):
            print "nooit opgeroepen"
            self.resetPatternMatcher()
        

    def resetPatternMatcher(self):
        global nmbMoves
        nmbMoves = 0
        global mapMatrix
        global possiblePositions
        global possibleSolutions
        possibleSolutions = []
        possiblePositions = []
    def calculateNewPaths2(self, previousTile, newTileType, ao, move):
        newPaths = []
        orientationRobot = self.calculateOrientation(previousTile)
        #print "print orientation robot: " + orientationRobot

        
        if(orientationRobot =="N"):
            if(move == "r"):
                coordX = previousTile.getPosition()[0]
                coordY = previousTile.getPosition()[1]
                if(self.isValidCoordY(coordY+1)):
                    tileOnMap = (mapMatrix[coordX])[coordY+1]
                    orientationTileOnMap = tileOnMap[-1]
                    typeTileOnMap = tileOnMap[:-1]
                    if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
                        if((ao == "S" or ao == "N")and(orientationTileOnMap == "S" or orientationTileOnMap == "N") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                           tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY+1), previousTile.getAngle(),previousTile)
                           newPaths.append(tile)
                        elif((ao == "E" or ao == "W")and(orientationTileOnMap == "E" or orientationTileOnMap == "W") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                           tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY+1), previousTile.getAngle(),previousTile)
                           newPaths.append(tile)
                        
                    elif(typeTileOnMap == newTileType and orientationTileOnMap == ao):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY+1), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
                   
                        
                    
            elif(move == "l"):
                coordX = previousTile.getPosition()[0]
                coordY = previousTile.getPosition()[1]
                if(self.isValidCoordY(coordY-1)):
                    tileOnMap = (mapMatrix[coordX])[coordY-1]
                    orientationTileOnMap = tileOnMap[-1]
                    typeTileOnMap = tileOnMap[:-1]

                    if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
                        if((ao == "S" or ao == "N")and(orientationTileOnMap == "S" or orientationTileOnMap == "N") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY-1), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                        elif((ao == "E" or ao == "W")and(orientationTileOnMap == "E" or orientationTileOnMap == "W") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY-1), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                    elif(typeTileOnMap == newTileType and orientationTileOnMap == ao):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY-1), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)

                        
            elif(move == "f"):
                coordX = previousTile.getPosition()[0]
                coordY = previousTile.getPosition()[1]
                if(self.isValidCoordX(coordX-1)):
                    tileOnMap = (mapMatrix[coordX-1])[coordY]
                    orientationTileOnMap = tileOnMap[-1]
                    typeTileOnMap = tileOnMap[:-1]
                    if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
                        if((ao == "S" or ao == "N")and(orientationTileOnMap == "S" or orientationTileOnMap == "N") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX-1,coordY), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                        elif((ao == "E" or ao == "W")and(orientationTileOnMap == "E" or orientationTileOnMap == "W") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX-1,coordY), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                    elif(typeTileOnMap == newTileType and orientationTileOnMap == ao):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX-1,coordY), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
            else:
                coordX = previousTile.getPosition()[0]
                coordY = previousTile.getPosition()[1]
                if(self.isValidCoordX(coordX+1)):
                    tileOnMap = (mapMatrix[coordX+1])[coordY]
                    orientationTileOnMap = tileOnMap[-1]
                    typeTileOnMap = tileOnMap[:-1]
                    if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
                        if((ao == "S" or ao == "N")and(orientationTileOnMap == "S" or orientationTileOnMap == "N") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX+1,coordY), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                        elif((ao == "E" or ao == "W")and(orientationTileOnMap == "E" or orientationTileOnMap == "W") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX+1,coordY), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                    elif(typeTileOnMap == newTileType and orientationTileOnMap == ao):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX+1,coordY), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
                
        elif (orientationRobot == "S"):
            if(move == "r"):
                coordX = previousTile.getPosition()[0]
                coordY = previousTile.getPosition()[1]
                if(self.isValidCoordY(coordY-1)):
                    tileOnMap = (mapMatrix[coordX])[coordY-1]
                    orientationTileOnMap = tileOnMap[-1]
                    typeTileOnMap = tileOnMap[:-1]
                if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
                    if((ao == "S" or ao == "N")and(orientationTileOnMap == "S" or orientationTileOnMap == "N") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY-1), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
                    elif((ao == "E" or ao == "W")and(orientationTileOnMap == "E" or orientationTileOnMap == "W") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY-1), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
                elif(typeTileOnMap == newTileType and orientationTileOnMap == ao):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY-1), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
            elif(move == "l"):
                coordX = previousTile.getPosition()[0]
                coordY = previousTile.getPosition()[1]
                if(self.isValidCoordY(coordY+1)):
                    tileOnMap = (mapMatrix[coordX])[coordY+1]
                    orientationTileOnMap = tileOnMap[-1]
                    typeTileOnMap = tileOnMap[:-1]
                    if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
                        if((ao == "S" or ao == "N")and(orientationTileOnMap == "S" or orientationTileOnMap == "N") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY+1), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                        elif((ao == "E" or ao == "W")and(orientationTileOnMap == "E" or orientationTileOnMap == "W") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY+1), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                    elif(typeTileOnMap == newTileType and orientationTileOnMap == ao):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY+1), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
            elif(move == "f"):
                coordX = previousTile.getPosition()[0]
                coordY = previousTile.getPosition()[1]
                if(self.isValidCoordX(coordX+1)):
                    tileOnMap = (mapMatrix[coordX+1])[coordY]
                    orientationTileOnMap = tileOnMap[-1]
                    typeTileOnMap = tileOnMap[:-1]
                    if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
                        if((ao == "S" or ao == "N")and(orientationTileOnMap == "S" or orientationTileOnMap == "N") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX+1,coordY), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                        elif((ao == "E" or ao == "W")and(orientationTileOnMap == "E" or orientationTileOnMap == "W") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX+1,coordY), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                    elif(typeTileOnMap == newTileType and orientationTileOnMap == ao):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX+1,coordY), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
            else:
                coordX = previousTile.getPosition()[0]
                coordY = previousTile.getPosition()[1]
                if(self.isValidCoordX(coordX-1)):
                    tileOnMap = (mapMatrix[coordX-1])[coordY]
                    orientationTileOnMap = tileOnMap[-1]
                    typeTileOnMap = tileOnMap[:-1]
                    if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
                        if((ao == "S" or ao == "N")and(orientationTileOnMap == "S" or orientationTileOnMap == "N") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX-1,coordY), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                        elif((ao == "E" or ao == "W")and(orientationTileOnMap == "E" or orientationTileOnMap == "W") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX-1,coordY), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)                             
                    elif(typeTileOnMap == newTileType and orientationTileOnMap == ao):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX-1,coordY), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
        elif(orientationRobot == "E"):
            if(move == "r"):
                coordX = previousTile.getPosition()[0]
                coordY = previousTile.getPosition()[1]
                if(self.isValidCoordX(coordX+1)):
                    tileOnMap = (mapMatrix[coordX+1])[coordY]
                    orientationTileOnMap = tileOnMap[-1]
                    typeTileOnMap = tileOnMap[:-1]
                    
                    if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
                       
                        if((ao == "S" or ao == "N")and(orientationTileOnMap == "S" or orientationTileOnMap == "N") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                           # print "S N"
                            tile = Tile(newTileType,orientationTileOnMap,(coordX+1,coordY), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                        elif((ao == "E" or ao == "W")and(orientationTileOnMap == "E" or orientationTileOnMap == "W") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            #print "E W"
                            tile = Tile(newTileType,orientationTileOnMap,(coordX+1,coordY), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                    elif(typeTileOnMap == newTileType and orientationTileOnMap == ao):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX+1,coordY), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
            elif(move == "l"):
                coordX = previousTile.getPosition()[0]
                coordY = previousTile.getPosition()[1]
                if(self.isValidCoordX(coordX-1)):
                    tileOnMap = (mapMatrix[coordX-1])[coordY]
                    orientationTileOnMap = tileOnMap[-1]
                    typeTileOnMap = tileOnMap[:-1]
                    #print "before type check"
                    #print newTileType
                    if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
                        #print "in typecheck"
                        if((ao == "S" or ao == "N")and(orientationTileOnMap == "S" or orientationTileOnMap == "N") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            #print "in typecheck"
                            tile = Tile(newTileType,orientationTileOnMap,(coordX-1,coordY), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                        elif((ao == "E" or ao == "W")and(orientationTileOnMap == "E" or orientationTileOnMap == "W") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            #print "E W"
                            tile = Tile(newTileType,orientationTileOnMap,(coordX-1,coordY), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                    elif(typeTileOnMap == newTileType and orientationTileOnMap == ao):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX-1,coordY), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
            elif(move == "f"):
                coordX = previousTile.getPosition()[0]
                coordY = previousTile.getPosition()[1]
                if(self.isValidCoordY(coordY+1)):
                    tileOnMap = (mapMatrix[coordX])[coordY+1]
                    orientationTileOnMap = tileOnMap[-1]
                    typeTileOnMap = tileOnMap[:-1]
                    if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
                        if((ao == "S" or ao == "N")and(orientationTileOnMap == "S" or orientationTileOnMap == "N") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY+1), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                        elif((ao == "E" or ao == "W")and(orientationTileOnMap == "E" or orientationTileOnMap == "W") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY+1), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                    elif(typeTileOnMap == newTileType and orientationTileOnMap == ao):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY+1), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
            else:
                coordX = previousTile.getPosition()[0]
                coordY = previousTile.getPosition()[1]
                if(self.isValidCoordY(coordY-1)):
                    tileOnMap = (mapMatrix[coordX])[coordY-1]
                    orientationTileOnMap = tileOnMap[-1]
                    typeTileOnMap = tileOnMap[:-1]
                    if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
                        if((ao == "S" or ao == "N")and(orientationTileOnMap == "S" or orientationTileOnMap == "N") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY-1), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                        elif((ao == "E" or ao == "W")and(orientationTileOnMap == "E" or orientationTileOnMap == "W") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY-1), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                    elif(typeTileOnMap == newTileType and orientationTileOnMap == ao):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY-1), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
        else:
            if(move == "r"):
                coordX = previousTile.getPosition()[0]
                coordY = previousTile.getPosition()[1]
                if(self.isValidCoordX(coordX-1)):
                    tileOnMap = (mapMatrix[coordX-1])[coordY]
                    orientationTileOnMap = tileOnMap[-1]
                    typeTileOnMap = tileOnMap[:-1]
                    if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
                        if((ao == "S" or ao == "N")and(orientationTileOnMap == "S" or orientationTileOnMap == "N") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX-1,coordY), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                        elif((ao == "E" or ao == "W")and(orientationTileOnMap == "E" or orientationTileOnMap == "W") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX-1,coordY), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                    elif(typeTileOnMap == newTileType and orientationTileOnMap == ao):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX-1,coordY), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)

            elif(move == "l"):
                coordX = previousTile.getPosition()[0]
                coordY = previousTile.getPosition()[1]
                if(self.isValidCoordX(coordX+1)):
                    tileOnMap = (mapMatrix[coordX+1])[coordY]
                    orientationTileOnMap = tileOnMap[-1]
                    typeTileOnMap = tileOnMap[:-1]
                    if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
                        if((ao == "S" or ao == "N")and(orientationTileOnMap == "S" or orientationTileOnMap == "N") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX+1,coordY), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                        elif((ao == "E" or ao == "W")and(orientationTileOnMap == "E" or orientationTileOnMap == "W") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX+1,coordY), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                    elif(typeTileOnMap == newTileType and orientationTileOnMap == ao):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX+1,coordY), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
            elif(move == "f"):
                coordX = previousTile.getPosition()[0]
                coordY = previousTile.getPosition()[1]
                if(self.isValidCoordY(coordY-1)):
                    tileOnMap = (mapMatrix[coordX])[coordY-1]
                    orientationTileOnMap = tileOnMap[-1]
                    typeTileOnMap = tileOnMap[:-1]
                    if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
                        if((ao == "S" or ao == "N")and(orientationTileOnMap == "S" or orientationTileOnMap == "N") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY-1), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                        elif((ao == "E" or ao == "W")and(orientationTileOnMap == "E" or orientationTileOnMap == "W") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY-1), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                    elif(typeTileOnMap == newTileType and orientationTileOnMap == ao):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY-1), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
            else:
                coordX = previousTile.getPosition()[0]
                coordY = previousTile.getPosition()[1]
                if(self.isValidCoordY(coordY+1)):
                    tileOnMap = (mapMatrix[coordX])[coordY+1]
                    orientationTileOnMap = tileOnMap[-1]
                    typeTileOnMap = tileOnMap[:-1]
                    if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
                        if((ao == "S" or ao == "N")and(orientationTileOnMap == "S" or orientationTileOnMap == "N") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY+1), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                        elif((ao == "E" or ao == "W")and(orientationTileOnMap == "E" or orientationTileOnMap == "W") and (typeTileOnMap == "2" or typeTileOnMap == "5" or typeTileOnMap == "6" or typeTileOnMap == "7")):
                            tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY+1), previousTile.getAngle(),previousTile)
                            newPaths.append(tile)
                    elif(typeTileOnMap == newTileType and orientationTileOnMap == ao):
                        tile = Tile(newTileType,orientationTileOnMap,(coordX,coordY+1), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
        realNewPaths = []
        for x in newPaths:
            if (not (self.wallBetween(x.getPosition(), x.getPrevious().getPosition()) == 1)):
                realNewPaths.append(x)
        return realNewPaths
    def calculateOrientation(self, tile):
        x = tile.getPosition()[0]
        y = tile.getPosition()[1]

        prevX = tile.getPrevious().getPosition()[0]
        prevY = tile.getPrevious().getPosition()[1]

        diffX = x - prevX
        diffY = y - prevY

        if(diffY < 0):
            return "W"
        elif(diffY > 0):
            return "E"
        elif( diffX < 0):
            return "N"
        else:
            return "S"
    def calculateNewPaths1(self, previousTile, newTileType, ao):
    
        newPaths = []
        tileType = previousTile.getTileType()
        x = previousTile.getPosition()[0]
        y = previousTile.getPosition()[1]
            
        coordXtoN = (previousTile.getPosition())[0]-1
        coordXtoS = (previousTile.getPosition())[0]+1
        coordYtoE = (previousTile.getPosition())[1]+1
        coordYtoW = (previousTile.getPosition())[1]-1

##        print "absolute orientation is " + ao
        
        # is van type 2,5,6 of 7?
        if(newTileType == "2" or newTileType == "5" or newTileType == "6" or newTileType == "7"):
            # bestaat tile boven de gegeven tile?
            if(self.isValidCoordX(coordXtoN)):
                tileOnMap = (mapMatrix[coordXtoN])[y]
                # hebben ze dezelfde type?
                if(tileOnMap[:-1] == "2" or tileOnMap[:-1] == "5" or tileOnMap[:-1] == "6" or tileOnMap[:-1] == "7"):
                    orientationTileOnMap = tileOnMap[-1]
                    if((ao == "N" or ao == "S") and (orientationTileOnMap == "N" or orientationTileOnMap == "S")):
                         #create Tile to add to newPaths
                        tile = Tile(newTileType,orientationTileOnMap,(coordXtoN,y), previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
                    
            # bestaat tile onder de gegeven tile?    
            if(self.isValidCoordX(coordXtoS)):
                tileOnMap = (mapMatrix[coordXtoS])[y]
                # hebben ze dezelfde type?
                if(tileOnMap[:-1] == "2" or tileOnMap[:-1] == "5" or tileOnMap[:-1] == "6" or tileOnMap[:-1] == "7"):
                    orientationTileOnMap = tileOnMap[-1]
                    if((ao == "N" or ao == "S") and (orientationTileOnMap == "N" or orientationTileOnMap == "S")):
                         #create Tile to add to newPaths
                        tile = Tile(newTileType,orientationTileOnMap,(coordXtoS,y),previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
                        
            if(self.isValidCoordY(coordYtoE)):
                tileOnMap = (mapMatrix[x])[coordYtoE]
                # hebben ze dezelfde type?
                if(tileOnMap[:-1] == "2" or tileOnMap[:-1] == "5" or tileOnMap[:-1] == "6" or tileOnMap[:-1] == "7"):
                    orientationTileOnMap = tileOnMap[-1]
                    if((ao == "E" or ao == "W") and (orientationTileOnMap == "E" or orientationTileOnMap == "W")):
                        #create Tile to add to newPaths
                        tile = Tile(newTileType,orientationTileOnMap,(x,coordYtoE),previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
                        
            if(self.isValidCoordY(coordYtoW)):
                tileOnMap = (mapMatrix[x])[coordYtoW]
                # hebben ze dezelfde type?
                if(tileOnMap[:-1] == "2" or tileOnMap[:-1] == "5" or tileOnMap[:-1] == "6" or tileOnMap[:-1] == "7"):
                    orientationTileOnMap = tileOnMap[-1]
                    if((ao == "E" or ao == "W") and (orientationTileOnMap == "E" or orientationTileOnMap == "W")):
                        #create Tile to add to newPaths
                        tile = Tile(newTileType,orientationTileOnMap,(x,coordYtoW),previousTile.getAngle(),previousTile)
                        newPaths.append(tile)
            
        else:
            if(self.isValidCoordX(coordXtoN)):
                tileOnMap = (mapMatrix[coordXtoN])[y]
                orientationTileOnMap = tileOnMap[-1]
                typeTileOnMap = tileOnMap[:-1]
                if(newTileType == typeTileOnMap and orientationTileOnMap == ao):
                    tile = Tile(newTileType,orientationTileOnMap,(coordXtoN,y),previousTile.getAngle(),previousTile)
                    newPaths.append(tile)
                
            if(self.isValidCoordX(coordXtoS)):
                tileOnMap = (mapMatrix[coordXtoS])[y]
                orientationTileOnMap = tileOnMap[-1]
                typeTileOnMap = tileOnMap[:-1]
                if(newTileType == typeTileOnMap and orientationTileOnMap == ao):
                    tile = Tile(newTileType,orientationTileOnMap,(coordXtoS,y),previousTile.getAngle(),previousTile)
                    newPaths.append(tile)
                    
            if(self.isValidCoordY(coordYtoE)):
                tileOnMap = (mapMatrix[x])[coordYtoE]
                orientationTileOnMap = tileOnMap[-1]
                typeTileOnMap = tileOnMap[:-1]
                if(newTileType == typeTileOnMap and orientationTileOnMap == ao):
                    tile = Tile(newTileType,orientationTileOnMap,(x,coordYtoE),previousTile.getAngle(),previousTile)
                    newPaths.append(tile)
                
            if(self.isValidCoordY(coordYtoW)):
                tileOnMap = (mapMatrix[x])[coordYtoW]
                orientationTileOnMap = tileOnMap[-1]
                typeTileOnMap = tileOnMap[:-1]
                if(newTileType == typeTileOnMap and orientationTileOnMap == ao):
                    tile = Tile(newTileType,orientationTileOnMap,(x,coordYtoW),previousTile.getAngle(),previousTile)
                    newPaths.append(tile)
        realNewPaths = []
        for x in newPaths:
            if (not (self.wallBetween(x.getPosition(), x.getPrevious().getPosition()) == 1)):
                realNewPaths.append(x)
        return realNewPaths

    def isValidCoordX(self, x):
        if(x < 0 or x > (len(mapMatrix)-1)):
            return False
        return True
    def isValidCoordY(self, y):
        if(y < 0 or y > (len(mapMatrix[0])-1)):
            return False
        return True
    
    def getAllTilesWithType(self, tileType,orientation):
        global possibleSolutions
        for i in range(0, len(mapMatrix)):
            for j in range(0, len(mapMatrix[0])):
                tileOnMap =(mapMatrix[i])[j]
                if (tileType == "2"):
                    if (tileOnMap[:-1] == "2" or tileOnMap[:-1] == "5" or tileOnMap[:-1] == "6" or tileOnMap[:-1] == "7"):
                        orientationTileOnMap = tileOnMap[-1]
                        angle = self.determineAngle(orientation,orientationTileOnMap)
                        newTile = Tile(tileType, orientation, (i,j),angle)
                        possibleSolutions.append(newTile)
                elif(tileOnMap[:-1] == tileType):
                    orientationTileOnMap = tileOnMap[-1]
                    angle = self.determineAngle(orientation,orientationTileOnMap)
                    newTile = Tile(tileType, orientation, (i,j),angle)
                    possibleSolutions.append(newTile)
                    
        

    def determineOrientation(self,ro,angle):
        if(ro == "N"):
            if(angle == 0):
                return "N"
            elif(angle == 90):
                return "E"
            elif(angle == 180):
                return "S"
            else:
                return "W"
        elif(ro == "E"):
            if(angle == 0):
                return "E"
            elif(angle == 90):
                return "S"
            elif(angle == 180):
                return "W"
            else:
                return "N"
        elif(ro == "S"):
            if(angle == 0):
                return "S"
            elif(angle == 90):
                return "W"
            elif(angle == 180):
                return "N"
            else:
                return "E"
        else:
            if(angle == 0):
                return "W"
            elif(angle == 90):
                return "N"
            elif(angle == 180):
                return "E"
            else:
                return "S"
            
        
                
    def determineAngle(self, ro, ao):
        if (ro == "N"):
            if(ao == "N"):
                return 0
            elif (ao == "E"):
                return 90
            elif (ao == "S"):
                return 180
            else:
                return 270
        elif (ro == "E"):
            if(ao == "N"):
                return 270
            elif (ao == "E"):
                return 0
            elif (ao == "S"):
                return 90
            else:
                return 180
        elif (ro == "S"):
            if(ao == "N"):
                return 180
            elif (ao == "E"):
                return 270
            elif (ao == "S"):
                return 0
            else:
                return 90
        else:
            if(ao == "N"):
                return 90
            elif (ao == "E"):
                return 180
            elif (ao == "S"):
                return 270
            else:
                return 0
            
        return 0
    
    def wallBetween(self,parent,child):
        # Check whether there is a wall between the specified parent and its child
        global tiles
        global mapMatrix
        walls = tiles.get(mapMatrix[parent[0]][parent[1]])
        if (child[0] < parent[0]): # N
            return walls[0]
        elif (child[1] > parent[1]): # E
            return walls[1]
        elif (child[0] > parent[0]): # S
            return walls[2]
        else: # W
            return walls[3]
                    
