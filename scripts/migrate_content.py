"""Rebuild the static site from the public WordPress content snapshot.

No CMS code, scripts, forms, credentials or third-party tracking are imported.
"""
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://dundasvets.com'
DEMO = 'https://bird-e-consulting.github.io/dundas-east-animal-hospital'
PRODUCTION = '--production' in sys.argv
BASE = '' if PRODUCTION else '/dundas-east-animal-hospital'
CONTENT = ROOT / 'content'
CONTENT.mkdir(exist_ok=True)
SERVICES = ['wellness-and-preventive-care', 'laser-surgery', 'in-house-laboratory-diagnostics', 'in-house-medical-imaging', 'reference-laboratory-testing', 'dentistry-services', 'surgical-services']
LEGACY = {'faq', 'services', 'service-detail', '404-2'}
EXCLUDE_SEO = {'faq', 'service-detail', '404-2'}


class Cleaner(HTMLParser):
    """Keep content and safe semantic markup, discard WordPress presentation."""
    allowed = {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'strong', 'b', 'em', 'i', 'br', 'blockquote', 'a', 'span'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.text = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'script', 'style', 'svg', 'noscript'}:
            self.skip += 1
        if self.skip:
            return
        if tag in self.allowed:
            tag = 'h2' if tag == 'h1' else tag
            extra = ''
            if tag == 'a':
                href = html.unescape(attrs.get('href', '#'))
                if href.startswith('/dundas-east-animal-hospital/'):
                    href = href[len('/dundas-east-animal-hospital'):]
                parsed = urlparse(href)
                if parsed.netloc in {'dundasvets.com', 'www.dundasvets.com'} or href.startswith('/'):
                    href = BASE + (parsed.path if parsed.netloc else href)
                if href.startswith(('https://', 'http://', 'tel:', 'mailto:', '/', '#')):
                    extra = ' href="' + html.escape(href, quote=True) + '"'
            self.out.append('<' + tag + extra + '>')
        elif tag in {'div', 'section', 'article'}:
            self.out.append('\n')

    def handle_endtag(self, tag):
        if tag in {'script', 'style', 'svg', 'noscript'}:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag in self.allowed and tag != 'br':
            self.out.append('</' + ('h2' if tag == 'h1' else tag) + '>')
        elif tag in {'div', 'section', 'article'}:
            self.out.append('\n')

    def handle_data(self, value):
        if not self.skip:
            self.text.append(value)
            self.out.append(html.escape(value))


def plain(markup):
    parser = Cleaner()
    parser.feed(markup)
    return re.sub(r'\s+', ' ', ' '.join(parser.text)).strip()


def clean(markup):
    parser = Cleaner()
    parser.feed(markup)
    markup = re.sub(r'\n\s*\n', '\n', ''.join(parser.out)).strip()
    return '\n'.join(line.strip() for line in markup.splitlines())


def slug_title(record):
    corrections = {'why-annual-vet-checkups-can-save-youre-your-pets-life': 'Why annual vet checkups can save your pet’s life', '10-signs-your-pet-needs-to-see-a-vet-dont-ignore-them': '10 signs your pet needs to see a vet — don’t ignore them'}
    if record['slug'] in corrections:
        return corrections[record['slug']]
    title = html.unescape(record['title']['rendered'])
    if title.isupper():
        title = title.lower().capitalize()
    return title


def href(slug=''):
    return BASE + '/' + (slug + '/' if slug else '')


def icon(name):
    return f'<svg class="icon" aria-hidden="true" focusable="false"><use href="{BASE}/assets/icons.svg#{name}"></use></svg>'


def disclosure(label, content, class_name='content-dropdown'):
    return f'<details class="{class_name}"><summary>{html.escape(label)}</summary><div class="dropdown-content">{content}</div></details>'


def replace_icons(markup):
    for glyph, name in {'✳':'brand', '♡':'heart', '⌂':'clinic', '✓':'check', '↗':'external', '→':'arrow'}.items():
        markup = markup.replace(glyph, icon(name))
    return markup


def service_menu():
    return '<div class="service-accordions">' + ''.join(
        disclosure(slug_title(by_slug[slug]), '<p>'+html.escape(description(by_slug[slug]))+'</p><a class="text-link" href="'+href(slug)+'">Explore this service ↗</a>')
        for slug in SERVICES) + '</div>'


