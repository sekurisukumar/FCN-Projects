#!/usr/bin/python

from struct import *
from random import randint
import socket, sys
import threading, time, thread
import json, subprocess
import httplib, urllib

count = 0

Opt = {}

################################################## Creating a dictionary for hosts ###########################################################

Hosts = {}
Hosts["Virginia"] = "ec2-54-85-32-37.compute-1.amazonaws.com"
Hosts["Oregon"] = "ec2-52-38-67-246.us-west-2.compute.amazonaws.com"
Hosts["California"] = "ec2-54-193-70-31.us-west-1.compute.amazonaws.com"
Hosts["Ireland"] = "ec2-52-51-20-200.eu-west-1.compute.amazonaws.com"
Hosts["Singapore"] = "ec2-54-169-117-213.ap-southeast-1.compute.amazonaws.com"
Hosts["Tokyo"] = "ec2-52-196-70-227.ap-northeast-1.compute.amazonaws.com"
Hosts["Sydney"] = "ec2-52-63-206-143.ap-southeast-2.compute.amazonaws.com"
Hosts["Sao_Paulo"] = "ec2-54-233-185-94.sa-east-1.compute.amazonaws.com"
Hosts["Frankfurt"] = "ec2-52-29-65-165.eu-central-1.compute.amazonaws.com"

##################################################### List of EC2 Host Names #################################################

EC2 = ("Virginia","Oregon","California","Ireland","Singapore","Tokyo","Sydney","Sao_Paulo","Frankfurt")

####################################################### IP addresses of EC2 Servers ##############################################

Ipaddr = {}
Ipaddr["Virginia"] = "54.85.32.37"
Ipaddr["Oregon"] = "52.38.67.246"
Ipaddr["California"] = "54.193.70.31"
Ipaddr["Ireland"] = "52.51.20.200"
Ipaddr["Singapore"] = "54.169.117.213"
Ipaddr["Tokyo"] = "52.196.70.227"
Ipaddr["Sydney"] = "52.63.206.143"
Ipaddr["Sao_Paulo"] = "54.233.185.94"
Ipaddr["Frankfurt"] = "52.29.65.165"

##################################### Defining Class for implementation on EC2 Servers ############################################

class repeat(threading.Thread):
    def __init__(self, interval, fun, *args):
        threading.Thread.__init__(self)
        self.interval = interval
        self.fun = fun
        self.args = args
        self.runable = True
    def run(self):
        while self.runable:
             self.fun(*self.args)
             time.sleep(self.interval)
    def stop(self):
        self.runable = False

lock = threading.RLock()

################################# Function to parse the DNS Query message ############################################################################

def dns_resp(packet,client_ip):
    iden,flags,qcount,acount,nscount,arcount = parse_dns(packet)
    qname,qtype,qclass = parse_query(packet[12:])

############################################ Validation of Domain name #################################################################################

    if qname == domain:        
       dns_hdr = header(iden,flags,qcount,acount,nscount,arcount)
       dns_query = send_query(qname,qtype,qclass)
       ################################### Creation of Threads for EC2 Servers ##########################################################################

       Sao_PauloThread = repeat(40, Scamper, "Sao_Paulo", port)
       CaliforniaThread = repeat(40, Scamper, "California", port)
       VirginiaThread = repeat(40, Scamper, "Virginia", port)
       IrelandThread = repeat(40, Scamper, "Ireland", port)
       TokyoThread = repeat(40, Scamper, "Tokyo", port)
       SydneyThread = repeat(40, Scamper, "Sydney", port)
       SingaporeThread = repeat(40, Scamper, "Singapore", port)
       OregonThread = repeat(40, Scamper, "Oregon", port)
       FrankfurtThread = repeat(40, Scamper, "Frankfurt", port)

###################################################### Starting the Threads ##############################################################################
       startThreads(Sao_PauloThread, CaliforniaThread, VirginiaThread, IrelandThread, TokyoThread, SydneyThread, SingaporeThread, OregonThread, FrankfurtThread)
       ipaddr = bestserver(client_ip)
       print ipaddr
       dns_sendans = answer(ipaddr)
       final_pkt = dns_hdr + dns_query + dns_sendans
       return final_pkt
    else:
	print "No name"
	sys.exit()

#################################### Function to start the threads for 9 EC2 Servers #######################################################

def startThreads(thr1,thr2,thr3,thr4,thr5,thr6,thr7,thr8,thr9):
   thr1.start()
   thr2.start()
   thr3.start()
   thr4.start()
   thr5.start()
   thr6.start()
   thr7.start()
   thr8.start()
   thr9.start()

################################# Function to parse DNS Packet Header #####################################################################################

def parse_dns(data):
    iden = 0
    flags = 0
    qcount = 0
    acount = 0
    nscount = 0
    arcount = 0

    iden,flags,qcount,acount,nscount,arcount = unpack('!HHHHHH',data[:12])

    return iden,flags,qcount,acount,nscount,arcount

