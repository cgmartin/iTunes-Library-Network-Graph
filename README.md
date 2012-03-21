# iTunes Music Library Network Graph


Experimentation with [D3.js](http://mbostock.github.com/d3/) force-directed 
graphs using iTunes library data.

**See a [running demo](http://cgmartin.com/itunes-library-network-graph).**

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