def folded_body(record):
    markup = original_body(record)
    labels = {
        'about-us': ['Serving Mississauga since 2010', 'Our services and technology', 'A personal approach', 'Our community relationships', 'A long-term partner in pet health'],
        'surgical-services': ['Surgical care, safety and procedures'],
        'dentistry-services': ['Dental health and warning signs', 'Annual dental assessments', 'Examinations and cleaning', 'How dental disease affects overall health', 'Home care and dental services'],
        'wellness-and-preventive-care': ['Why preventive care matters', 'Wellness visits and available services'],
        'laser-surgery': ['Care tailored to cats and dogs', 'Recognizing signs of illness', 'Laser surgery and its uses', 'Prevention and everyday health', 'Advances in veterinary care'],
        'in-house-medical-imaging': ['About medical imaging', 'X-rays, ultrasound and ECG', 'Our diagnostic approach'],
        'in-house-laboratory-diagnostics': ['About in-house testing', 'Results and timely care', 'Early detection', 'Available tests and reference laboratories', 'Questions and appointments'],
        'reference-laboratory-testing': ['About reference testing', 'When specialized testing is needed', 'Specialists and available tests', 'Questions about testing'],
        'how-weather-changes-affect-your-pets-health': ['Seasonal changes and warmer weather', 'Allergies, parasites and colder weather', 'Winter skin care and next steps'],
        'pet-allergies-symptoms-causes-and-treatments': ['Understanding allergies', 'Common symptoms', 'Causes of allergies', 'Environmental allergies', 'Food and flea allergies', 'Treatment options', 'Support from our team'],
        'understanding-common-skin-conditions-in-pets': ['Common skin concerns', 'Hot spots and other skin conditions', 'When to contact the clinic'],
        'spay-or-neuter-what-every-pet-owner-should-consider': ['Spaying, neutering and health', 'Population and behaviour considerations', 'Discussing the right time', 'Making an informed decision'],
        'the-ultimate-guide-to-puppy-and-kitten-care': ['Getting started with your new pet', 'Support as they grow'],
        'why-annual-vet-checkups-can-save-youre-your-pets-life': ['Why annual checkups matter', 'What happens during a wellness exam', 'Planning the next visit'],
        'vaccinations-for-pets-what-every-pet-parent-must-know': ['Vaccines and protection', 'Vaccination schedules and individual plans', 'Keeping vaccinations current', 'Prevention and next steps'],
        '10-signs-your-pet-needs-to-see-a-vet-dont-ignore-them': ['Ten signs to watch for', 'When to seek veterinary care']
    }[record['slug']]
    starts = [match.start() for match in re.finditer(r'<p\b[^>]*>.*?</p>', markup, re.S) if plain(match.group())]
    if len(starts) != len(labels):
        raise ValueError('Unexpected paragraph structure: '+record['slug'])
    starts[0] = 0
    starts.append(len(markup))
    return '<p class="article-intro">'+html.escape(description(record))+'</p><p class="expand-hint">Select a topic to read more.</p><div class="article-accordions">'+''.join(disclosure(label, markup[starts[i]:starts[i+1]]) for i,label in enumerate(labels))+'</div>'


def cards(records):
    return '<div class="content-grid">' + ''.join(
        f'<article class="content-card">{image_for(r)}<div><h3><a href="{href(r["slug"])}">{html.escape(slug_title(r))}</a></h3><details class="card-preview"><summary>Preview article</summary><p>{html.escape(description(r))}</p></details><a class="text-link" href="{href(r["slug"])}">Read more ↗</a></div></article>'
        for r in records) + '</div>'


