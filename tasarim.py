"""Profil README görsellerini üretir (assets/ altına SVG). Çalıştır: python3 tasarim.py

  hero.svg      — kapak: tam genişlik hareketli ASCII tablo (profil fotoğrafından) + slogan
  pipeline.svg  — 11 projenin gerçek aşaması: Idea → Prototype → Working → Built → Review → Live
  imza.svg      — sayfa sonu: terminal imzası

Renkler: lacivert-siyah zemin, sıcak turuncu vurgu #F47735, yumuşak beyaz yazı.
"""
import colorsys
import math
from html import escape
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

KOK = Path(__file__).parent
VARLIK = KOK / "assets"
FOTO = VARLIK / "avatar-kaynak.jpg"

ZEMIN = "#0A0F1C"
KART = "#0E1524"
KENAR = "#1C2638"
YAZI = "#F2EEE8"
SOLUK = "#8C95A8"
CIZGI = "#2A3550"
TURUNCU = "#F47735"

SERIF = "'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, 'Times New Roman', serif"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

AZ_HAREKET = "@media (prefers-reduced-motion:reduce){*{animation:none!important}.kare0{opacity:1!important}}"


def e(s):
    return escape(s, quote=True)


# ================================================================ ASCII portre

RAMPA = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"


def _boya(rgb, v):
    h, _, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    l = 0.20 + 0.80 * v ** 0.8
    r, g, b = (min(255, round(c * 255 / 20) * 20) for c in colorsys.hls_to_rgb(h, l, min(1, s * 1.5)))
    return f"#{r:02x}{g:02x}{b:02x}"


def izgara(sutun, satir, kaynak=None):
    """Her hücre: (parlaklık, renk, tür) — tür 'z' zemin, 'f' figür, 'k' güvercin."""
    renkli = (kaynak or Image.open(FOTO).convert("RGB")).resize((sutun, satir), Image.LANCZOS)
    gri = ImageEnhance.Contrast(ImageOps.autocontrast(renkli.convert("L"), cutoff=2)).enhance(1.3)
    zemin, kus = Image.new("L", renkli.size), Image.new("L", renkli.size)
    for y in range(satir):
        for x in range(sutun):
            r, g, b = renkli.getpixel((x, y))
            if (b - r) > 9 and (r + g + b) / 3 < 120:
                zemin.putpixel((x, y), 255)
            if gri.getpixel((x, y)) > 150 and y < satir * 0.5 and x > sutun * 0.55:
                kus.putpixel((x, y), 255)
    zemin = zemin.filter(ImageFilter.MedianFilter(3))
    kus = kus.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.MaxFilter(3))
    return [[(gri.getpixel((x, y)) / 255, _boya(renkli.getpixel((x, y)), gri.getpixel((x, y)) / 255),
              "k" if kus.getpixel((x, y)) else ("z" if zemin.getpixel((x, y)) else "f"))
             for x in range(sutun)] for y in range(satir)]


def _harf(d):
    n = len(RAMPA) - 1
    return RAMPA[max(1, min(n, round(d * n)))]


def _katman(g, tur, kare=None, kare_sayisi=6):
    satirlar = []
    for y, satir in enumerate(g):
        parca = []
        for x, (v, renk, t) in enumerate(satir):
            if t != tur:
                ch, renk = " ", None
            else:
                d = 0.30 + 0.70 * v
                if kare is not None:
                    d += 0.20 * math.sin(x * 0.32 + y * 0.21 - kare * 2 * math.pi / kare_sayisi)
                ch = _harf(d)
            if parca and parca[-1][0] == renk:
                parca[-1] = (renk, parca[-1][1] + ch)
            else:
                parca.append((renk, ch))
        while parca and parca[-1][0] is None:
            parca.pop()
        satirlar.append(parca)
    return satirlar


def _yaz(satirlar, x0, y0, lh):
    out = []
    for i, parca in enumerate(satirlar):
        if parca:
            ic = "".join(f'<tspan fill="{r}">{e(m)}</tspan>' if r else e(m) for r, m in parca)
            out.append(f'<text x="{x0}" y="{y0 + (i + 1) * lh - 2:.1f}" xml:space="preserve">{ic}</text>')
    return out


