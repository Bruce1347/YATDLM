# YATDLM - Yet Another ToDo Lists Manager

As said by the name, this aims to be a light and flexible todo lists manager.

# Development

The Python dependencies are in the requirements file, you can install them with pip :
```bash
    $ pip3 install -r requirements.txt
```

I use a virtualenv for the development, thanks to virtualenvwrapper, this part is simpler.

If you are on a Debian based OS, you'll have to set some environment variables :
```bash
    $ export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
```

Then :
```bash
    $ mkvirtualenv -r requirements.txt --python=python3.6 yatdlm
```

This will create a new virtualenv named `yatdlm` with a python 3.6 interpreter and then install the requirements specified in the requirements file.

Except for the first time, you will need to activate the virtualenv each time you want to launch the developement webserver or make your migration. You will have to do the following :
```bash
    $ source /usr/local/bin/virtualenvwrapper.sh
    $ workon yatdlm
```

Once you're in the virtualenv you can use pip as you want in order to manage the packages that are *inside* the virtualenv. When you are finished, you can deactivate the virtualenv simply by using :
```bash
    $ deactivate
```