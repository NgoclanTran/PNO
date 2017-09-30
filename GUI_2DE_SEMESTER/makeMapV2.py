
from PIL import Image
from mapImages import makeMapImage,getImage,getDraaiing,getColor,getShape
import os
import shutil
#
#  Hier komt de code voor het genereren van die rij
#
#  resize alle afbeeldingen van de map naar een 100,100 formaat
global listOfMapItems
global rijen
global kolommen
global xMax
global yMax
global pathToDraw
pathToDraw = ["[]"]
global roaming
roaming = False


def makeMap(positionList = "",path = 1):
    global pathToDraw
    global roaming
    if os.path.exists("mapimages/kaart.txt"):
        makeEmpMap()
        setTargetsOnMap(positionList)
        if path != 1:
            roaming = '$' in path
            paths = path.split("$")
            pathToDraw = paths
        for path in pathToDraw:
            constructLine(str(path))
        roaming = False
       
    else:
        shutil.copy2(r'mapimages/NOMAP.jpg',r'mapimages/map.jpg')
        
    
def makeEmpMap():
    global listOfMapItems
    global rijen
    global kolommen
    global xMax
    global yMax
    kaartFile = open(r"mapimages/kaart.txt", 'r')
    allLines = kaartFile.readlines()
    binaryLock = 1
    counter = 0
    while (binaryLock == 1):
        if (counter == len(allLines)):
            break
        if (allLines[counter][0] == "#" or allLines[counter] == "\n" or allLines[counter][0] == " "):
            del allLines[counter]
        else:
            counter += 1

    kolommen = allLines[0][0]
    hulpcounter = 1
    while (allLines[0][hulpcounter] != " "):
        kolommen += allLines[0][hulpcounter]
        hulpcounter+=1

    rijen = ""
    listOfMapItems = []
    while (len(allLines[0]) - 2 > hulpcounter):
        rijen += allLines[0][hulpcounter+1]
        hulpcounter += 1

    for x in range(0,int(rijen)):
        for y in range(0, int(kolommen)):
            try:
                if(allLines[x+1][2] != 'i'):
                    listOfMapItems.append(allLines[x+1][y*3] + allLines[x+1][y*3+1])
            except:
                pass
        onthoudX = x + 1
    beginImagesX = onthoudX + 1
    listOfMapPictures = []
    xMax = int(kolommen)
    yMax = int(rijen)
    for x in range(0,int(rijen)*int(kolommen)):
        try:
            if( listOfMapItems[x][0] == "0"):
                picture = Image.open("mapimages/0N.jpg")
            if( listOfMapItems[x][0] == "1"):
                picture = Image.open("mapimages/1N.jpg")
            if( listOfMapItems[x][0] == "2"):
                picture = Image.open("mapimages/2N.jpg")
            if( listOfMapItems[x][0] == "3"):
                picture = Image.open("mapimages/3N.jpg")
            if( listOfMapItems[x][0] == "4"):
                picture = Image.open("mapimages/4N.jpg")
            if( listOfMapItems[x][0] == "5"):
                picture = Image.open("mapimages/5N.jpg")
            if( listOfMapItems[x][0] == "6"):
                picture = Image.open("mapimages/6N.jpg")
            if( listOfMapItems[x][0] == "7"):
                picture = Image.open("mapimages/7N.jpg")
            if(listOfMapItems[x][1] == "N"):
                picture = picture.resize((100,100))
            if(listOfMapItems[x][1] == "E"):
                picture = picture.resize((100,100))
                picture = picture.rotate(-90)
            if(listOfMapItems[x][1] == "W"):
                picture = picture.resize((100,100))
                picture = picture.rotate(90)
            if(listOfMapItems[x][1] == "S"):
                picture = picture.resize((100,100))
                picture = picture.rotate(180)
    
            listOfMapPictures.append(picture)

        except:
            pass
    # Onthouden van de afbeeldingen
    for x in range(beginImagesX, len(allLines)):
        if (allLines[x][1] == "?" or allLines[x][2] == "?"):
            pass
        elif( allLines[x][1] != "N" and allLines[x][1] != "W" and allLines[x][1] != "S" and allLines[x][1] != "E"):
            plaatsAfbeelding = allLines[x][0] + allLines[x][1]
            draaiing = allLines[x][2]
            y = 10
            color = ""
            while (allLines[x][y] != "_"):
                color += allLines[x][y]
                y += 1
            y += 1
            shape = ""
            while (allLines[x][y] != "."):
                shape += allLines[x][y]
                y += 1
            makeMapImage(plaatsAfbeelding, draaiing, color, shape)
        else:
            plaatsAfbeelding = allLines[x][0]
            draaiing = allLines[x][1]
            y = 9
            color = ""
            while (allLines[x][y] != "_"):
                color += allLines[x][y]
                y += 1
            y += 1
            shape = ""
            while (allLines[x][y] != "."):
                shape += allLines[x][y]
                y += 1
            makeMapImage(plaatsAfbeelding, draaiing, color, shape)

    #creates a new empty image, RGB mode, and size rows*100, columns * 100.
    new_im = Image.new('RGB', (int(kolommen)*100,int(rijen)*100))

    #Iterate through a rows bij columns grid with 100 spacing, to place my image
    for i in xrange(0,int(kolommen)*100,100):
        for j in xrange(0,int(rijen)*100,100):
            if (i != 0):
                rescaledI = i/100
            else:
                rescaledI = i
            if (j != 0):
                rescaledJ = j/100
            else:
                rescaledJ = j
            try:
                im = listOfMapPictures[rescaledJ*int(kolommen) + rescaledI]
            
                #Here I resize my opened image, so it is no bigger than 100,100
                im.thumbnail((100,100))
                new_im.paste(im, (i,j))
                getImage(rescaledJ * int(kolommen) + rescaledI)
                if (getImage(rescaledJ * int(kolommen) + rescaledI)):
                    plaats = rescaledJ * int(kolommen) + rescaledI
                    imageUrl = "mapimages/" + getColor(plaats) + "_" + getShape(plaats) + "." + "png"
                    im = Image.open(imageUrl)
                    im.thumbnail((40,40))
                    if(getDraaiing(plaats) == "W"):
                        new_im.paste(im, (i,j+35))
                    if(getDraaiing(plaats) == "N"):
                        new_im.paste(im, (i+35,j))
                    if(getDraaiing(plaats) == "E"):
                        new_im.paste(im, (i+60,j+35))
                    if(getDraaiing(plaats) == "S"):
                        new_im.paste(im, (i+35,j+70))
                else:
                    new_im.paste(im, (i,j))
            except:
                pass
