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
import random
# from kmp import KMP_search

BOOK_INFO_LOCAL_URL = "" #"bookInfo/"
INDIVIDUAL_INDICES_URL = BOOK_INFO_LOCAL_URL+"bookIndices"
INDIVIDUAL_JACCARD_MATRICES_URL = BOOK_INFO_LOCAL_URL+"bookDistancesJacc"
CATALOG_FILE_NAME = "pg_catalog.csv"
GUTENBERG_CATALOGUE_URL="https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv"
UNTREATED_BOOKS_FILE_NAME = 'untreatedBookIds.txt'
LOCAL_INDEX_FILE_NAME = "global_index.json"
LOCAL_CLOSENESS_FILE_NAME = "all_closeness.json"

#INITIALISATION ----------------------------------------------------------------------------------------------------------------


def getGutenbergCatalog():
	mode = 'x'
	if (os.path.isfile(BOOK_INFO_LOCAL_URL+CATALOG_FILE_NAME)):
		mode='w'
	gutenbergCatalog_resp=requests.get(GUTENBERG_CATALOGUE_URL)
	print(gutenbergCatalog_resp.status_code)
	if gutenbergCatalog_resp.status_code==200:
		with open(BOOK_INFO_LOCAL_URL+CATALOG_FILE_NAME,'w') as catalogFile:
			catalogFile.write(gutenbergCatalog_resp.text)

#Get ids of books to add to local list of files
def updateBookList():
	newBookIds=[]
	with open(BOOK_INFO_LOCAL_URL+CATALOG_FILE_NAME, newline='') as csvfile:
		reader = csv.reader(csvfile,delimiter=',')
		for row in reader:
			newBookIds.append(row[0])

	#Add ids to list for treatment
	if (os.path.isfile(BOOK_INFO_LOCAL_URL+UNTREATED_BOOKS_FILE_NAME)):
		return
	with open(BOOK_INFO_LOCAL_URL+UNTREATED_BOOKS_FILE_NAME,'x') as newBookFile:
		for bookId in newBookIds:
			newBookFile.write(bookId+"\n")



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

def load_closeness():
	path = BOOK_INFO_LOCAL_URL+LOCAL_CLOSENESS_FILE_NAME
	with open(path,'r') as cc_file:
		ccs=json.load(cc_file)
		return ccs

# mt = load_all_metadata()
# # print(mt)
# print("------loaded metadata--------")
# idx = get_global_index()
# print("------loaded global index--------")
# allIndices = load_all_indices()
# print("------loaded individual indices--------")
# allDistances = load_all_dms()
# print("------loaded distance matrices--------")
# # allDistances = load_all_dms()
# print("------loaded distance matrices--------")
# allCloseness = load_closeness()
# print("------loaded closeness rankings--------")



def save_index_to_file(index,book_id):
	new_file_check = 'x'
	if (os.path.isfile(INDIVIDUAL_INDICES_URL+str(book_id)+".json")):
		new_file_check='w'
	with open(INDIVIDUAL_INDICES_URL+"/"+str(book_id)+".json",new_file_check) as index_file:
		json.dump(index,index_file,ensure_ascii=False,indent=4)

def getText(text_id):
	text = strip_headers(load_etext(text_id)).strip()
	return text


def makeIndex(text):
	punctuation = "!\"#$%&'()*+,./:;<=>?@[\\]^_`{|}~“" #string.punctuation excluding "-"
	index = {}
	text_lines = text.splitlines()
	for line_number in range(len(text_lines)):
		for word in text_lines[line_number].split():
			
			cleaned_word=word.translate(str.maketrans("","",punctuation))
			cleaned_word=cleaned_word.lower()
			if cleaned_word in index:
				index[cleaned_word].append(line_number)
			else:
				index[cleaned_word] = [line_number]
	return index

def updateGlobalIndex_1(text_id,text_index,global_index):
	for word in text_index.keys():
		if word in global_index:
			if text_id in global_index[word].keys():
				print("why")
				continue
			else:
				global_index[word][text_id]=len(text_index[word])
		else:
			global_index[word]={text_id:len(text_index[word])}
	return global_index

