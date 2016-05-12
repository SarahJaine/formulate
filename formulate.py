from hashlib import sha256
import click
import requests
from jinja2 import Template

resource_template = Template("""\tresource "{{ resource }}" do\n\
    \t\turl "{{ url }}"\n\
    \t\tsha256 "{{ sha256 }}"\n\
    \tend""")


def get_gz_url(r):
    '''return GNU zipped file url from pypi get response'''
    url_keys = r.json()['urls']
    for each in url_keys:
        if each['url'][-3:] == ".gz":
            url = each['url']
            return url


@click.command()
@click.option('--r', is_flag=True,
              help='Write resources for ./requirements.txt.')
def cli(r):
    '''Generate homebrew formula resources for your virutal environment's \
    pypi packages and their dependencies.'''
    if r:
        with open('requirements.txt', 'r') as requirements_file:
            requirements = requirements_file.read().strip().split('\n')

            for requirement in requirements:
                resources = {}
                if '==' in requirement:
                    requirement = requirement.split('==')
                    name = requirement[0]
                    version = requirement[1]

                    pypi_r = requests.get(
                            "https://pypi.python.org/pypi/{0}/{1}/json".format(
                                name, version))
                    if pypi_r.status_code != 200:
                        pypi_r = requests.get(
                            "https://pypi.python.org/pypi/{0}/json".format(
                                name))
                        if pypi_r.status_code == 200:
                            version_latest = pypi_r.json()['info']['version']
                            if click.confirm('{0} version {1} was not found. \
                            Would you like to use the latest stable release, \
                            version {2}, instead?'.format(
                                    name, version, version_latest)) is False:
                                continue
                    url = get_gz_url(pypi_r)
                    download_response = requests.get(url)
                    sha = sha256(download_response.content).hexdigest()
                    resources[name] = {
                        'name': name, 'url': url, 'sha256': sha}
                    for key, sub in resources.items():
                        print(resource_template.render(resource=key,
                              url=sub['url'], sha256=sub['sha256']))

                else:
                    pass
