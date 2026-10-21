"""Download the original hospital's public photographs used by the demo."""
import json
from pathlib import Path
from urllib.request import urlretrieve
from urllib.parse import urlparse

root = Path(__file__).resolve().parents[1]
assets = root/'assets'
assets.mkdir(exist_ok=True)
urls = {
    'Dr-V-Singla.jpg':'https://dundasvets.com/wp-content/uploads/2025/04/Dr-V-Singla.jpg',
    'g_pandher.jpg':'https://dundasvets.com/wp-content/uploads/2025/04/g_pandher.jpg',
    'Dr-H-Bansal.jpg':'https://dundasvets.com/wp-content/uploads/2025/04/Dr-H-Bansal.jpg',
    'Dr-S-Pandher.jpg':'https://dundasvets.com/wp-content/uploads/2025/04/Dr-S-Pandher.jpg',
    'clinic-care.jpg':'https://dundasvets.com/wp-content/uploads/elementor/thumbs/vet-doctors-working-with-little-dog-at-animal-clinic-close-up-r4c2eqixo1y2zi65pypp2kwofj93lj3mcf5qpy1j40.jpg',
    'clinic-icon.png':'https://dundasvets.com/wp-content/uploads/2025/04/cropped-logo-01-192x192.png'
}
posts = json.loads((root/'.audit/posts.json').read_text(encoding='utf-8-sig'))
ids = {p['featured_media'] for p in posts}
for item in json.loads((root/'.audit/media.json').read_text(encoding='utf-8-sig')):
    if item['id'] in ids:
        urls[Path(urlparse(item['source_url']).path).name] = item['source_url']
for name,url in urls.items():
    dest = assets/name
    if not dest.exists():
        urlretrieve(url,dest)
    print(name, dest.stat().st_size)
