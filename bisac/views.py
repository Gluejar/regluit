import json
from django.template import Context, Template
from django.http import HttpResponse

from mptt.templatetags.mptt_tags import cache_tree_children

from regluit.bisac.models import BisacHeading

nodes = BisacHeading.objects.all()

def recursive_node_to_dict(node):
    result = {
        'title': node.full_label,
        'key': node.pk,
    }
    children = [recursive_node_to_dict(c) for c in node.get_children()]
    if children:
        result['children'] = children
        result['folder'] = True
    return result

root_nodes = cache_tree_children(nodes)
dicts = []
for n in root_nodes:
    dicts.append(recursive_node_to_dict(n))


def tree(request):
    return HttpResponse(json.dumps(dicts, indent=4), content_type="application/json")