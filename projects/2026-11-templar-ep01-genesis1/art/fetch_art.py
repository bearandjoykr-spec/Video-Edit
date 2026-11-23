"""Download the chosen public-domain artworks from Wikimedia Commons (2400 px wide) into remotion/public/templar/art/."""
import time, urllib.parse, urllib.request, os, sys
UA = {'User-Agent': 'video-edit-tool/1.0 (educational; contact via repository)'}
ART = {
 'crusaders_jerusalem': 'Enthusiasm of Crusaders at the First View of Jerusalem.jpg',
 'crusaders': 'Gustave Doré - Crusaders.jpg',
 'knight_prayer': 'Dreux Jean (Flemish, active 1445 - about 1446) - A Young Knight in Armor Kneeling in Prayer before Saint Anthony - Google Art Project.jpg',
 'moses_sinai': '039.Moses Comes Down from Mount Sinai.jpg',
 'red_sea': '037.The Egyptians Drown in the Sea.jpg',
 'papyrus_ani': 'Papyrus of Ani BM Sheet 12.jpg',
 'creation_light': '001.The Creation of Light.jpg',
 'creation_eve': '002.The Creation of Eve.jpg',
 'sep_light': 'Michelangelo, Separation of Light from Darkness 00.jpg',
 'sep_waters': 'Michelangelo, Separation of the Earth from the Waters 00.jpg',
 'sun_moon': 'Michelangelo, Creation of the Sun, Moon, and Plants 01.jpg',
 'leviathan': '122.The Destruction of Leviathan.jpg',
 'adam': 'Michelangelo - Creation of Adam (cropped).jpg',
 'ancient_days': 'The Ancient of Days (Blake, Research Issues).jpg',
 'godfrey': 'Gustave Doré - Godfrey Enters Jerusalem.jpg',
 'angelus': 'Jean-François Millet - The Angelus - Google Art Project.jpg',
 'war_machinery': 'Gustave Doré - The Crusaders War Machinery.jpg',
}
import json
out = sys.argv[1]
def get(url, binary=False):
    for k in range(8):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            return r if binary else json.loads(r)
        except Exception as e:
            print('  wait', k, str(e)[:60], flush=True); time.sleep(20 * (k + 1))
for key, name in ART.items():
    dst = os.path.join(out, key + '.jpg')
    if os.path.exists(dst): continue
    # standard thumbnail size (1920) via the API, then fetch that URL from upload.wikimedia.org
    info = get('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({'action': 'query', 'titles': 'File:' + name,
               'prop': 'imageinfo', 'iiprop': 'url', 'iiurlwidth': 1920, 'format': 'json'}))
    page = next(iter(info['query']['pages'].values()))
    url = page['imageinfo'][0].get('thumburl') or page['imageinfo'][0]['url']
    time.sleep(4)
    data = get(url, binary=True)
    open(dst, 'wb').write(data); print('ok', key, len(data) // 1024, 'KB', flush=True)
    time.sleep(8)
