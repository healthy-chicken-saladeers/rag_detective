NER_PROMPT = """Using the context, do entity recognition of these texts using PER (person), ORG (organization),
LOC (place name or location), TIME (actually date or year), and MISC (formal agreements and projects).

EXAMPLES:
Here are the definitions with a few examples, do not use these examples to answer the question:

PER (person): Proper nouns which refer to specific individuals, including titles. It is not common nouns or groups.
Example:
- Barack Obama, former President of the United States
- J. R. R. Tolkien, author of the Lord of the Rings book series
- Michelle Wu, current mayor of Boston

ORG (organization): Refers to formally organized groups of people, public and private, including companies, armed forces, and governments, whether their departments or as a whole.
Example:
- Microsoft Corporation, a multinational technology company
- United Nations, an intergovernmental organization
- the Ministry of Culture of the Republic of Tajikistan, a ministry in the government of Tajikistan

LOC (place name or location): Refers to specific geographic locations such as countries, bodies of water, cities, and other landmarks. It does not refer to anything larger than a country, such as a region or continent. It can be a noun or adjective.
Example:
- London, capital of England
- Eiffel Tower, a landmark in Paris, France
- the Mediterranean, a European sea connected to the Atlantic Ocean

TIME (date or year): Refers to dates, months, and years, but not hours or times of day.
Example:
- January 1st, 2023, the start of a new year
- 1995, the year Toy Story was released

MISC (formal agreements and projects): Formal agreements and projects between two or more countries or organizations, including treaties and task forces.
Example:
- Apollo program, a series of manned spaceflight missions undertaken by NASA
- the Joint Control Commission, a trilateral peacekeeping force and joint military command structure from Moldova, Transnistria, and Russia

FORMAT:
Provide them in JSON format with the following 6 keys:
- PER: (list of people)
- ORG: (list of organizations)
- LOC: (list of locations)
- TIME: (list of times)
- MISC: (list of formal agreements and projects)

Before you generate the output, make sure that the named entities are correct and part of the context. 
Do not include any named entities that are part of the EXAMPLES.
If the named entities are not part of the context, do not include them in the output. 
Please add a comma after each value in the list except for the last one. 

Context: {page_content}

Output in JSON format: 
"""


NER_LOC_PROMPT = """Using the context, extract one location. If there are multiple locations, extract the most important one.

EXAMPLES:
Here are the definition with a few examples, do not use these examples to answer the question:

LOC (location name): Refers to specific geographic locations such as a country or a city. It does not refer to a region, a continent, an island or body of water.
Example:
- London
- United States
- Peru
- Montreal
- Jakarta

Bad Examples:
- East of the Mississippi River
- the Mediterranean
- East Jakarta

FORMAT:
The location should be a string and have no other characters or spaces.
LOC: (location name)

Before you generate the output, make sure that the location is correct and part of the context. 
Make sure that location is a real location.
Do not include any locations that are part of the EXAMPLES.
If the location is not part of the context, do not include it in the output. 
If there is no location of a country or city mentioned in the context, return empty string: ''

Context: {page_content}

LOC: 
"""


NER_LOC_RADIUS_PROMPT = """Using the context, extract one location and the kilometer radius. If there are multiple locations, extract the most important one.

EXAMPLES:
Here are the definition with a few examples, do not use these examples to answer the question:

LOC (location name): Refers to specific geographic locations such as a country or a city. It does not refer to a region, a continent, an island or body of water.
Example:
- London
- United States
- Peru
- Montreal
- Jakarta

Bad Examples:
- East of the Mississippi River
- the Mediterranean
- East Jakarta

RADIUS (kilometer radius): Refers to the distance from the location in kilometers. 
If there is no radius, return 0. If radius is in miles, convert it to kilometers.
Example:
- 19
- 100
- 0.5


FORMAT:
Provide them in JSON format with the following 2 keys:
LOC: (location name as a string)
RADIUS: (kilometer radius as a float)

Before you generate the output, make sure that the location is correct and part of the context. 
Make sure that location is a real location.
Do not include any locations that are part of the EXAMPLES.
If the location is not part of the context, do not include it in the output. 
If there is no location of a country or city mentioned in the context, return None.

Context: {page_content}

Output in JSON format: 
"""


