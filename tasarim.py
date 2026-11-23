"""Profil README görsellerini üretir (assets/ altına SVG). Çalıştır: python3 tasarim.py

  hero.svg               — kapak: başlık + hareketli ASCII portre (profil fotoğrafından)
  bolum-<ad>-<tema>.svg  — bölüm başlıkları, açık/koyu tema
  proje-<ad>.svg         — öne çıkan proje kartları (her temada koyu; KESEN büyük)

Renkler: lacivert-siyah zemin, sıcak turuncu vurgu #F47735, yumuşak beyaz yazı.
"""
import colorsys
import math
from html import escape
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

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


def izgara(sutun, satir):
    """Her hücre: (parlaklık, renk, tür) — tür 'z' zemin, 'f' figür, 'k' güvercin."""
    renkli = Image.open(FOTO).convert("RGB").resize((sutun, satir), Image.LANCZOS)
    gri = ImageEnhance.Contrast(ImageOps.autocontrast(renkli.convert("L"), cutoff=2)).enhance(1.3)
    zemin, kus = Image.new("L", renkli.size), Image.new("L", renkli.size)
    for y in range(satir):
        for x in range(sutun):
            r, g, b = renkli.getpixel((x, y))
            if (b - r) > 9 and (r + g + b) / 3 < 120:
                zemin.putpixel((x, y), 255)
            if gri.getpixel((x, y)) > 150 and y < satir * 0.5:
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


def portre(x0, y0, sutun, satir, pf, lh, kare_sayisi=6, dongu=4.8):
    g = izgara(sutun, satir)
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
           f"@keyframes kare{{0%{{opacity:1}}{100 / kare_sayisi:.3f}%{{opacity:0}}}}"
           ".kus{animation:suz 5s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
           "@keyframes suz{0%,100%{transform:translate(0,0) rotate(0)}50%{transform:translate(2px,-4px) rotate(-1.2deg)}}")
    return "\n".join(p), css


# ================================================================ kapak

def hero():
    W, H = 960, 420
    # portre: 86×44 karakter, 7.6px → ~392×401
    sut, sat, pf = 86, 44, 7.6
    lh = pf * 1.2
    pw, ph = sut * pf * 0.6, sat * lh
    px, py = W - pw - 16, (H - ph) / 2
    govde, css = portre(px, py, sut, sat, pf, lh)

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'role="img" aria-label="Emre Yıldırım — Turning ideas into real products. Big Data Analytics student at SUBÜ.">']
    p.append(f"<style>{css}{AZ_HAREKET}</style>")
    p.append(f"""<defs>
<clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath>
<linearGradient id="solgecis" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".16" stop-color="#fff"/></linearGradient>
<linearGradient id="altgecis" x1="0" x2="0" y1="0" y2="1"><stop offset=".86" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="m1"><rect x="{px}" y="0" width="{pw}" height="{H}" fill="url(#solgecis)"/></mask>
<mask id="m2"><rect x="0" y="{py}" width="{W}" height="{ph}" fill="url(#altgecis)"/></mask>
<radialGradient id="isilti" cx=".78" cy=".45" r=".55"><stop offset="0" stop-color="{TURUNCU}" stop-opacity=".10"/><stop offset="1" stop-color="{TURUNCU}" stop-opacity="0"/></radialGradient>
</defs>""")
    p.append(f'<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{ZEMIN}"/>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#isilti)"/>')
    p.append(f'<g mask="url(#m1)"><g mask="url(#m2)">{govde}</g></g>')

    x = 60
    p.append(f'<text x="{x - 3}" y="178" font-family="{SERIF}" font-size="68" letter-spacing="-1.5" fill="{YAZI}">Emre Yıldırım</text>')
    p.append(f'<text x="{x}" y="236" font-family="{SANS}" font-size="29" letter-spacing="-.3" fill="{YAZI}">'
             f'Turning ideas into <tspan fill="{TURUNCU}">real products.</tspan></text>')
    p.append(f'<rect x="{x}" y="268" width="44" height="3" fill="{TURUNCU}"/>')
    p.append(f'<text x="{x}" y="310" font-family="{SANS}" font-size="19" fill="{SOLUK}">Big Data Analytics student at SUBÜ.</text>')
    p.append(f'<text x="{x}" y="338" font-family="{SANS}" font-size="19" fill="{SOLUK}">Data tools, mobile apps and games.</text>')
    p.append(f'</g><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{KENAR}"/>')
    p.append("</svg>")
    return "\n".join(p)


