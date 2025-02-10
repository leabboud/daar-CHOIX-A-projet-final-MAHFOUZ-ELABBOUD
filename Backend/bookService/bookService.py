from flask import Flask, request, jsonify, Response, make_response
import csv
import requests
import string
import os.path
import json
import re
from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from shortestDist import *
from functools import partial
from kmp import KMP_search

BOOK_INFO_LOCAL_URL = "bookInfo/"
INDIVIDUAL_INDICES_URL = BOOK_INFO_LOCAL_URL+"bookIndices"
INDIVIDUAL_JACCARD_MATRICES_URL = BOOK_INFO_LOCAL_URL+"bookDistancesJacc"
CATALOG_FILE_NAME = "pg_catalog.csv"
GUTENBERG_CATALOGUE_URL="https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv"
UNTREATED_BOOKS_FILE_NAME = 'untreatedBookIds.txt'
LOCAL_INDEX_FILE_NAME = "global_index.json"
LOCAL_CLOSENESS_FILE_NAME = "all_closeness.json"

#INITIALISATION ----------------------------------------------------------------------------------------------------------------

def load_index_from_file(index_path):
	if not (os.path.isfile(index_path)):
		raise Exception("error, index specified does not exist")
	with open(index_path,'r') as index_file:
		index = json.load(index_file)
		return index

def load_all_metadata():
	book_metadata={}
	with open(BOOK_INFO_LOCAL_URL+CATALOG_FILE_NAME, newline='') as csvfile:
		reader = csv.reader(csvfile,delimiter=',')
		next(reader)
		for row in reader:
			book_metadata[int(row[0])]=row
	return book_metadata

def get_global_index():
	if (os.path.isfile(BOOK_INFO_LOCAL_URL+LOCAL_INDEX_FILE_NAME)):
		with open(BOOK_INFO_LOCAL_URL+LOCAL_INDEX_FILE_NAME) as index_file:
			index = json.load(index_file)
			return index
	else: return {}

def get_all_stored_indices():
	return (list(map(lambda x: x[:len(x)-5],os.listdir(INDIVIDUAL_INDICES_URL))))

def load_all_indices():
	allIndices = {}
	allIndexNumbers = get_all_stored_indices()
	total = len(allIndexNumbers)
	actual = 1
	for idx in  allIndexNumbers:
		print(str(actual/total*100)+"%",end='\r')
		allIndices[idx]=load_index_from_file(INDIVIDUAL_INDICES_URL+"/"+(idx)+".json")
		actual+=1
		print(end='\x1b[2K')
	return allIndices

def load_dist_matrix(book_id):
	path = INDIVIDUAL_JACCARD_MATRICES_URL+"/"+str(book_id)+".json"
	if not (os.path.isfile(path)):
		raise Exception("error, index specified does not exist")
	with open(path,'r') as dm_file:
		dm = json.load(dm_file)
		return dm

def load_all_dms():
	allBookIds=(list(map(lambda x: x[:len(x)-5],os.listdir(INDIVIDUAL_JACCARD_MATRICES_URL))))
	dms={}
	for bid in allBookIds:
		dms[bid]=load_dist_matrix(bid)
	return dms

def load_closeness():
	path = BOOK_INFO_LOCAL_URL+LOCAL_CLOSENESS_FILE_NAME
	with open(path,'r') as cc_file:
		ccs=json.load(cc_file)
		return ccs

mt = load_all_metadata()
# print(mt)
print("------loaded metadata--------")
idx = get_global_index()
print("------loaded global index--------")
allIndices = load_all_indices()
print("------loaded individual indices--------")
allDistances = load_all_dms()
print("------loaded distance matrices--------")
# allDistances = load_all_dms()
print("------loaded distance matrices--------")
allCloseness = load_closeness()
print("------loaded closeness rankings--------")

#SEARCHING ----------------------------------------------------------------------------------------------------------------

def simple_search(query,global_index):
	try:
		ret = global_index[query]
		return ret
	except:
		return []

def search_in_metadata(query,allmetadata):
	hits=[]
	for row in allmetadata:
		title_check = query.lower() in allmetadata[row][3].lower()
		author_check = query.lower() in allmetadata[row][5].lower()
		subjects_check = query.lower() in allmetadata[row][6].lower()
		if title_check or author_check or subjects_check:
			hits.append(row)
	return hits

