#!/usr/bin/env python

"""
iTunes Graph Parser

Parses an iTunes library XML file and generates a JSON file
for use in the InfoVis JavaScript library.

    Example Track info:
    {
        'Album': 'Nirvana',
        'Persistent ID': 'A50FE1436726815C',
        'Track Number': 4,
        'Location': 'file://localhost/Users/cmartin/Music/iTunes/iTunes%20Music/Nirvana/Nirvana/04%20Sliver.mp3',
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

import os
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


    def toJson(self, indent=None):
        self._maxArtistSongs = 0
        self._maxArtistPlays = 0
        self._maxGenreSongs = 0
        self._maxGenrePlays = 0

        self._processArtists()
        self._processGenres()

        jsonObj = {
                'nodes': [],
                'maxArtistSongs': self._maxArtistSongs,
                'maxArtistPlays': self._maxArtistPlays,
                'maxGenreSongs': self._maxGenreSongs,
                'maxGenrePlays': self._maxGenrePlays
                }

        # Append genres/artists to jsonObj nodes
        for k in self._genres:
            jsonObj['nodes'].append(self._genres[k])

        #for k in self._artists:
            #jsonObj['nodes'].append(self._artists[k])

        return json.dumps(jsonObj, indent=indent, cls=SetEncoder)

    def toJsonP(self, indent=None):
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
                    'Rating' not in track) or (track['Rating'] < 60):
                continue

            akey = track['Artist']
            if akey not in self._artists:
                self._artists[akey] = { 
                        'id': 'a' + str(len(self._artists)), 
                        'name': akey,
                        'adjacencies': set(), 
                        'data': { 'type': 'a', 'count': 0, 'plays': 0, 'rating': 0 },
                        'genres': set()
                        }

            rating = (track['Rating'] // 20)
            plays = track['Play Count'] if 'Play Count' in track else 0

            self._artists[akey]['data']['count'] += 1
            self._artists[akey]['data']['rating'] += rating
            self._artists[akey]['data']['plays'] += plays

            self._maxArtistSongs = max(self._maxArtistSongs, self._artists[akey]['data']['count'])
            self._maxArtistPlays = max(self._maxArtistPlays, self._artists[akey]['data']['plays'])

            # Split up the Genres
            genreParts = track['Genre'].split('/')
            self._artists[akey]['genres'] |= set(genreParts)


    def _processGenres(self):
        self._genres = {}

        for akey in self._artists.keys():
    
            # Filter out any one-hit wonders
            if self._artists[akey]['data']['count'] <= 2:
                del self._artists[akey]
                continue

            genreParts = self._artists[akey]['genres']
            for gkey in genreParts:

                if gkey not in self._genres:
                    self._genres[gkey] = { 
                            'id': 'g' + str(len(self._genres)),
                            'name': gkey,
                            'adjacencies': set(),
                            'data': { 'type': 'g', 'count': 0, 'plays': 0, 'rating': 0 }
                            }

                self._genres[gkey]['data']['count'] += 1
                self._genres[gkey]['data']['rating'] += self._artists[akey]['data']['rating']
                self._genres[gkey]['data']['plays'] += self._artists[akey]['data']['plays']

                self._maxGenreSongs = max(self._maxGenreSongs, self._genres[gkey]['data']['count'])
                self._maxGenrePlays = max(self._maxGenrePlays, self._genres[gkey]['data']['plays'])

                # Add adjacencies between genres and songs
                #self._genres[gkey]['adjacencies'].add(self._artists[akey]['id'])
                #self._artists[akey]['adjacencies'].add(self._genres[gkey]['id'])

            # Add adjacencies between genre parts 
            for gkey in genreParts:
                for gkey2 in genreParts:
                    gid = self._genres[gkey2]['id']
                    if gid != self._genres[gkey]['id']:
                        self._genres[gkey]['adjacencies'].add(gid)

            # remove genres from artist obj
            del self._artists[akey]['genres']



#### main block ####

defaultLibraryFile = os.path.expanduser('~/Music/iTunes/iTunes Music Library.xml')

parser = OptionParser(version="%prog 1.0")
parser.add_option('-f', '--file', dest='file', type='string',
        help='iTunes Library XML file path',
        default=defaultLibraryFile)
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
        print itunesParser.toJsonP(options.indent)
    else:
        print itunesParser.toJson(options.indent)

