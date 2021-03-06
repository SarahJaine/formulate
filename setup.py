from setuptools import setup

long_description = open('README.md').read()

setup(
        name='formulate',
        version='0.1',
        description='',
        long_description=long_description,
        url='',
        author='Sarah-Jaine Szekeresh',
        author_email='sarahjaine@isl.co',
        license='MIT',
        classifiers=[
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Programming Language :: Python :: 3.5',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        py_modules=['formulate'],
        install_requires=[
            'click>=6.6,<7',
            'requests>=2.9.1,<3',
            'jinja2>=2.7,<3',
            'semver>=2.4.1,<3'
         ],
        entry_points='''
            [console_scripts]
            formulate=formulate:cli
        '''
)