def description(record):
    slug = record['slug']
    custom = {
        'home': 'Veterinary care for cats and dogs in Mississauga since 2010. Explore preventive care, dentistry, surgery, diagnostics, our doctors and both clinic locations.',
        'about-us': 'Learn about Dundas East Animal Hospital, serving Mississauga since 2010 with compassionate veterinary care, clear communication and personalized treatment.',
        'team': 'Meet Dr V Singla, Dr G Pandher, Dr H Bansal and Dr S Pandher at Dundas East Animal Hospital in Mississauga.',
        'contact-us': 'Find phone numbers, addresses, email and published opening hours for Dundas East Animal Hospital and Eglinton Animal Hospital in Mississauga.',
        'blog': 'Explore all eight original pet health articles from Dundas East Animal Hospital, covering wellness, vaccinations, skin, allergies and more.',
        'services': 'Explore seven veterinary services at Dundas East Animal Hospital, including wellness, surgery, dentistry, imaging and laboratory diagnostics.'
    }
    service_descriptions = {
        'wellness-and-preventive-care': 'Wellness exams, vaccinations, parasite prevention, nutrition advice and puppy and kitten programs at Dundas East Animal Hospital in Mississauga.',
        'laser-surgery': 'Learn about laser surgery for cats and dogs and discuss surgical care options with the veterinary team at Dundas East Animal Hospital in Mississauga.',
        'in-house-laboratory-diagnostics': 'Explore on-site bloodwork and urinalysis at Dundas East Animal Hospital in Mississauga, with reference laboratory support when advanced tests are needed.',
        'in-house-medical-imaging': 'Veterinary X-rays, ultrasound and ECG at Dundas East Animal Hospital in Mississauga. Learn how imaging supports your pet’s diagnosis and care.',
        'reference-laboratory-testing': 'Access specialized bloodwork, pathology, urinalysis, fecal testing and imaging interpretation through Dundas East Animal Hospital in Mississauga.',
        'dentistry-services': 'Dental exams, cleaning, tooth extractions and home care guidance for cats and dogs at Dundas East Animal Hospital in Mississauga.',
        'surgical-services': 'Spay, neuter, orthopedic, soft tissue, cryosurgery and cystotomy services at Dundas East Animal Hospital in Mississauga, with specialist referrals when needed.'
    }
    custom.update(service_descriptions)
    if slug in custom:
        return custom[slug]
    paragraphs = re.findall(r'<p\b[^>]*>(.*?)</p>', record['content']['rendered'], re.S)
    text = plain(paragraphs[0]) if paragraphs else plain(record['content']['rendered'])
    return text[:152].rsplit(' ', 1)[0].rstrip('.,;:') + '…' if len(text) > 155 else text


records = []
snapshot_file = CONTENT / 'site-content.json'
if (ROOT / '.audit/pages.json').exists() and '--snapshot' not in sys.argv:
    for kind in ['pages', 'posts']:
        for record in json.loads((ROOT / '.audit' / (kind + '.json')).read_text(encoding='utf-8-sig')):
            record['kind'] = kind
            if record['slug'] == 'home':
                names = re.findall(r'class="ti-name"[^>]*>(.*?)</div>', record['content']['rendered'], re.S)
                texts = re.findall(r'<!-- R-CONTENT -->(.*?)<!-- R-CONTENT -->', record['content']['rendered'], re.S)
                record['reviews'] = [{'name':plain(name),'text':plain(text)} for name,text in zip(names,texts)]
            records.append(record)
    media_items = json.loads((ROOT / '.audit/media.json').read_text(encoding='utf-8-sig'))
    snapshot_records = [{**r, 'content':{'rendered':clean(r['content']['rendered'])}} for r in records]
    snapshot_file.write_text(json.dumps({'records':snapshot_records,'media':media_items},ensure_ascii=False,indent=2),encoding='utf-8', newline='\n')
else:
    snapshot = json.loads(snapshot_file.read_text(encoding='utf-8'))
    records = snapshot['records']
    media_items = snapshot['media']
by_slug = {r['slug']: r for r in records}
posts = [r for r in records if r['kind'] == 'posts']
media = {r['id']: r for r in media_items}


def image_for(record):
    item = media.get(record.get('featured_media'))
    if not item:
        return ''
    source = item['source_url']
    local = 'assets/' + Path(urlparse(source).path).name
    return f'<img src="{BASE}/{local}" alt="{html.escape(item.get("alt_text") or slug_title(record), quote=True)}" loading="lazy" width="800" height="500">'


source = []
for record in records:
    source.append({
        'slug': record['slug'], 'title': slug_title(record), 'original_url': record['link'],
        'kind': record['kind'], 'date': record['date'], 'modified': record['modified'],
        'html': clean(record['content']['rendered']), 'text': plain(record['content']['rendered'])
    })
(CONTENT / 'original-content.json').write_text(json.dumps(source, ensure_ascii=False, indent=2), encoding='utf-8', newline='\n')

