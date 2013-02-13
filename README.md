# iTunes Music Library Network Graph


Experimentation with [D3.js](http://mbostock.github.com/d3/) force-directed 
graphs using iTunes library data.

**See a [running demo](http://cgmartin.com/itunes-library-network-graph).**

## Installation

1. Clone project into a public web server path.
2. Run `./iTunesGraphParser.py` to scan your iTunes library and write a new ./js/music-data.json file.
3. Point browser to `index.html` on your web server.

### iTunesGraphParser.py

A python command line script is included that parses an iTunes library file
and outputs JSON data.

    Usage: iTunesGraphParser.py [options]

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -f FILE, --file=FILE  iTunes Library XML file path
      -o OUTPUT, --output=OUTPUT
                            Output to file (default=./js/music-data.json)
      -c, --console         Output to console instead of file
      -r RATING, --rating=RATING
                            Minimum rating filter (default = 4)
      -p, --jsonp           Output in JSON-P format
      -i INDENT, --indent=INDENT
                            Indent level for output format (default=None)
      -v, --verbose         Verbose output

