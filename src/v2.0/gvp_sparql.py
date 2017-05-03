"""
gvp_sparql: functions to search Getty Vocabulary Program's SPARQL endpoint.

FIXME:
- This should be a whole class, GVPQuery or something.
"""
import requests

# Sparql query and URLs against which we will be searching
url_base = 'http://vocab.getty.edu/sparql.json'

def aat_search(query):

	matches = []

	# Build AAT sparql query: search by lucene index (a somewhat fuzzy search), 
	# minus the activities facet, and then filtered for entries that are either 
	# objects or materials, then finds exact matches in gvp:term.

	aat_sparql_query = 'select ?entry ?label ?score { ?entry luc:term "%s"; gvp:prefLabelGVP/xl:literalForm ?label; luc:score ?score. filter ( exists { ?entry gvp:broaderExtended aat:300264092 } || exists { ?entry gvp:broaderExtended aat:300264091 } ) filter exists { ?entry (xl:prefLabel|xl:altLabel)/gvp:term ?term. filter (lcase(str(?term)) = "%s")}}' % (query.lower(),query.lower())

	# Send the HTTP request, parse from JSON.
	# FIXME (PRI 3): should be try/catch for HTTP errs

	aat_query_response = requests.get(url_base, params={'query': aat_sparql_query})
	aat_response_json = aat_query_response.json()
	aat_matches = aat_response_json['results']['bindings'] # strip header from response
	
	if not aat_matches:
		# FIXME: 
		# * If we didn't find any matches, try re-parsing the query, getting rid of parenteses,
		# colons, semicolons?
		# *	If there are parens in the term, axe them, if there are numbers, get rid of them, 
		# 	if there are special chars or punctuation, if there are two terms, split them and search 
		# 	for each, etc
		return matches
	else:	
		# The results are sorted by Lucene match scores, which is a relative scale.
		# So, grab the top match score and normalize to it.
		max_score = float(aat_matches[0]['score']['value'])

		for match in aat_matches:
			
			 # FIXME (PRI 2): should correctly handle non-ASCII chars
			label_literal = match['label']['value']		
			aat_uri = match['entry']['value']
			aat_id = aat_uri.split('/')[-1] # get the last element of the URI, the AAT ID
			
			# Matches are sent to OpenRefine w GVP term as string, AAT:(ID in parens)
			result_literal = '%s AAT:(%s)' % (label_literal, aat_id)			
			if max_score != 0:
				score = (float(match['score']['value'])/max_score)*100 # scores normalize to their own max lucene score (a hack...) 

			# FIXME: All this metadata logic should be up in the Flask section.
			matches.append({
				"id": aat_id,
				"name": result_literal,
				"score": score,
				"match": False,
				"type": [
					{"id": "/gvp/aat",
					"name": "Material Descriptor canary"},
					{"id": "/gvp/aat_full",
					"name": "Unparsed Material Description canary"}]})


	return matches

def ulan_search(query):

	matches = {}
	
	# Build sparql around the incoming service query.
	ulan_sparql_query = 'select * {?artists luc:term "' + query.lower() 
	+ '"skos:inScheme ulan:; rdf:type gvp:PersonConcept'

	# send requests 
	# FIXME: This should be in a try/catch block.
	ulan_query_response = requests.get(url_base, params={'query': ulan_sparql_query})
	ulan_response_json = ulan_query_response.json()

