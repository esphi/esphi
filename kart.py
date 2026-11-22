"""Neofetch tarzı profil kartı: solda hareketli renkli ASCII portre, sağda bilgiler.
Açık + koyu SVG üretir. Çalıştır: python3 kart.py

Portre üç katmandan oluşur:
  zemin  — lacivert arka plan; KARE adet karede karakterleri dalga gibi akar
  figür  — adam; sabit
  kuş    — güvercin; yavaşça süzülür
"""
import colorsys
import math
from html import escape
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

KOK = Path(__file__).parent
FOTO = KOK / "assets" / "avatar-kaynak.jpg"

SUTUN, SATIR = 92, 46          # ASCII portre boyutu
PF, PLH = 8, 9.6               # portre yazı boyu ve satır yüksekliği (px)
FONT = 15                      # bilgi paneli yazı boyu (px)
CW, LH = FONT * 0.6, 21        # karakter genişliği (monospace ~0.6em), satır yüksekliği
KARE, DONGU = 6, 2.4           # zemin dalgası: kare sayısı, bir tur (sn)
RAMPA = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

TEMA = {
    "koyu": dict(zemin="#0d1117", kenar="#30363d", yazi="#c9d1d9", anahtar="#ffa657",
                 deger="#a5d6ff", nokta="#484f58", komut="#7ee787"),
    "acik": dict(zemin="#f6f8fa", kenar="#d1d9e0", yazi="#24292f", anahtar="#953800",
                 deger="#0a3069", nokta="#b7bfc7", komut="#1a7f37"),
}

GENIS = 46  # sağ panel satır genişliği (anahtar + noktalar + değer)

BILGI = [
    ("baslik", "emre@yildirim"),
    ("cizgi", None),
    ("kv", "Okul", "SUBÜ · Büyük Veri Analistliği"),
    ("kv", "Konum", "Türkiye"),
    ("kv", "Arıyor", "İME, veri analizi · Şub 2027"),
    ("bos", None),
    ("kv", "Dil.Programlama", "Python, SQL, JavaScript, Dart"),
    ("kv", "Dil.Veri", "pandas, DuckDB, PostgreSQL"),
    ("kv", "Araç", "Streamlit, FastAPI, Flutter"),
    ("kv", "Altyapı", "Supabase, Vercel, Git"),
    ("bos", None),
    ("kv", "Kural", "sayıyı yapay zekâ değil,"),
    ("devam", "kod hesaplar"),
    ("bos", None),
    ("bolum", "Proje"),
    ("kv", "KESEN", "günlük sayı bulmacası"),
    ("kv", "KESEN.Site", "kesen.online"),
    ("kv", "KESEN.Platform", "iOS · Android"),
    ("bos", None),
    ("bolum", "İletişim"),
    ("kv", "GitHub", "esphi"),
]


# ---------------------------------------------------------------- portre

def boya(rgb, v):
    """Pikselin rengini koyu zeminde okunur yapar, birleştirmek için kabalaştırır."""
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    s = min(1, s * 1.5)
    l = 0.20 + 0.80 * v ** 0.8
    r, g, b = (min(255, round(c * 255 / 20) * 20) for c in colorsys.hls_to_rgb(h, l, s))
    return f"#{r:02x}{g:02x}{b:02x}"


def izgara():
    """Her hücre için (parlaklık 0-1, renk, tür) döner. tür: 'z' zemin, 'f' figür, 'k' kuş."""
    renkli = Image.open(FOTO).convert("RGB").resize((SUTUN, SATIR), Image.LANCZOS)
    gri = ImageOps.autocontrast(renkli.convert("L"), cutoff=2)
    gri = ImageEnhance.Contrast(gri).enhance(1.3)

    zemin = Image.new("L", renkli.size)
    kus = Image.new("L", renkli.size)
    for y in range(SATIR):
        for x in range(SUTUN):
            r, g, b = renkli.getpixel((x, y))
            if (b - r) > 9 and (r + g + b) / 3 < 120:  # lacivert zemin
                zemin.putpixel((x, y), 255)
            if gri.getpixel((x, y)) > 150 and y < SATIR * 0.5:  # beyaz güvercin
                kus.putpixel((x, y), 255)
    zemin = zemin.filter(ImageFilter.MedianFilter(3))
    kus = kus.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.MaxFilter(3))

    g = []
    for y in range(SATIR):
        satir = []
        for x in range(SUTUN):
            v = gri.getpixel((x, y)) / 255
            tur = "k" if kus.getpixel((x, y)) else ("z" if zemin.getpixel((x, y)) else "f")
            satir.append((v, boya(renkli.getpixel((x, y)), v), tur))
        g.append(satir)
    return g