NER_PROMPT_1 = """Using the context, do entity recognition of these texts using PER (person), ORG (organization),
LOC (place name or location), TIME (actually date or year), and MISC (formal agreements and projects) and the Sources (the name of the document where the text is extracted from).
The source can be extract at the end of the context after '\nSource: '.
"Make sure the sure is prefixed with 'Source: ' and is on a new line. Do not include any sources that are part of the text."


FORMAT:
Provide them in JSON format with the following 6 keys:
- PER: {list of people}
- ORG: {list of organizations}
- LOC: {list of locations}
- TIME: {list of times}
- MISC: {list of formal agreements and projects}
- SOURCES: {list of sources}


EXAMPLES:
Here are the definitions with a few examples, do not use these examples to answer the question:
PER (person): Proper nouns which refer to specific individuals, including titles. It is not common nouns or groups.
Example:
- Barack Obama, former President of the United States
- J. R. R. Tolkien, author of the Lord of the Rings book series
- Michelle Wu, current mayor of Boston

ORG (organization): Refers to formally organized groups of people, public and private, including companies, armed forces, and governments, whether their departments or as a whole.
Example:
- Microsoft Corporation, a multinational technology company
- United Nations, an intergovernmental organization
- the Ministry of Culture of the Republic of Tajikistan, a ministry in the government of Tajikistan

LOC (place name or location): Refers to specific geographic locations such as countries, bodies of water, cities, and other landmarks. It does not refer to anything larger than a country, such as a region or continent. It can be a noun or adjective.
Example:
- London, capital of England
- Eiffel Tower, a landmark in Paris, France
- the Mediterranean, a European sea connected to the Atlantic Ocean

TIME (date or year): Refers to dates, months, and years, but not hours or times of day.
Example:
- January 1st, 2023, the start of a new year
- 1995, the year Toy Story was released

MISC (formal agreements and projects): Formal agreements and projects between two or more countries or organizations, including treaties and task forces.
Example:
- Kyoto Protocol, an international agreement to address climate change
- Apollo program, a series of manned spaceflight missions undertaken by NASA
Obamacare, a healthcare reform law in the United States.
- the Joint Control Commission, a trilateral peacekeeping force and joint military command structure from Moldova,
Transnistria, and Russia

Sources (list of sources of the text).
Example:
- Tom Clancy's Jack Ryan
- The New York Times
- Harry Potter and the Sorcerer's Stone
----------------

Before you generate the output, make sure that the named entities are correct and part of the context. 
If the named entities are not part of the context, do not include them in the output.
"""

NER_REFINE_TEMPLATE = (
    "The original question is as follows: {question}\n"
    "We have provided an existing answer: {existing_answer}\n"
    "Do not remove any entities or sources from the existing answer.\n"
    "We have the opportunity to update the list of named entities and sources\n"
    "(only if needed) using the context below delimited by triple backticks.\n"
    "Make sure any entities extracted are part of the context below. If not, do not add them to the list.\n"
    "If you see any entities that are not extracted, add them.\n"
    "The new source can be extracted at the end of the context after 'Source: '.\n"
    "Use only the context below.\n"
    "------------\n"
    "{context_str}\n"
    "------------\n"
    "Given the new context, update the original answer to extract additional entities and sources.\n"
    "Create a more accurate list of named entities and sources.\n"
    "If you do update it, please update the sources as well while keeping the existing sources.\n"
    "If the context isn't useful, return the existing answer in JSON format unchanged.\n"
    "Output in JSON format:"
)

NER_QUESTION_TEMPLATE = (
    "Context information is below. \n"
    "---------------------\n"
    "{context_str}"
    "\n---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the question: {question}\n"
    "Output in JSON format:"
)
