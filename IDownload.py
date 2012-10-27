'''
Created on Jul 9, 2012

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

