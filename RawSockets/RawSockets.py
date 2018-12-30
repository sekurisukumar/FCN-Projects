#!/usr/bin/python

import socket, sys, random, fcnt1, collections, urlparse
from struct import *

sack_no = 0
sseq_no = 0
cwnd = 1

def filename(url):
    try:
        spl = url.rsplit('/',1)
        global file_name
        file_name = spl[1]
    except:
        file_name = "index.html"
    return file_name

def check_200(data):

    if "HTTP/" in data:
       if "200 OK" in data:
          return True       
       else:
          print "Error Status Code"
          sys.exit()

def store_data():
    content = collections.OrderedDict(sorted(addict.items()))
    f = open(file_name,'w')    
    for i in content:
        j = str(content[i])
        f.write(j)
    sys.exit()

def pkt(flag,seq_num,ack_num,data,src_mac,dest_mac):
    tcp_head = tcp_header(flag,0,seq_num,ack_num)
    ps_head = pseudoheader(src_ip,dest_ip,tcp_head,data)
    tcp_check = checksum(ps_head)					#Calculate checksum over pseudoheader
    tcp_hdr = tcp_header(flag,tcp_check,seq_num,ack_num)		#Final TCP_ACK header
    ip_head = ip_header(0,src_ip,dest_ip)				#Make IP header
    fin_pkt = ip_head + tcp_hdr + data					#Final Packet
    ip_chksum = checksum(fin_pkt)
    ip_hdr = ip_header(ip_chksum,src_ip,dest_ip)
    ip_packet = ip_hdr + tcp_hdr + data
    ethernet_frame = ethernet(src_mac,dest_mac,0x0800,ip_packet)
    
    return ethernet_frame

def tcp_header(flag,chk_sum,seq_num,ack_num):
    source_port = src_port
    dest_port = 80
    data_off = 5
    flag_get = tcp_flag(flag)   
    adv_window = socket.htons(5840)              #Maximum allowed window size
    urg_ptr = 0
 
    offset = (data_off << 4)
    
    tcp_header = pack('!HHLLBBHHH',source_port,dest_port,seq_num,ack_num,offset,flag_get,adv_window,chk_sum,urg_ptr)

    return tcp_header

def tcp_flag(flag):
    fin = 0
    syn = 0
    rst = 0
    psh = 0
    ack = 0
    urg = 0

    if flag == "ack":
       ack = 1
    elif flag == "syn":
       syn = 1
    elif flag == "fa":
       fin = 1
       ack = 1
    elif flag == "pa":
       psh = 1
       ack = 1
    elif flag == "sa":
       syn = 1
       ack = 1

    fin_flag = fin + (syn << 1) + (rst << 2) + (psh << 3) + (ack << 4) + (urg << 5) 
    return fin_flag    


def ip_header(chksum,src_ip,dest_ip):    
    
    ihl = 5
    ver = 4
    tos = 0
    total_len = 40
    iden = 6545
    frag_off = 0
    ttl = 255
    protocol = socket.IPPROTO_TCP
    check_sum = chksum
    src_addr = socket.inet_aton(src_ip)
    dest_addr = socket.inet_aton(dest_ip)

    ihl_ver = (ver << 4) + ihl

    ip_header = pack('!BBHHHBBH4s4s',ihl_ver,tos,total_len,iden,frag_off,ttl,protocol,check_sum,src_addr,dest_addr)

    return ip_header

def arp(src_hwaddr, src_ipaddr, dest_hwaddr, dest_ipaddr):

    src_hwaddr = src_hwaddr
    src_ipaddr = src_ipaddr
    dest_hwaddr = dest_hwaddr
    dest_ipaddr = dest_ipaddr
    hw_type = 0x0001
    protocol_type = 0x0800
    hw_addrlen = 0x0006
    proto_addrlen = 0x0004
    oprtn = 0x0001

    arp_frame = pack("!HHBBH6s4s6s4s",hw_type,protocol_type,hw_addrlen,proto_addrlen,oprtn,src_hwaddr,src_ipaddr,dest_hwaddr,dest_ipaddr)
    
    return arp_frame