def loadBookData(bookDownloadRange,global_index):
	books_to_process=[]
	with open(BOOK_INFO_LOCAL_URL+UNTREATED_BOOKS_FILE_NAME,'r') as unprocessed_books:
		books_to_process=(unprocessed_books.read().split()[:bookDownloadRange])
	random.shuffle(books_to_process)
	books_to_process=["56667"]+books_to_process[1:]
	for bookId in books_to_process:
		try:
			text=getText(int(bookId))
			text_index=makeIndex(text)
			save_index_to_file(text_index,bookId)
			global_index=updateGlobalIndex_1(bookId,text_index,global_index)
			print("PROCESSED TEXT "+bookId)
		except Exception as e:
			print("FAILED TO PROCESS TEXT: "+bookId)
			print(e)
	return global_index

def initialise(dl_range):
	if len(get_global_index())>0:
		return
	updateBookList()
	global_index = loadBookData(dl_range,{})
	with open(BOOK_INFO_LOCAL_URL+"global_index.json",'x') as writeIndex:
		json.dump(global_index,writeIndex,ensure_ascii=False,indent=4)

def save_distance_matrix(dm,book_id):
	new_file_check = 'x'
	if (os.path.isfile(INDIVIDUAL_JACCARD_MATRICES_URL+"/"+str(book_id)+".json")):
		new_file_check='w'
	with open(INDIVIDUAL_JACCARD_MATRICES_URL+"/"+str(book_id)+".json",new_file_check) as dm_file:
		json.dump(dm,dm_file,ensure_ascii=False,indent=4)

def jaccard_dist_indices(index_1,index_2):
	words_in_intersection = set(index_1.keys()).intersection(set(index_2.keys()))
	if len(words_in_intersection)==0:
		return 0
	words_outside_intersection = set(index_1.keys()).symmetric_difference(set(index_2.keys()))
	if len(words_outside_intersection)==0:
		return 1
	return len(words_in_intersection)/len(words_outside_intersection)			

def get_distance_matrix(index_list, allIndices):
	matrix={} #REVISE
	for i in range(len(index_list)):
		print(i)
		index_1 = allIndices[index_list[i]]
		# print("loaded i1")
		if i not in matrix:
			matrix[i]={}
		for j in range(i+1,len(index_list)):
			if j not in matrix:
				matrix[j]={}
			if i not in matrix[j]:
				index_2 = allIndices[index_list[j]]
				# print("loaded i2")
				dist = jaccard_dist_indices(index_1,index_2)
				matrix[i][j]=dist
				matrix[j][i]=dist
		save_distance_matrix(matrix[i],i)
	return matrix

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
		# print(bid)
		dms[bid]=load_dist_matrix(bid)
	return dms

def get_all_stored_indices():
	return (list(map(lambda x: x[:len(x)-5],os.listdir(INDIVIDUAL_INDICES_URL))))

def load_all_indices():
	allIndices = {}
	allIndexNumbers = get_all_stored_indices()
	total = len(allIndexNumbers)
	actual = 1
	for idx in  allIndexNumbers:
		print(str(actual/total*100)+"%",end='\r')
		# print(idx)
		allIndices[idx]=load_index_from_file(INDIVIDUAL_INDICES_URL+"/"+(idx)+".json")
		actual+=1
		print(end='\x1b[2K')
	return allIndices

getGutenbergCatalog()
initialise(200)
# get_distance_matrix
allIndexNumbers = get_all_stored_indices()
allIndices = load_all_indices()
dm=get_distance_matrix(allIndexNumbers,allIndices)

allDistances=load_all_dms()
allCentralities={}
tot=len(allDistances)
print(tot)
current=1
for bid in allDistances:
	print(str(current)+"/"+str(tot))
	cc=closenessCentrality(bid,allDistances)
	allCentralities[bid]=cc
	current+=1

write_check='x'
if (os.path.isfile(BOOK_INFO_LOCAL_URL+"all_closeness.json")):
		write_check='w'
with open(BOOK_INFO_LOCAL_URL+"all_closeness.json",write_check) as writeIndex:
		json.dump(allCentralities,writeIndex,ensure_ascii=False,indent=4)