brand = '<span class="brand-icon" aria-hidden="true">✳</span><span>DUNDAS EAST<small>ANIMAL HOSPITAL</small></span>'
header = f'''<a class="skip-link" href="#main-content">Skip to content</a><div class="demo-bar">Website & payment portal concept by Bird E Consulting · Original clinic information retained <a href="{href()}#portal">Try the demo ↗</a></div>
<header class="header wrap"><a class="brand" href="{href()}" aria-label="Dundas East Animal Hospital home">{brand}</a><nav aria-label="Main navigation"><a href="{href('services')}">Services</a><a href="{href('about-us')}">About us</a><a href="{href('team')}">Our doctors</a><a href="{href('blog')}">Pet health</a><a href="{href('contact-us')}">Contact</a></nav><a class="button small" href="{href()}#portal">Client portal ↗</a></header>'''
service_links = ''.join(f'<li><a href="{href(s)}">{slug_title(by_slug[s])}</a></li>' for s in SERVICES)
footer = f'''<footer class="site-footer"><div class="wrap footer-grid"><div><a class="brand" href="{href()}">{brand}</a><p>Compassionate care for Mississauga pets since 2010.</p><a href="{href('about-us')}">About us</a> · <a href="{href('team')}">Our doctors</a><br><a href="{href('blog')}">Pet health articles</a> · <a href="{href('faq')}">FAQ</a></div><div><h2>Our services</h2><ul>{service_links}</ul></div><div><h2>Dundas East Animal Hospital</h2><address>966 Dundas St. East, Unit 1<br>Mississauga, ON L4Y 4H5</address><a href="tel:+19058038400">(905) 803-8400</a><br><a href="mailto:deahstaff@gmail.com">deahstaff@gmail.com</a></div><div><h2>Eglinton Animal Hospital</h2><address>3435 Eglinton Ave W, Unit 1<br>Mississauga, ON L5M 7Z5</address><a href="tel:+19056078400">(905) 607-8400</a><br><a href="mailto:eglintonstaff2007@gmail.com">eglintonstaff2007@gmail.com</a><p><a href="{href('contact-us')}">Hours & directions ↗</a></p></div></div><div class="wrap footer-bottom"><p>© 2026 Dundas East Animal Hospital · Demo by Bird E Consulting. No real payments or orders.</p><a href="https://dundasvets.com/">Current website ↗</a></div></footer>'''


def schema(record, title, canonical):
    graph = [{ '@type':'VeterinaryCare', '@id':ORIGIN+'/#hospital', 'name':'Dundas East Animal Hospital', 'url':ORIGIN+'/', 'telephone':'+1-905-803-8400', 'email':'deahstaff@gmail.com', 'address':{'@type':'PostalAddress','streetAddress':'966 Dundas St. East, Unit 1','addressLocality':'Mississauga','addressRegion':'ON','postalCode':'L4Y 4H5','addressCountry':'CA'}}]
    if record['slug'] in {'home', 'contact-us'}:
        graph.append({'@type':'VeterinaryCare','@id':ORIGIN+'/#eglinton','name':'Eglinton Animal Hospital','telephone':'+1-905-607-8400','email':'eglintonstaff2007@gmail.com','address':{'@type':'PostalAddress','streetAddress':'3435 Eglinton Ave W, Unit 1','addressLocality':'Mississauga','addressRegion':'ON','postalCode':'L5M 7Z5','addressCountry':'CA'}})
    if record['slug'] not in {'home', '404-2'}:
        graph.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':ORIGIN+'/'},{'@type':'ListItem','position':2,'name':title,'item':canonical}]})
    if record['kind'] == 'posts':
        graph.append({'@type':'BlogPosting','headline':title,'datePublished':record['date']+'Z','dateModified':record['modified']+'Z','mainEntityOfPage':canonical,'publisher':{'@id':ORIGIN+'/#hospital'}, **({'image':media[record['featured_media']]['source_url']} if record.get('featured_media') in media else {})})
    return json.dumps({'@context':'https://schema.org','@graph':graph}, ensure_ascii=False).replace('</', '<\\/')


def page(record, body, heading=None):
    slug = record['slug']
    title = heading or slug_title(record)
    canonical = ORIGIN + '/' + (slug + '/' if slug != 'home' else '')
    page_title = ('Veterinarian in Mississauga | Dundas East Animal Hospital' if slug == 'home' else title + ' | Dundas East Animal Hospital')
    desc = description(record)
    return replace_icons(f'''<!doctype html><html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="{'index,follow' if PRODUCTION and slug not in EXCLUDE_SEO else 'noindex,follow'}"><meta name="theme-color" content="#183d41"><title>{html.escape(page_title)}</title><meta name="description" content="{html.escape(desc, quote=True)}"><link rel="canonical" href="{canonical}"><meta property="og:type" content="{'article' if record['kind']=='posts' else 'website'}"><meta property="og:title" content="{html.escape(page_title, quote=True)}"><meta property="og:description" content="{html.escape(desc, quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:site_name" content="Dundas East Animal Hospital"><meta property="og:image" content="{ORIGIN}/wp-content/uploads/2025/04/Dr-V-Singla.jpg"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="{BASE}/assets/clinic-icon.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="{BASE}/style.css"><link rel="stylesheet" href="{BASE}/content-layout.css"><script type="application/ld+json">{schema(record,title,canonical)}</script></head><body>{header}<main id="main-content">{body}</main>{footer}</body></html>''')


