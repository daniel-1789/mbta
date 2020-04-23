# mbta
## User Documentation
### Usage
```
mbta --get-lines
mbta --get-stops <line_id>
mbta --help
```

### Installing/Using the Program
This can be called from either the command line or an IDE.

If called from the command line it can be called by using the python command followed by mbta.py.

Examples (depending on if your environment needs to explicitly specify Python 3):
```shell script
python mbta.py --get-stops Red
python3 mbta.py --get-stops Red
```
 
A very basic shell script, `mbta`, has been 
provided, which simply makes a Python3 call to 
trigger the script, passing to it all 
command-line arguments. Depending on your 
environment you might need to remove the 3 
from the internals of the script (i.e. if your 
interpreter treats a python call as being to 
Python3)


A virtual environment for the setup has been 
provided. It would also be fairly simple 
to use this without a virtual environment or to 
create your own, you would simply need to install 
the needed libraries. For example, the following 
should do it:
```shell script
pip install PyYAML
pip install requests

-- or --
pip3 install PyYAML
pip3 install requests
```
Presumably sys and enum will already be installed.

To activate the venv you could simply do from the
directory.
```shell script
source activate venv/bin/activate
```

## Homework Notes

I tried to keep this a simple program. One optimization I made is
the MBTA API gives a ton of information - far more than we 
needed. I made certain that we only got the needed
data from the MBTA API, greatly reducing the amount
of data this program needs to ingest. While I went for 
a simple command line interface, one thing I kept in
mind is if this were functioning as a microservice
or if it were running from a mobile device, you'd 
definitely want to mimimize the amount of data it
consumes.

One thing I wrestled with was the use of `mbta.yaml` to store
the URL's for the API. It's not essentially required but 
given I access those URLs in two separate files (the main
Python program and the Unit Test one) it seemed reasonable
to pull in the data from a common source. That said, the only 
real reason I needed to pass the URL to `print_all_lines`
and `print_stops` was I wanted the Unit Test to be able
to pass a bogus URL to the MBTA API in order to force
a non-200 response from the API. It
seemed important to be able to force bad responses
from the API. It's the sort of thing I'd definitely
be asking for input on from code reviewers as it
does introduce a vulnerability if the yaml file were
to be missing.

I made the decision to alphabetize the IDs for the
`--get-lines` command. However, the order of the
stops in the `--get-stops` command corresponded to the
ordering on the real MBTA maps so it seemed important
to preserve that.

I did give some thought to allowing `--get-stops` to
accept multiple lines as input but that was beyond
the scope of the requirements. It would be a 
fairly simple enhancement to make.

As I was a daily rider of the Commuter Rail when I 
was working at Toast, at least until everyone had to 
work from home, I was a frequent user of the 3rd-party
`MBTA Rail` mobile app and I really enjoyed getting
insight as to how that and similar apps gather their
data. I was fairly impressed by the amount of data
available from the MBTA.