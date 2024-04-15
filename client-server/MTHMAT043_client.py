# Matshepo Mathoto
# MTHMAT043
import platform
import sys
from socket import *
import os.path
import hashlib

BUFFERSIZE = 4096
SEPARATOR = "<SEPARATOR>"
#to let the client know the option available
def menu():
    print("\nSelect query from the following option.")
    print("Enter 'U' to upload file.")
    print ("Enter 'V' to view availale files.")
    print("Enter 'D' to download file.")
    print("Enter 'I' to file information.")
    print("Enter 'H' to Hidden files.")
    print("Enter 'R' to delete a file")
    print("Enter 'C' to close the server")
    print ("Enter 'E' to exit.")


def get_hex(name_of_file):
    hasher = hashlib.md5()
    openfile = open(name_of_file, "rb")
    content = openfile.read()
    hasher.update(content)
    return hasher.hexdigest()

def upload_File(Socket,filename,filesize):
    open_file = open(filename, "rb")
    print("Sending to the server...")
    #get a line to send to the server
    line = open_file.read(BUFFERSIZE)   
    byte =0
    jump =0
    #while the files have more lines
    while(line):
        Socket.send(line)
        percentage = byte/(filesize+1) *100

        if int(percentage) >=jump:
            print("Uploading:", round(percentage, 2), "%")
            jump += 10
        #receive message from the socket
        Socket.recv(BUFFERSIZE).decode()
        byte+=BUFFERSIZE
        line = open_file.read(BUFFERSIZE)
    #completed sending the file line
    print("Uploading: 100%")
    Socket.send(b"DONE!")
    open_file.close()


def checkAndDownload(Socket,filename):

    line = Socket.recv(BUFFERSIZE)
    # print("____",line)
    if line == b"Failed!":
        print("File \"" + filename + "\" was not found!")
        return 0
    #separate the string into an info array

    info = line.decode()
    info = info.split(SEPARATOR)
    protected = info[0]
    filesize = int(info[1])

    #send both the inputs to server to be stored 
    if protected == "Y":
        key = input("The file is protected, Enter key:\n")
        Socket.send(key.encode())
    elif protected == "N":
        Socket.send("0000".encode())
    # receive the permission message
    permission = Socket.recv(BUFFERSIZE).decode()
    
    if permission == "DENIED":
        print("Incorrect key. Request failed!")
        return 0
    else:
        print("Accepted")
    #print("Problem2")
    return downloadFile(filename, filesize, Socket)

def check_sum(serverFile,ClientFile):
    if serverFile == ClientFile:
        return True
    return False

def downloadFile(filename, filesize, Socket):
    # open file to write data from the socket
    #print("Problem3")
    open_file = open(filename,"wb")
    print("Downloading file...")

    byte =0
    jump=0
    Socket.send("Receiving..".encode())
    line = line = Socket.recv(BUFFERSIZE)

    while(line != b"DONE!"):
        percentage = byte/(filesize+1)*100

        if int(percentage)>=jump:
            print("Downloading progress: ",round(percentage, 2),"%")
            jump += 10
        open_file.write(line)
        # print(line)
        Socket.send("Receiving..".encode())
        line =Socket.recv(BUFFERSIZE)
        byte +=BUFFERSIZE

    print("Download Complete: 100%")
    open_file.close()
    return 1


