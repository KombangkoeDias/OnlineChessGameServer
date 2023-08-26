import pymongo

db = None

def connect():
    
    client = pymongo.MongoClient("mongodb+srv://analytics:analytics-password@chessgame.p59zi.mongodb.net/chessgame?retryWrites=true&w=majority") 
    global db
    
    db = client.chessgame
    return db

def count(queryResult):
    count = 0
    for result in queryResult:
        count += 1
    return count

def addData(code):
    queryResult = db.board.find({"code": code})
    if(count(queryResult) == 0):
        print("insert new board")
    else:
        print("yes")

def findOrAddNewBoardWithCode(code):
    queryResult = db.board.find_one({"code": str(code)})
    if queryResult is None :
        print("new game")
        startBoardfen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        db.board.insert_one({"code": str(code), "board": startBoardfen, "white": "", "black": ""})
        return {"board": startBoardfen, "newgame": True, "whitePlayer": False, "blackPlayer": False}
    else:
        print("continue playing")
        if(queryResult['white'] == ''):
            whitePlayer = False
        else:
            whitePlayer = queryResult['white']
        if(queryResult['black'] == ''):
            blackPlayer = False
        else:
            blackPlayer = queryResult['black']
        return {"board":queryResult['board'], "newgame":False, "whitePlayer": whitePlayer, "blackPlayer": blackPlayer}

def addPlayer(username,code,side):
    queryResult = db.board.find_one({"code": str(code)})
    if (queryResult is not None):
        if(str(side)=="white" and queryResult['white'] == ""):
            db.board.update_one({"code": str(code)}, {"$set": {str(side): str(username)}})
            return code, True
        elif(str(side) == "black" and queryResult['black'] == ""):
            db.board.update_one({"code": str(code)}, {"$set": {str(side): str(username)}})
            return code, True
        return code, False
    else:
        return None, False

def checkCode(code):
    queryResult = db.board.find_one({"code": str(code)})
    if queryResult is None:
        return True
    else:
        return False


def updateFen(code,fen):
    db.board.update_one({"code": str(code)}, {"$set": {"board": str(fen)}})

def LoginUser(username,password):
    queryResult = db.user.find_one({"username": username, "password": password})
    if (queryResult is not None):
        return True
    return False

def SignupUser(username,password):
    queryResult = db.user.find_one({"username": username})
    if queryResult is not None:
        return False
    try:
        db.user.insert_one({"username": str(username), "password": str(password)})
    except Exception as e:
        print(e)
        raise e
    return True

def Fen(code):
    queryResult = db.board.find_one({"code": str(code)})
    if(queryResult is not None):
        return queryResult['board']
    else:
        return False