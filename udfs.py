import json


def ieee(match):
    found_affs=set()
    msg=''
    
    json_str = match.group(1)
    data = json.loads(json_str)
    try:
        for author in data["authors"]:
            try:
                found_affs.add(author["affiliation"][0])
            except: 
                pass  # not all entries have an "aff
    except:
        pass
    return found_affs

def oup(match):
    found_affs=set()
    msg=''
    json_str = match.group(1)
    data = json.loads(json_str)
    try:
        for author in data['author']:
            try:
                found_affs.add(author.get('affiliation', 'N/A'))
            except:
                pass
    except:
        pass 
    return found_affs

def zenodo(match):
    found_affs=set()
    msg=''
    json_str = match.group(1)
    data = json.loads(json_str)
    try:
        for creator in data['metadata']['creators']:
            #print(f"Creator: {creator['person_or_org']['name']}")
            # Check if 'affiliations' key exists and has items
            if 'affiliations' in creator and creator['affiliations']:
                for affiliation in creator['affiliations']:
                    try:
                        found_affs.add(affiliation['name'])
                        #print(f"  Affiliation: {affiliation['name']}")
                    except:
                        pass
            else:
                msg+= "No affiliations listed."
    except:
        pass
    return found_affs
