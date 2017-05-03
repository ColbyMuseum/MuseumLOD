"""
gvpquery: class for OpenRefine reconciliation queries against the GVP, inherits from ORQuery.
"""

import requests, re, itertools
from orquery import ORQuery, Match
from pprint import pprint

class GVPQuery(ORQuery):

	def __init__(self, incoming_query):
		ORQuery.__init__(self, incoming_query)
		self.types_dictionary = {"/gvp/aat_full": "Full Material Description", 
					"/gvp/aat": "Single Material"}
		self.url_base = 'http://vocab.getty.edu/sparql.json'
		self.preview_base = 'http://localhost:5000/preview/'
		self.view_base = 'http://localhost:5000/preview/'

	def search(self):

		if self.search_type == u"/gvp/aat":
			print "Search type is %s." % self.search_type
			self.aat_search()
		elif self.search_type == u"/gvp/aat_full":
			print "Search type is %s." % self.search_type
			self.parse_media_description()
		else:
			print "Untyped query, searching all."
			self.aat_search()
			self.parse_media_description()
		#self.search()
 
	def aat_search(self):

		# FIXME: This should check for (and disregard):
		colors = ['yellow', 'pink','white']
		adjectives = []
		# - State information
		# - Color names
		# - Integers
		# - Adjectives (dark, light, etc)
		# - Toss anything in parens
		# - Toss printer/publisher stuff

		# Build AAT sparql query: search by lucene index (a somewhat fuzzy search), 
		# minus the activities facet, and then filtered for entries that are either 
		# objects or materials, then finds exact matches in gvp:term.

		aat_sparql_query = 'select ?entry ?label ?score { ?entry luc:term "%s"; gvp:prefLabelGVP/xl:literalForm ?label; luc:score ?score. filter ( exists { ?entry gvp:broaderExtended aat:300264092 } || exists { ?entry gvp:broaderExtended aat:300264091 } ) filter exists { ?entry (xl:prefLabel|xl:altLabel)/gvp:term ?term. filter (lcase(str(?term)) = "%s")}}' % (self.query.lower(),self.query.lower())

		# Send the HTTP request, parse from JSON.
		# FIXME: should be try/catch for HTTP errs

		aat_query_response = requests.get(self.url_base, params={'query': aat_sparql_query})
		aat_response_json = aat_query_response.json()
		aat_results = aat_response_json['results']['bindings'] # strip header from response

		if not aat_results:
			print "No matches found. Bummer!"
		else:	
			# The results are given w Lucene match scores, which is a relative scale.
			# So, grab the top match score and normalize to it.
			max_score = float(aat_results[0]['score']['value'])

			for result in aat_results:
		
				aat_uri = result['entry']['value']
				score = float(result['score']['value'])/max_score*100.0
			
				# Match ID is AAT IDs on single-term searches,
				# so take the end of the URI of the GVPConcept	
				aat_id = aat_uri.split('/')[-1]
				
				# Match names are sent the GVP term as string, "AAT:(ID in parens)" at end
				name =  '%s AAT:(%s)' % (result['label']['value'], aat_id)
				match = Match(aat_id,aat_uri,score,name,False)
			
				self.matches.append(match)

	def ulan_search(self):
		print "Searching ULAN..."

	def parse_media_description(self):
	
		separator = ' and | on | to | with | in |\; |\, '

		aat_candidates = re.split(separator, self.query)
		
		"""
		# FIXME: rudimentary search filter: don't search for colors, numbers, "state",
		# things in parens, adjectival qualifiers (dark, light, etc)
		"""
		result_names = []
		result_ids = []
		name_combos = []
		id_combos = []

		for term in aat_candidates:
			aat_match_names = []
			aat_match_ids = []
			aat_query = { u'query': term, u'type': u"/gvp/aat" }
			gvp_query = GVPQuery(aat_query)
			gvp_query.search()
	
			if len(gvp_query.matches) > 0:
				for match in gvp_query.matches:
					aat_match_names.append(match.name)
					aat_match_ids.append(str(match.match_id))
				result_names.append(aat_match_names)
				result_ids.append(aat_match_ids)

		for element in itertools.product(*result_names):
			# Make this a Match() object, and...
			match_name = ",".join(element)
			print "Full Text Match is: %s" % match_name
			name_combos.append(match_name) 
		
		for element in itertools.product(*result_ids):
			match_id = ",".join(element)
			id_combos.append(match_id)
			
		for i in range(0,len(name_combos)):
			match = Match(id_combos[i],'',100,name_combos[i],False)
			self.matches.append(match)
