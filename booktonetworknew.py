import csv
# import nltk
import networkx

#
tokenlist = list(csv.reader(open('data/tokens/dickens.oliver.tokens', 'rb'),delimiter='\t', quoting=csv.QUOTE_NONE))

stopchars = ['he','she','him','her', 'Mr.', 'Mrs.', 'Ms.', 'his', 'hers', 'She', 'He', 'His', 'Her', 'originalWord']

"""
#typing friendly dict of duplicate name entries, reverse mapped as strings in next block
duplicate_dict = {'Don Gately' : (551, 375, 171, 431), 'Joelle van Dyne' : (329, 473, 638, 167), 'Mario' : (210, 449, 466, 507), 'Hal Incandenza' : (385, 73, 347, 633), 'Jim Incandenza' : (622, 126, 179, 567, 616), 'Avril' : (583, 155), 'Poor Tony Krause' : (660, 176, 287), 'Jim Troeltsch' : (237, 98), 'Charles Tavis' : (19, 295), 'Pat' : (258, 113),'Esther Thode': (95, 168, 593), 'Steeply' : (248, 481, 650), 'Johnny Gentle' : (249, 637), 'Rodney Tine' : (266, 358, 625), 'Randy Lenz' : (285, 566), 'Yolanda W' : (360, 410), 'Kate Gompert' : (596, 409, 477, 606), 'Orin' : (240, 240), 'Roy Tony': (322, 322), 'Schtitt' : (465, 91, 160, 590), 'Pemulis' : (482, 81), 'Schacht' : (502, 257), 'Bruce Green': (341, 112)}
reverse_duplicate_dict = {}
for entry in duplicate_dict:
	for value in duplicate_dict[entry]:
		reverse_duplicate_dict[str(value)] = (str(duplicate_dict[entry][0]), entry)

# same with false positive characterID tokens
token_scrub = [78, 96, 191, 183, 291, 312, 318, 364, 529, 594]
token_scrub = map(str, wallace_scrub)

for row in tokenlist:
	if row[14] in reverse_duplicate_dict:
		row[14] = reverse_duplicate_dict[row[14]][0]
		row[7] = reverse_duplicate_dict[row[14]][1]
	if row[14] in token_scrub:
		row[14] = '-1'
"""
# then pick out our CSV columns, where it identifies a character (not charID -1); row[11]=='PERSON' removes
# setup array of [CharID, Char Name, WordID]
charcsv = [[row[14],row[7],row[2]] for row in tokenlist if row[11]!='ORGANIZATION' and row[14]!='-1'] 

node_dict = {}

for row in charcsv:
	if row[0] in node_dict:
		if len(node_dict[row[0]]) < len(row[1]) and row[1].lower() not in stopchars:
			node_dict[row[0]] = row[1]
	else:
		node_dict[row[0]] = row[1]

edge_dict = {}
node_dict['-1'] = '' #ugly error fix for ugly adjacency-finder method below
prevcharid = '-1'
prevwordid = '0'
proximity = 20 # ugh, realizing there's a scene break problem, technically. no scene break markers unless: double \n, all caps?

# From here below adapted from Neal Caren http://www.unc.edu/~ncaren/cite_network/citenet.py not currently [25 Apr 2016] in https://github.com/nealcaren?tab=repositories

for row in charcsv:
	#check if the char is in node list, add CharID/Char Name keys to node list (drop wordid)

	# Character proximity: not yet working ... if (row[0] != prevcharid and int(row[2])-int(prevwordid) < proximity):
	if row[0] != prevcharid:
		# add edge between row and prevcharid to edge_dict ... wait: weight; are we adding one to weight, or are we doing what?
			name = node_dict[row[0]]
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
    if edge_dict[edge]>3:# and cite_dict[edge[0]]>=8 and cite_dict[edge[1]]>=8 :
        G.add_edge(edge[0],edge[1],weight=edge_dict[edge])
for node in G:    
    G.add_node(node) #adds list of nodes separately thru dict lookup

import community

partition=community.best_partition(G)

for node in G:    
    G.add_node(node, group=str(partition[node]))

d3_js.export_d3_js(G,files_dir="netweb",graphname="cites",node_labels=True,group="group")

fix=open('netweb/cites.json','rb').read()
# Not sure what this is fixing tbh
# for n in G:			
#     try:
#         fix=re.sub(str(n)+'''"''',str(n)+'''" , "nodeSize":'''+str(cite_dict[n]),fix) 
#     except:
#         print 'error with',n
f = open('netweb/cites.json', 'w+')
f.write(fix)
f.close()






