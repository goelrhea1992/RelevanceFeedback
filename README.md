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
	
	Optional additional parameter:
	[weightingSchema] the desired weighting schema to use in Rocchio's algorithm.
	WeightingSchema can have the following values: 1 = tf-idf, 2 = ntf-idf, 3 = wf-idf

Internal Design:
	Summary: 
	Implementation of Rocchio's algorithm using term-frequency, tf-idf, or ntf-idf 
	as the word/document scoring method. 
	
	Description:
	
	The user enters a bing account key, desired precision, and a single-word query.
	This triggers a loop:  1) query bing  2) display the results  3) request user 
	feedback on the relevance of each document 4) index the results and compute a 
	new query and 5) repeat until the desired precision is reached. 
	
	The new query computed by Rocchio's algorithm using constants alpha=1, 
	beta=.75, and gamma=.15 as suggested in Manning et. al. 183. Tests were
	performed with gamma=0, thereby removing the negative feedback. We did not
	notice significant differences in our small sample size. 
	
	Using term frequencies alone in the document vectors resulted in issues with 
	stopwords. Adding the idf values generally removes the affects of these words,
	but not always. Therefore, stopwords are removed from the calculations prior
	to all calculations. This shortens the document vectors, giving us better 
	efficiency.

	To allow for special cases, numbers are left in the document vectors. Ex. 
	a 'columbia' query sometimes targets 1754 as a significant term. 

	The document-word scores are calculated using the tf-idf (term frequency-
	inverse document frequency) method. Tests were also performed using the 
	ntf-idf (maximum normalized term frequency - inverse document frequency) and 
	the wf-idf ( sublinear/logarithmic tf scaling - inverse document frequency) methods
	explained in eqns 6.13 and 6.15 of Manning et. al. pg. 127. However, these alternative schemas
	did not noticibly improve the number of itterations taken to acheive the target 
	precision for our small-scale analysis. 

	Three transcripts are attached displaying the results for three initial user
	queries: 'gates', 'musk', and 'columbia'. 


	Regarding Query Drift: 
	The user can produce significantlly different results by slightly different 
	responses. This was especially evident in the 'columbia' query. Avoiding 
	references to Columbia Athletics or Teachers College in early feedback tends
	to produce more targeted results later on. However, innocently selecting these
	as relevant in early queries often resulted in overly specified results 
	(targeting only Columbia Athletics, or the only Teachers College of CU) in later 
	itterations. This potential for query drift was evident in all three weighting methods.
	
	Regarding Word Order:
	Using different weighing algorithms generally produced the same additional words to 
	add to the query. However, they were often ordered differently because of slightly 
	different weights, and slightly different results from bing. The different 
	word ordering tended to then produce variations in the bing results. We noticed 
	this the most often in the 'gates' query. When the word 'william' was before the 
	word 'gates' in the query (often happening using wf-idf), there were
	more results relating to William Gates, the basketball player of Chicago, IL
	and a 3rd itteration was required to clarify.
	

	Transcripts: 
	Transcripts are provided for three different initial queries, using the default
	weighting method (tf-idf): 'musk' 'columbia' and 'gates'
	
	'musk' reached perfect precision after a single itteration.
	'columbia' reached the target precision in its 3rd itteration
	'gates' reached the target precision in its 3rd itteration.
	
	Additional transcripts are provided for the 'gates' query using the 
	NTF-IDF and the WF-IDF weighting schemes: 
	TF-IDF:  1) 'gates' 2) 'bill william gates' 3) 'bill william gates iii october'
	NTF-IDF: 1) 'gates' 2) 'bill gates william'
	WF-IDF:  1) 'gates' 2) 'bill william gates' 3) 'bill william gates iii october'
	

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
