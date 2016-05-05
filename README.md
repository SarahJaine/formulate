# formulate
Formulate takes the pain out of writing homebrew formulae for projects in virtual environments. Formulate looks at the pypi packages installed in your active virtual environment and writes the formula resource url and sha256 lines for you.
Formulate works with virtual environments created with either [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) or [virtualenvwrapper](http://virtualenvwrapper.readthedocs.io/en/latest/index.html).
## Usage
Generate homebrew formula resources for your virutal environment's pypi packages and their dependencies:

`formulate virtual`

Write the formula resources to a new file:

`formulate virtual --write brand_new_file.rb`

Append the formula resources to the end of an existing file:

`formulate virtual --append some_old_file.rb`

