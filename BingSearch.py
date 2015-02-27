import urllib2
import base64
import json
import string
import sys
import math

topResults = {}
allWords = []
idf = []
docs = {key: list() for key in range(10)}
allDocVectors = {}
stopWords = []

def reset(element):
	""" 
	Clears the contents of list or dictionary element
	"""
	if type(element)==list:
		element[:] = []
	elif type(element)==dict:
		element.clear()

def computeIDF():
	""" 
	Computes IDF values for all words in all documents
	"""
	global idf
	#print 'allWords, before idf: ',allWords
	#print docs
	idf = [0] * len(allWords)
	for i in range(len(allWords)):
		word = allWords[i]
		df = 0
		for j in range(10):
			if word and word in docs[j]:
				df = df + 1
		# if query word is not in any documents. Will not affect later results.
		if df < 1:
			df = .1
		idf[i] = math.log(10/df)

def formatQuery(query):
	""" 
	Formats a query od space separated words to a format needed by Bing URL
	"""
	formattedQuery = "%27"
	for term in query.split():
		formattedQuery = formattedQuery + term + '%20'
	formattedQuery = formattedQuery[0: len(formattedQuery)-3]
	formattedQuery = formattedQuery + '%27'
	return formattedQuery

def getStopWords():
	""" 
	Reads a file containing English stop words and populates the list stopWords
	"""
	f = open('english','r')
	for word in f:
		word = word.strip()
		if word:
			stopWords.append(word)

def getTopResults(formattedQuery, accountKey):
	""" 
	Returns the search results for formattedQuery returned by Bing, in JSON format
	"""
	bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=' + formattedQuery + '&$top=10&$format=json'
	# accountKey = 'OWcbFzI/FPzmWjbmJcs8WSv0oZf1qkZ0Knxpz9nfyDI'
	accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
	headers = {'Authorization': 'Basic ' + accountKeyEnc}
	req = urllib2.Request(bingUrl, headers = headers)
	print '%-18s  =  %s'%('URL', bingUrl)

	response = urllib2.urlopen(req)
	content = response.read()
	return json.loads(content)

def getAllWords(topResults):
	""" Gets all words from titles and descriptions
	Computes termFrequency, inverse-document-frequency
	Populates the dictionary allWords
	"""
	print 'AllWords: prior ' , allWords
	for i in range(0, 10):
		desc = topResults['d']['results'][i]['Description']
		asciiDesc = desc.encode('ascii','ignore')
		title = topResults['d']['results'][i]['Title']
		asciiTitle = title.encode('ascii','ignore')

		# remove punctuation marks
		noPuncDesc = asciiDesc.translate(string.maketrans("",""), string.punctuation)
		noPuncTitle = asciiTitle.translate(string.maketrans("",""), string.punctuation)

		# Add all unique, non-stopwords to allWords - from both title and description
		for word in noPuncDesc.split(' '):
			word = word.lower()
			if word:
				docs[i].append(word)
				if (word not in allWords) and (word not in stopWords):
					allWords.append(word)

		for word in noPuncTitle.split(' '):
			word = word.lower()
			if word:
				docs[i].append(word)
				if (word not in allWords) and (word not in stopWords):
					allWords.append(word)
	
	# in case query words aren't in title or desc
	for word in query.split(' '):
		word = word.lower()
		if word:
			if (word not in allWords) and (word not in stopWords):
				allWords.append(word)
	
def createDocVectors():
	""" 
	Populates allDocVectors with the document vectors of all documents
	"""
	for i in range(10):
		thisDoc = docs[i]
		tf = [0] * len(allWords)
		thisDocVector = [0] * len(allWords)

		# compute term frequencies
		for word in thisDoc:
			if word not in stopWords:
				pos = allWords.index(word)
				tf[pos] = tf[pos] + 1

		# get tf-idf, ntf_idf, and wf_idf values
		for j in range(len(allWords)):
			tf_idf = tf[j]*idf[j]
			ntf_idf = (.3+(1-.3)*(tf[j]/float(max(tf))))*idf[j]
			if tf[j] > 0:
				wf_idf = (1+math.log(tf[j]))*idf[j]
			else: 
				wf_idf = 0
			thisDocVector[j] = [ tf_idf, ntf_idf, wf_idf ]
		
		allDocVectors[i] = thisDocVector
	#print 'docs: ', docs
	#print 'allWords: ', allWords
	#print 'allDocVectors: ', allDocVectors
	
def getQueryVector(query):
	"""
	Computes and returns the query vector for a space-separated string
	"""
	queryVector = [0] * len(allWords)
	for word in query.split():
		pos = allWords.index(word)
		queryVector[pos] = queryVector[pos] + 1
	return queryVector	

def Rocchio(relevance, queryVector, alpha, beta, gamma, method=0):
	""" Computes the modified query from the relevant and non-relevant documents...
		Based on Rocchio's algorithm
	"""
	relDocs = [allDocVectors[i] for i in range(len(allDocVectors)) if relevance[i] == 1]
	nonRelDocs = [allDocVectors[i] for i in range(len(allDocVectors)) if relevance[i] != 1]

	sumRelDocs = [0] * len(allWords)
	for thisRelDoc in relDocs:
		for i in range(len(allWords)):
			sumRelDocs[i] = sumRelDocs[i] + thisRelDoc[i][method]

	sumNonRelDocs = [0] * len(allWords)
	for thisNonRelDoc in nonRelDocs:
		for i in range(len(allWords)):
			sumNonRelDocs[i] = sumNonRelDocs[i] + thisNonRelDoc[i][method]

	term1 = [alpha*i for i in queryVector]
	term2 = [float(beta)/len(relDocs) * i for i in sumRelDocs]
	term3 = [-float(gamma)/len(nonRelDocs) * i for i in sumNonRelDocs]
	
	modQueryVec = [sum(wordCol) for wordCol in zip(term1,term2,term3)]
	return modQueryVec

