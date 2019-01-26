[![Build Status](https://travis-ci.org/computerwonk/horus.svg?branch=master)](https://travis-ci.org/computerwonk/horus)

# Horus

## About

This project is a tool to monitor data on the web and notify the users of changes in the data. It needs to be configured before it is executed as it is flexible in how it deals with data.

## Installing

Download the repository to a directory anywhere you want to install horus. Go to it.

Either create a virtual environment first or just install python package dependencies by running `pip install -r requirements.txt`

To (optionally) run all the tests run `python -m unittest discover test`. Ignore the gibberish it spits out. If everything's okay, you should see:

>Ran x tests in y s
>
>OK

## Configuring

Open `config.json` in a text editor and configure it. Open `horus.py` and hook in your customized policy objects 

~Until the documentation is up, refer to `main/interfaces.py` and the test cases like `test/test_*.py`~

## Running

Run it with `python horus.py` while in the installation directory. If it tires you to manually run the system, maybe run it with `cron`.

## Licensing

This project is licensed under [GNU GPL version 3](https://www.gnu.org/licenses/gpl-3.0.en.html).
