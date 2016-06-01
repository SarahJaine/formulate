import sys
import click
from hashlib import sha256
from jinja2 import Template
import re
import requests
import semver


resource_template = Template('''\tresource "{{ resource }}" do\n\
    \t\turl "{{ url }}"\n\
    \t\tsha256 "{{ sha256 }}"\n\
    \tend''')


def get_gz_url_from_version(r, version):
    '''from name and version in pypi response, return GNU zipped file url'''
    sub_list = r.json()['releases'][version]
    for each in sub_list:
        url = each.get('url')
        if url[-3:] == '.gz':
            return url


def get_gz_url_without_version(r):
    '''from name in pypi response, return GNU zipped file url'''
    url_keys = r.json()['urls']
    for each in url_keys:
        if each['url'][-3:] == '.gz':
            url = each['url']
            return url


def find_semantic_version(releases, versions):
    matching_releases = []
    for release in releases:
        if release.count('.') == 2:
            try:
                if semver.match(release, versions[0]) \
                        and semver.match(release, versions[1]):
                    matching_releases.append(release)
            except:
                pass
    if len(matching_releases) == 1:
        out = matching_releases[0]
    elif len(matching_releases) == 2:
        out = semver.max_ver(matching_releases[0], matching_releases[1])
    elif len(matching_releases) > 2:
        out = sorted(matching_releases)[-1]
    else:
        out = False
    return out


def find_numeric_version(releases, versions):
    matching_releases = []
    for release in releases:
        if release.count('.') > 1:
            continue
        else:
            operator_str_1 = release+versions[0]
            operator_str_2 = release+versions[1]
            if eval(operator_str_1) and eval(operator_str_2):
                matching_releases.append(release)
    if len(matching_releases) == 1:
        out = matching_releases[0]
    elif len(matching_releases) == 2:
        out = max(float(matching_releases[0]),
                  float(matching_releases[1]))
    elif len(matching_releases) > 2:
        out = sorted(matching_releases)[-1]
    else:
        out = False
    return out


@click.command()
@click.option('--r', is_flag=True,
              help='Write resources from ./requirements.txt.')
def cli(r):
    '''Generate homebrew formula resources for your virutal environment's \
    pypi packages and their dependencies.'''
    if r:
        try:
            with open('requirements.txt', 'r') as requirements_file:
                requirements = requirements_file.read().strip().split('\n')
        except FileNotFoundError:
            sys.exit(click.echo(
                'Could not find requirements.txt in the current directory.'))
        resources = {}
        for requirement in requirements:
            # Version requirement was given as an equality
            if '==' in requirement:
                requirement = requirement.split('==')
                name = requirement[0]
                version = requirement[1]

                pypi_r = requests.get(
                        'https://pypi.python.org/pypi/{0}/{1}/json'.format(
                            name, version))

                # If version not found, try to find by name only
                if pypi_r.status_code != 200:
                    pypi_r = requests.get(
                        'https://pypi.python.org/pypi/{0}/json'.format(
                            name))
                    if pypi_r.status_code != 200:
                        click.echo(
                            '{0} was not found on pypi.'.format(name))
                        continue
                    else:
                        version_latest = pypi_r.json()['info']['version']
                        if click.confirm(
                            '{0} version {1} was not found.\n'
                            'Would you like to use the latest stable release, '
                            'version {2}, instead?'.format(
                                name, version, version_latest)) is False:
                            continue

            # Version requirement was given as an inequation
            else:
                requirement_split = re.split('[<>=,]', requirement)
                requirement_split = list(filter(None, requirement_split))
                name = requirement_split[0]
                versions = requirement[len(name):].split(',')

                pypi_r = requests.get(
                    'https://pypi.python.org/pypi/{0}/json'.format(name))

                if pypi_r.status_code != 200:
                        click.echo('{0} was not found on pypi.'.format(
                            name))
                        continue

                # If package on pypi, find version that meets requirements
                else:
                    releases = list(pypi_r.json()['releases'].keys())
                    # Try semantic version parsing
                    try:
                        version = find_semantic_version(releases, versions)
                    # If error, try numeric version parsing
                    except:
                        version = find_numeric_version(releases, versions)

            # If a version was found, use that version
            if version:
                url = get_gz_url_from_version(pypi_r, version)
            # Else, just use name
            else:
                url = get_gz_url_without_version(pypi_r)

            if url:
                download_response = requests.get(url)
                sha = sha256(download_response.content).hexdigest()
                resources[name] = {
                    'name': name, 'url': url, 'sha256': sha}
            else:
                click.echo(
                    'An error occured while trying to formulate '
                    'url and sha256 for {0}.'.format(name))

        # Create and echo formula stanzas
        for key, sub in resources.items():
            click.echo(resource_template.render(resource=key,
                       url=sub['url'], sha256=sub['sha256']))
