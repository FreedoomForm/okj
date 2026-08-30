#!/usr/bin/env python3
"""CI: fetch HISTORICAL photos from Wikimedia Commons per site (search + geosearch).
Saves thumbs to work/images/{id}_cold_NN.jpg (old, <2000) and {id}_cnew_NN.jpg (>=2015).
Also writes output/commons_meta_shard_{i}.json with titles/years/descriptions.
"""
import argparse, json, os, re, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "work", "images")
OUT = os.path.join(ROOT, "output")
os.makedirs(IMG, exist_ok=True); os.makedirs(OUT, exist_ok=True)

sys.path.insert(0, os.path.join(ROOT, "scripts"))
from manifest import CANDIDATES

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "TashkentAlbumBot/1.0 (educational photo album; contact: ozodbek@ttsu.uz)"}

# Russian/English query variants per site id (for Commons full-text search)
QUERIES = {
    "kukeldash": ["Kukeldash Madrasah Tashkent", "Кукельдаш Ташкент"],
    "juma_masjid": ["Juma Mosque Tashkent", "мечеть Джами Ташкент"],
    "hazratimom": ["Khast Imam Tashkent", "Баракхан медресе Ташкент", "Hazrati Imam complex"],
    "qaffol": ["Kaffal Shashi mausoleum", "Каффаль Шаши Ташкент"],
    "shayxontohur": ["Sheikhantaur Tashkent", "Шейхантаур Ташкент"],
    "yunusxon": ["Yunus Khan mausoleum Tashkent", "мавзолей Юнусхана"],
    "abdulkosim": ["Abdul Kasim madrassah Tashkent", "медресе Абдулкасым Ташкент"],
    "hadra": ["Khadra Tashkent", "Хадра Ташкент"],
    "cherch": ["Sacred Heart Cathedral Tashkent", "костёл Ташкент"],
    "polovsev": ["Museum of Applied Arts Tashkent", "Музей прикладного искусства Ташкент", "Polovtsev house Tashkent"],
    "vokzal_eski": ["Tashkent railway station", "Ташкентский вокзал"],
    "sinagoga": ["Tashkent synagogue", "синагога Ташкент"],
    "passage": ["Alexander passage Tashkent", "пассаж Ташкент"],
    "uspenskiy": ["Uspensky Cathedral Tashkent", "Успенский собор Ташкент", "Assumption Cathedral Tashkent"],
    "kaldirgoch": ["Kaldyrgach biy mausoleum", "Калдыргач-бий мавзолей"],
    "milliy_teatr": ["Uzbek National Academic Drama Theatre Tashkent", "театр Хамзы Ташкент", "National Theatre Tashkent"],
    "muqimiy_teatr": ["Muqimi Theatre Tashkent", "театр Мукими Ташкент"],
    "kutubxona": ["Navoi Library Tashkent", "публичная библиотека Ташкент"],
    "konservatoriya": ["Tashkent Conservatory", "Ташкентская консерватория"],
    "sabir": ["Monument to Sabir Tashkent", "памятник Сабиру Ташкент"],
    "nizomiy": ["Nizami monument Tashkent", "памятник Низами Ташкент"],
    "pushkin": ["Pushkin monument Tashkent", "памятник Пушкину Ташкент"],
    "anhor": ["Anhor canal Tashkent", "Анхор Ташкент", "Bozsu canal Tashkent"],
    "dinamo": ["Dinamo Stadium Tashkent", "стадион Динамо Ташкент"],
    "toqimachilik": ["Tashkent Textile Combine", "Ташкентский текстильный комбинат"],
    "amirtemur_1970": ["Amir Timur Square Tashkent", "площадь Карла Маркса Ташкент", "Karl Marx monument Tashkent"],
    "tarix_muzeyi": ["State Museum of History of Uzbekistan", "музей Ленина Ташкент", "Central Lenin Museum Tashkent"],
    "teleminora": ["Tashkent Tower", "Ташкентская телебашня"],
    "metro_amirtimur": ["Amir Timur Xiyoboni metro", "метро Пушкина Ташкент", "Pushkinskaya metro Tashkent"],
    "paxtakor_stadion": ["Pakhtakor Stadium Tashkent", "стадион Пахтакор Ташкент"],
    "bobur_maydoni": ["Bobur Square Tashkent", "парк Горького Ташкент", "Gorky Park Tashkent"],
    "panfilov": ["Panfilov park Tashkent", "парк Панфилова Ташкент"],
    "dengiz": ["Tashkent Sea", "Ташкентское море"],
    "shevchenko": ["Shevchenko monument Tashkent", "памятник Шевченко Ташкент"],
    "planetariy": ["Tashkent Planetarium", "планетарий Ташкент"],
    "toshkent_kino": ["cinema Tashkent soviet", "кинотеатр Ташкент"],
    "yosh_teatr": ["Youth Theatre Tashkent", "ТЮЗ Ташкент", "Young spectator theatre Tashkent"],
    "toshkent_mehmonxona": ["Hotel Tashkent", "гостиница Ташкент"],
    "tsum": ["TsUM Tashkent", "ЦУМ Ташкент", "central department store Tashkent"],
    "humo": ["Humo Arena Tashkent", "дворец культуры Ташкент авиазавод"],
    "qoyliq": ["Qoyliq bazaar Tashkent", "Куйлюкский рынок Ташкент"],
    "yunusobod": ["Yunusabad Tashkent", "Юнусабад Ташкент"],
    "hukumat": ["Council of Ministers building Tashkent", "дом Советов Ташкент"],
    "ulugbek_yodgorlik": ["Ulugbek monument Tashkent", "памятник Улугбеку Ташкент"],
    "navoiy_yodgorlik": ["Navoiy monument Tashkent", "памятник Навои Ташкент"],
    "trolleybus": ["trolleybus Tashkent", "троллейбус Ташкент"],
    "rodina_kino": ["Rodina cinema Tashkent", "кинотеатр Родина Ташкент"],
    "filarmoniya": ["Philharmonia Tashkent", "филармония Ташкент"],
    "toshtech": ["Tashkent Polytechnic Institute", "Ташкентский политехнический институт", "Tashkent State Technical University"],
    "dtu": ["National University of Uzbekistan", "Ташкентский государственный университет"],
    "chorsu_gumbaz": ["Chorsu Bazaar Tashkent", "Чорсу Ташкент", "Chorsu dome"],
    "ippirodrom": ["Tashkent hippodrome", "ипподром Ташкент"],
    "tit": ["Tashkent Institute of Railway Engineers", "институт инженеров транспорта Ташкент"],
}

