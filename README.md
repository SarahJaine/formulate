# formulate
Formulate takes the pain out of writing homebrew formulae for projects in virtual environments. Formulate looks at the pypi packages installed in your active virtual environment and writes the formula resource url and sha256 lines for you.
Formulate works with virtual environments created with either [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) or [virtualenvwrapper](http://virtualenvwrapper.readthedocs.io/en/latest/index.html).
## Usage

Generate homebrew formula resources for requirements.txt file.
From same directory as requirements.txt:

`formulate --r`

From different directory:

`formulate --r some/pathway/`

Generate homebrew formula resources for all pypi packages within a system pathway:

`formulate --p some/system/path`

Generate homebrew formula resources for a virutal environment's pypi packages and their dependencies:

`formulate --v some-venv`
