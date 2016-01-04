#Written in python3#
#Daniel Vinakovsky#

import requests
from DocketPuller import *

class DocketPusher:

    def __init__(self,username,password,REGAPIKEY,docketID):
        ###When creating an instance of this class, automatically authenticate and get authtoken###
        self.username  = username
        self.password  = password
        self.REGAPIKEY = REGAPIKEY
        self.docketID  = docketID
        self.baseURL   = "https://api.crimsonhexagon.com/api/"
        self.authenticate()
        self.puller    = DocketPuller(REGAPIKEY,docketID)

    def authenticate(self):
        ###Authenticate against Crimson Hexagon servers using provided username and password###
        url = self.baseURL+"authenticate?username=" + \
              self.username+"&password="+self.password
        req = urllib.request.Request(url)
        req.add_header("Accept",
                       "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
        req.add_header("User-Agent","Mozilla/5.0")
        try:
            response = urllib.request.urlopen(req)
            contents = response.read()
        except urllib.error.HTTPError as error:
            contents = error.read()
        kvdict = json.loads(contents.decode())
        if kvdict["status"] == "error":
            self.authtoken = ""
        elif kvdict["status"] == "success":
            self.authtoken = json.loads(contents.decode())["auth"]
        return self.authtoken

    def pushCommentPages(self):
        ###Get all comments using DocketPuller, then push them to Crimson Hexagon###
        pageslist = self.puller.getAllComments()
        url       = self.baseURL+"content/upload?auth="+self.authtoken
        req       = urllib.request.Request(url)
        pagenum   = 0
        req.add_header("Accept",
                    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
        req.add_header("User-Agent","Mozilla/5.0")
        req.add_header("Content-Type","application/json")
        for commentpage in pageslist:
            print("Uploading comment page: "+str(pagenum)+"/"+str(len(pageslist))+" to Crimson Hexagon",end='')
            try:
                response = urllib.request.urlopen(req,commentpage.encode('utf-8'))
                contents = response.read()
            except urllib.error.HTTPError as error:
                contents = error.read()
            result = json.loads(contents.decode())
            print(" - "+result["status"]) if "status" in result else print(" - failed")
            pagenum+=1
        return True

def main():
    USER = ""
    PASS = ""
    APIKEY = ""
    if len(sys.argv) != 2:
        print("Usage: python3 DocketPusher.py <DOCKETID>")
        quit()
    pusher = DocketPusher(USER,PASS,
            APIKEY,sys.argv[1])
    pusher.pushCommentPages()

if __name__ == '__main__':
    main()

