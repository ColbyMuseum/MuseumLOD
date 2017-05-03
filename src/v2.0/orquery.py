"""
orquery: represents reconciliation queries from OpenRefine's Reconciliation Service API.
"""

class ORQuery:

	# FIXME: Currently stores, but doesnt use "type_strict," "limit," and "properties" query elements.

	def __init__(self, incoming_query):
		self.query = incoming_query['query']
		self.matches = []
		query_params = incoming_query.keys()
		types_dictionary = {} # Types dictionary expects keys as namespace id, values as namespace name 

		if 'limit' in query_params:
			self.limit = int(incoming_query['limit'])
		else:
			self.limit = 10

		if 'type' in query_params:
			self.search_type = incoming_query['type']
		else:
			self.search_type = ""

		if 'type_strict' in query_params:
			self.type_strict = incoming_query['type_strict']
		else:
			self.type_strict = ""

		if 'properties' in query_params:
			self.properties = incoming_query['properties']
		else:
			self.properties = {}

	def render_preview(self):
		results = "an HTML page"
		return results

	@property
	def result(self):
		"""
		Returns list object with matches formatted for the OpenRefine API in JSON.
		At present this assumes only multiple query mode, so OR is getting results in the form:

		[ 'q1': { 'result': 
			[ { 
			'id': id_num0,
			'name': 'Match Name 0'
			'score': match_score_normalized_to_100
			'match': True/False
			'view': { 'url': 'http://localhost:5000/preview/{{id_num0}}' }
			'preview': {
				'url': 'http://localhost:5000/preview/{{id_num0}}',
				'width': 430,
				'height': 300 }
			},
			{'id': id_num1,
			'name': 'Match Name 1'
			'score': match_score_normalized_to_100
			'match': True/False
			'view': { 'url': 'http://localhost:5000/preview/{{id_num1}}' }
			'preview': {
				'url': 'http://localhost:5000/preview/{{id_num1}}',
				'width': 430,
				'height': 300 }
			}, 
			.
			.
			.
			.
			]},
		'q2': { 'result':
			.
			.
			.
			etc
		This object is only the query itself, so we return a dictionary w/ a single key
		of 'result'.		
		"""	

		all_matches = [] 
		types = []

		for match in self.matches:
		
			if self.search_type in self.types_dictionary.keys():
				types = [{ 'id': self.search_type,
					'name': self.types_dictionary[self.search_type] }]
			else:
				for key in self.types_dictionary:
					types.append({ 'id': key, 'name': self.types_dictionary[key] })

			all_matches.append({
				'id': match.match_id,
				'name': match.name,
				'score': match.score,
				'match': match.match_boolean,
				'view': match.view,
				'preview': match.preview,
				'type': types
				})
		
		result = { 'result': all_matches }
		return result
		   
class Match:

	def __init__(self,match_id, match_uri, score, name, match_boolean):
		self.match_id = match_id
		self.match_uri = match_uri
		self.score = score
		self.name = name
		self.match_boolean = match_boolean
		self.view = { 'url': 'http://localhost:5000/preview/%s' % self.match_id  }
		self.preview = { 'url': 'http://localhost:5000/preview/%s' % self.match_id,
			'width': 400,
			'height': 300
			}				
		
