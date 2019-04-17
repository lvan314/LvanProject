#coding:utf-8
import socketserver,json,time
import subprocess
import socket
import re
import base64
import hashlib
import threading as thread
import struct
import simplejson
#实时聊天系统
connLst = []
HOST = "localhost"
PORT = 9000
MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
HANDSHAKE_STRING = "HTTP/1.1 101 Switching Protocols\r\n" \
                   "Upgrade:websocket\r\n" \
                   "Connection: Upgrade\r\n" \
                   "Sec-WebSocket-Accept: {1}\r\n" \
                   "WebSocket-Location: ws://{2}/chat\r\n" \
                   "WebSocket-Protocol:chat\r\n\r\n"


# groupLst = []
##  代号 地址和端口 连接对象
class Connector(object):  ##存放连接
    def __init__(self, userid, addrPort, conObj):
        self.userid = userid
        self.addrPort = addrPort
        self.conObj = conObj
##握手
def handshake(serverSocket):
    while True:
        # print("getting connection")
        clientSocket, addressInfo = serverSocket.accept()
        # print("get connected")
        request = clientSocket.recv(2048)
        # print(request.decode())
        # 获取Sec-WebSocket-Key
        ret = re.search(r"Sec-WebSocket-Key: (.*==)", str(request.decode()))
        if ret:
            key = ret.group(1)
        else:
            return
        Sec_WebSocket_Key = key + MAGIC_STRING
        # print("key ", Sec_WebSocket_Key)
        # 将Sec-WebSocket-Key先进行sha1加密,转成二进制后在使用base64加密
        response_key = base64.b64encode(hashlib.sha1(bytes(Sec_WebSocket_Key, encoding="utf8")).digest())
        response_key_str = str(response_key)
        response_key_str = response_key_str[2:30]
        # print(response_key_str)
        # 构建websocket返回数据
        response = HANDSHAKE_STRING.replace("{1}", response_key_str).replace("{2}", HOST + ":" + str(PORT))
        clientSocket.send(response.encode())
        #握手成功
        resData=[]
        res={}
        res['fromuserid']=0
        res['type']='state'
        res['content']='connect success'
        res['ctime']=time.time()
        resData.append(res)
        fData = {'code': "success", 'msg': resData};
        send_data(clientSocket,json.dumps(fData))
        # print("send the hand shake data")
        t1 = thread.Thread(target=recv_data, args=(clientSocket, addressInfo))  # 负责接收消息
        t1.start()
        t2 = thread.Thread(target=send_data, args=(clientSocket, 'connect success'))  # 负责发送消息
        t2.start()
        # server = socketserver.ThreadingTCPServer(('127.0.0.1',9000),MyServer)
        # server.serve_forever()
#发送数据
def send_data(clientSocket, data):
    token = b'\x81'
    length = len(data.encode())
    if length <= 125:
        token += struct.pack('B', length)
    elif length <= 0xFFFF:
        token += struct.pack('!BH', 126, length)
    else:
        token += struct.pack('!BQ', 127, length)
    data = token + data.encode()
    clientSocket.send(data)
#接收数据
def recv_data(clientSocket, addressInfo):
    while True:
        try:
            info = clientSocket.recv(2048)
            if not info:
                return
        except:
            return
        else:
            code_len = info[1] & 0x7f
            if code_len == 0x7e:
                extend_payload_len = info[2:4]
                mask = info[4:8]
                decoded = info[8:]
            elif code_len == 0x7f:
                extend_payload_len = info[2:10]
                mask = info[10:14]
                decoded = info[14:]
            else:
                extend_payload_len = None
                mask = info[2:6]
                decoded = info[6:]
            bytes_list = bytearray()
            # print(mask)
            # print(decoded)
            for i in range(len(decoded)):
                chunk = decoded[i] ^ mask[i % 4]
                bytes_list.append(chunk)
            raw_str = str(bytes_list, encoding="utf8")
            json_res = json.loads(raw_str)
            if json_res['type'] == 'test':  # 测试连接
                #if connLst.userid.__contains__(json_res['userid']):
                 #   print("已登录的用户")
                userlist=[]
                for item in connLst:
                   userlist.append(item.userid)
                if json_res['userid'] in userlist:
                    for item in connLst:
                        if item.userid==json_res['userid']:
                            item.conObj=clientSocket
                            print('替换了socket'+item.userid)
                else:
                    conObj = Connector(json_res['userid'], addressInfo, clientSocket)
                    connLst.append(conObj)
                    print("用户：" + json_res['userid'] + "登入成功")
            elif json_res['type'] == 'text':
                userid = json_res['userid']
                touserid = json_res['to']
                # print("长度")
                # print(len(connLst))
                print("用户"+str(userid)+" -> "+str(touserid)+":"+json_res['content'])
                if len(connLst) > 0:
                    for item in connLst:
                        # print(item.userid + "<-->" + userid)
                        if item.userid == userid:  # 已注册过的用户
                            # print("①当前用户已注册")
                            for item in connLst:
                                if item.userid == touserid:
                                    resData = []
                                    res = {}
                                    res['fromuserid'] = userid
                                    res['type'] = 'text'
                                    res['content'] = json_res['content']
                                    res['ctime'] = time.time()
                                    resData.append(res)
                                    fData = {'code': "success", 'msg': resData};
                                    send_data(item.conObj, json.dumps(fData)) #转发给用户
                                    resData1 = []
                                    res1= {}
                                    res1['fromuserid'] =0
                                    res1['type'] = 'state'
                                    res1['content'] = json_res['content']
                                    res1['ctime'] = json_res['ctime']
                                    resData1.append(res1)
                                    fData = {'code': "success", 'msg': resData1};
                                    send_data(clientSocket,json.dumps(fData))#状态回复
                else:
                    pass
            elif json_res['type'] == 'end':
                # 用户退出应用,将connLst保存对象去除，并将用户状态改为离线
                print(json_res['content'])
#启动服务
class starchatserver(thread.Thread):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host = (HOST, PORT)
    serverSocket.bind(host)
    serverSocket.listen(128)
    print('waiting for connection...')
    handshake(serverSocket)
   # #前台命令启动聊天服务
   #  def startchatserver(request):
   #      if request.method=='POST':
   #          request = simplejson.loads(request.body)
   #          userid = request.get("userid")
   #          if userid == 1:
   #              serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   #              serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   #              host = (HOST, PORT)
   #              serverSocket.bind(host)
   #              serverSocket.listen(128)
   #              print('waiting for connection...')
   #              handshake(serverSocket)