def portre(x0, y0, sutun, satir, pf, lh, kare_sayisi=6, dongu=4.8, kaynak=None):
    g = izgara(sutun, satir, kaynak)
    p = [f'<g font-family="{MONO}" font-size="{pf}px">']
    for k in range(kare_sayisi):
        p.append(f'<g class="kare kare{k}" style="animation-delay:{-k * dongu / kare_sayisi:.2f}s">')
        p += _yaz(_katman(g, "z", k, kare_sayisi), x0, y0, lh)
        p.append("</g>")
    p += _yaz(_katman(g, "f"), x0, y0, lh)
    p.append('<g class="kus">')
    p += _yaz(_katman(g, "k"), x0, y0, lh)
    p.append("</g></g>")
    css = (f".kare{{opacity:0;animation:kare {dongu}s steps(1) infinite}}"
           f".kare0{{opacity:1}}@keyframes kare{{0%{{opacity:1}}{100 / kare_sayisi:.3f}%{{opacity:0}}100%{{opacity:0}}}}"
           ".kus{animation:suz 5s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
           "@keyframes suz{0%,100%{transform:translate(0,0) rotate(0)}50%{transform:translate(2px,-4px) rotate(-1.2deg)}}")
    return "\n".join(p), css


# ================================================================ kapak (tam ASCII)