# ================================================================ bölüm başlıkları

def bolum(baslik):
    W, H = 900, 60
    out = {}
    for tema, (yazi, cizgi) in {"koyu": (YAZI, "#30363D"), "acik": ("#1F2328", "#D1D9E0")}.items():
        genis = len(baslik) * 15.5 + 22
        out[tema] = "\n".join([
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{e(baslik)}">',
            f'<text x="0" y="40" font-family="{SERIF}" font-size="31" letter-spacing="-.4" fill="{yazi}">{e(baslik)}</text>',
            f'<line x1="{genis}" y1="34" x2="{W}" y2="34" stroke="{cizgi}"/>',
            "</svg>"])
    return out


# ================================================================ proje kartları
# Sağdaki küçük çizimler: her projenin ne yaptığını gösteren ince çizgi motifleri (cx, cy merkez).

def m_kesen(cx, cy):
    kare = [[2, 7, 6], [9, 5, 1], [4, 3, 8]]
    s, a = 28, 4
    x0, y0 = cx - (3 * s + 2 * a) / 2, cy - (3 * s + 2 * a) / 2
    p = []
    for r in range(3):
        for c in range(3):
            x, y = x0 + c * (s + a), y0 + r * (s + a)
            orta = r == c == 1
            p.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="4" fill="{"#F4773522" if orta else "none"}" stroke="{TURUNCU if orta else CIZGI}"/>')
            p.append(f'<text x="{x + s/2}" y="{y + s/2 + 5}" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{TURUNCU if orta else YAZI}">{kare[r][c]}</text>')
    bx = x0 + 3 * s + 2 * a + 10
    for r in range(3):
        p.append(f'<text x="{bx}" y="{y0 + r * (s + a) + s/2 + 4}" font-family="{MONO}" font-size="10" fill="{SOLUK}">15</text>')
    return "".join(p)


def m_pass(cx, cy):
    x, y, w, h = cx - 52, cy - 50, 104, 96
    p = [f'<path d="M{x},{y + h} V{y} H{x + w} V{y + h}" fill="none" stroke="{CIZGI}"/>',
         f'<polyline points="{" ".join(f"{x + w - i * 8},{y + h + (4 if i % 2 else 0)}" for i in range(14))}" fill="none" stroke="{CIZGI}"/>']
    satirlar = [("Masa 4", ""), ("2× Adana", "640"), ("1× Ayran", "45"), ("1× Künefe", "180")]
    for i, (a, b) in enumerate(satirlar):
        yy = y + 18 + i * 15
        p.append(f'<text x="{x + 9}" y="{yy}" font-family="{MONO}" font-size="9.5" fill="{SOLUK if i else YAZI}">{e(a)}</text>')
        if b:
            p.append(f'<text x="{x + w - 9}" y="{yy}" text-anchor="end" font-family="{MONO}" font-size="9.5" fill="{SOLUK}">{b}</text>')
    p.append(f'<line x1="{x + 9}" y1="{y + 76}" x2="{x + w - 9}" y2="{y + 76}" stroke="{CIZGI}" stroke-dasharray="2 3"/>')
    p.append(f'<text x="{x + 9}" y="{y + 90}" font-family="{MONO}" font-size="10" fill="{TURUNCU}">TOPLAM</text>')
    p.append(f'<text x="{x + w - 9}" y="{y + 90}" text-anchor="end" font-family="{MONO}" font-size="10" fill="{TURUNCU}">865</text>')
    return "".join(p)