def harf(d):
    n = len(RAMPA) - 1
    return RAMPA[max(1, min(n, round(d * n)))]


def katman(g, tur, kare=None):
    """Bir katmanın satırlarını [(renk|None, metin), ...] olarak üretir."""
    satirlar = []
    for y, satir in enumerate(g):
        parcalar = []
        for x, (v, renk, t) in enumerate(satir):
            if t != tur:
                ch, renk = " ", None
            else:
                d = 0.30 + 0.70 * v
                if kare is not None:  # zemin dalgası
                    faz = x * 0.32 + y * 0.21 - kare * 2 * math.pi / KARE
                    d += 0.22 * math.sin(faz) + 0.08 * math.sin(x * 0.11 - y * 0.37 + kare * math.pi / 3)
                ch = harf(d)
            if parcalar and parcalar[-1][0] == renk:
                parcalar[-1] = (renk, parcalar[-1][1] + ch)
            else:
                parcalar.append((renk, ch))
        while parcalar and parcalar[-1][0] is None:
            parcalar.pop()
        satirlar.append(parcalar)
    return satirlar


def satirlari_yaz(satirlar, x0, y_ust, gecikme, adim):
    out = []
    for i, parcalar in enumerate(satirlar):
        if not parcalar:
            continue
        ic = "".join(f'<tspan fill="{r}">{escape(m)}</tspan>' if r else escape(m) for r, m in parcalar)
        out.append(f'<text class="s" style="animation-delay:{gecikme + i*adim:.2f}s" x="{x0}" '
                   f'y="{y_ust + (i + 1) * PLH - 2:.1f}" xml:space="preserve">{ic}</text>')
    return out


# ---------------------------------------------------------------- bilgi paneli

def kv_satir(t, anahtar, deger):
    noktalar = max(GENIS - len(anahtar) - len(deger) - 3, 2)
    return (f'<tspan fill="{t["anahtar"]}">{escape(anahtar)}</tspan>'
            f'<tspan fill="{t["yazi"]}">:</tspan>'
            f'<tspan fill="{t["nokta"]}"> {"." * noktalar} </tspan>'
            f'<tspan fill="{t["deger"]}">{escape(deger)}</tspan>')


def bilgi_satiri(t, satir):
    tur = satir[0]
    if tur == "baslik":
        return (f'<tspan fill="{t["komut"]}" font-weight="700">emre</tspan>'
                f'<tspan fill="{t["yazi"]}">@</tspan>'
                f'<tspan fill="{t["komut"]}" font-weight="700">yildirim</tspan>')
    if tur == "cizgi":
        return f'<tspan fill="{t["nokta"]}">{"—" * GENIS}</tspan>'
    if tur == "bolum":
        baslik = f"- {satir[1]} "
        return (f'<tspan fill="{t["yazi"]}" font-weight="700">{escape(baslik)}</tspan>'
                f'<tspan fill="{t["nokta"]}">{"—" * (GENIS - len(baslik))}</tspan>')
    if tur == "kv":
        return kv_satir(t, satir[1], satir[2])
    if tur == "devam":
        return f'<tspan fill="{t["deger"]}">{" " * (GENIS - len(satir[1]))}{escape(satir[1])}</tspan>'
    return None


# ---------------------------------------------------------------- SVG

