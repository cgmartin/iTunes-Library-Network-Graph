# iTunes Music Library Network Graph

## Using [D3.js](http://mbostock.github.com/d3/)

Some experimentation with **D3.js** force graphs using my iTunes library data.

### iTunesGraphParser.py

A python command line script is included that parses an iTunes library file
and outputs JSON data.

    Usage: iTunesGraphParser.py [options]

    Options:
        --version             show program's version number and exit
        -h, --help            show this help message and exit
        -f FILE, --file=FILE  iTunes Library XML file path
        -r RATING, --rating=RATING
                              Minimum rating filter (default = 4)
        -j, --json            Output in JSON format (default)
        -p, --jsonp           Output in JSON-P format
        -i INDENT, --indent=INDENT
                              Indent level for output format (default=None)
        -v, --verbose         Verbose output

