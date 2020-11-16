#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
实现文件断点续传的服务器端
"""

import socket
import os
import ssl

#BASE_DIR = os.path.dirname(os.path.dirname(__file__))    #获取当前文件路径
                                                          #
#home = os.path.join(BASE_DIR, "home/file")               #在当前路径下创建home/file目录，作为默认传输目标路径，可在此指定默认传输路径
#home = os.path.join(BASE_DIR)                            #
context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

sk = socket.socket()
sk.bind(('0.0.0.0', 8001))
sk.listen(5)

while True:
    print("Waiting....")
    conn, addr = sk.accept()
    connstream = context.wrap_socket(conn, server_side=True)
    connstream.sendall(bytes('欢迎登录', encoding='utf-8'))
    flag = True
    while flag:
        client_bytes = connstream.recv(1024)   #接收客户端发送过来的内容
        client_str = str(client_bytes, encoding='utf-8')  #将内容转换成字符串

        # 将客户端发送过来的内容以"|"拆分为:命名方法，文件名，文件大小，目标路径
        func, file_name, file_byte_size, target_path = client_str.split('|', 3)
        file_byte_size = int(file_byte_size)
        path = os.path.join(target_path, file_name)
        print(path)
        has_received = 0

        #首先判断该路径下是否已存在文件
        if os.path.exists(path):
            connstream.sendall(bytes("2003", encoding='utf-8'))  #发送通知客户端，该文件已存在
            is_continue = str(connstream.recv(1024), encoding='utf-8')  #等待客户端选择回复
            if is_continue == "2004":
                has_file_size = os.stat(path).st_size
                connstream.sendall(bytes(str(has_file_size), encoding='utf-8'))  #将已接收的文件大小给客户端
                has_received += has_file_size
                f = open(path, 'ab')
            else:
                f = open(path, 'wb')
        else:
            connstream.sendall(bytes("2002", encoding='utf-8'))
            f = open(path, 'wb')

        while has_received < file_byte_size:
            try:
                data = connstream.recv(1024)
                if not data:
                    raise Exception
            except Exception:
                flag = False
                break
            f.write(data)
            has_received += len(data)
        print("文件已接收完成！")
        f.close()