'''
This module generates TTML subtitle files from different formats.

@author: Rodolfo Puig <Rodolfo.Puig@nbcuni.com>
@copyright: Telemundo Digital Media
@organization: NBCUniversal
'''
import os, re, time
from optparse import OptionParser
from xml.sax import saxutils
from HTMLParser import HTMLParser
from datetime import date

parser = OptionParser(usage='usage: %prog [options] subtitle')
parser.add_option('-v', action='count', dest='verbosity', default=0, help='increase output verbosity')
parser.add_option('-q', '--quiet', action='store_true', dest='quiet', help='hide all output')
parser.add_option('-l', '--lang', dest='lang', default='es', type='string', help='subtitle language (default: es)')
parser.add_option('-f', '--file', dest='file', default=None, type='string', help='file where to store the TTML output')
parser.add_option('-t', '--type', dest='type', default='ttml', type='string', help='file extension')
(options, args) = parser.parse_args()

class CaptionParser(HTMLParser):
    ''' Custom HTML Parser '''
    stack = None
    def __init__(self):
        self.stack = []
        self.reset()
    '''
    def handle_starttag(self, tag, attrs):
        if tag == 'i':
            style = ' tts:fontStyle="italic"'
        elif tag == 'b' or tag == 'strong':
            style = ' tts:fontStyle="bold"'
        else:
            style = ''
        self.stack.append('<span%s>' % style)
    def handle_endtag(self, tag):
        self.stack.append('</span>')
    '''
    def handle_data(self, data):
        self.stack.append(saxutils.escape(data))
    def render_output(self):
        return ''.join(self.stack)

def parse_srt_file(filename):
    ''' Parse SRT subtitle file '''
    lines = open(filename).read()
    return re.findall(r'(?P<data>.*?)\r?\n\r?\n', lines, re.MULTILINE + re.DOTALL)

def create_srt_caption(match):
    ''' Create SRT subtitle dictionary '''
    lines = match.splitlines()
    return {
        'pos': int(lines.pop(0)),
        'timecode': map(lambda x: x.replace(',', '.'), lines.pop(0).split(' --> ')),
        'text': '\n'.join(lines)
    }

def create_ttml_file(filename, subtitles):
    ''' Create TTML subtitle file '''
    fp = open(filename, 'wb')
    fp.write('<?xml version="1.0" encoding="utf-8"?>\n')
    fp.write('<tt xml:lang="%s" xmlns="http://www.w3.org/2006/10/ttaf1">\n' % options.lang)
    fp.write('  <head>\n')
    fp.write('    <metadata>\n')
    fp.write('      <ttm:title xmlns:ttm="http://www.w3.org/2006/10/ttaf1#metadata" />\n')
    fp.write('      <ttm:desc xmlns:ttm="http://www.w3.org/2006/10/ttaf1#metadata" />\n')
    fp.write('      <ttm:copyright xmlns:ttm="http://www.w3.org/2006/10/ttaf1#metadata">(c) Telemundo %s, all rights reserved.</ttm:copyright>\n' % date.today().year)
    fp.write('    </metadata>\n')
    fp.write('  </head>\n')
    fp.write('  <body>\n')
    fp.write('    <div>\n')
    for subtitle in subtitles:
        parser = CaptionParser()
        parser.feed(subtitle['text'])
        caption = parser.render_output()
        line = '      <p id="cation%d" begin="%s" end="%s">%s</p>\n' % (subtitle['pos'], subtitle['timecode'][0], subtitle['timecode'][1], caption)
        if options.verbosity >= 2 and not options.quiet:
            print '[%s] DEBUG: %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), saxutils.unescape(caption))
        fp.write(line)
    fp.write('    </div>\n')
    fp.write('  </body>\n')
    fp.write('</tt>\n')
    fp.close()

def main():
    ''' Main routine '''
    if len(args) < 1:
        parser.error('you must specify a subtitle file to parse.')
    filename = args[0]
    filepath = os.path.basename(filename)
    filedir = os.path.dirname(filename)
    (filebase, fileext) = os.path.splitext(filepath)
    if not os.path.exists(filename):
        parser.error('the subtitle file %s does not exist.' % filename)
    subtitles = []
    matches = parse_srt_file(filename)
    for match in matches:
        subtitle = create_srt_caption(match)
        if subtitle:
            subtitles.append(subtitle)
    if options.verbosity >= 1 and not options.quiet:
        print '[%s] NOTICE: found %d subtitles' % (time.strftime('%Y-%m-%d %H:%M:%S'), len(subtitles))
    if subtitles:
        if options.file is not None:
            ttmlfile = options.file
        else:
            ttmlfile = '%s_%s.%s' % (filebase, options.lang.upper(), options.type)
        create_ttml_file('%s/%s' % (filedir, ttmlfile), subtitles)
        if options.verbosity >= 1 and not options.quiet:
            print '[%s] NOTICE: %s was generated succesfully' % (time.strftime('%Y-%m-%d %H:%M:%S'), ttmlfile)
    else:
        if options.verbosity >= 0 and not options.quiet:
            print '[%s] WARNING: no subtitles found' % (time.strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == '__main__':
    main()