##    new_im.show()
    new_im.save(r'mapimages/map.jpg')
    return allLines

def setTargetsOnMap(positionList):
    global xMax
    global yMax
    gesplitsteLijst = positionList.split()

    kaart = Image.open("mapImages/map.jpg", 'r')
    pixelsX, pixelsY = kaart.size
    widthSquare = pixelsX/xMax
    heightSquare = pixelsY/yMax

    i=0
    while (i < len(gesplitsteLijst)):

        team = gesplitsteLijst[i]
        tegelMetOrientatie = gesplitsteLijst[i+1]
        Orientatie = tegelMetOrientatie[-1]
        tegelNr = int(tegelMetOrientatie[:-1])

        x = (tegelNr%xMax) + 1
        y = (tegelNr/xMax) + 1

        xValue = widthSquare/2 + (x-1)*widthSquare
        yValue = heightSquare/2 + (y-1)*heightSquare

        target = Image.open('target-small-' + team + '.png')
        if (Orientatie == 'N'):
            target = target.rotate(90)
        elif (Orientatie == 'W'):
            target = target.rotate(180)
        elif (Orientatie == 'S'):
            target = target.rotate(270)
        targetX, targetY = target.size
        #target.convert('RGBA')
        offset = (xValue-targetX/2, yValue-targetY/2)

        kaart.paste(target, offset, target.convert('RGBA'))

        i += 2

    kaart.save("mapimages/map.jpg")

def constructLine(listOfLocationTuples):
    global roaming
    if (listOfLocationTuples == "[]"):
        return
    picture = Image.open("mapimages/map.jpg")
    #(width, height) = picture.size

    tijdelijk1 = listOfLocationTuples.split(', ')
    tijdelijk2 = []
    tijdelijk2.append(int(tijdelijk1[0][2:]))
    i = 1
    while (i < len(tijdelijk1)-1):
        tijdelijk2.append(int(tijdelijk1[i][:-1]))
        tijdelijk2.append(int(tijdelijk1[i+1][1:]))
        i += 2
    tijdelijk2.append(int(tijdelijk1[-1][:-2]))    
    print tijdelijk2            
    i = 0
    locationTuples = []
    while (i<len(tijdelijk2)):
        locationTuples.append((tijdelijk2[i],tijdelijk2[i+1]))
        i += 2    
    
    print locationTuples
    
    pix = picture.load()
    newListRows = []
    newListColumns = []
    for i,j in locationTuples:
        newListRows.append(i)
        newListColumns.append(j)
    
    for x in range(0,len(newListRows)):
        try:
            if (newListRows[x] - newListRows[x+1] == 0):
                if (newListColumns[x] < newListColumns[x+1]):
                    for z in range((newListColumns[x]*100) + 50, (newListColumns[x+1] * 100) + 60):
                        for y in range((newListRows[x]*100) + 50, (newListRows[x]*100)+60):
                            if roaming:
                                pix[z,y] = (255,0,0)
                            else:
                                pix[z,y] = (0,100,0)
                else:
                    for z in range((newListColumns[x+1]*100) + 50, (newListColumns[x] * 100) + 60):
                        for y in range((newListRows[x]*100) + 50, (newListRows[x]*100)+60):
                            if roaming:
                                pix[z,y] = (255,0,0)
                            else:
                                pix[z,y] = (0,100,0)
            else:
                if (newListRows[x] < newListRows[x+1]):
                    for z in range((newListRows[x] * 100) + 50, (newListRows[x+1] * 100) + 50):
                        for y in range((newListColumns[x]*100)+50, (newListColumns[x]*100)+60):
                            if roaming:
                                pix[y,z] = (255,0,0)
                            else:
                                pix[y,z] = (0,100,0)
                else:
                    for z in range((newListRows[x+1] * 100) + 50, (newListRows[x] * 100) + 50):
                        for y in range((newListColumns[x]*100)+50, (newListColumns[x]*100)+60):
                            if roaming:
                                pix[y,z] = (255,0,0)
                            else:
                                pix[y,z] = (0,100,0)
        except:
            pass
        
    picture.load()
    picture.save(r'mapimages/map.jpg')
    