def main():
    # for user to be able to delete we will use the username and password to keep\
    # track
    username = input("Enter username:\n")
    password = input("Enter user password:\n")
    args_num = len(sys.argv)

    if args_num<=3:
        host = "NDLMDU011"
        port = 120
        menu()
        query = input("Enter a query or request:\n")
        query = (query.upper())[0:1]

    else:
       host =sys.argv[1]
       port = int(sys.argv[2])
       query = (sys.argv[3])[0:1].upper()
    
    while True:
       if query == "E":
           break
       # define socket and connect the client to the server
       Socket = socket(AF_INET,SOCK_STREAM)
       Socket.connect((host,port))
    
       # Check for the user desired query
       if query == "U":
           filename = input("Enter file name to upload to the server:\n")
           fileExists = os.path.exists(filename)
            
            # check what this does
           
           while fileExists ==False:
               print(filename + " does not exist.")
               filename = input("Enter file name to upload to the server:\n")
               fileExists = os.path.exists(filename)
            
           filesize = os.path.getsize(filename)
           base_name = os.path.basename(filename)
           
           #ask if the file is open or private
           visible = input("Should the file be visible to all users, Y/N?\n").upper()
           Vpin ="0000"
           if visible[0:1] =="N":
               Vpin = input("Enter the code to view the file by:\n")
           
           protected = input("Encrypt the File, Y/N?\n").upper()
           Ppin = "0000"
           if protected[0:1].upper() == "Y":
               pin = input("Enter an encryption key:\n")
           hexValue = get_hex(filename)
           # send the upload request to the server
           Socket.send(query.encode())

           print("from server:",Socket.recv(BUFFERSIZE).decode()) 

           Socket.send(base_name.encode('utf-8'))
           #send the fileinfo to the server
           newFilename =Socket.recv(BUFFERSIZE).decode()

           upload_File(Socket,filename,filesize)
           print("Done Uploading.")
           message = Socket.recv(BUFFERSIZE).decode()

           #Add the infomation to the dictionary FileInfo = [Visibility, Protected, Key, hexValue, fileSize, clientName, Password]
           fileInf = visible[0:1] + SEPARATOR + protected[0:1] + SEPARATOR + Ppin + SEPARATOR + hexValue + SEPARATOR +str(filesize) + SEPARATOR + username+ SEPARATOR + password + SEPARATOR + Vpin
           
           Socket.send(fileInf.encode())
           print("From server: ",Socket.recv(BUFFERSIZE).decode())
           # print(fileInf)
    
       elif query =="D":
           Socket.send(query.encode())

           print("From Server: ", Socket.recv(BUFFERSIZE).decode())
           filename = input("Enter file name to Download to the server:\n")
           base_name = os.path.basename(filename)
           Socket.send(base_name.encode())

           results = checkAndDownload(Socket,filename)
           # If a file doesn't exist
           if(results ==0):
                pass
           else:
               Socket.send("SendInfo".encode())
               serverFile = Socket.recv(BUFFERSIZE).decode()
               client_File_hexV = get_hex(filename)
               # To compare the files if they are not corrupted
               print("Hex:", serverFile, client_File_hexV)
               if check_sum(serverFile,client_File_hexV):
                   print("The file were successful in tansist")
               else:
                   print("The file was corrupted in tansist")

       elif query =="V":
           Socket.send(query.encode())
           print("Loading file list...")
            # receive the filename and check if it is not Done to terminate
            # the loop
           line = Socket.recv(BUFFERSIZE).decode()
           count =1
           while line !="DONE!":
               Socket.send("Receiving".encode())
               print(count,". ", line)
               line = Socket.recv(BUFFERSIZE).decode()
               count+=1
           print("List View complete")

       elif query == "H":
           passCode = input("Enter pass code:\n")

           Socket.send(query.encode())
           #check what is being received 
           msg = Socket.recv(BUFFERSIZE).decode()

           Socket.send(passCode.encode())
           line = Socket.recv(BUFFERSIZE).decode()
            # get the code to check if the client have some 
            # acess to the encypted files
           if line == "NONE":
               print("Access Denied.")
               pass
           else:
               count =1
               while line != "DONE!":
                   Socket.send("Receiving..".encode())
                   print(count, ".",line)
                   line = Socket.recv(BUFFERSIZE).decode()
                   count+=1
               print("List View complete")

       elif query == "I":
            print("File Information")
            Socket.send(query.encode())
            inputs = Socket.recv(BUFFERSIZE).decode()
            # get the base name of the file
            filename = input("Enter the name of the File:\n")
            baseFile = os.path.basename(filename)
            Socket.send(baseFile.encode())
            # print the information of a file
            print(Socket.recv(BUFFERSIZE).decode())
            
       elif query == "R":
            filename = input("Enter the name of the file to remove:\n")
            baseFile = os.path.basename(filename)  
            # details of the user to be sent
            line = baseFile + SEPARATOR + username + SEPARATOR + password
            
            Socket.send(query.encode())
            msg = Socket.recv(BUFFERSIZE).decode()
            Socket.send(line.encode())
            print("File was sucessfully deleted.")


       elif query == "C":
           Socket.send(query.encode())
           print("Server:", Socket.recv(BUFFERSIZE).decode())
           break
       else:
           print("Query Does not exist.\n")
       Socket.close()

       menu()
       query = input("\nEnter a query or request: \n")
       query = (query.upper())[0:1]


if __name__ == "__main__":
    main()
