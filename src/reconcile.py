"""
GVP Reconciliation service for OpenRefine 2.6-beta1.

Takes query data from URL request, coarsely searches for it against the Getty Vocab SPARQL endpoint, returns JSON of possible .

Adapted by Charlie Butcosk from http://code.google.com/p/google-refine/wiki/ReconciliationServiceApi, Mike Stephens' demo reconciler service, https://github.com/mikejs/reconcile-demo, and Alex Dergachev's redmine-reconciler, https://github.com/dergachev/redmine-reconcile 

The service takes in multi-mode queries from a RESTful URL call and formats as a SPARQL query on the Getty Vocabularies' endpoint (http://vocab.getty.edu).

Results from the endpoint are then parsed and formatted as the response to the initial call of the service.

TODO:
- Half-implemented code to take in english-langauge material descriptions of objects and return CSV lists of GVP terms.
- ULAN searching.
- Preview/suggest function to streamline picking through multiple term entries. 
"""

import re, requests, pprint

from flask import Flask, request, jsonify, json
app = Flask(__name__)

# Basic service metadata. "preview" functionality is not implemented yet, though the metadata tag is there.
metadata = {
	"name" : "GVP Reconciliation Service",
	"preview" : {
		"url" : "http://www.getty.edu/vow/AATFullDisplay?find=&logic=AND&note=&subjectid={{id}}",
		"width" : 430,
		"height" : 300
	}, 
	"defaultTypes": [{"id": "/gvp/aat", "name": "Material Descriptor"}]
	}

# Sparql query and URLs against which we will be searching
url_base = 'http://vocab.getty.edu/sparql.json'

def ulan_search(query):

	matches = []
	# fuzz query
	
	# build sparql requests for query
	ulan_query_head = 'XXX'
	ulan_query_tail = 'XXX'
	ulan_sparql_query = ulan_query_head+query.lower()+ulan_query_tail # after fuzzing, this will become a for loop for every fuzzed query

	# send requests
	ulan_query_response = requests.get(url_base, params={'query': sparql_query}) # should be try/catch for HTTP errs
	ulan_response_json = ulan_query_response.json()

	# strip header from response
	ulan_matches = ulan_response_json['results']['bindings']

	#if matches, add matches
	if not ulan_matches:
		return matches
	else:
		for match in ulan_matches:
			matches.append(match)

	return matches

def parse_media(media):
	
	results = []
	
	separator = ' and | on | to | with | in |\; |\, '
	regex_separator = re.compile(separator)

	# Check that media is composed of chars/string data, change from unicode
	if type(media) is not ascii:
		media_ascii = media.encode('ascii', 'ignore')
	else:
		medai_ascii = media

	# FIXME: Need to strip anything in parentheses
	media_split = media_ascii.split(regex_separator)

	for term in media_split:
	 	matches = aat_search(term)
		if len(matches) > 1:
			print 'Multiple matches found.\nMatch string was: %s\nPossible matches for %s are:\n' % (media,term)
			for i,match in matches:
				print "%s. %s(%s)\n" % (i,match['name'],match['score'])
			
			choice = raw_input('Which of these is a match?')
			results.append(matches[choice])
		elif matches:
			results.append(matches)
		else:
			print 'No matches found.'
	
	# FIXME: 
	# - It would be nice if this returned a dictionary and term matches were saved so we only query on terms we haven't already
	

	return results

