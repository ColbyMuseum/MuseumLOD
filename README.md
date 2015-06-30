# Open-licensed Collections Data for the Colby College Museum of Art

This repository contains the Colby College Museum of Art's first open release of collections data! This first release represents about one quarter of the museum's collection, including data for much of the Lunder Collection and for most of the works by Alex Katz in the collection. It is published under a Creative Commons 1.0 License, and its associated code is published under a BSD-style license (see below).

The data is the first result of the Museum's project to clean, normalize, and release collections data under an open license. At present, it is published in a flat text file without images (the data is also available in a searchable, but web-only, form at http://www.colby.edu/museum/?s). Our goal is ultimately to release this data as semantically-expressed linked data.

## Format

For V1.0, data are presented in a simple object/properties schema, JSON-wrapped as:

{
	"objects" : [
	{
		"embark_ID" : {{value)}}, 
		"artist" : {{value}},
		"title" : {{value}},
		"year_made" : {{value}},
		"year_acqd" : {{value}},
		"media" : {{value)}},
		"media_AAT" : {{value)}},
		"dimensions" : {{value)}},
		"printer" : {{value)}},
		"label" : {{value)}},
		"credit_Line" : {{value)}},
		"notes" : {{value)}},
		"accession_num" : {{value)}}
	} ]
}

## Schema

The properties of a given object are:

*embark_ID*: unique identifier field
*artist*: full name of object's creator
*title*: object's title
*year_made*: year of the object's creation
*year_acqd*: year the object entered Colby's collection 
*media*: description of object's material composition
*media_AAT*: media description as a comma-separated list of Getty Vocabulary terms 
*dimensions*: the object's physical dimensions as A x B in. (C x D cm)
*printer*: where applicable and available, an object's printer or replicator
*label*: where available, wall label data (historical notes, nationality notes, etc)
*credit_line*: collection 
*notes*: miscellaneous data (usually truncated tails from material descriptions)
*accession_num*: the object's accession number

Notes: 

- Because *accession_num*, though unique, can change over time, *embark_ID* is the object's key value. 

- *media_AAT* is a convenience field that provides the terms of *media* that reconcile to the Getty Vocabulary Project's Art and Architecture Thesaurus. Our intention is to expose this field as links to these terms on the GVP, so this field is expressed as the term's preferred Getty Vocabulary label, along w its Getty Vocabulary ID number (formatted as: term AAT:(gvp_id)). These terms are then comma-separated.

- The signal exceptions to the above dimension schema are 300-odd works on paper by James McNeil Whistler, which carry plate and sheet dimensions in mm, formatted as: "plate: A x B mm, sheet: C x D mm". 

## reconcile.py

Also in this repository is reconcile.py, a simple python script that provides a Flask-based reconciliation service for OpenRefine, (https://github.com/OpenRefine/OpenRefine). 

The service follows OpenRefine's reconciliation API, (https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API), and takes individual material terms (e.g., *oil paint*, *canvas*, or *engraving*, etc) and reconciles them to the object and material facets of the Getty Vocabulary Project's Art and Architecture Thesaurus via their SPARQL endpoint, (http://vocab.getty.edu). The code that supports this feature is based on two implementations of the OpenRefine API, primarily (https://github.com/dergachev/redmine-reconcile) and (https://github.com/mikejs/reconcile-demo).

## License

Collections Data of the Colby Museum of Art are provided with a Creative Commons 1.0 license, and reconcile.py is provided under the original BSD-style license of Michael Stephens' demo reconciliation service.

## Contact

museum@colby.edu
