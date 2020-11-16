#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
实现文件断点续传的客户端
"""

import socket
import sys
import re
import os
import ssl
import time

FILE_DIR = os.path.dirname(__file__)

ck = socket.socket()
ssl_sock = ssl.wrap_socket(ck, ca_certs="cert.pem", cert_reqs=ssl.CERT_REQUIRED)
ssl_sock.connect(('223.91.78.9', 8001))
print(str(ssl_sock.recv(1024), encoding='utf-8'))


#定义一个函数，计算进度条
def bar(num = 1, sum = 100):
    rate = float(num) / float(sum)
    rate_num = int(rate * 100)
    temp = '\r%d %%' % (rate_num)
    sys.stdout.write(temp)

#定义建立ssl连接的函数
def client_ssl():
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

while True:
    inp = input('请输入（内容格式：文件路径 目标路径）: \n >>> ').strip()  #输入内容格式：命令|文件路径 目标路径
    #func, file_path =inp.split("|", 1)  #将输入的内容拆分为两部分，方法名和路径
    local_path, target_path = re.split("\s+", inp, 1) #再将路径部分，通过正则表达式。以空格拆分为：文件路径和上传的目标路径
    file_byte_size = os.stat(local_path).st_size  #获取文件的大小
    file_name = os.path.basename(local_path)   #设置文件名

    post_info = "post|%s|%s|%s" % (file_name, file_byte_size, target_path)  #将发送的内容进行拼接
    ssl_sock.sendall(bytes(post_info, encoding='utf-8'))  #向服务器端发送内容

    result_exist = str(ssl_sock.recv(1024), encoding='utf-8')
    has_sent = 0
    if result_exist == "2003":
        inp = input("文件已存在，是否续传？Y/N:").strip()
        if inp.upper() == 'Y':
            ssl_sock.sendall(bytes("2004", encoding='utf-8'))
            result_continue_pos = str(ssl_sock.recv(1024), encoding='utf-8')  #已经传输了多少的文件内容
            print(result_continue_pos)
            has_sent = int(result_continue_pos)

        else:
            ssl_sock.sendall(bytes("2005", encoding='utf-8'))  #发送2005代表不续传

    file_obj = open(local_path, 'rb')  #对文件进行读操作
    file_obj.seek(has_sent)  #调整指针

    time_before = time.time()

    while has_sent < file_byte_size:
        data = file_obj.read(1024)
        ssl_sock.sendall(data)
        has_sent += len(data)
        bar(has_sent, file_byte_size)  #进度条

    time_after = time.time()

    file_obj.close()
    print("文件上传成功！用时", time_after - time_before, "秒")