def aat_search(query):

	matches = []

	# build AAT sparql queries, searching by lucene index (a somewhat fuzzy search), minus the activities facet, and then filtered for entries that are either objects or materials, then finds exact matches in gvp:term.

	aat_query_head = 'select ?entry ?label ?score { ?entry luc:term "'
	aat_query_mid = '"; gvp:prefLabelGVP/xl:literalForm ?label; luc:score ?score. filter ( exists { ?entry gvp:broaderExtended aat:300264092 } || exists { ?entry gvp:broaderExtended aat:300264091 } ) filter exists { ?entry (xl:prefLabel|xl:altLabel)/gvp:term ?term. filter (lcase(str(?term)) = "'
	aat_query_tail = '")}}'
	
	aat_sparql_query = aat_query_head+query.lower()+aat_query_mid+query.lower()+aat_query_tail

	# send request, get json
	aat_query_response = requests.get(url_base, params={'query': aat_sparql_query}) # FIXME: should be try/catch for HTTP errs
	aat_response_json = aat_query_response.json()

	# strip header from response
	aat_matches = aat_response_json['results']['bindings']

	# if matches, add matches
	if not aat_matches:
		# FIXME: need term-filter logic here.
		# If there are parens in the term, axe them, if there are numbers, get rid of them, if there are special chars or punctuation, if there are two terms, split them and search for each, et
		return matches
	else:
		max_score = float(aat_matches[0]['score']['value'])
		for match in aat_matches:
			
			label_literal = match['label']['value'].encode('ascii','ignore') # FIXME: should not just drop special chars
			aat_uri = match['entry']['value']
			aat_id = aat_uri.split('/')[-1] # get the last element of the URI, the AAT ID
			
			result_literal = label_literal+' AAT:('+aat_id+')' # matches are sent to OpenRefine as GVP tpref term as string, AAT:(ID in parens)
			
			if max_score != 0:
				score = (float(match['score']['value'])/max_score)*100 # scores normalize to their own max lucene score (a hack...) 

			matches.append({
				"id": aat_id,
				"name": result_literal,
				"score": score,
				"match": False,
				"type": [
					{"id": "/gvp/aat",
					"name": "Material Descriptor"}]})


	return matches

def new_search(query):
	
	# for now this packages query results as a JSON for an OpenRefine reconciliation service
	# ideally this would happen in reconcile()

	print query

	matches = []
	#ulan_matches = ulan_search(query)
	#if ulan_matches:
		# matches.append()
	aat_matches = aat_search(query)
	#if aat_matches:
		#matches.append()
	return aat_matches

	

def search(query):
	"""
	Format of JSON objects returned from the SPARQL endpoint:
	{'results' : { 'bindings' : { 'entry' : { 'type' : 'uri' , 'value' : 'XXX'}}}

	But if no results are returned, there is no 'entry'
	"""
	print query

	matches = []
	sparql_query = query_head+query.lower()+query_tail

	query_response = requests.get(url_base,
			params={'query': sparql_query}) # should be try/catch for HTTP errs
	response_json = query_response.json()

	response_json_nohead = response_json['results']['bindings'] # strip header of 'results' and 'bindings, leaves either null obj (no results) or { 'entry' : { 'type' : 'uri', 'value' : 'XXX'} , 'title' : { ....} 

	if not response_json_nohead:
		return matches
	else:
		for result in response_json_nohead:
			
			label_literal = result['label']['value'].encode('ascii','ignore') # should not just drop special chars
			aat_uri = result['entry']['value']
			aat_id = aat_uri.split('/')[-1]
			print aat_id
			result_literal = label_literal+' AAT:('+aat_id+')' # should show AAT ID in parens

			score = int(100/len(response_json_nohead))

			pprint.pprint(score)
			matches.append({
				"id": len(matches),
				"name": result_literal,
				"score": score,
				"match": True,
				"type": [
					{"id": "/gvp/aat",
					"name": "Material Descriptor"}]})

		return matches


def jsonpify(obj):
    """
    Like jsonify but wraps result in a JSONP callback if a 'callback'
    query param is supplied.
    """
	
    try:
        callback = request.args['callback']
        response = app.make_response("%s(%s)" % (callback, json.dumps(obj)))
        response.mimetype = "text/javascript"
        return response
    except KeyError:
        return jsonify(obj)


@app.route("/reconcile", methods=['POST', 'GET'])
def reconcile():
    # If a single 'query' is provided do a straightforward search.
#	str("Let's start reconciling!")
    query = request.form.get('query')
    if query:
	pprint.pprint('query')
        # If the 'query' param starts with a "{" then it is a JSON object
        # with the search string as the 'query' member. Otherwise,
        # the 'query' param is the search string itself.
        if query.startswith("{"):
            query = json.loads(query)['query']
        results = new_search(query)
        return results #jsonpify({"result": results})

    # If a 'queries' parameter is supplied then it is a dictionary
    # of (key, query) pairs representing a batch of queries. We
    # should return a dictionary of (key, results) pairs.
    queries = request.form.get('queries')
    if queries:
        queries = json.loads(queries)
        results = {}
        for (key, query) in queries.items():
            results[key] = {"result": new_search(query['query'])}
        return jsonpify(results)

    # If neither a 'query' nor 'queries' parameter is supplied then
    # we should return the service metadata.
    return jsonpify(metadata)

if __name__ == '__main__':
    app.run(debug=True)
