#!/usr/bin/env python

"""
iTunes Graph Parser

Parses an iTunes library XML file and generates a JSON file
for use in the D3.js JavaScript library.

    Example Track info:
    {
        'Album': 'Nirvana',
        'Persistent ID': 'A50FE1436726815C',
        'Track Number': 4,
        'Location': 'file://localhost/Users/foo/Music/iTunes/iTunes%20Music/Nirvana/Nirvana/04%20Sliver.mp3',
        'File Folder Count': 4,
        'Album Rating Computed': True,
        'Total Time': 134295,
        'Sample Rate': 44100,
        'Genre': 'Rock/Alternative',
        'Bit Rate': 236,
        'Kind': 'MPEG audio file',
        'Name': 'Sliver',
        'Artist': 'Nirvana',
        'Date Added': datetime.datetime(2006, 10, 11, 4, 31, 38),
        'Album Rating': 60,
        'Rating': 40,
        'Date Modified': datetime.datetime(2009, 7, 18, 4, 57, 41),
        'Library Folder Count': 1,
        'Year': 2002,
        'Track ID': 7459,
        'Size': 3972838,
        'Track Type': 'File',
        'Play Count': 2,
        'Play Date UTC': datetime.datetime(2009, 7, 18, 5, 00, 00)
    }

"""

from __future__ import division
from optparse import OptionParser
from operator import itemgetter

import os
import io
import plistlib
import json


class SetEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)



class ITunesGraphParser:

    def __init__(self, libraryFile):
        self.libraryFile = libraryFile


    def toJson(self, rating=4, indent=None):
        self._rating = rating * 20
        self._maxArtistSongs = 0
        self._maxArtistPlays = 0
        self._maxGenreSongs = 0
        self._maxGenrePlays = 0

        self._processArtists()
        self._processGenres()
        self._processNodes()

        jsonObj = {
                'nodes': self._nodes,
                'links': self._links,
                'maxArtistSongs': self._maxArtistSongs,
                'maxArtistPlays': self._maxArtistPlays,
                'maxGenreSongs': self._maxGenreSongs,
                'maxGenrePlays': self._maxGenrePlays
                }
        
        return json.dumps(jsonObj, indent=indent, cls=SetEncoder)

    def toJsonP(self, rating=4, indent=None):
        self._rating = rating * 20
        json = self.toJson(indent)
        jsonp = 'itgCallback(' + json + ');'
        return jsonp


    def _readTracks(self):
        pl = plistlib.readPlist(self.libraryFile)
        return pl['Tracks']


    def _processArtists(self):
        tracks = self._readTracks()
        self._artists = {}

        for k in tracks:
            track = tracks[k]
        
            # Filter out any non-music with ratings lower than 3 stars
            if (track['Track Type'] != 'File') or ('Artist' not in track) or ('Genre' not in track) or (
                    'Rating' not in track) or (track['Rating'] < self._rating) or (track['Artist'] == 'Various Artists'):
                continue

            akey = track['Artist']
            if akey not in self._artists:
                self._artists[akey] = { 
                        'id': len(self._artists), 
                        'name': akey,
                        'type': 'a', 'count': 0, 'plays': 0, 'rating': 0,
                        'genres': set()
                        }

            rating = (track['Rating'] // 20)
            plays = track['Play Count'] if 'Play Count' in track else 0

            self._artists[akey]['count'] += 1
            self._artists[akey]['rating'] += rating
            self._artists[akey]['plays'] += plays

            self._maxArtistSongs = max(self._maxArtistSongs, self._artists[akey]['count'])
            self._maxArtistPlays = max(self._maxArtistPlays, self._artists[akey]['plays'])

            # Split up the Genres
            genreParts = track['Genre'].split('/')
            self._artists[akey]['genres'] |= set(genreParts)


    def _processGenres(self):
        self._genres = {}

        for akey in self._artists.keys():
    
            # Filter out any one-hit wonders
            if self._artists[akey]['count'] <= 2:
                del self._artists[akey]
                continue

            genreParts = self._artists[akey]['genres']
            for gkey in list(genreParts):
                if gkey == 'Mix':
                    genreParts.remove(gkey)
                    continue

                if gkey not in self._genres:
                    self._genres[gkey] = { 
                            'id': len(self._genres),
                            'name': gkey,
                            'type': 'g', 'count': 0, 'plays': 0, 'rating': 0,
                            'adjGenres': set()
                            }

                self._genres[gkey]['count'] += self._artists[akey]['count']
                self._genres[gkey]['rating'] += self._artists[akey]['rating']
                self._genres[gkey]['plays'] += self._artists[akey]['plays']

                self._maxGenreSongs = max(self._maxGenreSongs, self._genres[gkey]['count'])
                self._maxGenrePlays = max(self._maxGenrePlays, self._genres[gkey]['plays'])

            # Add adjacencies between genre parts 
            for gkey in genreParts:
                for gkey2 in genreParts:
                    if gkey != gkey2:
                        self._genres[gkey]['adjGenres'].add(gkey2)



    def _processNodes(self):
        self._links = []
        self._nodes = sorted(self._genres.itervalues(), key=itemgetter('id'))
        
        for idx, genre in enumerate(self._nodes):
            #for gid in genre['adjGenres']:
                #self._links.append({ 'source': gid, 'target': idx })

            del genre['adjGenres']

        idx = len(self._nodes);
        for akey in self._artists.keys():
            self._nodes.append(self._artists[akey])
            for g in self._artists[akey]['genres']:
                self._links.append({ 'source': idx, 'target': self._genres[g]['id'] }) 
            idx += 1


#### main block ####

defaultLibraryFile = os.path.expanduser('~/Music/iTunes/iTunes Music Library.xml')
defaultOutputFile = os.path.dirname(os.path.realpath(__file__)) + '/js/music-data.json'

parser = OptionParser(version="%prog 1.0")
parser.add_option('-f', '--file', dest='file', type='string',
        help='iTunes Library XML file path',
        default=defaultLibraryFile)
parser.add_option('-o', '--output', dest='output', type='string',
        help='Output File',
        default=defaultOutputFile)
parser.add_option('-r', '--rating', dest='rating', type='int',
        help='Minimum rating filter (default = 4)',
        default=4)
parser.add_option('-j', '--json', dest='json', action='store_true',
        help='Output in JSON format (default)')
parser.add_option('-p', '--jsonp', dest='jsonp', action='store_true',
        help='Output in JSON-P format')
parser.add_option('-i', '--indent', dest='indent', type='int',
        help='Indent level for output format (default=None)')
parser.add_option('-v', '--verbose', dest='verbose', action='store_true', 
        help='Verbose output')

if __name__ == '__main__':
    (options, args) = parser.parse_args()

    itunesParser = ITunesGraphParser(options.file)
    if options.jsonp:
        output = itunesParser.toJsonP(options.rating, options.indent)
        with io.open(options.output, 'wb') as outfile:
            json.dump(output, outfile)        
        print output        
    else:
        output = itunesParser.toJson(options.rating, options.indent)
        with io.open(options.output, 'wb') as outfile:
            json.dump(output, outfile)        
        print output
