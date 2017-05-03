"""
Reconciliation service (against the Getty Vocab) for OpenRefine 2.6-beta1.

Takes query data from URL request, coarsely searches for it against the Getty Vocab SPARQL endpoint, 
returns JSON of potential matches. The service takes in multi-mode queries from a RESTful URL call
and formats as a SPARQL query on the Getty Vocabularies' endpoint (http://vocab.getty.edu).

Results from the endpoint are then parsed and formatted as the response to the initial call of the service.

Tested on the Colby College Museum of Art dataset (http://github.com/CoblyMuseum/MuseumLOD).
Adapted by Charlie Butcosk from:

* Example code at http://code.google.com/p/google-refine/wiki/ReconciliationServiceApi 
* Mike Stephens' demo reconciler service at https://github.com/mikejs/reconcile-demo
* Alex Dergachev's redmine-reconciler, https://github.com/dergachev/redmine-reconcile 


FIXME:
- ULAN searching. FIXME (PRI 1)
- Fix preview flyouts. FIXME (PRI 0) 
"""

import re, requests
from pprint import pprint
from flask import Flask, request, jsonify, json, render_template
from gvpquery import GVPQuery

app = Flask(__name__)

# Basic service metadata. "preview" functionality is not implemented yet, though the metadata tag is there.
metadata = {
	"name" : "GVP Reconciliation Service",
	"limit": 10,
	"view": { "url" : "http://localhost:5000/preview/{{id}}"},
	"preview": {
		"url": "http://localhost:5000/preview/{{id}}",
		"width" : 430,
		"height" : 300
	},
	"defaultTypes": [{"id": "/gvp/aat", "name": "Single Material"},
	{"id": "/gvp/aat_full", "name": "Full Material Description"}]
	}

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

	query = request.form.get('query')
        
	if query:
	# If the 'query' param starts with a "{" then it is a JSON object
        # with the search string as the 'query' member. Otherwise,
        # the 'query' param is the search string itself.
        
		if query.startswith("{"):
            		query = json.loads(query)['query']
			query_full = json.loads(query)
        	results = search(query)
        	return jsonpify({gvp_query.result})

	# If a 'queries' parameter is supplied then it is a dictionary
	# of (key, query) pairs representing a batch of queries. We
	# should return a dictionary of (key, results) pairs.

	queries = request.form.get('queries')
	
	if queries:
		queries = json.loads(queries)

		# If there is a type,
		# /gvp/aat searches on aat_search.
		# /gvp/aat_full calls parse_media_description on query.

		results = {}

		for (key, query) in queries.items():
			gvp_query = GVPQuery(query)
			gvp_query.search()
			results[key] = gvp_query.result
        	return jsonpify(results)

	# If neither a 'query' nor 'queries' parameter is supplied then
	# we should return the service metadata.
	return jsonpify(metadata)

@app.route('/preview/')
@app.route('/preview/<id_num>')
def preview(id_num=None):
	# FIXME: should repackage gvp data to make selection simpler
	# - Can use two render templates (one for AAT, one for AAT_FULL)
	# - Shows any @en ScopeNote for an ID, along w full text hierarchy
	# - AAT_FULL shows that for each ID in the statement
	
	if ',' not in id_num: # Multi-entry IDs are passed w/ commas
		# single-item AAT
		vocab_uri = "http://vocab.getty.edu/aat/%d.json" % id_num
		r = requests.get(vocab_uri)
		entry_data = r.json()
		# - Parse Pred/Obj tuples out of data
		# - Take GVPPrefLabel (or xl:prefLabel), get data from getty, assign literal to name 
		# - Take any ScopeNotes, get data from getty, assign literal to name
		# - Pass those to render_template
		scope_note = ""
		pref_name = ""

		

		return render_template('aat_entry.html', scope_note = "This is a note.", 
			pref_name = "This is a pref_name.", id_num=id_num)
	else:
		# multiple-item AAT result
		# - Sep(id_num) by ','
		# - Get each term's JSON rep
		# - pass each to a different template for multiple entries
		return render_template('preview.html', id_num=id_num)

		
	
if __name__ == '__main__':
	app.run(debug=True)
