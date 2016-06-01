import formulate
from click.testing import CliRunner
import unittest

runner = CliRunner()


class Tests(unittest.TestCase):
    def test_requirements_are_missing(self, **kwargs):
        with runner.isolated_filesystem():
            result = runner.invoke(formulate, ['--r'])
            assert result.exit_code != 0

    def test_template_render(self, **kwargs):
        resources = {}
        resources['foo'] = {'url': 'bar.com', 'sha256': 'bar'}
        for key, sub in resources.items():
            output = formulate.resource_template.render(
                resource=key, url=sub['url'], sha256=sub['sha256'])
        assert output == ('''\tresource "foo" do\n\
    \t\turl "bar.com"\n\
    \t\tsha256 "bar"\n\
    \tend''')


def main():
    unittest.main()

if __name__ == '__main__':
    main()
