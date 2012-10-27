'''
This is a script that takes a list of OSM IDs (one per line) and clusters them into API requests in 
groups of 50 objects to download them from an API endpoint. It then assembles them into a single .osm file.

I use this when I have a SQL query that finds certain objects of interest in my pgsnapshot database but I 
want to actually download and manipulate the data in an OSM editor. I have the query return nothing but 
object IDs, drop those into a file and then run it through this script to download the data from my 
local jxapi instance.

It is pretty braindead and may not be suitable for all situations. Specific limitations:
1) It straight up copies XML from the API response into the output file. This means order of object type 
   is not guaranteed and there may also be duplicate objects. For example, if two ways share a node, 
   that node may appear twice in the resulting .osm file, depending on if the ways were requested from 
   the API in the same request or not.
2) It builds the OSM XML document in memory. This limits  how many objects can be downloaded on any given 
   system. I estimate it takes a little over 1 GB per 10,000 OSM ways but this could vary by quite a bit 
   depending on how many nodes the ways have.
3) I have only run this against the jxapi. It behaves a little differently than the normal API as far as 
   returning member objects. When you request a way from the jxapi, you also get all of its member nodes. 
   when you request a way from the osm.org API, it only returns the way with node refs but not the nodes 
   themselves. (Same goes for relations and their members)

@author: toby
'''

import argparse
import urllib
from xml.dom.minidom import parseString

def chunks(l, n):
    for i in xrange(0,len(l), n):
        yield l[i:i+n]

class Output:
    
    def __init__(self, outputFile):
        self.outputFileName = outputFile
        self.isFirst = True
        
    def addChunk(self, apiResponse):
        if self.isFirst:
            self.outputXML = parseString(apiResponse)
            self.isFirst = False
        else:
            newChunk = parseString(apiResponse)
            elements = newChunk.getElementsByTagName("osm")
            for node in elements[0].childNodes:
                nodeCopy = self.outputXML.importNode(node, True)
                self.outputXML.childNodes[0].appendChild(nodeCopy)
            
    def finish(self):
        outputFile = open(self.outputFileName, 'w')
        outputFile.write(self.outputXML.toxml('UTF-8'))
        outputFile.close()

if __name__ == '__main__':
    
    MAX_OBJECTS = 50
    APIURL = 'http://localhost:8080/xapi/api/0.6/'
        
    argParser = argparse.ArgumentParser(description="Parse OSM Changeset metadata into a database")
    argParser.add_argument('-u', '--url', action='store', default=False, dest='apiUrl', help='URL of the API to query')
    argParser.add_argument('-f', '--file', action='store', dest='fileName', help='File containing a list of IDs to download')
    argParser.add_argument('-t', '--type', action='store', dest='type', help='OSM object type (N, W, R)')
    argParser.add_argument('-o', '--output', action='store', dest='outputFile', help='file to store the resulting data in')
    args = argParser.parse_args()
    
    output = Output(args.outputFile)
    
    idFile = open(args.fileName, 'r')
    
    idChunks = chunks(idFile.read().splitlines(), MAX_OBJECTS)
    chunkCount = 0
    for idChunk in idChunks:
        chunkCount += 1
        print 'fetching chunk: ' + str(chunkCount)
        idStr = ','.join(idChunk)
        typeStr = ''
        if args.type == 'N':
            typeStr = 'nodes?nodes='
        elif args.type == 'W':
            typeStr = 'ways?ways='
        elif args.type == 'R':
            typeStr = 'relations?relations='
        url = APIURL + typeStr + idStr
        #print url
        opener = urllib.FancyURLopener({})
        apiResponse = opener.open(url)
        output.addChunk(apiResponse.read())
        
    output.finish()

