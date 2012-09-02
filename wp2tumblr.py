'''
wp2tumblr by Jon Thornton
thornton.jon@gmail.com
Updated 2010-03-29

This script will take an exported WordPress blog and import it into
a Tumblr account. Everything will be posted as text.

'''

from xml.dom import minidom
import urllib, urllib2, time, sys, os, getopt, types
from urllib2 import URLError, HTTPError

tumblr_credentials = {}
start_loop = 0
tumblr_api = 'http://www.tumblr.com/api/write'
USAGE = 'Useage: python wp2tumblr.py -u tumblr-email-address -p tumblr-passwordd [-g blog-url] [-s start-post] wordpress-xml-export-path'


# check the command arguments
try:
	login_opts, file_path = getopt.getopt(sys.argv[1:], 'u:p:g:s:')
	wp_xml = file_path[0]

	for opt, value in login_opts:
		if opt == '-u':
			tumblr_credentials['email'] = value;
		elif opt == '-p':
			tumblr_credentials['password'] = value
		elif opt == '-g':
			tumblr_credentials['group'] = value.replace('http:', '').strip('/')
		elif opt == '-s':
			start_loop = int(value)

except:
	print USAGE
	sys.exit(2)

if len(tumblr_credentials) < 2:
	print USAGE
	sys.exit(2)

if not os.path.exists(wp_xml):
	print 'WordPress xml file ' + wp_xml + ' not found!'
	sys.exit(2)

try:
	dom = minidom.parse(wp_xml)
except Exception, detail:
	print 'XML file must be well-formed. You\'ll need to edit the file to fix the problem.'
	print detail
	sys.exit(2)

items = dom.getElementsByTagName('item')
total_post = items.length
print "Total posts " + str(total_post)
for x in xrange(start_loop,total_post):
	print "start post number " + str(x)
	item = items[x]
	# only import published
	if item.getElementsByTagName('wp:status')[0].firstChild.nodeValue != 'publish':
		continue;

	# only import posts, not pages or other stuff
	if item.getElementsByTagName('wp:post_type')[0].firstChild.nodeValue != 'post':
		continue;

	if len(item.getElementsByTagName('title')[0].childNodes) == 0:
		continue;

	post = tumblr_credentials
	post['type'] = 'text';
	post['title'] = item.getElementsByTagName('title')[0].firstChild.nodeValue.strip().encode('utf-8', 'xmlcharrefreplace')
	post['date'] = item.getElementsByTagName('pubDate')[0].firstChild.nodeValue

	content = item.getElementsByTagName('content:encoded')[0].firstChild

	if content.__class__.__name__ != 'CDATASection':
		continue

	post['body'] = item.getElementsByTagName('content:encoded')[0].firstChild.nodeValue.encode('utf-8', 'xmlcharrefreplace')
	print post["title"]

	# deal with WordPress's stupid embedded Unicode characters
	post = dict([(k,v.encode('utf-8') if type(v) is types.UnicodeType else v) for (k,v) in post.items()])

	data = urllib.urlencode(post) # Use urllib to encode the parameters

	try:
		request = urllib2.Request(tumblr_api, data)
		response = urllib2.urlopen(request) # This request is sent in HTTP POST

		page = response.read(200000)
		print page
	except HTTPError, e:
	    print 'The server couldn\'t fulfill the request.'
	    print 'Error code: ', e.code
	    print e.read()
	    sys.exit(2)
	except URLError, e:
	    print 'We failed to reach a server.'
	    print 'Reason: ', e.reason
	    sys.exit(2)

	time.sleep(1) # don't overload the Tumblr API
