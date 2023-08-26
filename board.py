import flask
import json
import bson.json_util as json_util
from flask import request
from flask_cors import CORS, cross_origin
import datetime

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, verify_jwt_in_request
)

from mongoconnector import connect, addData, findOrAddNewBoardWithCode,checkCode, updateFen,LoginUser,SignupUser,addPlayer,Fen

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['JWT_SECRET_KEY'] = "Kombangkoe Dias"
jwt = JWTManager(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
expire_access_token_time = datetime.timedelta(hours=1)
expire_refresh_token_time = datetime.timedelta(weeks=1)

localFenStorage = dict()

@app.route('/test', methods=['GET'])
@cross_origin()
def test():
    return {"test": "test"}

@app.route('/code', methods=['GET'])
@cross_origin()
@jwt_required
def start():
    global localFenStorage
    data = request.get_data()
    code = json.loads(request.args['code'])
    connect()
    result = findOrAddNewBoardWithCode(code)
    board = result['board']
    whitePlayer = result['whitePlayer']
    blackPlayer = result['blackPlayer']
    return json.loads(json_util.dumps({"board": board, "white_player": whitePlayer, "black_player": blackPlayer}))


@app.route('/getFen', methods=['POST'])
@cross_origin()
@jwt_required
def getFen():
    request.get_data()
    data = request.get_json()
    code = data.get('code')
    global localFenStorage
    fen = Fen(code)
    '''
    if(str(code) in localFenStorage.keys()):
        fen = localFenStorage[code]
    else:
        fen = Fen(code)
    '''
    return json.loads(json_util.dumps({"fen": str(fen)}))

@app.route('/code/check', methods=['GET'])
@cross_origin()
@jwt_required
def codeCheck():
    data = request.get_data()
    code = json.loads(request.args['code'])
    db = connect()
    isCodeViable = checkCode(code)
    return json.loads(json_util.dumps({"viable" : isCodeViable}))

@app.route('/updateFen', methods=['POST'])
@cross_origin()
@jwt_required
def fenUpdate():
    request.get_data()
    data = request.get_json()
    code = data.get("code")
    fen = data.get("fen")
    db = connect()
    try:
        global localFenStorage
        localFenStorage[str(code)] = fen
        updateFen(code,fen)
    except:
        return json.loads(json_util.dumps({"error": True}))
    return json.loads(json_util.dumps({"error": True}))

@app.route('/login', methods=['POST'])
@cross_origin()
def login():

    request.get_data()
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    db = connect()
    access_token = create_access_token(username, expires_delta=expire_access_token_time)
    refresh_token = create_refresh_token(username, expires_delta=expire_refresh_token_time)
    try:
        if(LoginUser(username,password)):
            return json.loads(json_util.dumps(
                {"error": False, "login": True, "access_token": access_token, "refresh_token": refresh_token}))
        else:
            return json.loads(json_util.dumps({"error": False, "login": False, "access_token": False, "refresh_token": False}))
    except:
        return json.loads(json_util.dumps({"error": True, "login": False, "access_token": False, "refresh_token": False}))

@app.route('/signup', methods=['POST'])
@cross_origin()
def signup():
    request.get_data()
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    db = connect()

    access_token = create_access_token(username, expires_delta=expire_access_token_time)
    refresh_token = create_refresh_token(username, expires_delta=expire_refresh_token_time)
    try:
        if(SignupUser(username,password)):
            return json.loads(json_util.dumps(
                {"error": False, "signup": True,"access_token": access_token, "refresh_token": refresh_token }))
        else:
            return json.loads(json_util.dumps(
                {"error": False, "signup": False, "access_token": False, "refresh_token": False}))
    except Exception as e:
        print(e)
        return json.loads(json_util.dumps({"error": True, "signup": False, "access_token": False, "refresh_token": False}))

@app.route('/refreshToken', methods=['POST'])
@cross_origin()
@jwt_refresh_token_required
def refreshToken():
    username = get_jwt_identity()
    access_token_new = create_access_token(username, expires_delta=expire_access_token_time)
    refresh_token_new = create_refresh_token(username, expires_delta=expire_refresh_token_time)
    return json.loads(json_util.dumps({"access_token": access_token_new, "refresh_token": refresh_token_new}))

@app.route('/checkToken', methods=['POST'])
@cross_origin()
def checkLoginState():
    try:
        verify_jwt_in_request()
        print("yes")
        return json.loads(json_util.dumps({"login_state": True})), 200
    except Exception as e:
        print("no")
        return json.loads(json_util.dumps({"login_state": False})), 401

@app.route("/addPlayer", methods=['POST'])
@cross_origin()
@jwt_required
def PlayerAdding():
    try:
        request.get_data()
        data = request.get_json()
        code = data.get("code")
        side = data.get("side")
        print(code)
        print(side)
        currCode, isPlayerAvailable = addPlayer(get_jwt_identity(),code,side)
        return json.loads(json_util.dumps({"UserIsInCode": currCode, "available": isPlayerAvailable}))
    except Exception as e:
        print(e)
connect()
