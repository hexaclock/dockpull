        #fout = open("comments_out.json","w")
        #fout.write(''.join(commentslist))
        #fout.close()

        #print(sys.argv[1])
        #DocumentIDs = getDocumentIDs(sys.argv[1])
        #pool = multiprocessing.Pool(10)
        #for docid in DocumentIDs:
        #    pool.apply_async(func=getComment,args=(docid, ),callback=logComment)
        #pool.close()
        #pool.join()
        #print(len(COMLOG))
        #pool.map(printComment,DocumentIDs)


COMLOG = {}
	
	def getReqAsDict(regtype,ID):
		if "docket" in regtype:
			baseURL = "http://api.data.gov:80/regulations/v3/docket.json?api_key="
			url = baseURL+APIKEY+"&docketId="+ID
		else:
			baseURL = "http://api.data.gov:80/regulations/v3/document.json?api_key="
			url = baseURL+APIKEY+"&documentId="+ID
		req = urllib.request.Request(url)
		req.add_header("Accept","text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
		req.add_header("User-Agent","Mozilla/5.0")
		try:
			response = urllib.request.urlopen(req)
			contents = response.read()
		except urllib.error.HTTPError as error:
			contents = error.read()
		jsondict = json.loads(contents.decode())
		return jsondict

	def getDocket(docketID):
		return getReqAsDict("docket",docketID)

	def getDocument(documentID):
		return getReqAsDict("document",documentID)

	def formatNum(i):
		if i <= 9:
			return "000"+str(i)
		elif i <= 99:
			return "00"+str(i)
		elif i <= 999:
			return "0"+str(i)
		else:
			return str(i)

	def getDocumentIDs(docketID):
		Docket = getDocket(docketID)
		DocIDs = []
		for i in range(1,Docket['numberOfComments']+1):
			DocIDs.append(docketID+"-"+formatNum(i))
		return DocIDs

	def getComment(documentID):
		Doc = getDocument(documentID)
		if 'comment' in Doc:
			return [documentID,Doc['comment']['value']]
		return []

	def logComment(Comment):
		global COMLOG
		if Comment and Comment[0] not in COMLOG:
			COMLOG[Comment[0]] = Comment[1]
		print(len(COMLOG))
		return len(COMLOG)
