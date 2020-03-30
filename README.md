# NLP Tools
This package will contain some useful modules and subpackages containing useful utilities for working with NLP and spaCy.
These are often supplemental to medSpaCy.

- `nlp_preprocessor`: A component for modifying text before it is tokenized by a spaCy model
- `nlp_postprocessor`: A component which executes rules on entities in `doc.ents` and can remove entities, change labels,
or execute other custom logic based on entities
- `target_matcher`: A wrapper class for rule-based matching in spaCy, with allowing for other functionality such as 
passing in custom attributes or metadata to the rules