YEAR_RE = re.compile(r"(1[89]\d\d|20[0-2]\d)")

def api(params, tries=3):
    qs = urllib.parse.urlencode(params)
    for a in range(tries):
        try:
            req = urllib.request.Request(f"{API}?{qs}", headers=UA)
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except Exception as e:
            if a == tries - 1:
                print(f"  api fail {params.get('list')}: {e}")
                return {}
            time.sleep(5 * (a + 1))
    return {}

def search_titles(q, limit=40):
    d = api(dict(action="query", list="search", srsearch=q, srnamespace=6,
                 srlimit=limit, format="json"))
    return [r["title"] for r in d.get("query", {}).get("search", [])]

def geosearch_titles(lat, lng, radius=1200, limit=200):
    d = api(dict(action="query", list="geosearch", gscoord=f"{lat}|{lng}",
                 gsradius=radius, gslimit=limit, gsnamespace=6, format="json"))
    return [r["title"] for r in d.get("query", {}).get("geosearch", [])]

def imageinfo(titles):
    """batch imageinfo; returns {title: {url, thumburl, year, desc}}"""
    out = {}
    for i in range(0, len(titles), 25):
        chunk = titles[i:i + 25]
        d = api(dict(action="query", titles="|".join(chunk), prop="imageinfo",
                     iiprop="url|extmetadata|size", iiurlwidth=900, format="json"))
        for p in d.get("query", {}).get("pages", {}).values():
            ii = (p.get("imageinfo") or [{}])[0]
            if not ii.get("thumburl"):
                continue
            em = ii.get("extmetadata", {})
            dt = (em.get("DateTimeOriginal") or {}).get("value", "")
            m = YEAR_RE.search(re.sub(r"<[^>]+>", "", dt))
            year = int(m.group(1)) if m else None
            desc = re.sub(r"<[^>]+>", "", (em.get("ImageDescription") or {}).get("value", ""))[:160]
            out[p["title"]] = dict(url=ii.get("url"), thumb=ii.get("thumburl"),
                                   w=ii.get("width"), h=ii.get("height"),
                                   year=year, desc=desc)
    return out