def ethernet(src_mac,dest_mac,typ,data):
    ether_head = pack("!6s6sH",dest_mac,src_mac,typ)
    ether_frame = ''.join([ether_head, data])

    return ether_frame

def checksum(data):
    checksum = 0	       
    
    if len(data)%2!=0:
       checksum = checksum + (ord(data[(len(data)-1)]) & socket.ntohs(0xFF00))
       data += chr(0)
  
    for i in range(0,len(data),2):
        word_16bit = (ord(data[i+1])) + (ord(data[i]) << 8)
        checksum = checksum + word_16bit

    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum = checksum + (checksum >> 16)

    checksum = ~checksum & 0xffff
    return checksum

def pseudoheader(src_ip,dest_ip,tcp_header,data):
    src_addr = socket.inet_aton(src_ip)
    dest_addr = socket.inet_aton(dest_ip)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_len = len(tcp_header)+ len(data)
    ps_hdr = pack('!4s4sBBH',src_addr,dest_addr,placeholder,protocol,tcp_len)
    ps_header = ps_hdr + tcp_header + data
    return ps_header

def send(packet):
    soc.sendto(packet, (dest_ip,80))

def parse_packet(pkt):
    global sack_no
    global sseq_no
    global src_mac
    global dest_mac
    
    eth_protocol, eth_len = parse_eth(pkt)
    if eth_protocol == 8:
       s_addr,d_addr,validate,ip_len,eth_hdrlen = parse_ip(pkt, eth_len)
       if validate == "True":
          seq,ack,validate,flag,lenofdata,data = parse_tcp(s_addr,d_addr,pkt,ip_len,eth_hdrlen)
          if seq!=sack_no and lenofdata!=0:
             print "Retransmission"
             cwnd = 1
	     serv_resp(sseq_no, sack_no, flag, 0, "",src_mac,dest_mac)	
          else:
             if validate == "True":
                serv_resp(seq,ack,flag,lenofdata,data,src_mac,dest_mac)

def parse_arp():

    calcsize("!HHBBH6s4s6s4s")
    arp_frame_unpack = unpack("!HHBBH6s4s6s4s", frame[0:size])
    hw_type = arp_frame_unpack[0]
    proto_type = arp_frame_unpack[1]
    hw_addrlen = arp_frame_unpack[2]
    proto_addrlen = arp_frame_unpack[3]
    oprtn = arp_frame_unpack[4]
    src_hwaddr = arp_frame_unpack[5]
    src_ipaddr = arp_frame_unpack[6]
    dest_hwaddr = arp_frame_unpack[7]
    dest_ipaddr = arp_frame_unpack[8]

    return src_hwaddr
                          
def parse_eth(pkt):
    
    eth_hlen = calcsize("!6s6sH")
    eth_hdr = pkt[:length]
    eth_frame = unpack("!6s6sH",ether_hdr)
    dest_mac = ether_frame[0]
    src_mac = ether_frame[1]
    eth_type = ntohs(ether_frame[2])
    data = pkt[length:]
       
    return eth_type,eth_hlen

def parse_eth_arp(pkt):
    
    eth_hlen = calcsize("!6s6sH")
    eth_hdr = pkt[:length]
    eth_frame = unpack("!6s6sH",ether_hdr)
    dest_mac = ether_frame[0]
    src_mac = ether_frame[1]
    eth_type = ntohs(ether_frame[2])
    data = pkt[length:]
       
    return eth_type,data

def parse_ip(pkt,ether_hlen):

    ip_hdr = pkt[ether_hlen:ether_hlen + 20]    #Extracting the first 20 bytes
    iph = unpack('!BBHHHBBH4s4s',ip_hdr)   #Unpacking it
    ver_ihl = iph[0]    
    ver = ver_ihl >> 4
    ihl = ver_ihl & 0xF
    iph_len = ihl * 4

    ttl = iph[5]
    protocol = iph[6]
    src_addr = socket.inet_ntoa(iph[8])
    dest_addr = socket.inet_ntoa(iph[9])
    
    if dest_addr == src_ip:
       chksum = 0
       ip_header = pack('!BBHHHBBH4s4s',iph[0],iph[1],iph[2],iph[3],iph[4],iph[5],iph[6],chksum,iph[8],iph[9])
       checksum_recvip = checksum(ip_header)
       
       if checksum_recvip == iph[7]:
          validate = "True"

       return src_addr,dest_addr,validate,iph_len,ether_hlen

