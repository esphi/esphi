"""Profil README görsellerini üretir (assets/ altına SVG). Çalıştır: python3 tasarim.py

  hero.svg               — kapak: başlık + hareketli ASCII portre (profil fotoğrafından)
  bolum-<no>-<tema>.svg  — bölüm başlıkları, açık/koyu tema
  proje-<ad>.svg         — öne çıkan proje kartları (her temada koyu)

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
    W, H = 960, 440
    # portre: 84×42 karakter, 7.4px → ~373×373
    sut, sat, pf = 84, 42, 7.4
    lh = pf * 1.2
    pw, ph = sut * pf * 0.6, sat * lh
    px, py = W - pw - 28, (H - ph) / 2
    govde, css = portre(px, py, sut, sat, pf, lh)

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'role="img" aria-label="Emre Yıldırım — Turning ideas into real products.">']
    p.append(f"<style>{css}{AZ_HAREKET}</style>")
    p.append(f"""<defs>
<clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath>
<linearGradient id="solgecis" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".28" stop-color="#fff"/></linearGradient>
<linearGradient id="altgecis" x1="0" x2="0" y1="0" y2="1"><stop offset=".72" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="m1"><rect x="{px}" y="0" width="{pw}" height="{H}" fill="url(#solgecis)"/></mask>
<mask id="m2"><rect x="0" y="{py}" width="{W}" height="{ph}" fill="url(#altgecis)"/></mask>
<radialGradient id="isilti" cx=".78" cy=".45" r=".55"><stop offset="0" stop-color="{TURUNCU}" stop-opacity=".10"/><stop offset="1" stop-color="{TURUNCU}" stop-opacity="0"/></radialGradient>
</defs>""")
    p.append(f'<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{ZEMIN}"/>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#isilti)"/>')
    # ince teknik ızgara noktaları
    for gx in range(56, 520, 24):
        for gy in range(40, H - 30, 24):
            p.append(f'<circle cx="{gx}" cy="{gy}" r=".7" fill="{CIZGI}" opacity=".55"/>')
    p.append(f'<g mask="url(#m1)"><g mask="url(#m2)">{govde}</g></g>')

    x = 56
    p.append(f'<rect x="{x}" y="58" width="8" height="8" fill="{TURUNCU}"/>')
    p.append(f'<text x="{x + 18}" y="66" font-family="{MONO}" font-size="12.5" letter-spacing="2.2" fill="{SOLUK}">EMRE YILDIRIM  /  ESPHI</text>')
    p.append(f'<text font-family="{SERIF}" font-size="58" fill="{YAZI}" letter-spacing="-1">'
             f'<tspan x="{x - 3}" y="168">Turning ideas</tspan>'
             f'<tspan x="{x - 3}" y="234">into <tspan fill="{TURUNCU}" font-style="italic">real products</tspan>.</tspan></text>')
    p.append(f'<text font-family="{SANS}" font-size="17" fill="{SOLUK}">'
             f'<tspan x="{x}" y="290">Data analytics, software and AI-powered tools —</tspan>'
             f'<tspan x="{x}" y="315">taken from a first idea to a working product.</tspan></text>')
    p.append(f'<line x1="{x}" y1="356" x2="{x + 430}" y2="356" stroke="{CIZGI}"/>')
    alt = [("BIG DATA ANALYTICS", 0), ("SUBÜ", 182), ("TÜRKİYE", 250)]
    for metin, dx in alt:
        p.append(f'<text x="{x + dx}" y="384" font-family="{MONO}" font-size="11.5" letter-spacing="1.8" fill="{SOLUK}">{e(metin)}</text>')
    for dx in (168, 236):
        p.append(f'<line x1="{x + dx}" y1="373" x2="{x + dx}" y2="388" stroke="{CIZGI}"/>')
    p.append(f'</g><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{KENAR}"/>')
    p.append("</svg>")
    return "\n".join(p)


# ================================================================ bölüm başlıkları

def bolum(no, baslik, not_=""):
    W, H = 640, 64
    out = {}
    for tema, (yazi, soluk, cizgi, tur) in {
        "koyu": (YAZI, SOLUK, "#30363D", TURUNCU),
        "acik": ("#1F2328", "#59636E", "#D1D9E0", "#D9601F"),
    }.items():
        genis = 22 + len(baslik) * 15.5
        p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{e(baslik)}">',
             f'<text x="0" y="40" font-family="{MONO}" font-size="13" letter-spacing="1.5" fill="{tur}">{no}</text>',
             f'<text x="34" y="42" font-family="{SERIF}" font-size="30" letter-spacing="-.4" fill="{yazi}">{e(baslik)}</text>',
             f'<line x1="{34 + genis}" y1="36" x2="{W - (len(not_) * 8 + 16 if not_ else 0)}" y2="36" stroke="{cizgi}"/>']
        if not_:
            p.append(f'<text x="{W}" y="40" text-anchor="end" font-family="{MONO}" font-size="11.5" letter-spacing="1.5" fill="{soluk}">{e(not_)}</text>')
        p.append("</svg>")
        out[tema] = "\n".join(p)
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
    # dosya, no, ad, kategori, tek satır, durum, motif
    ("kesen", "01", "KESEN", "DAILY NUMBER PUZZLE · iOS / ANDROID",
     "Every row, column and diagonal has a target sum.", "iOS IN APP STORE REVIEW · ANDROID IN CLOSED TESTING", m_kesen),
    ("pass", "02", "Pass", "RESTAURANT OPERATIONS",
     "Waiter orders, kitchen display, cashier and QR menu.", "PRODUCT BUILT · NOT YET ON SALE", m_pass),
    ("veripilot", "03", "VeriPilot", "EXCEL → DASHBOARD",
     "Upload a spreadsheet, get an automated dashboard.", "WORKING PROJECT", m_veripilot),
    ("veri-temizleyici", "04", "Veri Temizleyici", "DATA QUALITY",
     "Duplicates, outliers and inconsistent spellings.", "LOCAL VERSION COMPLETE", m_temizleyici),
    ("odanda-gor", "05", "Odanda Gör", "AUGMENTED REALITY · FURNITURE",
     "See furniture in your own room at real-world size.", "EARLY DEVELOPMENT · DEMO READY", m_odanda),
    ("biiip", "06", "BİİİP", "TURKISH RAP LYRIC GAME",
     "Hear the track, complete the missing bar.", "EXPERIMENTAL · IN DEVELOPMENT", m_biiip),
]


def proje(no, ad, kategori, satir, durum, motif):
    W, H = 900, 176
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{e(ad)} — {e(satir)}">',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{KART}" stroke="{KENAR}"/>',
         f'<rect x="0" y="22" width="3" height="40" fill="{TURUNCU}"/>',
         f'<text x="36" y="47" font-family="{MONO}" font-size="12.5" letter-spacing="1.6" fill="{TURUNCU}">{no}</text>',
         f'<text x="68" y="47" font-family="{MONO}" font-size="11.5" letter-spacing="1.8" fill="{SOLUK}">{e(kategori)}</text>',
         f'<text x="34" y="100" font-family="{SERIF}" font-size="46" letter-spacing="-.8" fill="{YAZI}">{e(ad)}</text>',
         f'<text x="36" y="130" font-family="{SANS}" font-size="16" fill="{SOLUK}">{e(satir)}</text>']
    # durum
    p.append(f'<circle cx="40" cy="152" r="3.2" fill="{TURUNCU}"/>')
    p.append(f'<text x="51" y="156" font-family="{MONO}" font-size="10.5" letter-spacing="1.4" fill="{YAZI}" opacity=".82">{e(durum)}</text>')
    # motif alanı
    p.append(f'<line x1="{W - 230}" y1="26" x2="{W - 230}" y2="{H - 26}" stroke="{KENAR}"/>')
    p.append(motif(W - 115, H / 2))
    p.append("</svg>")
    return "\n".join(p)


# ================================================================ alt çizgi

def ayrac():
    W, H = 900, 40
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="esphi">'
            f'<line x1="0" y1="20" x2="{W/2 - 40}" y2="20" stroke="{CIZGI}"/>'
            f'<rect x="{W/2 - 4}" y="16" width="8" height="8" fill="{TURUNCU}" transform="rotate(45 {W/2} 20)"/>'
            f'<line x1="{W/2 + 40}" y1="20" x2="{W}" y2="20" stroke="{CIZGI}"/></svg>')


BOLUMLER = [
    ("01", "About", ""),
    ("02", "Featured Work", "6 PROJECTS"),
    ("03", "Other Experiments", ""),
    ("04", "Tech Stack", ""),
    ("05", "Current Focus", ""),
    ("06", "Contact", ""),
]

if __name__ == "__main__":
    (VARLIK / "hero.svg").write_text(hero(), encoding="utf-8")
    for no, baslik, not_ in BOLUMLER:
        for tema, icerik in bolum(no, baslik, not_).items():
            (VARLIK / f"bolum-{no}-{tema}.svg").write_text(icerik, encoding="utf-8")
    for dosya, no, ad, kat, satir, durum, motif in PROJELER:
        (VARLIK / f"proje-{dosya}.svg").write_text(proje(no, ad, kat, satir, durum, motif), encoding="utf-8")
    (VARLIK / "ayrac.svg").write_text(ayrac(), encoding="utf-8")
    print("tamam:", sorted(f.name for f in VARLIK.glob("*.svg")))