def m_veripilot(cx, cy):
    p = []
    # küçük tablo → ok → çubuk grafik
    tx, ty = cx - 74, cy - 30
    for r in range(4):
        for c in range(3):
            p.append(f'<rect x="{tx + c * 14}" y="{ty + r * 14}" width="12" height="12" fill="none" stroke="{CIZGI}"/>')
    p.append(f'<path d="M{cx - 22},{cy - 2} h18 m-5,-5 l5,5 l-5,5" fill="none" stroke="{SOLUK}"/>')
    bx, taban = cx + 6, cy + 28
    for i, h in enumerate([22, 34, 28, 48, 40]):
        renk = TURUNCU if i == 3 else CIZGI
        p.append(f'<rect x="{bx + i * 13}" y="{taban - h}" width="9" height="{h}" fill="{renk if i == 3 else "none"}" stroke="{renk}"/>')
    p.append(f'<line x1="{bx - 4}" y1="{taban}" x2="{bx + 66}" y2="{taban}" stroke="{SOLUK}"/>')
    return "".join(p)


def m_temizleyici(cx, cy):
    x = cx - 66
    satirlar = [("Ahmet Yılmaz", "ok"), ("ahmet yilmaz ", "kopya"), ("Ayşe Demir", "ok"), ("9.999.999", "aykiri")]
    p = []
    for i, (m, t) in enumerate(satirlar):
        y = cy - 30 + i * 20
        renk = YAZI if t == "ok" else SOLUK
        p.append(f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="11" fill="{renk}" xml:space="preserve">{e(m)}</text>')
        if t != "ok":
            p.append(f'<line x1="{x - 2}" y1="{y - 4}" x2="{x + len(m) * 6.6}" y2="{y - 4}" stroke="{TURUNCU}"/>')
            p.append(f'<text x="{x + 122}" y="{y}" font-family="{MONO}" font-size="9" fill="{TURUNCU}">{"DUP" if t == "kopya" else "OUT"}</text>')
        else:
            p.append(f'<path d="M{x + 122},{y - 4} l3,3 l6,-7" fill="none" stroke="{SOLUK}"/>')
    return "".join(p)


def m_odanda(cx, cy):
    # izometrik mobilya kutusu + AR köşe işaretleri + ölçü çizgisi
    s = 30
    a = (cx, cy - s)
    b = (cx + s * 1.5, cy - s * 0.25)
    c = (cx, cy + s * 0.5)
    d = (cx - s * 1.5, cy - s * 0.25)
    h = 34
    pts = lambda *q: " ".join(f"{x:.1f},{y:.1f}" for x, y in q)
    p = [f'<polygon points="{pts(a, b, c, d)}" fill="#F4773514" stroke="{TURUNCU}"/>',
         f'<polyline points="{pts(d, (d[0], d[1] + h), (c[0], c[1] + h), (b[0], b[1] + h), b)}" fill="none" stroke="{TURUNCU}"/>',
         f'<line x1="{c[0]}" y1="{c[1]}" x2="{c[0]}" y2="{c[1] + h}" stroke="{TURUNCU}"/>']
    L = 10
    for (x, y, sx, sy) in [(cx - 88, cy - 58, 1, 1), (cx + 88, cy - 58, -1, 1), (cx - 88, cy + 64, 1, -1), (cx + 88, cy + 64, -1, -1)]:
        p.append(f'<path d="M{x},{y + sy * L} V{y} H{x + sx * L}" fill="none" stroke="{SOLUK}"/>')
    p.append(f'<line x1="{c[0] + 6}" y1="{c[1] + h + 8}" x2="{b[0] + 6}" y2="{b[1] + h + 8}" stroke="{SOLUK}" stroke-dasharray="2 2"/>')
    p.append(f'<text x="{cx + 30}" y="{cy + 64}" font-family="{MONO}" font-size="9.5" fill="{SOLUK}">120 cm</text>')
    return "".join(p)


def m_biiip(cx, cy):
    p = []
    x0 = cx - 72
    for i in range(24):
        h = 6 + 26 * abs(math.sin(i * 0.9) * math.cos(i * 0.37))
        x = x0 + i * 6
        if 9 <= i <= 14:
            continue
        p.append(f'<line x1="{x}" y1="{cy - h/2}" x2="{x}" y2="{cy + h/2}" stroke="{CIZGI}" stroke-width="2.4" stroke-linecap="round"/>')
    p.append(f'<rect x="{x0 + 9 * 6 - 4}" y="{cy - 11}" width="{6 * 6 + 2}" height="22" rx="3" fill="{TURUNCU}"/>')
    p.append(f'<text x="{x0 + 9 * 6 + 15}" y="{cy + 4}" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="700" fill="{ZEMIN}">BİİİP</text>')
    p.append(f'<text x="{cx}" y="{cy + 40}" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{SOLUK}">“… ____ ____”</text>')
    return "".join(p)


PROJELER = [
    # dosya, ad, kategori, motif, büyük mü
    ("kesen", "KESEN", "Daily number puzzle · iOS & Android", m_kesen, True),
    ("pass", "Pass", "Restaurant operations", m_pass, False),
    ("veripilot", "VeriPilot", "Excel → dashboard", m_veripilot, False),
    ("veri-temizleyici", "Veri Temizleyici", "Data quality", m_temizleyici, False),
    ("odanda-gor", "Odanda Gör", "Augmented reality · furniture", m_odanda, False),
    ("biiip", "BİİİP", "Turkish rap lyric game", m_biiip, False),
]


def proje(ad, kategori, motif, buyuk):
    W, H = 900, 210 if buyuk else 132
    olcek = 1.45 if buyuk else 0.8
    ad_boy, ad_y = (64, 128) if buyuk else (44, 84)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{e(ad)} — {e(kategori)}">',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{KART}" stroke="{TURUNCU if buyuk else KENAR}" stroke-opacity="{.55 if buyuk else 1}"/>',
         f'<text x="38" y="{ad_y}" font-family="{SERIF}" font-size="{ad_boy}" letter-spacing="-1" fill="{YAZI}">{e(ad)}</text>',
         f'<text x="40" y="{ad_y + (44 if buyuk else 30)}" font-family="{SANS}" font-size="{19 if buyuk else 16}" fill="{SOLUK}">{e(kategori)}</text>']
    mx = W - (170 if buyuk else 120)
    p.append(f'<g transform="translate({mx} {H / 2}) scale({olcek}) translate({-mx} {-H / 2})">{motif(mx, H / 2)}</g>')
    p.append("</svg>")
    return "\n".join(p)


