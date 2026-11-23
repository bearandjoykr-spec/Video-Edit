"""Search Wikimedia Commons (public-domain art) politely. usage: find_art.py "query" [...]"""
import json, sys, time, urllib.parse, urllib.request
UA = {'User-Agent': 'video-edit-tool/1.0 (educational; contact via repository)'}
def get(url):
    for k in range(5):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
        except Exception as e:
            time.sleep(3 * (k + 1))
    return {}
for q in sys.argv[1:]:
    d = get('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(
        {'action': 'query', 'list': 'search', 'srnamespace': 6, 'srlimit': 6, 'format': 'json', 'srsearch': q + ' filetype:bitmap'}))
    print('==', q)
    for r in d.get('query', {}).get('search', []): print('   ', r['title'])
    time.sleep(2)