def parse_tcp(src_addr,dest_addr,pkt,iph_len,eth_len):

    tcp_hdr = pkt[iph_len + eth_len:iph_len + 20 + eth_len]
    tcp = unpack('!HHLLBBHHH',tcp_hdr)
    source_port = tcp[0]
    dest_port = tcp[1]
    seq_no = tcp[2]
    ack_no = tcp[3]
    doff = tcp[4]
    flag = tcp[5]
    chksum = tcp[6]
    tcp_h_len = (doff >> 4)
    hdr_size = iph_len + (tcp_h_len * 4)
    data_size = len(pkt) - hdr_size
    data = pkt[hdr_size:]   
    validate = False
    lenofdata = len(data)
   
    if dest_port == src_port:
       check = 0
       tcp_pack = pack('!HHLLBBHHH',tcp[0],tcp[1],tcp[2],tcp[3],tcp[4],tcp[5],tcp[6],check,tcp[8])
       pseudo_hdr = pseudoheader(dest_addr,src_addr,tcp_pack,data)
       pseudo_chk = checksum(pseudo_hdr)
       pseudo_chk = pseudo_chk >> 8 | ((pseudo_chk & 0x00ff) << 8)
       validate = "True" 
        
       return seq_no,ack_no,validate,flag,lenofdata,data

    else:
       return 0,0,0,0,0,0             	

def gather_data(seq,data):
    
    if ("HTTP" in data) and (seq not in addict) and (len(data)!=0):
       split_resp = strip(data)
       addict[seq] = split_resp
    elif ((seq not in addict) and len(data)!=0):
       addict[seq] = data

def strip(data):

    header = data.split('\r\n\r\n',1)[0]
    data = data.replace(header+'\r\n\r\n','')
    return data

def serv_resp(seq,ack,flag,len_data,data):

    global finish
    global sseq_no
    global sack_no
    global cwnd
    
    if flag == 18:
       send_seq = ack
       send_ack = seq+1
       send_data = ""
       flag = "ack"
       packet = pkt(flag,send_seq,send_ack,send_data,src_mac,dest_mac)
       send(packet)
       if cwnd <= 1000:
           cwnd = cwnd + 1
       else:
           cwnd = 1
       sseq_no = send_seq
       sack_no = send_ack
       global get_req
       if get_req != "True":
          send_data = ("GET" + " %s" + " HTTP/1.0\r\n" + "Host:" + hostname +"\r\n" + "Connection: close\r\n\r\n")%url	  	
          flag = "pa"
          send_pkt = pkt(flag,send_seq,send_ack,send_data,src_mac,dest_mac)
          send(send_pkt)
          if cwnd <= 1000:
              cwnd = cwnd + 1
          else:
              cwnd = 1
          get_req = "True"
    
    elif finish == "True":
		
       send_seq = ack
       send_ack = seq + len_data
       send_data = ""
       flag = "ack"
       packet = pkt(flag,send_seq,send_ack,send_data,src_mac,dest_mac)
       send(packet)
       if cwnd <= 1000:
           cwnd = cwnd + 1
       else:
           cwnd = 1
       sseq_no = send_seq
       sack_no = send_ack
       gather_data(seq,data)
       store_data()

    elif (flag == 16 or flag == 18 or flag == 24) and "HTTP" in data:

       response = check_200(data)
       gather_data(seq,data)
       send_seq = ack
       send_ack = seq + len_data
       send_data = ""
       flag = "ack"
       packet = pkt(flag,send_seq,send_ack,send_data,src_mac,dest_mac)
       send(packet)
       if cwnd <= 1000:
           cwnd = cwnd + 1
       else:
           cwnd = 1
       sseq_no = send_seq
       sack_no = send_ack


    elif (flag == 16 or flag == 18 or flag == 24):

       if len(data) != 0:
          gather_data(seq,data)
          send_seq = ack
          send_ack = seq + len_data
          send_data = ""
          flag = "ack"
          packet = pkt(flag,send_seq,send_ack,send_data,src_mac,dest_mac)
          ack.append(send_ack)
          send(packet)
          if cwnd <= 1000:
              cwnd = cwnd + 1
          else:
              cwnd = 1
          sack_no = send_ack
          sseq_no = send_seq
       else:
          pass
    
    elif (flag == 25 or flag == 17 or flag == 1):
       if len(data)!=0:
          gather_data(seq,data)
       finish = "True"
       send_seq = ack
       send_ack = seq+1+len_data
       send_data = ""
       flag = "fa"
       packet = pkt(flag,send_seq,send_ack,send_data,src_mac,dest_mac)
       ack.append(send_ack)
       send(packet)
       if cwnd <= 1000:
           cwnd = cwnd + 1
       else:
           cwnd = 1
       sack_no = send_ack
       sseq_no = send_seq

