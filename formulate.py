from hashlib import sha256
import click
import requests


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

                    pypi = requests.get(
                            "https://pypi.python.org/pypi/{0}/{1}/json".format(
                                name, version))
                    if pypi.status_code == 200:
                        url = pypi.json()['urls'][0]['url']
                        download_response = requests.get(url)
                        sha = sha256(download_response.content).hexdigest()
                        resources[name] = {
                            'name': name, 'url': url, 'sha256': sha}

                    else:
                        pypi = requests.get(
                            "https://pypi.python.org/pypi/{0}/json".format(
                                name))
                        if pypi.status_code == 200:
                            version_latest = pypi.json()['info']['version']
                            click.confirm("{0} version {1} was not found. \
                                Would you like to use the latest \
                                stable release, version {2}, instead?".format(
                                    name, version, version_latest))
                            url_keys = pypi.json()['urls']
                            for each in url_keys:
                                if each['url'][-3:] == ".gz":
                                    url = each['url']
                            download_response = requests.get(url)
                            sha = sha256(download_response.content).hexdigest()
                            resources[name] = {
                                'name': name, 'url': url, 'sha256': sha}
                    click.echo(resources)

                else:
                    pass
