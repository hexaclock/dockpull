#Written in python3#
#Daniel Vinakovsky#

import json
import urllib.parse
import urllib.request
import sys
import multiprocessing
import time

class DocketPuller:

        def __init__(self,APIKEY,docketID):
                ###In order to create an instance of this class, we need a data.gov APIKEY, and a docketID###
                self.APIKEY   = APIKEY
                self.docketID = docketID
                self.baseURL  = "http://api.data.gov:80/regulations/v3/documents.json?api_key="+APIKEY
        
        def getCommentPage(self,countsonly,rpp,po):
                ###Get a page of comments.###
                #countsonly = 0 or 1, rpp = results/comments per page (max 1000), po = page offset
                rpp = 1000 if rpp > 1000 else rpp
                url = self.baseURL + "&countsOnly="+str(countsonly) \
                      +"&encoded=0&dktid="+self.docketID+"&rpp="+str(rpp)+"&po="+str(po)
                req = urllib.request.Request(url)
                req.add_header("Accept",
                               "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
                req.add_header("User-Agent","Mozilla/5.0")
                try:
                        response = urllib.request.urlopen(req)
                        contents = response.read()
                except urllib.error.HTTPError as error:
                        contents = error.read()
                return contents

        def getTotalNumComments(self):
                ###Get the total number of comments posted on a docket###
                if not hasattr(self,"numcomments"):
                        kvdict = json.loads(self.getCommentPage(1,10,0).decode())
                        self.numcomments = kvdict["totalNumRecords"]
                return self.numcomments
                
        def getAllComments(self):
                ###Return a list of comment pages, fixed/sanitized for Crimson Hexagon###
                numcomments  = self.getTotalNumComments()
                commentslist = []
                for po in range(0,numcomments,1000):
                        print("Downloading comments "+str(po)+"-"+str(po+1000)+" out of "+str(numcomments),end='')
                        commentslist.append(self.fixNames(self.getCommentPage(0,1000,po)))
                        print(" - done!")
                return commentslist

        def fixNames(self,commentpg):
                ###Change keys/names, and fix values if needed. Delete unnecessary/invalid keys###
                dictlist = json.loads(commentpg.decode())
                dictlist.pop("totalNumRecords",None)
                dictlist["items"] = dictlist.pop("documents",None)
                for comment in dictlist["items"]:
                        documentId          = comment.pop("documentId",None)
                        comment["author"]   = comment.pop("title",None)[13:] 
                        comment["date"]     = comment.pop("postedDate",None)[0:19]
                        comment["contents"] = comment.pop("commentText",None)
                        comment["url"]      = "http://www.regulations.gov/#!documentDetail;D="+documentId
                        comment["title"]    = documentId
                        comment["language"] = "en"
                        comment["type"]     = "regulationsGov"
                        comment.pop("agencyAcronym",None)
                        comment.pop("allowLateComment",None)
                        comment.pop("attachmentCount",None)
                        comment.pop("commentDueDate",None)
                        comment.pop("commentStartDate",None)
                        comment.pop("docketTitle",None)
                        comment.pop("docketType",None)
                        comment.pop("documentStatus",None)
                        comment.pop("documentType",None)
                        comment.pop("numberOfCommentReceived",None)
                        comment.pop("openForComment",None)
                        comment.pop("rin",None)
                        comment.pop("totalNumRecords",None)
                return json.dumps(dictlist)

def runner():
        APIKEY = ""
        if len(sys.argv) != 2:
                print("Usage: python3 DocketPuller.py <DOCKETID>")
                quit()
        dp = DocketPuller(APIKEY,sys.argv[1])
        commentslist = dp.getAllComments()
        print(commentslist[0])

if __name__ == '__main__':
    runner()
