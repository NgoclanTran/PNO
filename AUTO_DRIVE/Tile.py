class Tile():
    
    def __init__(self, tileType, orientation, position, angle, previous = None):
        self._tileType = tileType
        self._orientation = orientation
        self._position = position
        self._previous = previous
        self._angle = angle
        
    def getTileType(self):
        return self._tileType

    def getOrientation(self):
        return self._orientation

    def getPosition(self):
        return self._position

    def getPrevious(self):
        return self._previous
    def getAngle(self):
        return self._angle
