from flask import Flask, request, jsonify, Response, make_response
from gutenberg.acquire.text import _etextno_to_uri_subdirectory
import requests
import re
import os

_GUTENBERG_MIRROR = os.environ.get('GUTENBERG_MIRROR',
                                   'http://www.mirrorservice.org/sites/ftp.ibiblio.org/pub/docs/books/gutenberg/')


app = Flask(__name__)

def getImageUrl(bookId,imagePath):
	url=_GUTENBERG_MIRROR+_etextno_to_uri_subdirectory(int(bookId))+"/"+str(bookId)+"-h/images/"+imagePath
	return url

def getImageLinks(bookId):
	url=_GUTENBERG_MIRROR+_etextno_to_uri_subdirectory(int(bookId))+"/"+str(bookId)+"-h/images"
	# print(url)
	allImages=[]
	resp = requests.get(url)
	if resp.status_code==200:
		respPlainText=resp.text
		# print(respPlainText)
		matches=re.findall(r"f=\".+\.jpg\">",respPlainText)
		# matches=pattern.match()
		for m in matches:
			allImages.append(m.split("\"")[1])
		# print(matches.captures(1))
	return allImages

def get_book_images(bid):
	bid2imgs={}
	bid2imgs[str(bid)]={"cover":"","imgs":[]}
	il=(getImageLinks(bid))
		# print(il)
	if len(il)>0:
		for img in il:
			# print(img)
			if "cover" in img:
				bid2imgs[str(bid)]["cover"]=getImageUrl(bid,img)
			else:
				bid2imgs[str(bid)]["imgs"].append(getImageUrl(bid,img))
	return bid2imgs

def initialise_images_all_books(bids):
	bid2imgs={}
	for i in range(100,1000):
		bid2imgs[i]={"cover":"","imgs":[]}
		il=(getImageLinks(i))
		# print(il)
		if len(il)>0:
			for img in il:
				# print(img)
				if "cover" in img:
					bid2imgs[i]["cover"]=getImageUrl(i,img)
				else:
					bid2imgs[i]["imgs"].append(getImageUrl(i,img))
		# print(bid2imgs)
	return bid2imgs



@app.route('/images/<string:search_query>',methods=['GET'])
def getImages(search_query):
	ret = get_book_images(int(search_query))
	resp = make_response(ret)
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp

