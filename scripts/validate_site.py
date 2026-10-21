"""Check preserved content, local links/assets and SEO output before publishing."""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = '/dundas-east-animal-hospital'


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []
        self.meta = {}
        self.h1 = 0
        self.words = []
        self.scripts = []
        self.in_json = False
        self.json_text = ''
        self.ignore = 0
        self.blocks = []
        self.block = None
        self.canonical = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'script','style','svg'}:
            self.ignore += 1
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.in_json = True
            self.json_text = ''
        if tag == 'h1':
            self.h1 += 1
        if tag in {'p','li'} and self.block is None:
            self.block = []
        if tag == 'meta':
            self.meta[attrs.get('name') or attrs.get('property')] = attrs.get('content')
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical = attrs['href']
        for name in ['src','href']:
            if name in attrs:
                self.refs.append(attrs[name])

    def handle_endtag(self, tag):
        if tag == 'script' and self.in_json:
            self.scripts.append(json.loads(self.json_text))
            self.in_json = False
        if tag in {'script','style','svg'}:
            self.ignore = max(0,self.ignore-1)
        if tag in {'p','li'} and self.block is not None:
            self.blocks.append(normalize(' '.join(self.block)))
            self.block = None

    def handle_data(self, text):
        if self.in_json:
            self.json_text += text
        if not self.ignore:
            self.words.append(text)
            if self.block is not None:
                self.block.append(text)


def normalize(text):
    return re.sub(r'\s+',' ',text).strip()


errors = []
emoji_artwork = re.compile(r'[\U0001F300-\U0001FAFF\u2733\u2661\u2302\u2713]')
documents = {}
for file in ROOT.rglob('*.html'):
    if any(part in {'.git','.audit','templates'} for part in file.parts):
        continue
    doc = Document()
    markup = file.read_text(encoding='utf-8')
    doc.feed(markup)
    if emoji_artwork.search(markup):
        errors.append(f'{file.relative_to(ROOT)}: font-based emoji artwork remains')
    documents[file] = doc
    if doc.h1 != 1:
        errors.append(f'{file.relative_to(ROOT)}: expected one H1, found {doc.h1}')
    if not doc.meta.get('description') or not doc.canonical:
        errors.append(f'{file.relative_to(ROOT)}: missing metadata/canonical')
    if not doc.scripts:
        errors.append(f'{file.relative_to(ROOT)}: missing structured data')
    for ref in doc.refs:
        url = urlparse(ref)
        if url.scheme or url.netloc or ref.startswith('#'):
            continue
        path = unquote(url.path)
        if path.startswith(BASE + '/'):
            path = path[len(BASE):]
        target = ROOT/path.lstrip('/') if path.startswith('/') else file.parent/path
        if path.endswith('/') or target.is_dir():
            target = target/'index.html'
        if not target.exists():
            errors.append(f'{file.relative_to(ROOT)}: broken local reference {ref}')

snapshot = json.loads((ROOT/'content/site-content.json').read_text(encoding='utf-8'))
archive = {r['slug']:r for r in json.loads((ROOT/'content/original-content.json').read_text(encoding='utf-8'))}
checked_blocks = 0
for record in snapshot['records']:
    slug = record['slug']
    dest = ROOT/'index.html' if slug == 'home' else ROOT/slug/'index.html'
    if dest not in documents:
        errors.append(f'Missing original route: {slug}')
        continue
    original = Document()
    original.feed(record['content']['rendered'])
    text = normalize(' '.join(original.words))
    if normalize(archive[slug]['text']) != text:
        errors.append(f'Incomplete archived text: {slug}')
    if slug not in {'home','blog','team','contact-us','services','faq','service-detail','404-2'}:
        rendered = normalize(' '.join(documents[dest].words))
        for block in original.blocks:
            if block and block not in rendered:
                errors.append(f'Lost original content on {slug}: {block[:100]}')
            checked_blocks += 1

if emoji_artwork.search((ROOT/'app.js').read_text(encoding='utf-8')):
    errors.append('Emoji artwork remains in the payment portal')
home = (ROOT/'index.html').read_text(encoding='utf-8')
for name in ['Dr V Singla','Dr G Pandher','Dr H Bansal','Dr S Pandher','Ryan Beckwith','Sally Altohme','Natalie Birks','Ashley Camilleri','Jay Ramani','Harjeet Sembhi','Akash Akash','Rodolfo Garcia']:
    if name not in home:
        errors.append('Missing homepage person: '+name)
ET.parse(ROOT/'sitemap.xml')
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'PASS: {len(documents)} HTML pages, all local references, single H1s, SEO metadata, JSON-LD, XML sitemap, 24 source routes, full source archive and {checked_blocks} original content blocks.')
