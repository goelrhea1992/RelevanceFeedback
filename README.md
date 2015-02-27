# RelevanceFeedback
Team Members:
	Karl Bayer <ksb2153@columbia.edu>
	Rhea Goel <rg2936@columbia.edu>

Files:
	README.md
	english.txt
	BingSearch.py

Description:
	Run the program by typing the following in your terminal...
	
	python BingSearch.py [accountKey] [precision] ['query']

	[accountKey] the bing account key you wish to reference
	[precision] the desired target precision for the query results
	['query'] a single word starting query

Internal Design:
	Summary: Implementation of Rocchio's algorithm using term-frequency, tf-idf, or ntf-idf 
	as the word/document scoring method. 
	Description:
	The user enters a bing account key, desired precision, and a single-word query.
	This triggers a loop which queries bing, displays the results, 
	request user feedback on the relevance of each document, computes a new query, 
	and repeats until the desired precision is reached. 
	The new query computed by Rocchio's algorithm using constants alpha=1, 
	beta=.75, and gamma=.15 as suggested in Manning et. al. 183. 
	The document-word scores are calculated using the tf-idf (term frequency-
	inverse document frequency) method. Tests were also performed using the 
	ntf-idf (maximum normalized term frequency - inverse document frequency)
	explained in eqn 6.15 of Manning et. al. pg. 127. However, this schema did
	not noticibly improve the number of itterations taken to acheive the target 
	precision. 
	

Bing Account Keys:
	OWcbFzI/FPzmWjbmJcs8WSv0oZf1qkZ0Knxpz9nfyDI
	-or-
	H2EarNgdMNX/DKlxOnRdLWByH/XzZJKpBsULFSbnkIs

Additional information - Sources:
	Natural Language Toolkit v3.0 available @ www.nltk.org
		Used for its list of stopwords.
	Christopher D. Manning, Prabhakar Raghavan and Hinrich Schütze, Introduction to Information Retrieval, 
		Cambridge University Press. 2008. Available <http://nlp.stanford.edu/IR-book>
		Chapters 6 and 9 used for word/document weighting schemes and Rocchio's algorithm.
