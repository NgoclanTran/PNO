
listOfMapImages = []

def makeMapImage(plaatsAfbeelding, draaiing, color, shape):
    listOfMapImages.append(plaatsAfbeelding + " " + draaiing + " " + color + " " + shape + " ")
    
def getImage(plaatsAfbeelding):
    for x in range(0,len(listOfMapImages)):
        y = 0
        tempPlaats = ""
        while (listOfMapImages[x][y] != " "):
            tempPlaats += listOfMapImages[x][y]
            y += 1
        if (tempPlaats == str(plaatsAfbeelding)):
            return "true"
def getDraaiing(plaatsAfbeelding):
    for x in range(0,len(listOfMapImages)):
        y = 0
        tempPlaats = ""
        while (listOfMapImages[x][y] != " "):
            tempPlaats += listOfMapImages[x][y]
            y += 1
        if (tempPlaats == str(plaatsAfbeelding)):
            return listOfMapImages[x][y+1]

def getColor(plaatsAfbeelding):
    for x in range(0,len(listOfMapImages)):
        y = 0
        tempPlaats = ""
        while (listOfMapImages[x][y] != " "):
            tempPlaats += listOfMapImages[x][y]
            y += 1
        if (tempPlaats == str(plaatsAfbeelding)):
            color = ""
            while (listOfMapImages[x][y+3] != " "):
                color += listOfMapImages[x][y+3]
                y += 1
            return color

def getShape(plaatsAfbeelding):
    for x in range(0,len(listOfMapImages)):
        y = 0
        tempPlaats = ""
        while (listOfMapImages[x][y] != " "):
            tempPlaats += listOfMapImages[x][y]
            y += 1
        if (tempPlaats == str(plaatsAfbeelding)):
            shape = ""
            while(listOfMapImages[x][y+3+len(getColor(plaatsAfbeelding)) + 1] != " "):
                shape += listOfMapImages[x][y+3+len(getColor(plaatsAfbeelding)) + 1]
                y += 1
            return shape




            