def heading(record, label='YOUR NEIGHBOURHOOD VETERINARY TEAM'):
    title = html.escape(slug_title(record))
    return f'<section class="page-heading wrap"><nav aria-label="Breadcrumb"><a href="{href()}">Home</a><span aria-hidden="true">/</span><span>{title}</span></nav><p class="eyebrow">{label}</p><h1>{title}</h1></section>'


def original_body(record):
    markup = clean(record['content']['rendered'])
    # Original page hero/breadcrumb repeated the title; the shared page heading replaces it.
    if record['slug'] in SERVICES or record['slug'] in {'about-us', 'contact-us'}:
        marker = re.search(r'<p\b|Let&#x27;s|Let.s Ge', markup)
        if marker and record['slug'] != 'contact-us':
            markup = markup[marker.start():]
    if record['slug'] == 'about-us':
        marker = markup.find('Affordable Cost Veterinary')
        if marker >= 0:
            # Keep the source's unfinished promotional headings as review material.
            split = markup.rfind('<h', 0, marker)
            markup = markup[:split] + '<aside class="review-note">Original template section retained below for clinic review; these claims are unconfirmed.</aside><details class="source-archive"><summary>Original unfinished promotional section</summary>' + markup[split:] + '</details>'
    return markup


def contact_cards():
    return f'''<div class="location-grid"><article class="location"><p class="eyebrow">DUNDAS EAST ANIMAL HOSPITAL</p><h2>Visit us on Dundas East.</h2><address>966 Dundas St. East, Unit 1<br>Mississauga, ON L4Y 4H5</address><p><a href="tel:+19058038400">(905) 803-8400</a><br><a href="mailto:deahstaff@gmail.com">deahstaff@gmail.com</a></p><details class="hours-dropdown"><summary>Opening hours &amp; availability</summary><dl><div><dt>Mon – Fri</dt><dd>8 A.M – 8 P.M</dd></div><div><dt>Wednesday</dt><dd>11 A.M – 6 P.M</dd></div><div><dt>Saturday</dt><dd>9 A.M – 8 P.M</dd></div></dl><p class="field-note">The original site lists both a weekday range and separate Wednesday hours. Please call to confirm; Sunday hours are not published.</p></details><a class="button" href="https://www.google.com/maps/search/?api=1&query=966+Dundas+St+East+Mississauga">Get directions ↗</a></article><article class="location"><p class="eyebrow">EGLINTON ANIMAL HOSPITAL</p><h2>Our Eglinton location.</h2><address>3435 Eglinton Ave W, Unit 1<br>Mississauga, ON L5M 7Z5</address><p><a href="tel:+19056078400">(905) 607-8400</a><br><a href="mailto:eglintonstaff2007@gmail.com">eglintonstaff2007@gmail.com</a></p><details class="hours-dropdown"><summary>Opening hours &amp; availability</summary><dl><div><dt>Mon – Fri</dt><dd>8 A.M – 8 P.M</dd></div><div><dt>Saturday</dt><dd>9 A.M – 8 P.M</dd></div></dl><p class="field-note">Please call to confirm current availability. Sunday hours are not published.</p></details><a class="button" href="https://www.google.com/maps/search/?api=1&query=3435+Eglinton+Ave+W+Mississauga">Get directions ↗</a></article></div>'''


