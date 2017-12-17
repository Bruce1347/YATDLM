# YATDLM - Yet Another ToDo Lists Manager

As said by the name, this aims to be a light and flexible todo lists manager.

# Development

The Python dependencies are in the requirements file, you can install them with pip :
    $ pip3 install -r requirements.txt

I use a virtualenv for the development, thanks to virtualenvwrapper, this part is simpler.

If you are on a Debian based OS, you'll have to set some environment variables :
    $ export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3

Then :
    $ mkvirtualenv -r requirements.txt --python=python3.6 yatdlm

This will create a new virtualenv named `yatdlm` with a python 3.6 interpreter and then install the requirements specified in the requirements file.