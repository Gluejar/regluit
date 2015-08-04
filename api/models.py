from django.db import models



#https://github.com/GITenberg/Adventures-of-Huckleberry-Finn_76/raw/master/metadata.yaml

def repo_allowed(repo_url):
    if not repo_url.startswith('https://github.com/'):
        return (False, "repo url must start with 'https://github.com/'")
    try:
        (org,repo_name,raw,branch,filename) = repo_url[19:].split('/')
    except ValueError:
        return (False, "repo url must be well formed, metadata at top repo level")
    if not raw == 'raw':
        return (False, "repo url must point at 'raw' file")
    if not filename == 'metadata.yaml':
        return (False, "repo filename must be 'metadata.yaml'")
    if not branch == 'master':
        return (False, "repo branch must be 'master'")
    allowed_repos = AllowedRepo.objects.filter(org=org)
    for allowed_repo in allowed_repos:
        if allowed_repo.repo_name == '*':
            return (True, '*')
        if allowed_repo.repo_name == repo_name:
            return (True, '*')
    return  (False, "no allowed repos in that org")

class AllowedRepo(models.Model):
    org = models.CharField(max_length=39) 
    repo_name = models.CharField(max_length=100)
    