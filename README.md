# Open-licensed Collections Data for the Colby College Museum of Art

This repository contains open-licensed releases of the Colby College Museum of Art's collections data. This release consists of nearly every object in the collection, including data for the Lunder Collection (including a number of prints by James McNeil Whistler), many works Alex Katz, a trove of works by Bernard Langlais, and much more. It is published under a [Creative Commons 1.0 License](https://creativecommons.org/publicdomain/zero/1.0/). Associated code is published under a BSD-style license (see below).

This data is the result of the Museum's project to clean, normalize, and release collections data under an open license as part of [the American Art Collaborative](http://www.americanartcollaborative.org). We have a human-legible interface at our [collection website](http://www.colby.edu/museum/?s=), our repo contains data as a JSON structure (detailed below), is available as N3 at [our AAC github repo](https://github.com/american-art/ccma), and will be available soon at our SPARQL endpoint.  

## JSON structure

In our JSON release, data is formatted as a dictionary containing three keys, "objects", "artists", and "exhibitions" that each contain an array of that record type. Each record is a dictionary of fields and their values. Objects have an array of dictionary, "Images", that express images about reproductions of individual objects (web URLs, primariness, reproduction date, etc). 

Strings without values are expressed as empty strings and there are no NULL values.

```
{
	"objects" : [
		{
      		"embark_ID" : *unique identifier*,
      		"URL" : "URL to record in CCMA's online collections",
      		"Disp_Access_No" : "CCMA accession number",
      		"_AccNumSort1" : "Sort order of accession number (usually nil)",
      		"Disp_Create_DT" : "Generated date field (usually 1234-5678 or ca.)",
      		"_Disp_Start_Dat" : "Earliest date of object creation",
 	     	"_Disp_End_Date" : "Latest date of object creation",
	      	"Disp_Title" : "Full title",
	      	"Alt_Title" : "Alternate title",
      		"Obj_Title" : "Object title",
      		"Series_Title" : "Series title",
      		"Disp_Maker_1" : "Maker name (usually FirstName LastName)",
      		"Sort_Artist" : "Sortable maker name (usually LastName, FirstName)",
      		"Disp_Dimen" : "Generated object dimensions (usually in x in (cm x cm))",
      		"Medium" : "Object medium (may also contain edition information for works on paper)",
		"Support" : "Object support (may also contain edition information for works on paper)",
      		"Info_Page_Comm" : "Object description for web access (deprecated)",
      		"Dedication" : "Object dedication and collection information",
      		"Copyright_Type" : "Object copyright limitations (deprecated)",
      		"Disp_Obj_Type" : "Object type (Sculpture, Ceramics, etc)",
      		"Creation_Place2" : "Object's place of creation (deprecated)",
      		"Department" : "Department of responsibility for object (deprecated)",
      		"Obj_Name" : "Object name (deprecated)",
      		"Period" : "Period of object creation",
      		"Style" : "Object style (deprecated)",
      		"Edition" : "Edition and state information for works on paper (where available)",
      		"Curator" : "Curator responsible for object description (deprecated)",
		"Images" : [
				{
				"IIIF_URL" : "IIIF ID URL for this image",
				**FIXME 
				},
				.
				.
				.
			]
    		},
		.
		.
		.
		.
    ]

	"exhibitions" : [
		{
		"embark_ID" : "Object present at exhibition",
		"Exhibition_Name" : "Exhibition name",
		"Start_Date" : "Start date of exhibition",
		"End_Date" : "End date of exhibition",
		"User_Def_1" : "Unique identifier for exhibition (projected)"
		},
		.
		.
		.
		.
		
	]
}
```

### Notes: 

- This release strips our previous release's *media_AAT* field, which should return in our planned LIDO-XML release of this data.

- A signal exceptions to the above dimension schema are 300-odd works on paper by James McNeil Whistler, which carry plate and sheet dimensions in mm, formatted as: "plate: A x B mm, sheet: C x D mm". 

## License

Collections Data of the Colby Museum of Art are provided with a Creative Commons 1.0 license, and reconcile.py is provided under the original BSD-style license of Michael Stephens' demo reconciliation service.

## Contact

If you have any questions about this release, or the Colby College Museum of Art's other digital projects, please contact us:
museum at colby.edu, cbutcosk at colby.edu