team_names = [('Dr V Singla','Dr-V-Singla.jpg'),('Dr G Pandher','g_pandher.jpg'),('Dr H Bansal','Dr-H-Bansal.jpg'),('Dr S Pandher','Dr-S-Pandher.jpg')]
audit_rows = []
for record in records:
    slug = record['slug']
    if slug == 'home':
        continue
    body = heading(record, 'PET HEALTH ARTICLES' if record['kind']=='posts' else 'DUNDAS EAST ANIMAL HOSPITAL')
    if slug == 'team':
        body += '<section class="wrap section"><p class="eyebrow">OUR DOCTORS</p><h2>Meet our veterinary team.</h2><div class="doctor-grid">' + ''.join(f'<article><img src="{BASE}/assets/{image}" alt="{name}" width="820" height="1024" loading="lazy"><h3>{name}</h3><p>DVM, BVSc &amp; AH</p></article>' for name,image in team_names) + '</div></section>'
    elif slug == 'blog':
        body += '<section class="wrap section">' + cards(posts) + '</section>'
    elif slug == 'contact-us':
        body += '<section class="wrap section"><p>Have questions or need to book an appointment? Reach out to either clinic below.</p>' + contact_cards() + '<details class="map-dropdown"><summary>View the Dundas East location map</summary><div class="map-panel"><iframe title="Dundas East Animal Hospital map" src="https://maps.google.com/maps?q=966%20dundas%20St.E.%2C%20Mississauga%2C%20ON%2C%20Canada%2C%20Ontario&amp;t=m&amp;z=16&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div></details><details class="source-archive"><summary>Original contact page wording & social labels</summary><div class="source-content">' + original_body(record) + '</div></details></section>'
    elif slug in LEGACY:
        if slug == 'services':
            body += '<section class="wrap section"><h2>Care for every stage of life.</h2>' + service_menu() + '</section>'
        elif slug == 'faq':
            body += f'<section class="wrap section"><h2>Questions? Let’s talk.</h2><p>The original FAQ contains template answers. For appointments, availability and accepted payment methods, please <a class="text-link" href="{href("contact-us")}">contact the clinic</a>.</p></section>'
        body += '<section class="wrap legacy-notice"><h2>Original template content, retained for review</h2><p>This published page on the previous site contains unfinished template text, example prices, contacts or claims. It is preserved below for a complete content review and does not describe verified clinic services, prices or availability.</p><details class="source-archive"><summary>View all original page content</summary><div class="source-content">' + original_body(record) + '</div></details></section>'
    else:
        if record['kind'] == 'posts':
            body += f'<div class="wrap article-meta">Originally published <time datetime="{record["date"]}">{record["date"][:10]}</time> · Original hospital article</div>'
        body += '<section class="wrap article-layout"><article class="source-content">' + image_for(record) + folded_body(record) + '</article><aside class="article-sidebar"><p class="eyebrow">HERE FOR YOUR PET</p><h2>A question about care?</h2><p>Talk with our team about your pet’s individual needs.</p><a class="button" href="tel:+19058038400">Call (905) 803-8400</a><details class="sidebar-services"><summary>Explore our services</summary><ul>' + service_links + '</ul></details></aside></section>'
        if record['kind'] == 'posts':
            body += '<section class="wrap section"><p class="eyebrow">KEEP READING</p><h2>More from the pet health journal.</h2>' + cards([p for p in posts if p['id']!=record['id']][:3]) + '</section>'
    body += f'<section class="wrap page-cta"><h2>Let’s take the next step together.</h2><a class="button" href="{href("contact-us")}">Contact our team ↗</a></section>'
    dest = ROOT / slug / 'index.html'
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(page(record,body), encoding='utf-8', newline='\n')
    audit_rows.append((slug, record['link'], href(slug), 'Retained for review: unfinished template' if slug in LEGACY else 'Migrated'))

# Keep the portal implementation independent of the static content migration.
template_path = ROOT / 'templates/home.html'
template_path.parent.mkdir(exist_ok=True)
if not template_path.exists():
    template_path.write_text((ROOT / 'index.html').read_text(encoding='utf-8'), encoding='utf-8', newline='\n')
