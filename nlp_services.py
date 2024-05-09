from collections import defaultdict

import spacy


def load_nlp_model(model_name="en_core_web_trf"):
    return spacy.load(model_name)

def extract_entities(nlp_model,text):
    document = nlp_model(text)
    entities_dict = defaultdict(set)
    for entity in document.ents:
        entities_dict[entity.label_].add(entity.text)
    #return entities_dict
    #print(entities_dict)
    return entities_dict["ORG"]

def ner(affiliations):
    output =[]
    nlp_model = load_nlp_model("en_core_web_trf")
    for text in affiliations:
        output.append(extract_entities(nlp_model,str(text)))
    return output