def search(query,global_index,allmetadata):
	operands=["(",")","|","*","."]
	hits=[]
	# if any(x in query for x in operands):
	# 	regex = re.compile(query)
	# 	matches = list(filter(regex.match,global_index.keys()))
	# 	for w in matches:
	# 		hits+=list(global_index[w].keys())
	# else:
	hits+=search_in_metadata(query,allmetadata)
	hits+=list(simple_search(query,global_index))
	return list(set(hits))

def regex_search(query,global_index,allmetadata):
	operands=["(",")","|","*","."]
	hits=[]
	if not any(x in query for x in operands):
		query=query.lower()
		matches = [k for k in global_index.keys() if query in k]
		for w in matches:
			hits+=list(global_index[w].keys())
		return hits
	
	query=query.lower()
	regex = re.compile(query)
	matches = [k for k in global_index.keys() if regex.match(k)]
	# matches = list(filter(regex.match,global_index.keys()))
	for w in matches:
		hits+=list(global_index[w].keys())

	return list(set(hits))

def getCloseness(book_id,all_cc):
	if book_id in all_cc:
		return all_cc[book_id]
	else: return 0

def getReccomendations(book_id,alldistances):
	try:
		bookid2others=allDistances[book_id]
		# sortedDict={k: v for k, v in sorted(bookid2others.items(), key=lambda item: item[1])}
		pairs=[(k,bookid2others[k]) for k in bookid2others]
		pairs.sort(key=lambda x:[1])
		recs=pairs[len(pairs)-10:]
		return [a[0] for a in recs]
	except:
		return []

def jaccard_dist_list_words(l1,l2):
	words_in_intersection = set(l1).intersection(set(l2))
	if len(words_in_intersection)==0:
		return 0
	union = set(l1).union(l2)

	return len(words_in_intersection)/len(union)

def getSuggestions(book_id):
	try:
		punctuation = "!\"#$%&'()*+,./:;<=>?@[\\]^_`{|}~“--"
		print(mt[int(book_id)])
		category=mt[int(book_id)][-1]
		
		category=category.replace('Browsing:','')
		
		category=category.replace('/',' ')
		
		category=category.translate(str.maketrans("","",punctuation))
		
		category=category.split()
		
		category=[t.lower() for t in category if len(t)>2]
		

		subjects=mt[int(book_id)][-3]
		# print(subjects)
		subjects=subjects.translate(str.maketrans("","",punctuation))
		# print(subjects)
		subjects=subjects.split()
		# print(subjects)
		subjects=[t.lower() for t in subjects if len(t)>2]
		# print(subjects)

		# print("Book: ")
		# print(mt[int(book_id)][3])
		# print("Subject: ")
		# print(subjects)
		# print("Category: ") 
		# print(category)
		
		similarities={}
		for bid in get_all_stored_indices():
			other_category=mt[int(bid)][-1]
			other_category=other_category.replace('Browsing:','')
			other_category=other_category.replace('/',' ')
			other_category=other_category.translate(str.maketrans("","",punctuation))
			other_category=other_category.split()
			other_category=[t.lower() for t in other_category if len(t)>2]
			
			other_subjects=mt[int(bid)][-3]
			other_subjects=other_subjects.translate(str.maketrans("","",punctuation))
			other_subjects=other_subjects.split()
			other_subjects=[t.lower() for t in other_subjects if len(t)>2]



			j_1 = jaccard_dist_list_words(category,other_category)
			j_2 = jaccard_dist_list_words(subjects,other_subjects)

			# print("Book: "+(mt[int(book_id)][3]))
			# print("Subject: "+str(subjects))
			# print("Category: "+str(category))
			# print("Other book:"+mt[int(bid)][3])
			# print("Other subjects: "+str(other_subjects))
			# print(" dist: "+str(j_1))
			# print("Other category: "+str(other_category)) 
			# print("dist: "+str(j_2))
			# print("Other category: "+mt[int(bid)][0])
			# print(j_1)
			# print(j_2)
			
			similarities[bid]={'bookshelves': j_1, 'subjects': j_2}

		pairs=[(k,similarities[k]['bookshelves']+similarities[k]['subjects']) for k in similarities]
		# pairs.sort(key=lambda x:[1])
		pairs=sorted(pairs, key=lambda x: x[1])
		return ([k for (k,v) in pairs[len(pairs)-10:]])
		# recs=pairs[len(pairs)-10:]
		# return [a[0] for a in recs]

		# return similarities
	except Exception as e:
		print("error in jaccard dist calculation")
		print(e)
			