template = template_path.read_text(encoding='utf-8')
hero = re.search(r'<section class="hero wrap">.*?</section>', template, re.S).group()
hero = hero.replace('For their whole life.<br><em>And your peace<br>of mind.</em>', 'Your Mississauga vet.<br><em>Care for their<br>whole life.</em>')
hero = hero.replace('YOUR NEIGHBOURHOOD VET IN MISSISSAUGA', 'DUNDAS EAST ANIMAL HOSPITAL · SINCE 2010')
hero = hero.replace('https://images.unsplash.com/photo-1552053831-71594a27632d?auto=format&fit=crop&w=1100&q=85', BASE+'/assets/clinic-care.jpg').replace('A golden retriever looking up with a happy expression', 'Veterinary team caring for a dog at an animal clinic')
hero = hero.replace('href="#visit"', 'href="'+href('contact-us')+'"')
portal = re.search(r'<section id="portal".*?</section>', template, re.S).group()
dialog = re.search(r'<dialog .*?</dialog>', template, re.S).group() + '<div id="toast" class="toast" role="status"></div>'
home_record = by_slug['home']
home_source = clean(home_record['content']['rendered'])
# Preserve the full original home copy and all eight Google review excerpts in a readable section.
# Repeated blog previews remain here as source content; complete articles have their own routes.
home_source = re.sub(r'<[^>]+>\s*(?:Lorem ipsum[^<]*|No content is added yet\.)\s*</[^>]+>', '', home_source, flags=re.I)
home_body = hero + '<section class="wrap section"><div class="section-heading"><div><p class="eyebrow">COMPLETE CARE, CLOSE TO HOME</p><h2>Our veterinary services.</h2></div><a class="text-link" href="'+href('services')+'">Explore all services ↗</a></div>' + service_menu() + '</section>'
features = [
    ('Experienced team', 'A skilled, dedicated staff with a true passion for animals. Our veterinarians and support staff bring years of trusted expertise.'),
    ('Modern & clean facility', 'A safe, hygienic, and welcoming environment for you and your pet.'),
    ('On-site pharmacy', 'Quick access to medications and wellness plans to keep your pet healthy long-term.'),
    ('Compassionate care', 'We treat your pets like family, with warmth, empathy, and dedication.'),
    ('Modern technology', 'Advanced diagnostic and treatment tools support your pet’s care.'),
    ('Convenient services', 'From consultations to flexible appointments, we make pet care easy.')
]
home_body += '<section class="hospital-story"><div class="wrap section"><p class="eyebrow">WHY CHOOSE DUNDAS EAST?</p><h2>Your pet’s health and happiness.<br>Our top priority.</h2><p class="story-intro">From routine checkups to advanced treatments, we’re here with compassionate, expert care every step of the way.</p><div class="feature-grid">' + ''.join(disclosure(title, '<p>'+text+'</p>') for title,text in features) + '</div><details class="care-details"><summary>Our approach, care options &amp; urgent enquiries</summary><div class="care-overview"><div><h3>Personalized, comprehensive care.</h3><p>Our team, modern diagnostics and clean facility support care tailored to your pet, from routine exams to advanced treatments.</p><ul><li>Wellness exams, vaccinations, surgeries and dental care.</li><li>Digital X-rays and ultrasound for precise results.</li><li>Convenient appointments and easy scheduling.</li></ul></div><div><h3>Don’t hesitate to contact us.</h3><p>Whether it’s a quick question or an urgent concern, our friendly team is here to assist you and your pet.</p><p>The original site says “Available anytime your pet needs urgent care.” Please call to confirm availability; this demo does not confirm 24-hour service.</p><a class="button" href="'+href('contact-us')+'">Contact our team ↗</a></div></div></details><details class="source-archive"><summary>Read the original homepage wording in full</summary><div class="source-content">' + home_source + '</div></details></div></section>'
reviews = home_record.get('reviews', [])
home_body += '<section class="wrap section"><p class="eyebrow">OUR COMMUNITY</p><div class="section-heading"><h2>Kind words from pet families.</h2><div><strong>EXCELLENT</strong><p class="field-note">Based on 235 reviews on the original website</p></div></div><p class="field-note">Google review excerpts retained from the original website snapshot; this is not a live rating feed. The original widget states that Trustindex verified Google as the review source.</p><details class="reviews-dropdown"><summary>Read all 8 client reviews</summary><div class="reviews-grid">' + ''.join('<figure><blockquote>'+html.escape(review['text'])+'</blockquote><figcaption>'+html.escape(review['name'])+' <span>· Google review</span></figcaption></figure>' for review in reviews) + '</div></details></section>'
home_body += '<section class="wrap section"><div class="section-heading"><div><p class="eyebrow">MEET YOUR TEAM</p><h2>People behind the care.</h2></div><a class="text-link" href="'+href('team')+'">Meet all four doctors ↗</a></div><div class="doctor-grid">' + ''.join(f'<article><img src="{BASE}/assets/{image}" alt="{name}" width="820" height="1024" loading="lazy"><h3>{name}</h3><p>DVM, BVSc &amp; AH</p></article>' for name,image in team_names) + '</div></section>'
home_body += portal + '<section class="wrap section"><div class="section-heading"><div><p class="eyebrow">THE PET HEALTH JOURNAL</p><h2>Helpful reading. Healthier pets.</h2></div><a class="text-link" href="'+href('blog')+'">All eight articles ↗</a></div>'+cards(posts[:3])+'</section><section class="wrap section"><p class="eyebrow">TWO MISSISSAUGA LOCATIONS</p><h2>Find your familiar place.</h2>'+contact_cards()+'</section>'
home_html = page(home_record, home_body)
home_html = home_html.replace('</head>', f'<script src="{BASE}/app.js" defer></script></head>').replace('</body>',dialog+'</body>')
(ROOT / 'index.html').write_text(home_html, encoding='utf-8', newline='\n')
(ROOT/'home').mkdir(exist_ok=True)
(ROOT/'home/index.html').write_text(home_html, encoding='utf-8', newline='\n')
(ROOT / '404.html').write_text(page(by_slug['404-2'], '<section class="wrap section"><h1>Page not found.</h1><p>Let’s get you back to the care you’re looking for.</p><a class="button" href="'+href()+'">Back home ↗</a></section>'),encoding='utf-8', newline='\n')

