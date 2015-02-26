import urllib2
import base64
import json
import string
import sys
import math
# execfile('algorithms.py')

topResults = {}
allWords = {}
docs = {key: list() for key in range(10)}
termFreqs = []
tf_Idf = []
stopWords = []

def reset(element):
	if type(element)==list:
		element[:] = []
	elif type(element)==dict:

		element.clear()

def formatQuery(query):
	formattedQuery = "%27"
	for term in query.split():
		formattedQuery = formattedQuery + term + '%20'
	formattedQuery = formattedQuery[0: len(formattedQuery)-3]
	formattedQuery = formattedQuery + '%27'
	return formattedQuery

def getStopWords():
	f = open('english','r')
	for word in f:
		word = word.strip()
		if word:
			stopWords.append(word)

def getTopResults(formattedQuery, accountKey):

	bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=' + formattedQuery + '&$top=10&$format=json'
	# accountKey = 'OWcbFzI/FPzmWjbmJcs8WSv0oZf1qkZ0Knxpz9nfyDI'
	accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
	headers = {'Authorization': 'Basic ' + accountKeyEnc}
	req = urllib2.Request(bingUrl, headers = headers)
	response = urllib2.urlopen(req)
	content = response.read()
	return json.loads(content)
	#print topResults
	#with open('data.txt','w') as outfile:
	#	json.dump(topResults, outfile)
	
""" Gets all words from titles and descriptions
	Computes termFrequency, inverse-document-frequency

"""
def getAllWords(topResults):
	for i in range(0, 10):
		desc = topResults['d']['results'][i]['Description']
		
		asciiDesc = desc.encode('ascii','ignore')
		noPuncDesc = asciiDesc.translate(string.maketrans("",""), string.punctuation)

		title = topResults['d']['results'][i]['Title']
		asciiTitle = title.encode('ascii','ignore')
		noPuncTitle = asciiTitle.translate(string.maketrans("",""), string.punctuation)

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
	
	print 'allWords.keys(): \t', allWords
	# put document frequencies and idf's in allWords dictionary
	for word in allWords.keys():
		for i in range(10):
			if docs[i].count(word) > 0:
				allWords[word][0] += 1
				allWords[word][1] = math.log(10./allWords[word][0])

	#print allWords
	print 'allWords.keys(): \t', allWords

	#print 'Documents: '
	#print docs

	#essentially our document vectors:
	#term frequency: number of occurences of every word in every document
	global termFreqs 
	termFreqs = [[docs[docKey].count(word) for word in allWords.keys()] for docKey in docs.keys()]
	print '\ndocs[0]: ', docs[0]
	#print '\nzip(termFreqs[0],allWords.keys()): ', zip(termFreqs[0],allWords.keys())
	#print termFreqs
	print '\nallWords: ', [allWords[word] for word in allWords]

	#tf-idf: number of occurences of every word in every document, normalized by log(N/df)
	global tf_Idf
	tf_Idf = [[docs[docKey].count(word)*allWords[word][1]  for word in allWords.keys()] for docKey in docs.keys()]
	#print tf_Idf
	
	return tf_Idf	
	
	
'''
	termFreqs = 
	for i in range(0, 10):
		doc = 
		termFreqs[i] = [document.count(term) for term in 
	termFreqs = [[doc.count(term) for term in allWords] for doc in list(
'''



""" Computes and returns the queryVector

query: the query as a simple white-space-delimited string
allWords: the word vector (expanded list of all words in the query and the documents)
"""
def getQueryVector(query, allWords):
	lquery = query.split(' ')
	# this can't be right... should the 
	queryVector = [1 if word in lquery else 0 for word in allWords.keys()]
	return queryVector

""" Computes the similarity between two items of the smae length
"""
def sim(queryVector, docVectorWeight):
	#Euclidian length (norm)
	normQuery = math.sqrt(sum([p*p for p in queryVector]))
	normDoc = math.sqrt(sum([p*p for p in docVectorWeight]))
	#dot product (would be easier if we were using numpy)
	sim = sum((p*d) for (p,d) in zip(queryVector, docVectorWeight)) / (normQuery*normDoc)
	return sim

""" Computes the similarities between the query and all documents
"""
def sims(queryVector,docVectorWeights):
	sims = [0]*10
	for i in range(10):
		sims[i] = sim(queryVector,docVectorWeights[i])
	return sims


""" Computes the modified query from the relevant and non-relevant documents...
	Based on Rocchio's algorithm
"""
def Rocchio(relevance, queryVector, Docs, alpha, beta, gamma):

	relDocs = [Docs[i] for i in range(len(Docs)) if relevance[i] == 1]
	nonRelDocs = [Docs[i] for i in range(len(Docs)) if relevance[i] != 1]
	
	sumRelDocs = [sum(wordCol) for wordCol in zip(*relDocs)]
	sumNonRelDocs = [sum(wordCol) for wordCol in zip(*nonRelDocs)]

	term1 = [alpha*i for i in queryVector]
	term2 = [float(beta)/len(relDocs) * i for i in sumRelDocs]
	term3 = [float(gamma)/len(nonRelDocs) * i for i in sumNonRelDocs]
	
	modQueryVec = [sum(wordCol) for wordCol in zip(term1,term2,term3)]
	
	return modQueryVec

def getNewQuery(query, allWordsKeys, queryMod):
	words = query.split(' ')
	values = zip(queryMod,allWordsKeys)
	#print values, ' ' , words
	for i in range(len(values)):
		if values[i][1] not in words:
			maxVal1 = values[i]
			maxVal2 = values[i]
	for tup in values:	
		#print 'query: ',query,'  tup: ',tup
		if tup[0] > maxVal1[0] and tup[1] not in words:
			maxVal1 = tup
		elif tup[0] > maxVal2[0]  and tup[1] not in words:
			maxVal2 = tup
	return query + ' ' + maxVal1[1] + ' ' + maxVal2[1]
	
	

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
	
	while currPrecision < precision:
		formattedQuery = formatQuery(query)
		getStopWords()
		# print stopWords

		topResults = getTopResults(formattedQuery, accountKey)
		tf_Idf = getAllWords(topResults)

		# print allWords

		print "\ntf_Idf: " , tf_Idf
		queryVector = getQueryVector(query, allWords)
		print "\nsims: " , sims(queryVector,tf_Idf)
		
		#loop over topResults, get feedback
		relevance = [0]*10
		for i in range(10):
			print '\n Result: ' + topResults['d']['results'][i]['Title']
			print '\t' + topResults['d']['results'][i]['Description']
			print '\t' + topResults['d']['results'][i]['DisplayUrl']
			uin = raw_input('\tRelevant? [Y/n] ')
			while True:
				if uin is "" or uin is 'y' or uin is 'Y':
					relevance[i] = 1
					break
				elif uin is 'n' or uin is 'N':
					break
				else:
					uin = raw_input("Invalid input, enter 'y' or 'n': ")
		print relevance
		currPrecision = sum(relevance)/10.0
		print currPrecision

		queryMod = Rocchio(relevance, queryVector, tf_Idf, 1, .75, .15)
		#print qMod
		#print allWords.keys()
		query = getNewQuery(query, allWords.keys(), queryMod)
		print query

		reset(allWords)
		reset(topResults)
		reset(docs)
		docs = {key: list() for key in range(10)}
		reset(tf_Idf)
		reset(termFreqs)

	#make sure to clear allwords df and idf values before looping. 		
			
