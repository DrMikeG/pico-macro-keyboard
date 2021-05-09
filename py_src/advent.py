import os
import re
import copy
import math

# odd-r horizontal row layout shoves odd rows right
# [0,0][1,0][2,0][3,0][4,0][5,0][6,0]
#   [0,1][1,1][2,1][3,1][4,1][5,1][6,1]
# [0,2][1,2][2,2][3,2][4,2][5,2][6,2]


def convertDirectionToGridMovement(directionStr):
    if directionStr == "e":
        return (1,0)
    if directionStr == "w":
        return (-1,0)
    
    if directionStr == "se":
        return (0,1)
    if directionStr == "sw":
        return (-1,1)
    
    if directionStr == "ne":
        return (1,-1)
    if directionStr == "nw":
        return (0,-1)

    assert False

def nextTokenLength(line):
    position = 0
    if line[position] == "e" or line[position] == "w":
        return 1
    if line[position] == "n" or line[position] == "s":
        return 2

def convertLineDirectionToGridPosition(line):
    #Because the tiles are hexagonal, every tile has six neighbors: 
    # east, southeast, southwest, west, northwest, and northeast. 
    # These directions are given in your list, respectively, as 
    # e, 
    # w, 
    # se, sw,
    # nw, and ne.
    tile =[0,0]

    while len(line) > 0:
        chop = nextTokenLength(line)
        token = line[:chop]
        line =  line[chop:]
        move = convertDirectionToGridMovement(token)
        tile[0] += move[0]
        tile[1] += move[1]

    return (tile[0],tile[1])

def flipTilePosition(tiles,tilePosition):
    if tilePosition in tiles:
        if tiles[tilePosition] == "Black":
            tiles[tilePosition] = "White"
        elif tiles[tilePosition] == "White":
            tiles[tilePosition] = "Black"
    else:
        tiles[tilePosition] = "Black"

def countBlack(tiles):
    count = 0
    for k in tiles:
        if tiles[k] == "Black":
            count += 1
    return count

def getBoundingBox(tiles):
    minX = 0
    minY = 0
    maxX = 0
    maxY = 0

    for k in tiles:
        assert len(k) == 2
        if k[0] < minX:
            minX = k[0]
        if k[0] > maxX:
            maxX = k[0]
        if k[1] < minY:
            minY = k[1]
        if k[1] > maxY:
            maxY = k[1]
    return [minX,maxX,minY,maxY]

def isBlack(tiles,pos):
    if not pos in tiles:
        return False
    else:
        if tiles[pos] == "Black":
            return True
        else:
            return False

def countNeighbours(tiles,pos):
    neigbours = []
    neigbours.append(convertDirectionToGridMovement("nw"))
    neigbours.append(convertDirectionToGridMovement("ne"))
    neigbours.append(convertDirectionToGridMovement("e"))
    neigbours.append(convertDirectionToGridMovement("se"))
    neigbours.append(convertDirectionToGridMovement("sw"))
    neigbours.append(convertDirectionToGridMovement("w"))
    count = 0
    editPos= [0,0]
    for n in neigbours:
        editPos[0]= pos[0]
        editPos[1]= pos[1]
        editPos[0] += n[0]
        editPos[1] += n[1]
        blackNeighbour = isBlack(tiles,(editPos[0],editPos[1]))
        #print("pos (%d,%d) %s"%(editPos[0],editPos[1],blackNeighbour))
        if blackNeighbour:
            count = count + 1
    return count

def printHexGrid(tiles):
    print("\n")
    [minX,maxX,minY,maxY] = getBoundingBox(tiles)
    # odd rows areindented by 3
    for y in range(minY-1,maxY+1):
        rowStr = ""
        if y % 2 == 1:
            rowStr = rowStr + "   "
        for x in range(minX-2,maxX+2):
            tile = "    "
            if isBlack(tiles,(x,y)):
                tile = "BBBB"
            if x==0 and y==0:
                tile = " 00 "
                if isBlack(tiles,(x,y)):
                    tile = "B00B"
            rowStr = rowStr + "[" + tile + "]"
        print(rowStr)

def conway(tiles):
    [minX,maxX,minY,maxY] = getBoundingBox(tiles)

    #printHexGrid(tiles)

    dictOrig = dict(tiles)
    tiles.clear()
    for x in range(minX-2,maxX+2):
        for y in range(minY-2,maxY+2):
            n = countNeighbours(dictOrig,(x,y))
            #Any black tile with zero or more than 2 black tiles immediately adjacent to it is flipped to white.
            #Any white tile with exactly 2 black tiles immediately adjacent to it is flipped to black.
            if isBlack(dictOrig,(x,y)):
                if n == 0 or n > 2:
                    tiles[(x,y)] = "White"
                else:
                    tiles[(x,y)] = "Black"
            else:
                if n == 2:
                    tiles[(x,y)] = "Black"
                else:
                    tiles[(x,y)] = "White"
    
    #printHexGrid(tiles)


def processInputFile(filePath):
    
    tiles = {}
    if os.path.exists(filePath):
        f = open(filePath, "r")
        for x in f:
            tilePosition = convertLineDirectionToGridPosition(x.strip())
            flipTilePosition(tiles,tilePosition)
        f.close()
    else :
        print("%s does not exist"%(filePath))

    #count = countBlack(tiles)
    #print(count)
    return tiles

def getInputPath():
    return os.path.join(os.path.dirname(__file__),"input.txt")


def mainTask():
    input_path = getInputPath()
    tiles =processInputFile(input_path)
    for _ in range(100):
        conway(tiles)
    print(countBlack(tiles))

if __name__ == "__main__":

    mainTask()
