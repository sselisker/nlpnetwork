import csv
# import nltk
import networkx

tokenlist = list(csv.reader(open('data/tokens/wallace.infj.tokens', 'rb'),delimiter='\t', quoting=csv.QUOTE_NONE))
# also to fix: weird quotes in the CSV file.

#  TODO: function Add a string in the tokens as a character


# *then* pick out our CSV columns: [0] = charid, [1] = charname, [2] = wordid:
charcsv = [[row[14],row[7],row[2]] for row in tokenlist if row[14]!='-1'] # setup array of [CharID, Char Name, WordID]


node_dict = {}
stopchars = ['he','she','him','her', 'Mr.', 'Mrs.', 'Ms.', 'his', 'hers', 'She', 'He', 'His', 'Her']
for row in charcsv:
	if row[0] in node_dict:
		if node_dict[row[0]] < row[1] and row[1].lower() not in stopchars:
			node_dict[row[0]] = row[1]
	else:
		node_dict[row[0]] = row[1]

print node_dict

# todo: implement function to further cluster characters by diff mention (Hal, Inc, Hallie, etc)

edge_dict = {}

prevcharid = '0'
prevwordid = '0'
edgethreshold = 20 # ugh, realizing there's a scene break problem, technically. no scene break markers unless: double \n, all caps?

# From here below adapted from Neal Caren http://www.unc.edu/~ncaren/cite_network/citenet.py not currently in https://github.com/nealcaren?tab=repositories

for row in charcsv:
	#check if the char is in node list, add CharID/Char Name keys to node list (drop wordid)

	# Character proximity: not yet working ... if (row[0] != prevcharid and int(row[2])-int(prevwordid) < edgethreshold):
	if row[0] != prevcharid:
		# add edge between row and prevcharid to edge_dict ... wait: weight; are we adding one to weight, or are we doing what?
			name = node_dict[row[0]]
			print name
			prevname = node_dict[prevcharid]
			if (name,prevname) in edge_dict:
				edge_dict[(name,prevname)]=edge_dict[(name,prevname)]+1
			elif (prevname,name) in edge_dict:
				edge_dict[(prevname,name)]=edge_dict[(prevname,name)]+1 
			else:
				edge_dict[(name,prevname)]=1
	prevcharid = row[0]
	prevwordid = row[2]

import networkx as nx
from networkx.readwrite import d3_js
import re
G=nx.Graph()
for edge in edge_dict:
    if edge_dict[edge]>4:# and cite_dict[edge[0]]>=8 and cite_dict[edge[1]]>=8 :
        G.add_edge(edge[0],edge[1],weight=edge_dict[edge])
for node in G:    
    G.add_node(node) #adds list of nodes separately thru dict lookup

import community

partition=community.best_partition(G)

print len(partition)

for node in G:    
    G.add_node(node, group=str(partition[node]))

d3_js.export_d3_js(G,files_dir="netweb",graphname="cites",node_labels=True,group="group")

fix=open('netweb/cites.json','rb').read()
for n in G:
    try:
        fix=re.sub(str(n)+'''"''',str(n)+'''" , "nodeSize":'''+str(cite_dict[n]),fix)
    except:
        print 'error with',n
f = open('netweb/cites.json', 'w+')
f.write(fix)
f.close()