def svg(ad, t, g):
    koyu = ad == "koyu"
    px = 34                          # iç boşluk
    portre_g = SUTUN * PF * 0.6
    portre_y = SATIR * PLH
    sag_x = px + portre_g + 40
    W = round(sag_x + (GENIS + 2) * CW + px)
    y0 = px + 6                      # komut satırı
    taban = y0 + 34                  # ilk bilgi satırının taban çizgisi
    y_ust = taban - 15               # portrenin üst kenarı
    yc = round(y_ust + portre_y + 34)  # imleç satırı
    H = yc + px - 6

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, \'Liberation Mono\', monospace" '
         f'font-size="{FONT}px" role="img" aria-label="Emre Yıldırım — profil kartı">']
    adim_kare = DONGU / KARE
    p.append(f"""<style>
.s{{opacity:0;animation:yaz .01s linear forwards}}
.imlec{{animation:yanip 1.1s steps(1) infinite}}
.kare{{opacity:0;animation:kare {DONGU}s steps(1) infinite}}
.kus{{animation:suz 3.6s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
.isik{{animation:isik 7s ease-in-out 2.4s infinite}}
@keyframes yaz{{to{{opacity:1}}}}
@keyframes yanip{{50%{{opacity:0}}}}
@keyframes kare{{0%{{opacity:1}}{100 / KARE:.3f}%{{opacity:0}}}}
@keyframes suz{{0%,100%{{transform:translate(0,0) rotate(0deg)}}50%{{transform:translate(3px,-6px) rotate(-1.6deg)}}}}
@keyframes isik{{0%{{transform:translateX(0)}}45%,100%{{transform:translateX({portre_g + 220:.0f}px)}}}}
@media (prefers-reduced-motion:reduce){{.s,.kus,.isik{{animation:none;opacity:1}}.kare{{animation:none}}.kare0{{opacity:1}}.imlec{{animation:none}}}}
</style>""")
    cer = 10
    fx, fy, fw, fh = px - cer, y_ust - cer, portre_g + 2 * cer, portre_y + 2 * cer
    p.append(f"""<defs>
<clipPath id="tablo"><rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="6"/></clipPath>
<linearGradient id="isikrenk" x1="0" x2="1" y1="0" y2="0">
<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".09"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
</defs>""")
    p.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="{t["zemin"]}" stroke="{t["kenar"]}"/>')
    p.append(f'<text x="{px}" y="{y0}" xml:space="preserve"><tspan fill="{t["komut"]}">~</tspan>'
             f'<tspan fill="{t["yazi"]}"> $ neofetch</tspan></text>')

    # portre: her temada koyu tablo
    p.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="6" fill="#0d1117"'
             f'{"" if koyu else " stroke=" + chr(34) + t["kenar"] + chr(34)}/>')
    gecikme, adim = 0.3, 0.03
    p.append(f'<g clip-path="url(#tablo)" font-size="{PF}px">')
    for k in range(KARE):
        p.append(f'<g class="kare kare{k}" style="animation-delay:{-k * adim_kare:.2f}s">')
        p += satirlari_yaz(katman(g, "z", k), px, y_ust, gecikme, adim)
        p.append("</g>")
    p += satirlari_yaz(katman(g, "f"), px, y_ust, gecikme, adim)
    p.append('<g class="kus">')
    p += satirlari_yaz(katman(g, "k"), px, y_ust, gecikme, adim)
    p.append("</g>")
    p.append(f'<rect class="isik" x="{fx - 200}" y="{fy}" width="160" height="{fh}" fill="url(#isikrenk)"/>')
    p.append("</g>")

    # bilgi paneli
    for i, satir in enumerate(BILGI):
        ic = bilgi_satiri(t, satir)
        if ic:
            p.append(f'<text class="s" style="animation-delay:{gecikme + i*0.06:.2f}s" x="{sag_x}" '
                     f'y="{taban + i*LH}" xml:space="preserve">{ic}</text>')

    son = gecikme + SATIR * adim + 0.1
    p.append(f'<text class="s" style="animation-delay:{son:.2f}s" x="{px}" y="{yc}" xml:space="preserve">'
             f'<tspan fill="{t["komut"]}">~</tspan><tspan fill="{t["yazi"]}"> $ </tspan>'
             f'<tspan class="imlec" fill="{t["yazi"]}">█</tspan></text>')
    p.append("</svg>")
    return "\n".join(p)


if __name__ == "__main__":
    g = izgara()
    for ad, t in TEMA.items():
        (KOK / "assets" / f"kart-{ad}.svg").write_text(svg(ad, t, g), encoding="utf-8")
    sayac = {"z": 0, "f": 0, "k": 0}
    for satir in g:
        for _, _, tur in satir:
            sayac[tur] += 1
    print("hücreler:", sayac)