# ================================================================ alt çizgi

def ayrac():
    W, H = 900, 40
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="esphi">'
            f'<line x1="0" y1="20" x2="{W/2 - 40}" y2="20" stroke="{CIZGI}"/>'
            f'<rect x="{W/2 - 4}" y="16" width="8" height="8" fill="{TURUNCU}" transform="rotate(45 {W/2} 20)"/>'
            f'<line x1="{W/2 + 40}" y1="20" x2="{W}" y2="20" stroke="{CIZGI}"/></svg>')


BOLUMLER = [("about", "About"), ("work", "Featured Work"), ("experiments", "Other Experiments"),
            ("stack", "Tech Stack"), ("now", "Current Focus")]

if __name__ == "__main__":
    for eski in VARLIK.glob("*.svg"):
        eski.unlink()  # hepsi bu betikten üretiliyor
    (VARLIK / "hero.svg").write_text(hero(), encoding="utf-8")
    for dosya, baslik in BOLUMLER:
        for tema, icerik in bolum(baslik).items():
            (VARLIK / f"bolum-{dosya}-{tema}.svg").write_text(icerik, encoding="utf-8")
    for dosya, ad, kat, motif, buyuk in PROJELER:
        (VARLIK / f"proje-{dosya}.svg").write_text(proje(ad, kat, motif, buyuk), encoding="utf-8")
    (VARLIK / "ayrac.svg").write_text(ayrac(), encoding="utf-8")
    print("tamam:", sorted(f.name for f in VARLIK.glob("*.svg")))