def dl(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 5000:
        return "exists"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=40) as r:
            raw = r.read()
        if len(raw) < 5000:
            return "small"
        with open(path, "wb") as f:
            f.write(raw)
        return "ok"
    except Exception as e:
        return f"err {str(e)[:40]}"

ap = argparse.ArgumentParser()
ap.add_argument("--shard", type=int, default=0)
ap.add_argument("--shards", type=int, default=1)
ap.add_argument("--ids", default="")
ap.add_argument("--max-old", type=int, default=10)
ap.add_argument("--max-new", type=int, default=6)
args = ap.parse_args()

sites = [c for c in CANDIDATES if c["id"] in QUERIES]
if args.ids.strip():
    want = set(args.ids.split())
    sites = [c for c in sites if c["id"] in want]
else:
    sites = [c for n, c in enumerate(sites) if n % args.shards == args.shard]

meta_all = {}
for c in sites:
    cid = c["id"]
    titles = []
    for q in QUERIES[cid][:2]:
        titles += search_titles(q)
        time.sleep(0.5)
    if c.get("lat"):
        titles += geosearch_titles(c["lat"], c["lng"])
    titles = [t for t in dict.fromkeys(titles)
              if t.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff"))]
    if not titles:
        print(f"{cid}: no commons files")
        continue
    infos = imageinfo(titles)
    VINT = re.compile(r"стар|открытк|postcard|vintage|1900|19[0-8]\d|советск|soviet|историч|прошл", re.I)
    olds = [t for t, v in infos.items() if v["year"] and v["year"] < 2000]
    undated_vint = [t for t, v in infos.items()
                    if v["year"] is None and VINT.search(t) or v["year"] is None and VINT.search(v.get("desc", ""))]
    olds += undated_vint[:4]
    news = [t for t, v in infos.items() if v["year"] and v["year"] >= 2015]
    # prefer pre-1990 for old; keep undated with 'old-ish' hints out (strictness)
    olds.sort(key=lambda t: infos[t]["year"] or 1950)
    meta_all[cid] = {}
    jobs = []
    for i, t in enumerate(olds[:args.max_old]):
        path = os.path.join(IMG, f"{cid}_cold_{i:02d}.jpg")
        meta_all[cid][f"cold_{i:02d}"] = dict(title=t, **infos[t])
        jobs.append((infos[t]["thumb"], path))
    for i, t in enumerate(news[:args.max_new]):
        path = os.path.join(IMG, f"{cid}_cnew_{i:02d}.jpg")
        meta_all[cid][f"cnew_{i:02d}"] = dict(title=t, **infos[t])
        jobs.append((infos[t]["thumb"], path))
    with ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(lambda j: dl(*j), jobs))
    n_ok = sum(1 for r in res if r in ("ok", "exists"))
    print(f"{cid}: found={len(titles)} old={len(olds)} new={len(news)} downloaded={n_ok}")
    time.sleep(1)

with open(os.path.join(OUT, f"commons_meta_shard_{args.shard}.json"), "w") as f:
    json.dump(meta_all, f, ensure_ascii=False, indent=1)
print(f"shard {args.shard}: sites={len(sites)}")
