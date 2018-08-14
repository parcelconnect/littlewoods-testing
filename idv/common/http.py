import json
import urllib.parse
from collections import OrderedDict


def extract_json_from_GET(request, param):
    data = request.GET.get(param)
    unquoted_data = urllib.parse.unquote(data)
    return json.loads(unquoted_data, object_pairs_hook=OrderedDict)