def source_ip():
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.connect(("david.choffnes.com",80))
    return sock.getsockname()[0]

def source_mac():

    try:
        intface = "eth0"
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        sock.bind(("eth0",socket.SOCK_RAW))
        src_mac = fcnt1.ioct1(sock.fileno(), 0x8927, pack('256s',intface[:15]))[18:24]
        print src_mac
        return src_mac
    except socket.error:
        print "Socket can't be created"
        sys.exit()

def destination_mac(src_ip,dest_ip,src_mac,iface):

    try:
        dest_hwaddr = pack("!6B", int("FF",16), int("FF",16), int("FF",16), int("FF",16), int("FF",16), int("FF",16))
        ether_data = arp(src_mac,src_ip,dest_hwaddr,dest_ip)
        ether_frame = ethernet(src_mac,dest_mac,0x0806,ether_data)
        
        eth_sock = socket.socket(socket.AF_PACKET,socket.SOCK_RAW)

    except socket.error:
        print "Socket creation error for ARP"

    try:
        eth_sock.bind((iface,socket.SOCK_RAW))
        eth_sock.send(ether_frame)

    except:
        print "Can't find Gateway MAC"
        sys.exit()

    while True:
        recv_ethframe = eth_sock.recv(4096)
        ethernet_type,eth_data = parse_eth_arp(recv_ethframe)
        if ethernet_type == 0x0806:
           break

    destin_mac = parse_arp(eth_data)

    eth_sock.close()
    return destin_mac  

url = sys.argv[1]
#url = "http://david.choffnes.com/classes/cs4700sp16/project4.php"
#url = "http://david.choffnes.com/classes/cs4700sp16/2MB.log"
#url = "http://david.choffnes.com/classes/cs4700sp16/10MB.log"
#url = "http://david.choffnes.com/classes/cs4700sp16/50MB.log"

hostname = urlparse.urlparse(url).hostname
port_no = 80
file_name = filename(url)
addict = {}
packet = ""
get_req = "False"
finish = "False"
global seq_num,soc,rec,src_port,src_ip,dest_ip,src_mac,dest_mac,response
src_ip = source_ip()
dest_ip = socket.gethostbyname(hostname)
src_mac = source_mac()
dest_mac = destination_mac(src_ip,dest_ip,src_mac,"eth0")                          
seq_num = 5000
src_port = random.randint(1025,65535)
response = ""

try:
    soc = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    soc.bind(("eth0",0x0800))
    rec = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    rec.bind(("eth0",0x0800))
    
except socket.error:
    print "Socket can't be created"
    sys.exit()

packet = pkt("syn",seq_num,0,response,src_mac,dest_mac)
send(packet)  

while True:
    recvd = rec.recvfrom(65565)
    parse_packet(recvd[0])

