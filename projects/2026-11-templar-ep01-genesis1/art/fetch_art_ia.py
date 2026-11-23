"""Download the chosen public-domain artworks from the Internet Archive into remotion/public/templar/art/
(resized to 2400 px wide JPEG). Sources: Gustave Doré, La Sainte Bible (1866, BnF scan) and Michelangelo's
Sistine Chapel ceiling (1508–12). All public domain."""
import os, sys, time, urllib.parse, urllib.request, io
from PIL import Image
D = 'dore-bible-illustrations-1866'
ART = {
 'army': (D, '84_david_attacks_the_ammonites.jpg'),
 'combat': (D, '83_combat_between_soldiers_of_ish_bosheth_and_david.jpg'),
 'jacob_prays': (D, '23_jacob_prays_for_protection_p1b_ccc3fc0ec504.jpg'),
 'gethsemane': (D, '203_jesus_prays_in_the_garden.jpg'),
 'moses_sinai': (D, '40_moses_comes_down_from_mount_sinai.jpg'),
 'red_sea': (D, '37_the_egyptians_drown_in_the_sea.jpg'),
 'pharaoh': (D, '32_moses_and_aaron_appear_before_pharaoh.jpg'),
 'creation_light': (D, '1_the_creation_of_light.jpg'),
 'creation_eve': (D, '2_the_creation_of_eve.jpg'),
 'canaan': (D, '11_abraham_goes_to_the_land_of_canaan.jpg'),
 'leviathan': (D, '128_the_destruction_of_leviathan.jpg'),
 'jacob_dream': (D, '21_jacob_s_dream_p1b_08484c26712f.jpg'),
 'samuel_saul': (D, '73_samuel_blesses_saul.jpg'),
 'goliath': (D, '75_david_slays_goliath.jpg'),
 'elijah_rest': (D, '97_elijah_is_nourished_by_an_angel.jpg'),
 'jacob_flocks': (D, '22_jacob_tends_laban_s_flocks_and_meets_rachel.jpg'),
 'jacob_journey': (D, '29_jacob_goes_to_egypt.jpg'),
 'isaac_blesses': (D, '20_isaac_blesses_jacob.jpg'),
 'first_day': ('the-first-day-of-creation-sistine-chapel-by-michelangelo-1508-1512-endlos', 'The First Day of Creation (Sistine Chapel) — by Michelangelo, 1508-1512.png'),
 'waters': ('separation-of-the-earth-from-the-waters-sistine-chapel-detail-by-michelangelo-1508-151-endlos', 'Separation of the Earth from the Waters (Sistine Chapel) Detail — by Michelangelo, 1508-1512.png'),
 'sun_moon': ('the-creation-of-the-sun-and-the-moon-sistine-chapel-by-michelangelo-1508-1512-endlos', 'The Creation of the Sun and the Moon (Sistine Chapel) — by Michelangelo, 1508-1512.png'),
 'adam': ('the-creation-of-adam-sistine-chapel-by-michelangelo-1508-1512-endlos', 'The Creation of Adam (Sistine Chapel) — by Michelangelo, 1508-1512.png'),
}
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for key, (item, name) in ART.items():
    dst = os.path.join(out, key + '.jpg')
    if os.path.exists(dst): continue
    url = f'https://archive.org/download/{item}/' + urllib.parse.quote(name)
    for k in range(4):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'video-edit-tool/1.0'}), timeout=180).read(); break
        except Exception as e:
            print('retry', key, e); time.sleep(10 * (k + 1))
    im = Image.open(io.BytesIO(data)).convert('RGB')
    if im.width > 2400: im = im.resize((2400, round(im.height * 2400 / im.width)), Image.LANCZOS)
    im.save(dst, quality=90); print('ok', key, im.size, flush=True)
