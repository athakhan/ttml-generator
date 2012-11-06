#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, time
from optparse import OptionParser
from telemundo.subtitles import SubtitleParser

parser = OptionParser(usage='usage: %prog [options] subtitle')
parser.add_option('-v', action='count', dest='verbosity', default=0, help='increase output verbosity')
parser.add_option('-q', '--quiet', action='store_true', dest='quiet', help='hide all output')
parser.add_option('-l', '--lang', dest='lang', default='en-ES', type='string', help='subtitle language (default: en-ES)')
parser.add_option('-f', '--file', dest='file', default=None, type='string', help='file where to store the TTML output')
parser.add_option('-t', '--type', dest='type', default='xml', type='string', help='file extension')
(options, args) = parser.parse_args()

def main():
    if len(args) < 1:
        parser.error('you must specify a subtitle file to parse.')

    filename = args[0]
    if not os.path.exists(filename):
        parser.error('the subtitle file "%s" does not exist.' % filename)
    
    subparser = SubtitleParser()
    captions = subparser.parse(filename, options.lang)

    if len(captions) > 0:
        if options.verbosity >= 1 and not options.quiet:
            print '[%s] NOTICE: found %d subtitles' % (time.strftime('%Y-%m-%d %H:%M:%S'), len(captions))

        if options.file is not None:
            outputfile = options.file
        else:
            filepath = os.path.basename(filename)
            filedir = os.path.dirname(filename)
            (filebase, _) = os.path.splitext(filepath)
            outputfile = '%s_%s.%s' % (filebase, options.lang.upper(), options.type)

        captions.export('%s/%s' % (filedir, outputfile))
        if options.verbosity >= 1 and not options.quiet:
            print '[%s] NOTICE: %s was generated successfully' % (time.strftime('%Y-%m-%d %H:%M:%S'), outputfile)
    else:
        if options.verbosity >= 0 and not options.quiet:
            print '[%s] WARNING: no subtitles found' % (time.strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == '__main__':
    main()
