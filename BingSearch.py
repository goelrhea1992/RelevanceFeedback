import urllib2
import base64
import json
import string
import sys
import math

topResults = {}
allWords = {}
docs = {key: list() for key in range(10)}
query = ''

def formatQuery(query):
	formattedQuery = "%27"
	for term in query.split():
		formattedQuery = formattedQuery + term + '%20'
	formattedQuery = formattedQuery[0: len(formattedQuery)-3]
	formattedQuery = formattedQuery + '%27'
	return formattedQuery


def getTopResults(formattedQuery, accountKey):

	bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=' + formattedQuery + '&$top=10&$format=json'
	# accountKey = 'OWcbFzI/FPzmWjbmJcs8WSv0oZf1qkZ0Knxpz9nfyDI'
	accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
	headers = {'Authorization': 'Basic ' + accountKeyEnc}
	req = urllib2.Request(bingUrl, headers = headers)
	response = urllib2.urlopen(req)
	content = response.read()
	topResults =  json.loads(content)
	with open('data.txt','w') as outfile:
		json.dump(topResults, outfile)
	
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
				if allWords.has_key(word)==0:
					allWords[word] = [0,0]

		for word in noPuncTitle.split(' '):
			word = word.lower()
			if word:
				docs[i].append(word)
				if allWords.has_key(word)==0:
					allWords[word] = [0,0]
	
	# in case query words aren't in title or desc
	for word in query.split(' '):
		word = word.lower()
		if word:
			if allWords.has_key(word)==0:
				allWords[word] = [0,0]

	# put document frequencies and idf's in allWords dictionary
	for word in allWords.keys():
		for i in range(10):
			if docs[i].count(word) > 0:
				allWords[word][0] += 1
				allWords[word][1] = math.log(10/allWords[word][0])

	#print allWords
	print allWords.keys()

	#print 'Documents: '
	#print docs

	#essentially our document vectors:
	#term frequency: number of occurences of every word in every document
	termFreqs = [[docs[docKey].count(word) for word in allWords.keys()] for docKey in docs.keys()]
	print '\ndocs[0]: ', docs[0]
	print '\nzip(termFreqs[0],allWords.keys()): ', zip(termFreqs[0],allWords.keys())
	#print termFreqs
	print '\nallWords: ', [allWords[word] for word in allWords]

	#tf-idf: number of occurences of every word in every document, normalized by log(N/df)
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


Attributes:
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

def usage():
	print """
	python BingSearch.py [accountKey] [precision] ['query']

	"""


if __name__ == "__main__":

	if len(sys.argv)!=4: # Expect exactly three arguments: the account key, precision, and query string
		usage()
		#sys.exit(2)

		#was having some problems with my wifi at one point so I ran from a data.txt file rather 
		# running the bing query every time...
		# obviously it won't work later on when we add the relevance feedback
		data = open('data.txt','r')
		topResults = json.load(data)
		data.close()
		tf_Idf = getAllWords(topResults)
		print "\ntf_Idf: " , tf_Idf
		query = 'gates'
		queryVector = getQueryVector(query, allWords)
		#docVectors = getDocVectors(docs, allWords)
		print "\nsims: " , sims(queryVector,tf_Idf)
		
	else:
		accountKey = sys.argv[1]
		precision = float(sys.argv[2])
		query = sys.argv[3]

		query = formatQuery(query)
		getTopResults(query, accountKey)
		getAllWords(topResults)










