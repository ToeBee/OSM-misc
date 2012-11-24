from optparse import OptionParser
import urllib
import math
import time

def buildURL(zoom, x, y):
    return 'http://a.tile.openstreetmap.org/{0}/{1}/{2}.png/dirty'.format(zoom, x, y)
    #return 'http://otile3.mqcdn.com/tiles/1.0.0/osm/{0}/{1}/{2}.png/dirty'.format(zoom, x, y)


parser = OptionParser()
parser.add_option('-z', action="store", type="int", dest="zoom")
parser.add_option('-t', action='store', type='int', nargs=2, dest='top')
parser.add_option('-b', action='store', type='int', nargs=2, dest='bot')
(options, args) = parser.parse_args()
left = 0
right = math.pow(2,options.zoom)-7
top = 0
bottom = math.pow(2,options.zoom)-7
try: 
  left = options.top[0]
  top = options.top[1]
  right = options.bot[0]
  bottom = options.bot[1]
except:
  print "error parsing args, using defaults"

#if options.top is None
#  options.top[0] = 0

#print options.top[0]

count = 0
for x in range(left, right+7, 8):
    for y in range(top, bottom+7, 8):
	url = buildURL(options.zoom, x, y)
	print url
	f = urllib.urlopen(url)
	#print f.read()
	count += 1
	time.sleep(0.3)

print "dirtyed out {0} tiles".format(count)
