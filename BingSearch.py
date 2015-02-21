import urllib2
import base64
import json
import string
import sys

allWords = {}

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
				if allWords.has_key(word)==0:
					allWords[word] = 0

		for word in noPuncTitle.split(' '):
			word = word.lower()
			if word:
				if allWords.has_key(word)==0:
					allWords[word] = 0

	print allWords.keys()

def usage():
    print """
    python BingSearch.py [accountKey] [precision] ['query']

    """

if __name__ == "__main__":

    if len(sys.argv)!=4: # Expect exactly three arguments: the account key, precision, and query string
        usage()
        sys.exit(2)
    accountKey = sys.argv[1]
    precision = float(sys.argv[2])
    query = sys.argv[3]

    query = formatQuery(query)
    getTopResults(query, accountKey)