def getBookById(book_id):
	ret = {}
	ret[int(book_id)]=mt[int(book_id)]
	ret[int(bid)]+=[str(getCloseness(str(bid),allCloseness))]
	ret[int(bid)]+=[str(getReccomendations((bid),allDistances))]
	return ret

# ----------------------------------------------------------------------------------------------------------------

app = Flask(__name__)

def initializeIndex():
	return True

@app.route('/books/<string:search_query>',methods=['GET'])
def searchForQuery(search_query):
	hits = search(search_query,idx,mt)
	ret = {}
	for bid in hits:
		ret[int(bid)]=mt[int(bid)].copy()
		ret[int(bid)]+=[str(getCloseness(str(bid),allCloseness))]
		# ret[int(bid)]+=[str(getReccomendations((bid),allDistances))]
		# getReccomendations(bid)
		# print(ret[int(bid)])
	# print(list(ret.keys()))
	print(hits)
	resp = make_response(ret)
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp

@app.route('/books/advancedSearch/<string:search_query>',methods=['GET'])
def advancedSearchForQuery(search_query):
	hits = regex_search(search_query,idx,mt)
	ret = {}
	for bid in hits:
		ret[int(bid)]=mt[int(bid)].copy()
		ret[int(bid)]+=[str(getCloseness(str(bid),allCloseness))]
		# ret[int(bid)]+=[str(getReccomendations((bid),allDistances))]
		# getReccomendations(bid)
		# print(ret[int(bid)])
	# print(list(ret.keys()))
	print(hits)
	resp = make_response(ret)
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp

@app.route('/books/id/<string:search_query>',methods=['GET'])
def bookById(search_query):
	try:
		ret = {}
		ret[int(search_query)]=mt[int(search_query)].copy()
		ret[int(search_query)]+=[str(getCloseness(str(search_query),allCloseness))]
		# ret[int(search_query)]+=[str(getReccomendations((search_query),allDistances))]
		# print(getReccomendations())
		resp = make_response(ret)
		resp.headers['Access-Control-Allow-Origin'] = '*'
		return resp
	except:
		resp = make_response("bookId not found")
		resp.headers['Access-Control-Allow-Origin'] = '*'
		return resp

@app.route('/getRecs/<string:search_query>',methods=['GET'])
def recomendationByBookID(search_query):
	recs=getSuggestions(search_query)
	ret = {}
	for bid in recs:
		ret[int(bid)]=mt[int(bid)].copy()
	resp = make_response(ret)
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp

# def getBookById(book_id):
# 	ret = {}
# 	ret[int(book_id)]=mt[int(book_id)]
# 	ret[int(bid)]+=[str(getCloseness(str(bid),allCloseness))]
# 	ret[int(bid)]+=[str(getReccomendations((bid),allDistances))]
# 	return ret

# # ----------------------------------------------------------------------------------------------------------------



# app = Flask(__name__)

# def initializeIndex():
# 	return True

# @app.route('/books/<string:search_query>',methods=['GET'])
# def searchForQuery(search_query):
# 	hits = search(search_query,idx,mt)
# 	ret = {}
# 	for bid in hits:
# 		ret[int(bid)]=mt[int(bid)]
# 		ret[int(bid)]+=[str(getCloseness(str(bid),allCloseness))]
# 		ret[int(bid)]+=[str(getReccomendations((bid),allDistances))]
# 		print(ret[int(bid)])
# 	# print(list(ret.keys()))
# 	resp = make_response(ret)
# 	resp.headers['Access-Control-Allow-Origin'] = '*'
# 	return resp

# @app.route('/books/id/<string:search_query>',methods=['GET'])
# def bookById(search_query):
# 	try:
# 		ret = {}
# 		ret[int(search_query)]=mt[int(search_query)]
# 		ret[int(search_query)]+=[str(getCloseness(str(search_query),allCloseness))]
# 		ret[int(search_query)]+=[str(getReccomendations((search_query),allDistances))]
# 		resp = make_response(ret)
# 		resp.headers['Access-Control-Allow-Origin'] = '*'
# 		return resp
# 	except:
# 		resp = make_response("bookId not found")
# 		return resp



# if __name__ == '__main__':
#     app.run(debug=True, port=5000)