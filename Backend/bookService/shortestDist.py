import math

EDGE_THRESH = 0.2

def getMinFromQ(Q,dist):
	min_v = None
	minimum = math.inf
	for v in Q:
		if dist[v]<minimum:
			min_v=v
			minimum=dist[v]
	return min_v

#Def G as distance matrix so list of vertices with dist to each other vertex
def getNeighbors(G, edgeThresh):
	neighbor_map = {}
	for v in G:
		neighbor_map[v]=set({})
		for u in G[v]:
			if G[v][u]<edgeThresh:
				neighbor_map[v].add(u)
	return neighbor_map


def Djikstra(G, source):

	Q = set({})
	dist = {}
	prev = {}
	neighbor_map = getNeighbors(G,EDGE_THRESH)

	for v in G:
		dist[v]=math.inf
		prev[v]=[]
		Q.add(v)
	dist[source]=0

	# print(source)
	while len(Q)>0:
		u= getMinFromQ(Q,dist)# u = min(dist,key=dist.get)
		# print(u)
		# print(Q)
		Q.remove(u)
		for v in Q.intersection(neighbor_map[u]):
			alt = dist[u] + 1
			if alt <= dist [v]:
				dist[v]= alt
				prev[v].append(u)

	return dist,prev

vertices = {'a','b','c','d','e'} 
G = {
	'a':{'b':0.1,'c':0.3,'d':0.3,'e':0.1},
	'b':{'a':0.1,'d':0.1,'c':0.1,'e':0.3},
	'c':{'a':0.3,'d':0.1,'b':0.1,'e':0.1},
	'd':{'a':0.3,'b':0.1,'c':0.1,'e':0.1},
	'e':{'a':0.1,'d':0.1,'c':0.1,'b':0.3}
}

# G = {
# 	'a':{'b':0.1,'c':0.1,'d':0.1,'e':0.1,'f':0.3,'g':0.3,'h':0.3},
# 	'b':{'a':0.1,'c':0.3,'d':0.3,'e':0.3,'f':0.1,'g':0.3,'h':0.3},
# 	'c':{'b':0.3,'a':0.1,'d':0.3,'e':0.3,'f':0.1,'g':0.3,'h':0.3},
# 	'd':{'b':0.3,'c':0.3,'a':0.1,'e':0.3,'f':0.3,'g':0.1,'h':0.3},
# 	'e':{'b':0.3,'c':0.3,'d':0.3,'a':0.1,'f':0.3,'g':0.1,'h':0.3},
# 	'f':{'b':0.1,'c':0.1,'d':0.3,'e':0.3,'a':0.3,'g':0.3,'h':0.1},
# 	'g':{'b':0.3,'c':0.3,'d':0.1,'e':0.1,'f':0.3,'a':0.3,'h':0.1},
# 	'h':{'b':0.3,'c':0.3,'d':0.3,'e':0.3,'f':0.1,'g':0.1,'a':0.3}
# }

# for v in G:
# 	print(Djisktra(G,v))

# def countShortestPaths(dist):

def reconstructPath(src,dst,prev):	
	paths=[]
	if src in prev[dst]:
		return prev[dst]
	else:
		for v in prev[dst]:
			paths+=([v]+reconstructPath(src,v,prev))
		return paths

# def reconstructPath_flattened(src,dst,prev):
# 	paths = reconstructPath(src,dst,prev)
# 	print(paths)	
# 	return [x for xs in paths for x in xs]


def countPaths(src,paths):
	return paths.count(src)
		

def betweenessCentrality(v, G):
	# pathsThroughV = 0
	# allPaths = 0
	bc = 0
	toCheck = set(G.keys())
	toCheck.remove(v)
	for src in toCheck:
		shortestPathResult = Djikstra(G,src)
		toCheck.remove(src)
		for dst in toCheck:
			paths = reconstructPath(src,dst,shortestPathResult[1])
			allPaths=paths.count(src)
			pathsThroughV=paths.count(v)
			# print("betweeness for: "+dst+" and "+src+": "+str(pathsThroughV))
			if allPaths>0:
				bc+=pathsThroughV/allPaths
		toCheck.add(src)
	# if allPaths==0:
	# 	return 0
	return bc/2
			
def closenessCentrality(v,G):
	if v not in G:
		return 0
	otherNodes=Djikstra(G,v)[0]
	otherNodes.pop(v)
	dist2others=0
	for v in otherNodes:
		dist2others+=otherNodes[v]
	return (len(otherNodes)-1)/dist2others


# aStart=(Djikstra(G,'a'))
# print(aStart[1])
# # print(reconstructPath('a','h',aStart[1]))
# print(betweenessCentrality('d',G))
# print(closenessCentrality('b',G))
# print(reconstructPath('c','a',aStart[1]))