def genis_tablo(W, H):
    """Kare portreyi geniş bir tabloya çevirir: sağda fotoğraf, solda tablonun kendi
    lacivert tonlarından üretilmiş yumuşak, boyalı bir arka plan."""
    import random
    foto = Image.open(FOTO).convert("RGB").resize((H, H), Image.LANCZOS)
    # fotoğrafın arka plan tonları (lacivert hücreler)
    kucuk = foto.resize((60, 60))
    tonlar = [kucuk.getpixel((i % 60, i // 60)) for i in range(3600)]
    tonlar = [c for c in tonlar if c[2] - c[0] > 9 and sum(c) / 3 < 120]
    ort = tuple(sum(c[i] for c in tonlar) // len(tonlar) for i in range(3))
    # düşük frekanslı gürültü: fırça darbesi gibi aydınlık-karanlık lekeler
    rnd = random.Random(7)
    gurultu = Image.new("L", (14, 6))
    gurultu.putdata([rnd.randint(0, 255) for _ in range(14 * 6)])
    gurultu = gurultu.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(H / 12))
    tuval = Image.new("RGB", (W, H))
    px = tuval.load()
    g = gurultu.load()
    for y in range(H):
        for x in range(W):
            k = 0.50 + 0.60 * g[x, y] / 255 - 0.20 * y / H
            px[x, y] = tuple(max(0, min(255, int(c * k))) for c in ort)
    maske = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(maske)
    for i in range(90):
        d.line([(W - H + i, 0), (W - H + i, H)], fill=int(255 * i / 90))
    d.rectangle([W - H + 90, 0, W, H], fill=255)
    tam = tuval.copy()
    tam.paste(foto, (W - H, 0))
    return Image.composite(tam, tuval, maske)


def hero():
    W, H = 960, 400
    pf = 7.6
    lh = pf * 1.2
    sut, sat = round(W / (pf * 0.6)), round(H / lh)
    tablo = genis_tablo(sut * 10, round(sat * 20))  # hücre oranı 1:2
    govde, css = portre(0, (H - sat * lh) / 2, sut, sat, pf, lh, kaynak=tablo)

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'role="img" aria-label="ASCII portrait. Turning ideas into real products. Big Data Analytics, SUBÜ.">']
    p.append(f"""<style>{css}
.imlec{{animation:yanip 1.1s steps(1) infinite}}
@keyframes yanip{{50%{{opacity:0}}}}
{AZ_HAREKET}
</style>""")
    p.append(f"""<defs>
<clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<linearGradient id="golge" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{ZEMIN}" stop-opacity="0"/><stop offset=".55" stop-color="{ZEMIN}" stop-opacity=".88"/></linearGradient>
<linearGradient id="yatay" x1="0" x2="1"><stop offset=".6" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="golgemaske"><rect x="0" y="{H - 150}" width="600" height="150" fill="url(#yatay)"/></mask>
</defs>""")
    p.append(f'<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{ZEMIN}"/>{govde}')
    p.append(f'<rect x="0" y="{H - 150}" width="600" height="150" fill="url(#golge)" mask="url(#golgemaske)"/>')
    x, y = 34, H - 54
    p.append(f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="19" fill="{YAZI}" xml:space="preserve">'
             f'<tspan fill="{TURUNCU}">&gt;</tspan> turning ideas into <tspan fill="{TURUNCU}">real products</tspan>'
             f'<tspan class="imlec" fill="{TURUNCU}"> █</tspan></text>')
    p.append(f'<text x="{x}" y="{y + 28}" font-family="{MONO}" font-size="13.5" fill="{SOLUK}" xml:space="preserve">'
             f'big data analytics @ SUBÜ  ·  data tools, apps, games</text>')
    p.append(f'</g><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{KENAR}"/>')
    p.append("</svg>")
    return "\n".join(p)


# ================================================================ pipeline

ASAMALAR = ["IDEA", "PROTOTYPE", "WORKING", "BUILT", "REVIEW", "LIVE"]
# ad, kısa tanım, aşama (0-5), öne çıkan mı
PIPELINE = [
    ("KESEN", "daily number puzzle", 4, True),
    ("Pass", "restaurant operations", 3, True),
    ("Veri Temizleyici", "data quality", 3, True),
    ("VeriPilot", "excel → dashboard", 2, True),
    ("Odanda Gör", "AR furniture", 1, True),
    ("BİİİP", "rap lyric game", 1, True),
    None,
    ("ZIP RUSH", "mobile puzzle", 1, False),
    ("Olta Diyarı", "pixel-art fishing", 1, False),
    ("Fossil Fusion", "roblox game", 1, False),
    ("Web Arena", "browser fps", 1, False),
    ("İHA Pilotu", "flight sim", 1, False),
]


def pipeline():
    W = 900
    sol, x0, x1 = 40, 290, 860
    adim = (x1 - x0) / (len(ASAMALAR) - 1)
    ust, rh = 112, 40
    H = round(ust + sum(rh if r else 34 for r in PIPELINE) + 22)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'role="img" aria-label="Project pipeline: where each project stands, from idea to live.">']
    p.append(f"""<style>
.iz{{stroke-dasharray:600;animation:ciz 1.1s cubic-bezier(.2,.7,.2,1) backwards}}
.nabiz{{transform-box:fill-box;transform-origin:center;animation:nabiz 2.2s ease-out infinite}}
@keyframes ciz{{from{{stroke-dashoffset:600}}to{{stroke-dashoffset:0}}}}
@keyframes nabiz{{0%{{transform:scale(1);opacity:.7}}100%{{transform:scale(2.6);opacity:0}}}}
{AZ_HAREKET}
</style>""")
    p.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="{ZEMIN}" stroke="{KENAR}"/>')
    p.append(f'<text x="{sol}" y="46" font-family="{MONO}" font-size="13" letter-spacing="1" fill="{TURUNCU}">$ pipeline --all</text>')
    p.append(f'<text x="{sol}" y="68" font-family="{SANS}" font-size="14" fill="{SOLUK}">Where every project actually stands. Nothing is live yet — KESEN is closest.</text>')
    for i, a in enumerate(ASAMALAR):
        x = x0 + i * adim
        canli = a == "LIVE"
        p.append(f'<text x="{x}" y="{ust - 10}" text-anchor="middle" font-family="{MONO}" font-size="11" letter-spacing="1.2" '
                 f'fill="{TURUNCU if canli else SOLUK}" opacity="{.75 if canli else 1}">{a}</text>')
        p.append(f'<line x1="{x}" y1="{ust}" x2="{x}" y2="{H - 18}" stroke="{TURUNCU if canli else CIZGI}" '
                 f'stroke-opacity="{.45 if canli else .55}" stroke-dasharray="{"3 5" if canli else "1 5"}"/>')
    y = ust
    sira = 0
    for r in PIPELINE:
        if r is None:
            p.append(f'<text x="{sol}" y="{y + 22}" font-family="{MONO}" font-size="10.5" letter-spacing="1.4" fill="{SOLUK}" opacity=".7">EXPERIMENTS</text>')
            p.append(f'<line x1="{sol + 98}" y1="{y + 18}" x2="{x0 - 30}" y2="{y + 18}" stroke="{CIZGI}"/>')
            y += 34
            continue
        ad, tanim, asama, one = r
        cy = y + rh / 2
        renk = TURUNCU if one else "#5A6684"
        p.append(f'<text x="{sol}" y="{cy + 1}" font-family="{SANS}" font-size="{16 if one else 14}" font-weight="{600 if one else 500}" fill="{YAZI if one else "#B6BDCC"}">{e(ad)}</text>')
        p.append(f'<text x="{sol}" y="{cy + 16}" font-family="{MONO}" font-size="10.5" fill="{SOLUK}">{e(tanim)}</text>')
        xs = x0 + asama * adim
        # gidilecek yol (soluk), gidilen yol (renkli, çizilerek gelir)
        p.append(f'<line x1="{xs}" y1="{cy}" x2="{x1}" y2="{cy}" stroke="{CIZGI}" stroke-dasharray="2 4"/>')
        if asama > 0:
            p.append(f'<line class="iz" style="animation-delay:{0.2 + sira * 0.08:.2f}s" x1="{x0}" y1="{cy}" x2="{xs}" y2="{cy}" stroke="{renk}" stroke-width="2"/>')
        for i in range(asama):
            p.append(f'<circle cx="{x0 + i * adim}" cy="{cy}" r="3" fill="{ZEMIN}" stroke="{renk}" stroke-width="1.5"/>')
        if one:
            p.append(f'<circle class="nabiz" style="animation-delay:{sira * 0.25:.2f}s" cx="{xs}" cy="{cy}" r="6" fill="none" stroke="{renk}"/>')
        p.append(f'<circle cx="{xs}" cy="{cy}" r="{6 if one else 4.5}" fill="{renk}"/>')
        y += rh
        sira += 1
    p.append("</svg>")
    return "\n".join(p)


# ================================================================ imza

def imza():
    """Sayfa sonu: kısa bir terminal oturumu (stack + sıradaki iş). Satırlar sırayla basılır;
    hareket oynamasa da hepsi görünür kalır."""
    W, H = 900, 128
    stack = "python  sql  javascript  typescript  dart  next.js  react  flutter  supabase  godot  unity  git"
    istem = f'<tspan fill="{TURUNCU}">esphi</tspan>@github:~$ '
    satirlar = [
        (istem + "ls stack/", SOLUK),
        (e(stack), YAZI),
        (istem + 'echo "next: ship KESEN"' + f'<tspan class="i" fill="{TURUNCU}"> █</tspan>', SOLUK),
    ]
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Stack: {stack}. Next: ship KESEN.">',
         f'<style>.s{{animation:bas .01s linear backwards}}@keyframes bas{{from{{opacity:0}}to{{opacity:0}}}}'
         f'.i{{animation:y 1.1s steps(1) infinite}}@keyframes y{{50%{{opacity:0}}}}{AZ_HAREKET}</style>',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="{ZEMIN}" stroke="{KENAR}"/>']
    for i, (metin, renk) in enumerate(satirlar):
        p.append(f'<text class="s" style="animation-delay:{0.4 + i * 0.5:.1f}s" x="28" y="{40 + i * 30}" '
                 f'font-family="{MONO}" font-size="14" fill="{renk}" xml:space="preserve">{metin}</text>')
    p.append("</svg>")
    return "\n".join(p)


if __name__ == "__main__":
    for eski in VARLIK.glob("*.svg"):
        eski.unlink()  # hepsi bu betikten üretiliyor
    (VARLIK / "hero.svg").write_text(hero(), encoding="utf-8")
    (VARLIK / "pipeline.svg").write_text(pipeline(), encoding="utf-8")
    (VARLIK / "imza.svg").write_text(imza(), encoding="utf-8")
    for f in sorted(VARLIK.glob("*.svg")):
        print(f.name, f.stat().st_size // 1024, "KB")