def getKey(item):
	return item[1]

def getNewQuery(query, queryMod):
	""" 
	Returns augmented query by finding the 2 maximum terms in the query vector
	"""

	# find 2 new words with maximum value
	temp = queryMod[:]
	temp.sort(reverse = True)
	count = 0
	for element in temp:
		pos = queryMod.index(element)
		word = allWords[pos]
		if word not in query:
			query = query + ' ' + word
			count = count + 1
			if count==2:
				break

	# reorder words in new query based on values in the query vector
	temp = []
	for word in query.split(' '):
		if word:
			pos = allWords.index(word)
			value = queryMod[pos]
			temp.append((word,value))
			temp = sorted(temp, key=getKey, reverse = True)
	newQuery = ""
	for (word, val) in temp:
		newQuery = newQuery + ' ' + word
	return newQuery.strip()
	
def printParameters(accountKey, query, precision):
	""" 
	Prints the parameters in the format below
	"""
	print '\nParameters:\n==================='
	print '%-18s  =  %s'%('Client Key',accountKey)
	print '%-18s  =  %s'%('Query', query)
	print '%-18s  =  %s'%('Desired Precision', precision)
	if method == 0:
		print '%-18s  =  %s'%('Weighting Method', 'tf-idf')
	elif method == 1:
		print '%-18s  =  %s'%('Weighting Method', 'ntf-idf')
	elif method == 2:
		print '%-18s  =  %s'%('Weighting Method', 'wf-idf')

def printFeedbackSummary(query, currPrecision, precision):
	""" 
	Prints the parameters in the format below
	"""
	print "\nFEEDBACK SUMMARY:\n==================="
	print '%-10s  =  %s'%('Query', query)
	print '%-10s  =  %s'%('Precision', currPrecision)
	
def usage():
	print """modQueryVec
	python BingSearch.py [accountKey] [precision] ['query']

	"""

if __name__ == "__main__":

	# Expect three arguments: the account key, precision, and space-separated query string within single quotes
	if len(sys.argv)!=4 and len(sys.argv)!=5: 
		usage()
		sys.exit(2)	
	else:
		accountKey = sys.argv[1]
		precision = float(sys.argv[2])
		query = sys.argv[3] 
		try:
			if len(sys.argv)==5:
				method = int(sys.argv[4])
				if method not in range(3):
					raise Exception()
			else:
				method = 0
		except:
			usage()
			sys.exit(2)

		
	currPrecision = 0.0
	reached = 0
	nIter = 1
	
	while currPrecision < precision:
		printParameters(accountKey, query, precision)

		# get results for query
		formattedQuery = formatQuery(query)
		topResults = getTopResults(formattedQuery, accountKey)
		
		# exit if bing returns less than 10 results
	 	numOfResults = len(topResults['d']['results'])
	 	if numOfResults<10:
	 		print 'Bing returned less than 10 results. Exiting.'
	 		sys.exit(2)

	 	print 'Total no of results : ' + str(numOfResults)
	 	print '\nBing Search Results\n==================='

		# form vector space model
		getStopWords()
		getAllWords(topResults)
		computeIDF()
		createDocVectors()
		queryVector = getQueryVector(query)

		#loop over topResults, get feedback
		relevance = [0]*10
		for i in range(10):
			print '\n Result '+ str(i+1) + '\n[\n' + ' URL: '+topResults['d']['results'][i]['DisplayUrl']
			print ' Title: ' + topResults['d']['results'][i]['Title']
			print ' Summary: ' + topResults['d']['results'][i]['Description'] + '\n]'
			uin = raw_input('\nRelevant? [Y/n] ')
			while True:
				if uin is 'y' or uin is 'Y':
					relevance[i] = 1
					break
				elif uin is 'n' or uin is 'N':
					break
				else:
					uin = raw_input("Invalid input, enter 'y' or 'n': ")

		# exit if no relevant documents
		if sum(relevance)==0:
			print 'Below desired precision, but can no longer augment the query.'
			sys.exit(2)

		currPrecision = sum(relevance)/10.0

		if currPrecision>=precision:
			reached = 1
			break

		#print feedback summary
		printFeedbackSummary(query, currPrecision, precision)
		print 'Still below the desired precision of ' + str(precision)
		print 'Indexing Results .... \nAugmenting query ...'

		# get new query vector using Rocchio's Algorithm
		queryMod = Rocchio(relevance, queryVector, 1, .75, .15, method)
		query = getNewQuery(query, queryMod)

		# reset the data structures before next iteration
		reset(allWords)
		reset(topResults)
		reset(docs)
		docs = {key: list() for key in range(10)}
		reset(allDocVectors)
		nIter = nIter + 1

	if reached:
		printFeedbackSummary(query, currPrecision, precision)
		print 'Desired Precision reached in ' + str(nIter) + ' iterations!\n'
			
