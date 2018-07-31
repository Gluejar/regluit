from __future__ import print_function
from itertools import islice
from urlparse import urlparse
import sys

import requests

from django.db.models import Q
from django.core.management.base import BaseCommand

from regluit.core.models import Ebook
from regluit.core.bookloader import load_from_yaml


def repo_name_from_url(url):
    u = urlparse(url)
    return u.path.split("/")[2]

def yaml_url(repo_name):
     return "https://github.com/GITenberg/{}/raw/master/metadata.yaml".format(repo_name)


def calc_problem_ebooks():

    results = []
    non302statuscode_count = 0


    for (i, ebook) in enumerate(islice(Ebook.objects.filter(
                Q(url__startswith="https://github.com/GITenberg/") &
                Q(active = True)),
                None)):

        status_code = requests.head(ebook.url).status_code
        
        if status_code <> 302:
            non302statuscode_count += 1
            
        self.stdout.write("\r", i, ebook.url, status_code, non302statuscode_count, end="")
        sys.stdout.flush()

        results.append(
           {'id':ebook.id, 
            'url':ebook.url, 
            'status_code': requests.head(ebook.url).status_code
           }
            
        )

    return [result for result in results if result['status_code'] <> 302]


class Command(BaseCommand):
    help = "deactivate GITenberg ebooks that have invalid URLs and reload the yaml for the corresponding repos"
    
    def handle(self, **options):

        problem_ebooks = calc_problem_ebooks()
        self.stdout.write("number of problem ebooks", len(problem_ebooks))

        # deactivate problem ebooks
        for (i, result) in enumerate(problem_ebooks):
            ebook = Ebook.objects.get(id=result['id'])
            self.stdout.write("\r", "deactivating ", i, ebook.id, end="")
            ebook.deactivate()

        # reload repos
        for (i, repo_name) in enumerate(set([repo_name_from_url(ebook['url']) for ebook in problem_ebooks])):
            self.stdout.write("reloading ", repo_name)
            load_from_yaml(yaml_url(repo_name))
