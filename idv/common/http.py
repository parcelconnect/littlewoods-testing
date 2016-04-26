import json
import urllib.parse


def extract_json_from_GET(request, param):
    data = request.GET.get(param)
    unquoted_data = urllib.parse.unquote(data)
    return json.loads(unquoted_data)
