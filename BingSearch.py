import urllib2
import base64
import json
import string
import sys
import math

topResults = {}
allWords = {}
docs = {key: list() for key in range(10)}
termFreqs = []
#tf_Idf = []
stopWords = []

def reset(element):
	""" 
	Clears the contents of list or dictionary element
	"""
	if type(element)==list:
		element[:] = []
	elif type(element)==dict:
		element.clear()

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
	print '%-10s  =  %s'%('URL', bingUrl)

	response = urllib2.urlopen(req)
	content = response.read()
	return json.loads(content)

def getAllWords(topResults):
	""" Gets all words from titles and descriptions
	Computes termFrequency, inverse-document-frequency
	Populates the dictionary allWords
	"""
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
				if allWords.has_key(word)==0 and (word not in stopWords):
					allWords[word] = [0,0]

		for word in noPuncTitle.split(' '):
			word = word.lower()
			if word:
				docs[i].append(word)
				if allWords.has_key(word)==0 and (word not in stopWords):
					allWords[word] = [0,0]
	
	# in case query words aren't in title or desc
	for word in query.split(' '):
		word = word.lower()
		if word:
			if allWords.has_key(word)==0 and (word not in stopWords):
				allWords[word] = [0,0]
	
	# put term frequencies and idf's in allWords dictionary
	for word in allWords.keys():
		for i in range(10):
			if docs[i].count(word) > 0:
				allWords[word][0] += 1
				allWords[word][1] = math.log(10./allWords[word][0])

	#essentially our document vectors:
	#term frequency: number of occurences of every word in every document
	#global termFreqs 
	#termFreqs = [[docs[docKey].count(word) for word in allWords.keys()] for docKey in docs.keys()]

	#tf-idf: number of occurences of every word in every document, normalized by log(N/df)
	#global tf_Idf
	#tf_Idf = [[docs[docKey].count(word)*allWords[word][1]  for word in allWords.keys()] for docKey in docs.keys()]
	#print "tfIdf: \n",tf_Idf
	#return tf_Idf	


def term_freqs(docs, allWords):
	""" Computes and returns the term frequencies, given the list of words, and the words in each document.
	docs: a representation of a document simply consisting of a list of the words in the title and description
	allWords: the word vector (expanded list of all words in the query and the documents)
	"""
	global termFreqs 
	termFreqs = [[docs[docKey].count(word) for word in allWords.keys()] for docKey in docs.keys()]
	return termFreqs

def tf_idf(docs, allWords):
	""" Computes and returns the tf-idf = abs(termFreqs*inverseDocFreq) for all words in each document.
	docs: a representation of a document simply consisting of a list of the words in the title and description
	allWords: the word vector (expanded list of all words in the query and the documents)
	"""
	global tf_Idf
	tf_Idf = [[abs(docs[docKey].count(word)*allWords[word][1])  for word in allWords.keys()] for docKey in docs.keys()]
	#print tf_Idf
	return tf_Idf

def max_tf_normalize(a,termFreqs):
	""" Maximum tf Normalization
	a: constant, generally set at .4
	termFreqs: the term frequencies of words in each document
	"""	
	#tf-idf: number of occurences of every word in every document, normalized by log(N/df)
	maxNormTermFreqs = [[]]*len(termFreqs)
	for i in range(len(termFreqs)):
		maxTF = max(termFreqs[i])
		maxNormTermFreqs[i] = [a+(1-a)*( tf/float(maxTF) ) for tf in termFreqs[i]]
	return maxNormTermFreqs

def ntf_idf(a,termFreqs, allWords):
	""" Gets the Maximum normalized tf-idf, or ntf_idf
	a: constant, generally set at .4
	termFreqs: the term frequencies of words in each document
	allWords: the word vector (expanded list of all words in the query and the documents)
	"""
	maxNormTermFreqs = max_tf_normalize(a,termFreqs)
	ntf_idf = [[]]*len(termFreqs)
	for i in range(len(termFreqs)):
		ntf_idf[i] = [ntf*allWords[word][1] for (ntf,word) in zip(maxNormTermFreqs[i],allWords)]
	return ntf_idf

def getQueryVector(query, allWords):
	""" Computes and returns the queryVector
		query: the query as a simple white-space-delimited string
	 allWords: the word vector (expanded list of all words in the query and the documents)
	"""
	lquery = query.split(' ')
	# this can't be right... should the 
	queryVector = [1 if word in lquery else 0 for word in allWords.keys()]
	return queryVector

def sim(queryVector, docVectorWeight):
	""" Computes the similarity between two items of the smae length
	Not Used!	
	"""
	#Euclidian length (norm)
	normQuery = math.sqrt(sum([p*p for p in queryVector]))
	normDoc = math.sqrt(sum([p*p for p in docVectorWeight]))
	#dot product (would be easier if we were using numpy)
	sim = sum((p*d) for (p,d) in zip(queryVector, docVectorWeight)) / (normQuery*normDoc)
	return sim

def sims(queryVector,docVectorWeights):
	""" Computes the similarities between the query and all documents
	Not Used!
	"""
	sims = [0]*10
	for i in range(10):
		sims[i] = sim(queryVector,docVectorWeights[i])
	return sims

