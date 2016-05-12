from hashlib import sha256
import click
import requests
from jinja2 import Template
import re


resource_template = Template('\tresource "{{ resource }}" do\n\
    \t\turl "{{ url }}"\n\
    \t\tsha256 "{{ sha256 }}"\n\
    \tend')


def get_gz_url(r):
    '''return GNU zipped file url from pypi get response'''
    url_keys = r.json()['urls']
    for each in url_keys:
        if each['url'][-3:] == '.gz':
            url = each['url']
            return url


def get_gz_url_from_version(r, version):
    '''return GNU zipped file url from pypi get response'''
    sub_list = r.json()['releases'][version]
    for each in sub_list:
        url = each.get('url')
        if url[-3:] == '.gz':
            return url


def find_version(string, operator):
    compare_position = string.index(str(operator))
    # Truncate sting if a comma follows
    try:
        comma_position = string[compare_position:].index(',')
        out = string[compare_position+(
            len(operator)): compare_position + comma_position-1]
    # Do not truncate sting if there is not a following comma
    except:
        out = string[compare_position+len(operator):]
    # Attempt to return as number
    try:
        return float(out)
    # Return as-is in case version contains non-numeric text
    except:
        return out


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
                            'https://pypi.python.org/pypi/{0}/{1}/json'.format(
                                name, version))
                    if pypi_r.status_code != 200:
                        pypi_r = requests.get(
                            'https://pypi.python.org/pypi/{0}/json'.format(
                                name))
                        if pypi_r.status_code != 200:
                            click.echo('{0} was not found on pypi.'.format(
                                name))
                            continue
                        else:
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

                # Some crazy long way to deal with requirements range
                # which I can hopefully remove
                else:
                    # pass
                    requirement_split = re.split('[<>=,]', requirement)
                    requirement_split = list(filter(None, requirement_split))
                    name = requirement_split[0]

                    greater_or_equal = 0
                    greater = 0
                    less_or_equal = 100
                    less = 100
                    if '>=' in requirement:
                        greater_or_equal = find_version(requirement, '>=')
                    elif '>' in requirement:
                        greater = find_version(requirement, '>')
                    if '<=' in requirement:
                        less_or_equal = find_version(requirement, '<=')
                    elif '<' in requirement:
                        less = find_version(requirement, '<')

                    pypi_r = requests.get(
                        "https://pypi.python.org/pypi/{0}/json".format(name))
                    if pypi_r.status_code == 200:
                        releases = pypi_r.json()['releases'].keys()
                        releases_clean = sorted(releases, reverse=True)
                        print("releases=", releases_clean)

                        matching_releases = []
                        for each in releases_clean:
                            # Using try bc may not be able to change each
                            # to float
                            try:
                                each = float(each)
                                if each >= greater_or_equal \
                                    and each > greater \
                                    and each <= less_or_equal \
                                        and each < less:
                                    matching_releases.append(each)
                            except:
                                continue
                        print("matching releases=", matching_releases)
                        version = str(max(matching_releases))
                        print("best match for ", requirement, "was", version)
                        url = get_gz_url_from_version(pypi_r, version)

                        download_response = requests.get(url)
                        sha = sha256(download_response.content).hexdigest()
                        resources[name] = {
                            'name': name, 'url': url, 'sha256': sha}

                for key, sub in resources.items():
                    print(resource_template.render(resource=key,
                          url=sub['url'], sha256=sub['sha256']))
