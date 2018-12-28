import socket
import sys
from HTMLParser import HTMLParser

# Defining the variables needed for the code

cs_token = ""
sess_id = ""
urls = []
visited = []
flags = []

# Defining a function to download the first page

def down_page(url):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                   # Creating a socket for comunication with the server
    sock.connect((hostname, port_no))                                                          # Establishing a TCP connection with the Server  
    first_get= ("GET" + " %s" + " HTTP/1.1\n" + "Host:" +  hostname +"\r\n\r\n")%url           # Sending the GET request
    sock.send(first_get)
    response = sock.recv(4096)

#Checking for the 200 response code and extracting csrftoken and sessionid

    if "200" in response:                       
        spl = response.split()
        for c_id in spl:
            if "csrftoken=" in c_id:
               global cs_token
               cs_token=c_id[len("csrftoken")+1:len(c_id)-1]   
        for s_id in spl:
            if "sessionid=" in s_id:
                global sess_id
                sess_id=s_id[len("sessionid")+1:len(s_id)-1]
        sock.close()
        
    else:
        error_handler1(response)   

# Defining a function to login into fakebook and send a POST request

def login_page(url):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, port_no))
    user = sys.argv[1]                                       #Passing the username as argument
    passw = sys.argv[2]                                      #Passing the Password as argument

# Sending a POST request to login to the first page

    data = "csrfmiddlewaretoken="+cs_token+"&"+"username="+user+"&"+"password="+passw+"&"+"next="+"%2Ffakebook%2F"
    post_req= "POST /accounts/login/ HTTP/1.1\r\n"+"Host: cs5700sp16.ccs.neu.edu\r\n"+"Content-Length: 109\r\n"+"Content-Type: application/x-www-form-urlencoded\r\n"+"Cookie: csrftoken="+ cs_token +";sessionid="+ sess_id + ";\r\n\r\n"+ data
    sock.send(post_req)
    respo = sock.recv(4096)
    sock.close()

# Checking for the 302 response code and extracting the Location url and sessionid

    if "302" in respo:                      
        spl = respo.split()
        i = 0
        for word in spl:
            i = i + 1
            a = i
            if word == "Location:":
               Location = spl[a] 
               break
            
            if "sessionid" in word:
                global sid
                sid=word[len("sessionid")+1:len(word)-1]
                 
        response = get_page(sid, Location)          # Downloading the appropriate page
	crawl(response, sid, Location)              # Starting the crawling

# To Check the condition of invalid username or password

    elif "200" in respo:
        print "Invalid Username or Password"

# To Handle the HTTP Status codes

    else:
        error_handler2(respo)
                
# To Define a class to fetch href, handle, store and print the flags
 
class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.h2_flag = 0
		self.curr_flag = 0
    
    def handle_starttag(self, tag, attrs): 
        if tag == "a":
	     for attr in attrs:
                 if attr[0] == "href" and attr[1].startswith("/fakebook"):
                      urls.append(attr[1])
        if tag == "h2":
             for attr in attrs:
                 if attr[0] == "class" and attr[1] == "secret_flag":
                      self.h2_flag = 1

    def handle_data(self, data):
        if self.h2_flag == 1:
             if flags.count(data) == 0:
	       temp = get_flag_value(data)
	       if temp != None:
	         flags.append(get_flag_value(data))
		 print temp
	     self.h2_flag = 0

# Extracting the flags from the response data

def get_flag_value(data):
        spl =data.split(" ",1)
	try:
	  z=spl.index("FLAG:")
	except:
	  return None
	return spl[z+1]

# Parsing the HTML Page

def htmlparse(page):
    parser = MyHTMLParser()
    parser.feed(page)

# Defining a function to perform Webcrawling

def crawl(resp, sid, Location):
      
      curr_url = Location
      htmlparse(resp)
      visitedFlag = 1
      while True:
	if visitedFlag == 1:
	  visited.append(curr_url)
	  visitedFlag = 0
	while True:
	  curr_url = urls[0]
	  del urls[0]
	  if visited.count(curr_url) == 0:
	    break
	resp = get_page(sid, curr_url)
	op = error_handler3(resp)

# Handling an appropriate status codes and performing necessary action
	
	if op == "200" and resp!=None:
            htmlparse(resp)
	    visitedFlag = 1
        elif op == "301":
            spl = resp.split()
            for word in spl:
                if word == "Location:":
                    i = spl.index("Location:")
                    url = spl[i+1]
		    urls.insert(0, url)
        elif op == "500":
	    urls.insert(0, curr_url)
        elif op == "403" or op == "404":
            pass            
	if len(flags) == 5:
	  break;

# Function to download the page at each intermediate stage of crawling

def get_page(sid, Location):
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
      sock.connect((hostname, port_no))

# Sending a GET request to download the Page

      toget=("GET " + "%s" + " HTTP/1.1\n" + "Host:" +  hostname + "\r\nCookie: csrftoken="+ cs_token +";sessionid="+sid+";\r\n\r\n")%Location
      sock.send(toget)
      response = sock.recv(4096)
      sock.close()
      #if "200" in response:
      return response
      #else:
          #error_handler3(response)

# Defining the error handler function to handle HTTP Status codes during downloading the First Page

def error_handler1(resp):

    if "301" in resp:
        spl = resp.split()
        for word in spl:
            if word == "Location:":
                i = spl.index("Location:")
                url = spl[i+1]
                down_page(url)

    elif "403" or "404" in resp:
        down_page(login_form)
    else:
        down_page(login_form)
       
# Defining the error handler function to handle HTTP Status codes during login at the Login page

def error_handler2(resp):

    if "301" in resp:
        spl = resp.split()
        for word in spl:
            if word == "Location:":
                i = spl.index("Location:")
                url = spl[i+1]
                login_page(url)
                
    elif "403" or "404" in resp:
        login_page(login_form)
    else:
        login_page(login_form)
    
# Defining the error handler function to handle HTTP Status codes during Crawling

def error_handler3(resp):

    if resp!=None:
        
        if "200" in resp:
            return "200"
        elif "301" in resp:
            return "301"
        elif "403" in resp:
            return "403"
        elif "404" in resp:
            return "404"
        else:
            return "500"
    else:
	return None
        
# Defining the hostname and portnumber for establishing a TCP connection to Server
              
hostname = "cs5700sp16.ccs.neu.edu"
port_no = 80
global login_form
login_form = "http://cs5700sp16.ccs.neu.edu/accounts/login/?next=/fakebook/"    # Specifying the starting URL for the Webcrawler
down_page(login_form)
login_page(login_form)