####################################### Function to parse the DNS Question field ########################################################################

def parse_query(data):
    qname = ''
    qtype = 0
    qclass = 0

    p = 0
    while ord(data[p]) != 0:
       p += 1
    (qtype,qclass) = unpack('!HH',data[p+1:p+5])

    s = []
    p1 = 0
    while p1 <= p:
        count = ord(data[p1])
        p1 += 1
        if count == 0:
            break
        s.append(data[p1:p1+count])
        p1 += count
    qname = '.'.join(s)
    return qname,qtype,qclass

################################### Function to build the send header ############################################################

def header(iden,flags,qcount,acount,nscount,arcount):

    siden = iden
    sflags = 0x8180
    sqcount = 1
    sacount = 1
    snscount = 0
    sarcount = 0

    send_hdr = pack('!HHHHHH',siden,sflags,sqcount,sacount,snscount,sarcount)

    return send_hdr

#################################### Function to build the send Question field ####################################################

def send_query(qname,qtype,qclass):

    query = "".join(chr(len(l)) + l for l in qname.split('.'))
    query += '\x00'
    query += pack('!HH',qtype,qclass)
    return query

#################################### Function to build the send Answer field ########################################################

def answer(ip):
    ttl = 60
    data_len = 4
    
    ans = "\xc0\x0c\x00\x01\x00\x01" + pack('!LH4s',ttl,data_len,socket.inet_aton(ip))
    return ans

#################################### Function to calculate RTT Value ###############################################################

def getRTT(host):
    connect = httplib.HTTPConnection(host)
    values = urllib.urlencode({'a': 1,'b': 2,'c': 3})
    hdrs = {"DNSScamper":"RunScamper"}
    connect.request("GET","/",values,hdrs)
    response = connect.getresponse()
    return str(response.read())

################################### Storing the RTT Value in the dictionary ########################################################

def Scamper(host_name, port):
    global Opt
    host = Hosts[host_name]
    host += ":" + str(port)
    rtt = getRTT(host)
    Opt[host_name] = str(rtt)

################################## Finding the best server ###########################################################################

def bestserver(clientIP):
  global Opt
  minNum = sys.float_info.max
  servername = ""
  if allKeys():
      for n in Opt.keys():
        value = Opt[n]
        if float(value) < minNum:
          minNum = float(value)
          servername = n
  else:
       servername = NextAvailableServer()
  
  return Ipaddr[servername]

def allKeys():
  global Opt
  if "Sao_Paulo" in Opt.keys() and "Sydney" in Opt.keys() and "Singapore" in Opt.keys() and "Oregon" in Opt.keys():
     if "California" in Opt.keys() and "Virginia" in Opt.keys() and "Tokyo" in Opt.keys() and "Ireland" in Opt.keys() and "Frankfurt" in Opt.keys():
         return True
     else:
         return False
  else:
      return False

#################################### Calculating the Next Available Server ##################################################################

def NextAvailableServer():
   global EC2
   global count
   head = count%8
   count += 1
   return EC2[head]

##################################### Function to Stop the threads for 9 EC2 Servers ########################################################

def stopThreads(t1,t2,t3,t4,t5,t6,t7,t8,t9):
   t1.stop()
   t2.stop()
   t3.stop()
   t4.stop()
   t5.stop()
   t6.stop()
   t7.stop()
   t8.stop()
   t9.stop()

################################################## Defining global variables ############################################################

global ipaddr,domain
ipaddr = ""
clientIP = ""
localip = ""
port = ""
domain = ""

################################################ Getting the IP address of localmachine #####################################################

try:
   s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
   s.connect(("david.choffnes.com",80))
   localip = s.getsockname()[0]
   s.close()

except:
   print "Socket Creation error"
   sys.exit()

################################################# Checking the Valid Port number and domain #####################################################

try:
    port = int(sys.argv[2])
    if port < 40000 or port > 65535:
       print "Invalid Port number"
       sys.exit()
    domain = sys.argv[4]

except:
    print "Invalid Port or domain"
    sys.exit()   


######################################################### Creation of UDP Socket #####################################################################
try:
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('',port))

except:
    print "UDP Socket can't be created" 
    stopThreads(Sao_PauloThread, CaliforniaThread, VirginiaThread, IrelandThread, TokyoThread, SydneyThread, SingaporeThread, OregonThread, FrankfurtThread)
    sys.exit()

##################################################### Receiving the data on the Socket #################################################################
try:
    while True:
        data,addr = udp_sock.recvfrom(1024)
        send_data = dns_resp(data,addr)
        udp_sock.sendto(send_data,addr)

except KeyboardInterrupt:
     print "Exiting the Program"
     stopThreads(Sao_PauloThread, CaliforniaThread, VirginiaThread, IrelandThread, TokyoThread, SydneyThread, SingaporeThread, OregonThread, FrankfurtThread)  
     udp_sock.close()
     sys.exit()