# Original path names are retained, so production migration does not rename service or article URLs.
indexable = [r for r in records if r['slug'] not in EXCLUDE_SEO]
urls = [ORIGIN+'/' + (r['slug']+'/' if r['slug']!='home' else '') for r in indexable]
(ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+u+'</loc></url>' for u in urls)+'</urlset>',encoding='utf-8', newline='\n')
(ROOT / 'robots.txt').write_text(('User-agent: *\nAllow: /\nSitemap: https://dundasvets.com/sitemap.xml\n' if PRODUCTION else '# Demo: page-level noindex prevents indexing while allowing crawlers to read it.\n# Production: remove noindex only after moving to the clinic domain.\nUser-agent: *\nAllow: /\n'),encoding='utf-8', newline='\n')
audit_rows.insert(0, ('home',ORIGIN+'/',href(),'Migrated; filler sentences omitted, original snapshot retained'))
report = '# Content migration audit\n\nSource: public WordPress pages and posts at dundasvets.com, captured October 21, 2026.\n\n16 published pages and 8 complete articles retained. Seven service detail pages, four doctors and their original photographs, hospital history, both locations, original opening-hour rows, all eight homepage review excerpts and all eight articles are present.\n\n| Source slug | Original URL | Demo path | Result |\n|---|---|---|---|\n' + ''.join(f'| {slug} | {url} | {dest} | {status} |\n' for slug,url,dest,status in audit_rows)
report += '\n## Explicit treatment of source issues\n\n- `content/original-content.json` preserves every page/post’s complete visible text and safe semantic HTML, including placeholders. Original scripts, styling, tracking and executable forms are intentionally not imported.\n- The original `faq`, `services`, `service-detail` and `404-2` routes contain unfinished template text. Every word remains accessible in a labelled original-content disclosure; the services route additionally provides the real service directory. Template phone numbers, $25 prices, free medicine and 24/7 claims are not presented as verified clinic facts.\n- The homepage no-content message and lorem ipsum sentence are omitted from its presentation, retained in the source snapshot.\n- About-page template headings (including pet shelter facility) remain in the original page content; their accompanying lorem ipsum is visibly labelled by the source-review notice added during QA.\n- Dundas weekday and separate Wednesday hours conflict. Both source rows are visible; no opening-hours schema is emitted pending clinic confirmation. No Sunday hours are invented.\n- Google reviews and their count are an original-site snapshot, clearly labelled; no aggregate-rating schema is emitted.\n- Original social icons point to #, so labels remain in the contact source disclosure without invented profiles.\n- All original service/article slugs are preserved. /home/ canonicalizes to /. The existing category and author archive URLs have local routes listing the same eight posts. The public sitemap was cross-checked: all 24 page/post URLs and both archive URLs are covered.\n- The static demo does not send appointment forms or process payments; phone/email contacts remain functional.\n'
(ROOT / 'CONTENT-AUDIT.md').write_text(report,encoding='utf-8', newline='\n')

# Original category archive remains navigable.
category = ROOT/'category/dundas'
category.mkdir(parents=True,exist_ok=True)
(category/'index.html').write_text(page(by_slug['blog'],heading(by_slug['blog'])+'<section class="wrap section">'+cards(posts)+'</section>'),encoding='utf-8', newline='\n')
author = ROOT/'author/rajkhanna1091gmail-com'
author.mkdir(parents=True,exist_ok=True)
(author/'index.html').write_text(page(by_slug['blog'],heading(by_slug['blog'])+'<section class="wrap section"><p class="eyebrow">DUNDAS · ORIGINAL AUTHOR ARCHIVE</p>'+cards(posts)+'</section>'),encoding='utf-8', newline='\n')
print(f'Generated {len(records)} original routes, category archive, 404, metadata, sitemap and source audit.')
