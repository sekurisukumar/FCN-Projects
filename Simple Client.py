#!/usr/bin/python     
import socket        #importing socket library
import sys          #importing sys library
import ssl         #importing ssl library

# Defining a function to execute the required mathematical expression
def math (num1,num2,sign):
    
            if sign == "+":
                  add = int(num1) + int(num2)
                  answer = "cs5700spring2016 %d\n" % add

            elif sign == "-":
                  sub = int(num1) - int(num2)
                  answer = "cs5700spring2016 %d\n" % sub
                  
            elif sign == "*":
                  mul = int(num1) * int(num2)
                  answer = "cs5700spring2016 %d\n" % mul
                 
            else:
                  div = int(num1) / int(num2)
                  answer = "cs5700spring2016 %d\n" % div

            return answer

def splitting(rec):   #Function to split the response message of server
    pa_1 = rec.split()[0]
    pa_2 = rec.split()[1]
    pa_3 = rec.split()[2]
    return (pa_1,pa_2,pa_3)

def solution(word):   #Function to call the math function to perform mathematical operation
    num_1 = word.split()[2]
    op = word.split()[3]
    num_2 = word.split()[4]
    sol = math(num_1,num_2,op)
    return sol
    
# Making up the condition based on the command line arguments

if len(sys.argv) == 6 or len(sys.argv) == 4: #Verifying the length of arguments to implement SSL
      
      if len(sys.argv)== 4: #If the command line consists only 4 arguments            

               port = 27994 #SSL Port Number
               s = sys.argv[1]
               hostname = sys.argv[2]
               neu_id = sys.argv[3]
                                     
      else:
            p = sys.argv[1]
            port = int(sys.argv[2])
            s = sys.argv[3]
            hostname = sys.argv[4]
            neu_id = sys.argv[5]

      if hostname == "cs5700sp16.ccs.neu.edu" or hostname == "cs5700sp16":   #Checking for a valid hostname
                  
                  if s == "-s":
                        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Socket Creation
                        clientsec = ssl.wrap_socket(client)     #Wrapping the socket with SSL 
                        clientsec.connect((hostname,port))  #Establishing a TCP Connection to Server 
                        clientsec.send("cs5700spring2016 HELLO %s\n"%neu_id)

                        while True:
                              response = clientsec.recv(256)       #Receiving the response message of 256 bytes from server
                              (p_1,p_2,p_3)= splitting(response)
                              
                              if p_3 == "BYE":  #Checking the condition for BYE message
                                    print response.split()[1]
                                    sys.exit()

                              elif p_2 == "STATUS": #Checking the condition for STATUS message
                                    ans = solution(response)
                                    clientsec.send(ans)
                              else:
                                    print "Unexpected message"
                                    sys.exit()
            
      else:
          print "Invalid hostname"
                  
                                                            
elif len(sys.argv) == 3 or len(sys.argv) == 5: #Verifying the length of arguments to implement without SSL

    if len(sys.argv) == 5:
        p = sys.argv[1]
        port = int(sys.argv[2])
        hostname = sys.argv[3]
        neu_id = sys.argv[4]

    else:
        port = 27993    #Assuming this port number when SSL is not considered
        hostname = sys.argv[1]
        neu_id = sys.argv[2]

    if hostname == "cs5700sp16.ccs.neu.edu" or hostname == "cs5700sp16":
                 
          client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          client.connect((hostname,port))
          client.send("cs5700spring2016 HELLO %s\n"%neu_id)
  
          while True:
                  response = client.recv(256)
                  (p_1,p_2,p_3)= splitting(response)                  
                                                             
                  if p_2 == "STATUS":
                        ans = solution(response)
                        client.send(ans)
                                                                                    
                  elif p_3 == "BYE":
                        print response.split()[1]
                        sys.exit()

    else:
            print "Invalid hostname"
                                                      
else:
      print "Invalid arguments"   #Error handling for invalid arguments
      sys.exit()
