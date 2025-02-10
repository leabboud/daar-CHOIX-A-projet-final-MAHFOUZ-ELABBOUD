from subprocess import call, run, check_output
import requests
import json
import csv
import os
import time

bookService_URL="http://127.0.0.1:5003/books/advancedSearch/"

# query="a"

# cmd = f"""egrep -lr \"{query}\" Texts"""
# out= (check_output(cmd,shell=True).decode('ascii'))
# out=out.replace('Texts/','')
# out=out.replace('.txt','')
# out=(out.split())
# print(out)

# r=requests.get(bookService_URL+query)
# server_r=(list(json.loads(r.text).keys()))
# print(server_r)

# print(set(server_r).intersection(set(out)))
# print(set(server_r).symmetric_difference(set(out)))


result_fields=[["pattern","matches","differences","accuracy","egrep time","server time"]]
queries = ["dar(tmouth|ling)","Sargon","S(a|o)rgon","a","ab","s(ord|tol)id","a*b*(i|o)(d|t)*(y|ie)","b","bb","c*a*r","h.llo","d.g","h(.)*s"]
accuracy = 0
for query in queries:
	print("PATTERN: "+query)
	cmd = f"""egrep -lri \"{query}\" Texts"""
	i1=time.time()
	out= (check_output(cmd,shell=True))
	i2=time.time()
	egrepTime=i2-i1
	out=out.decode('ascii')
	out=out.replace('Texts/','')
	out=out.replace('.txt','')
	out=(out.split())
	
	print("-------------EGREP-------------")
	# print(out)
	print("-------------SERVER-------------")
	r=requests.get(bookService_URL+query)
	serverTime=(r.elapsed.total_seconds())
	server_r=(list(json.loads(r.text).keys()))
	# print(server_r)
	print("--------------------------------")
	matches=(set(server_r).intersection(set(out)))
	differences=(set(server_r).symmetric_difference(set(out)))
	print("Number of matches: "+str(len(matches)))
	print("Number of differences: "+str(len(differences)))
	if (len(out)>len(matches)):
		print("EGREP got more matches than server")
		print("SERVER missed something: ")
		print([bid for bid in out if bid not in server_r])
		print("SERVER added something: ")
		print([bid for bid in server_r if bid not in out])
	if (len(out)<len(matches)):
		print("EGREP got less matches than server")
		print("SERVER missed something: ")
		print([bid for bid in out if bid not in server_r])
		print("SERVER added something: ")
		print([bid for bid in server_r if bid not in out])
	
	current_accuracy=len(matches)/(len(differences)+len(matches))
	result_fields.append([query,len(matches),len(differences),current_accuracy,egrepTime,serverTime])
	
	accuracy+=current_accuracy

write_check="x"
if (os.path.isfile("results.csv")):
	write_check="w"
with open('results.csv',write_check,newline='') as csvfile:
	writer = csv.writer(csvfile, delimiter=',')
	for row in result_fields:
		writer.writerow(row)

accuracy=accuracy/(len(queries))
print("SERVER ACCURACY: "+str(accuracy))

# c=run(["egrep", "-lr", "\"dar(tmouth|ling)\"", "Texts"],capture_output=True,text=True)
# print(c.returncode)

