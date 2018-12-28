#! /usr/bin/python

import os
import httplib, shutil, subprocess
import socket,sys
import threading, time
import urllib, json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from os import curdir, sep
import string, cgi
import BaseHTTPServer

global origin_serv
global port_no
global Cache
global cache_dir

Cache = {}
LRU1 = []

###Loading LRU function is used to laod the LRU in the LRU List. The LRU file is getting opened and then the LRU list is appended with this File.###

def loading_LRU():
    global LRU1
    my_loc = str(os.path.dirname(os.path.abspath(__file__)))
    file_name = "LRU1"
    my_root_loc = my_loc + file_name
    if os.path.exists(my_root_loc):
        try:
            file_handle = open(my_root_loc,"r")
            for word in file_handle.readlines():
                LRU1.append(str(word))
            file_handle.close()
        except:
            return
    else:
        subprocess.call(["touch", "LRU1"])

"""Function get_file_cont taks input as the path & name of the file and returns the output as the contents of these files.
   The file is opened in the read mode and saves all the data contained in a string named as the 'contents' and once all the lines are read, the 'contents' are given back."""

def get_file_cont(my_route,file_name):
    try:
        loc = my_route + "/" + file_name
        files = open(loc, "r")
        contents = ""
        for words in files.readlines():
            contents += str(words)
        files.close()
        return contents

    except:
        return None
"""This function stores the file contents in a directory named Cache Dictionary. All the files which are cached get stored under a directory named'cache/'.
All the contents of each files get cached in this directory."""
    
def load_cache():
    global Cache
    my_loc = str(os.path.dirname(os.path.abspath(__file__)))
    my_route = my_loc + "/cache"
    global cache_dir
    cache_dir = my_route
    if os.path.exists(my_route):
      try:
        for sdirec, direc, f in os.walk(my_route):
            for one_file in f:
                cont = get_file_cont(my_route,one_file)
                if cont != None:
                    Cache[str(one_file)] = cont
      except:
        return
    else:
	subprocess.call(["mkdir", my_route])

'''It is resposible to add new files to the cache directory. This firstly checks the if there is sufficient diskspace.
If the empty space is more than the minimum set value then, it gives True value else it returns false.'''

def new_file_cache(file_name,resp):
    global LRU1
    global Cache

    Cache[file_name] = str(resp)
    LRU_update(file_name)
    s = open(str(file_name),'w')
    s.writelines(resp)
    s.close()
    global cache_dir
    subprocess.call(["mv",file_name, cache_dir])

'''This function is used to calculate the available empty space in the cache directory'''
#Function to calculate the space in the cache
def cache_space():
    mini = 1572864
    s = os.statvfs('/home')
    empty_space = (s.f_bavail * s.f_frsize)/1024
    if empty_space > mini:
       return True
    else:
        return False

"""BaseHTTPRequestHadnler is used for handling the GET request for the HTTP Server so that it can obtain 'GET' request from DNS server
and all the clients who request  for contents of webpage"""

class MyHTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    global LRU1
    global Cache
    
    def do_GET(self):
        dnshead = None
        parts = self.path.split("/")
        b_name = Base_FileName(parts)
        client_IP = self.client_address[0]
	'''self.path = 'http://' + origin_serv+ ':8080'+self.path				#Sending request to origin server
	self.connection = urllib.urlopen(self.path)					#Connecting to the origin server
	self.data=self.connection.read()						#Reading data
	self.wfile.write(self.data)  '''                                                #Writing data
        my_loc = str(os.path.dirname(os.path.abspath(__file__)))
        my_root_loc = my_loc + "/cache/" + b_name

        dnshead = self.headers.getheader("DNSScamper", None)

########## If request is for Scamper from DNS Server, teh below block is executed.
        
        if dnshead != None:
            self.send_response(200)
            self.send_header('Content-type','text/plain')
            self.end_headers()
            out = subprocess.check_output(["scamper","-c", "ping", "-i", client_IP])
            rtt = RTT_for_Scamper(out)
            self.wfile.write(rtt)
            print rtt
        
########## If the cache is hit, find all the contents from the dictionary of the cache and give the output as the contents.

        if os.path.exists(my_root_loc):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            if b_name in Cache:
               self.wfile.write(Cache[b_name])
            LRU_update(b_name)
            return

########## If the cache miss is seen, forward the GET request to the Origin server and forward its response to the client.
########## Once  the response if forwarded, all the new files get added to the local cache dictionary.

        else:
            response = req_origin(self.path)
            if response != None:
                self.send_response(response.status)
                cType = response.getheader('content-type', 'text/html')
                self.send_header('Content-type', cType)
                self.end_headers()
                resp_b = response.read()
                self.wfile.write(resp_b)
                new_file_cache(b_name,resp_b)
                return

""" Class for initialising Threads """

class repeat(threading.Thread):
    def __init__(self, interval, fun, *args):
        threading.Thread.__init__(self)
        self.interval = interval  # seconds between calls
        self.fun = fun          # function to call
        self.args = args          # optional positional argument(s) for call
        self.runable = True
    def run(self):
        while self.runable:
            self.fun(*self.args)
            time.sleep(self.interval)
    def stop(self):
        self.runable = False


lock = threading.RLock()

""" This function calculates the RTT value which was obtained when Scamper was executed""" 

def RTT_for_Scamper(dev):
    v1 = dev.split(" ")
    loss = v1.pop()
    amt = v1.pop()
    rtts = amt.split("/")
    return rtts[1]


def Base_FileName(parts):
    file_name = []
    word = ""
    while len(parts) > 0:
        temp = parts.pop()
        if temp.find(".") == -1:
            file_name.append(temp)
        else:
            break
    while len(file_name) > 0:
        word += file_name.pop()
    return word

#Function to remove the pages from the cache

def delete_pages():
    global Cache
    global LRU1
    if len(LRU1) > 0:
    	word = LRU1[0]
   # print LRU1[0]
    	del LRU1[0]
    	if word in Cache.keys():
        	del Cache[word]
    
    	my_loc = str(os.path.dirname(os.path.abspath(__file__)))
    	my_root_loc = my_loc + "/cache/" + word
    	if os.path.exists(my_root_loc):
          try:
            subprocess.check_output(["rm", "-f", word])
          except:
            print "Error deleting file from Cache"
            return
'''This function is to upate the LRU1 list.
1. If the file is already present in the LRU1 list it removes it and then again adds it at the of the List.
2. If its not present simply add it to the list.
3. Remove the physical LRU file from the memory.
4.It also defines a new LRU file and copies all its contents into this file.'''
       
def LRU_update(word):
    global LRU1
    if LRU1.count(word) > 0:
        LRU1.remove(word)
        LRU1.append(word)
    else:
        LRU1.append(word)
    try:
        subprocess.call(["rm", "-f", "LRU1"])
    except:
        pass
    try:
        f = open("LRU1", 'w')
        f.write('\n'.join(LRU1))
        f.close()
    except:
        return

'''This function is used to send request to the origin server'''

def req_origin(p):
    try:
        con = httplib.HTTPConnection(origin_serv+":"+str(8080))
        con.request("GET",p)
        response = con.getresponse()
        return response
    except:
        return None          

port_no = int(sys.argv[2])

'''if port_no >= 40000 or port_no <= 65535:
    pass
else:
    print "Invalid Port Number"
    sys.exit()'''



origin_serv = sys.argv[4]

'''if origin_serv == "ec2-54-85-79-138.compute-1.amazonaws.com":
    pass
else:
    print "Incorrect Origin Server name"
    sys.exit()'''

con = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
con.connect(("www.myneu.neu.edu", 80))							#Connecting on port 80						
sysip = con.getsockname()[0]								#Getting system IP
con.close()

load_cache()
loading_LRU()

my_http = HTTPServer((sysip,port_no),MyHTTPHandler)

try:
    my_http.serve_forever()
except:
    my_http.socket.close()
