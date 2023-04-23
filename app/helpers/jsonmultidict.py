# Load in our dependencies
# Handle Pillow image key value pair json
from werkzeug.datastructures import MultiDict
def get_json_multidict(body):
    """Extract MultiDict from `request.get_json` to produce similar MultiDict"""
    # Extract our JSON
    # Iterate over the values
    multi_dict_items = []
    for key in body:
        value = body[key]
        if isinstance(value, list): # if value is list of key value pair [{title: 'Nice', name: 'rabbit'}, {title: 'Good', name: 'carrot'}]
            listitem = [] 
            for subvalue in value:
                if isinstance(subvalue, dict):
                    child = []
                    for k, v in subvalue.items():
                        child.append((k, v))
                    listitem.append(MultiDict(child))
            multi_dict_items.append((key, listitem))
        elif isinstance(value, dict):  # if value is key value pair {title: 'Good', name: 'carrot'}
            child = []
            for k, v in value.items():
                child.append((k, v))
            multi_dict_items.append((key, MultiDict(child)))
        else:
            multi_dict_items.append((key, value)) # value is a primitive data type
    # Return our generated multidict
    return MultiDict(multi_dict_items)