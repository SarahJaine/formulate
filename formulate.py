import click


@click.group()
def cli():
    pass


@cli.command()
@click.option('--to')
@click.option('--append')
def virtual(to, append):
    '''Generate homebrew formula resources for your virutal environment's \
    pypi packages and their dependencies'''
    print('hi')