def Rocchio(relevance, queryVector, Docs, alpha, beta, gamma):
	""" Computes the modified query from the relevant and non-relevant documents...
		Based on Rocchio's algorithm
	"""
	relDocs = [Docs[i] for i in range(len(Docs)) if relevance[i] == 1]
	nonRelDocs = [Docs[i] for i in range(len(Docs)) if relevance[i] != 1]
	
	sumRelDocs = [sum(wordCol) for wordCol in zip(*relDocs)]
	sumNonRelDocs = [sum(wordCol) for wordCol in zip(*nonRelDocs)]

	term1 = [alpha*i for i in queryVector]
	term2 = [float(beta)/len(relDocs) * i for i in sumRelDocs]
	term3 = [-float(gamma)/len(nonRelDocs) * i for i in sumNonRelDocs]
	
	modQueryVec = [sum(wordCol) for wordCol in zip(term1,term2,term3)]
	
	return modQueryVec

def getNewQuery(query, allWordsKeys, queryMod):
	""" 
	Returns augmented query by finding the 2 maximum terms in the query vector
	query: string the original query 
	allWordsKeys: the list of all possible words
	queryMod: the computed word scores for every word from Rocchio's algorithm
	"""

	words = query.split(' ')
	values = zip(queryMod,allWordsKeys)
	for i in range(len(values)):
		if values[i][1] not in words:
			maxVal1 = values[i]
			maxVal2 = values[i]
	for tup in values:	
		if tup[0] > maxVal1[0] and tup[1] not in words:
			maxVal1 = tup
		elif tup[0] > maxVal2[0]  and tup[1] not in words:
			maxVal2 = tup
	return query + ' ' + maxVal1[1] + ' ' + maxVal2[1]

def orderQuery(newQuery, allWordsKeys, queryMod):
	"""
	"""
	queryWords = newQuery.split(' ')
	temp = ''
	
	
	return orderedQuery
	
def printParameters(accountKey, query, precision):
	""" 
	Prints the parameters in the format below
	"""
	print '\nParameters\n==================='
	print '%-10s  =  %s'%('Client Key',accountKey)
	print '%-10s  =  %s'%('Query', query)
	print '%-10s  =  %s'%('Precision', precision)

def printFeedbackSummary(query, currPrecision, precision):
	""" 
	Prints the parameters in the format below
	"""
	print "\nFEEDBACK SUMMARY\n==================="
	print '%-10s  =  %s'%('Query', query)
	print '%-10s  =  %s'%('Precision', currPrecision)
	

def usage():
	print """modQueryVec
	python BingSearch.py [accountKey] [precision] ['query']

	"""

if __name__ == "__main__":

	if len(sys.argv)!=4: # Expect exactly three arguments: the account key, precision, and query string
		usage()
		#sys.exit(2)

		#debugging 
		accountKey = 'OWcbFzI/FPzmWjbmJcs8WSv0oZf1qkZ0Knxpz9nfyDI'		
		precision = .9
		query = 'gates'
		
	else:
		accountKey = sys.argv[1]
		precision = float(sys.argv[2])
		query = sys.argv[3] # what about multiple word queries?

	currPrecision = 0.0
	reached = 0
	nIter = 1
	
	while currPrecision < precision:
		printParameters(accountKey, query, precision)

		formattedQuery = formatQuery(query)

		topResults = getTopResults(formattedQuery, accountKey)
		getAllWords(topResults)

		numOfResults = len(topResults['d']['results'])
		if numOfResults<10:
			print 'Bing returned less than 10 results. Exiting.'
			sys.exit(2)

		print 'Total no of results : ' + str(numOfResults)
		print '\nBing Search Results\n==================='
		
		getStopWords()
		getAllWords(topResults)

		queryVector = getQueryVector(query, allWords)
		
		#loop over topResults, get feedback
		relevance = [0]*10
		for i in range(10):
			print '\n Result '+ str(i+1) + '\n[\n' + ' URL: '+topResults['d']['results'][i]['DisplayUrl']
			print ' Title: ' + topResults['d']['results'][i]['Title']
			print ' Summary: ' + topResults['d']['results'][i]['Description'] + '\n]'
			uin = raw_input('\nRelevant? [Y/n] ')
			while True:
				if uin is "" or uin is 'y' or uin is 'Y':
					relevance[i] = 1
					break
				elif uin is 'n' or uin is 'N':
					break
				else:
					uin = raw_input("Invalid input, enter 'y' or 'n': ")

		# if no relevant documents
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

		#compute optional values
		_termFreqs = term_freqs(docs, allWords)
		_tf_idf = tf_idf(docs, allWords)
		_ntf_idf = ntf_idf(.4,_termFreqs, allWords)
		
		# get augmented query based on Rocchio's Algorithm
		queryMod = Rocchio(relevance, queryVector, _tf_idf, 1, .75, .15)
		query = getNewQuery(query, allWords.keys(), queryMod)

		reset(allWords)
		reset(topResults)
		reset(docs)
		docs = {key: list() for key in range(10)}
		#reset(tf_Idf)
		reset(termFreqs)
		nIter = nIter + 1

	if reached:
		printFeedbackSummary(query, currPrecision, precision)
		print 'Desired Precision reached in ' + str(nIter) + ' iterations!\n'
			
