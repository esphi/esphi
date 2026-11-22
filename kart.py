"""Neofetch tarzı profil kartı: solda profil fotoğrafından ASCII portre, sağda bilgiler.
Açık + koyu SVG üretir. Çalıştır: python3 kart.py
"""
import colorsys
from html import escape
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

KOK = Path(__file__).parent
FOTO = KOK / "assets" / "avatar-kaynak.jpg"

SUTUN, SATIR = 80, 40          # ASCII portre boyutu
PF, PLH = 8, 9.6               # portre yazı boyu ve satır yüksekliği (px)
FONT = 15                      # px
CW, LH = FONT * 0.6, 20        # karakter genişliği (monospace ~0.6em), satır yüksekliği
RAMPA = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

TEMA = {
    "koyu": dict(zemin="#0d1117", kenar="#30363d", yazi="#c9d1d9", anahtar="#ffa657",
                 deger="#a5d6ff", nokta="#484f58", komut="#7ee787", portre="#c9d1d9"),
    "acik": dict(zemin="#f6f8fa", kenar="#d1d9e0", yazi="#24292f", anahtar="#953800",
                 deger="#0a3069", nokta="#b7bfc7", komut="#1a7f37", portre="#24292f"),
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


def portre(koyu: bool) -> list[str]:
    renkli = Image.open(FOTO).convert("RGB").resize((SUTUN, SATIR), Image.LANCZOS)
    gri = ImageOps.autocontrast(renkli.convert("L"), cutoff=2)
    gri = ImageEnhance.Contrast(gri).enhance(1.3)
    # arka plan lacivert: mavi kanal kırmızıdan belirgin yüksek ve parlak değilse zemindir
    maske = Image.new("L", renkli.size)
    for y in range(SATIR):
        for x in range(SUTUN):
            r, g, b = renkli.getpixel((x, y))
            on = (b - r) <= 9 or (r + g + b) / 3 > 120
            maske.putpixel((x, y), 255 if on else 0)
    maske = maske.filter(ImageFilter.MedianFilter(3))
    n = len(RAMPA) - 1
    satirlar = []  # her satır: [(renk, metin), ...] ; renk None = boşluk
    for y in range(SATIR):
        parcalar = []
        for x in range(SUTUN):
            if False:
                ch, renk = " ", None
            else:
                v = gri.getpixel((x, y)) / 255
                d = 0.30 + 0.70 * (v if koyu else 1 - v)
                ch = RAMPA[min(n, round(d * n))]
                renk = boya(renkli.getpixel((x, y)), v, koyu)
            if parcalar and parcalar[-1][0] == renk:
                parcalar[-1] = (renk, parcalar[-1][1] + ch)
            else:
                parcalar.append((renk, ch))
        while parcalar and parcalar[-1][0] is None:
            parcalar.pop()
        satirlar.append(parcalar)
    return satirlar


def boya(rgb, v, koyu):
    """Pikselin rengini zemine göre okunur hâle getirir, birleştirmek için kabalaştırır."""
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    s = min(1, s * 1.5)
    l = 0.20 + 0.80 * v ** 0.8 if koyu else 0.08 + 0.50 * v
    r, g, b = (round(c * 255 / 20) * 20 for c in colorsys.hls_to_rgb(h, l, s))
    return f"#{min(r,255):02x}{min(g,255):02x}{min(b,255):02x}"


def kv_satir(t, anahtar, deger):
    noktalar = GENIS - len(anahtar) - len(deger) - 3
    noktalar = max(noktalar, 2)
    return (f'<tspan fill="{t["anahtar"]}">{escape(anahtar)}</tspan>'
            f'<tspan fill="{t["yazi"]}">:</tspan>'
            f'<tspan fill="{t["nokta"]}"> {"." * noktalar} </tspan>'
            f'<tspan fill="{t["deger"]}">{escape(deger)}</tspan>')


def svg(ad, t):
    koyu = ad == "koyu"
    px = 26                         # iç boşluk
    portre_g = SUTUN * PF * 0.6
    px = 34
    sag_x = px + portre_g + 40
    W = round(sag_x + (GENIS + 2) * CW + px)
    ust = 30                        # komut satırı
    satir_sayisi = max(len(BILGI), -(-int(SATIR * PLH) // LH))
    H = round(px + ust + satir_sayisi * LH + LH + px)

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, \'Liberation Mono\', monospace" '
         f'font-size="{FONT}px" role="img" aria-label="Emre Yıldırım — profil kartı">']
    p.append(f"""<style>
.s{{opacity:0;animation:yaz .01s linear forwards}}
.imlec{{animation:yanip 1.1s steps(1) infinite}}
@keyframes yaz{{to{{opacity:1}}}}
@keyframes yanip{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.s{{animation:none;opacity:1}}.imlec{{animation:none}}}}
</style>""")
    p.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="{t["zemin"]}" stroke="{t["kenar"]}"/>')

    # komut satırı
    y0 = px + 6
    p.append(f'<text x="{px}" y="{y0}" xml:space="preserve"><tspan fill="{t["komut"]}">~</tspan>'
             f'<tspan fill="{t["yazi"]}"> $ neofetch</tspan></text>')

    gecikme = 0.35
    adim = 0.045
    taban = y0 + ust

    # portre (satır satır basılır)
    # portre her temada koyu bir tablonun içinde durur (açık zeminde ters çevrilmiş ASCII okunmuyor)
    cer = 10
    p.append(f'<rect x="{px - cer}" y="{taban - 4 - PLH - cer + 3}" width="{portre_g + 2*cer}" '
             f'height="{SATIR*PLH + 2*cer}" rx="6" fill="#0d1117"'
             f'{"" if koyu else " stroke=" + chr(34) + "#d1d9e0" + chr(34)}/>')
    for i, parcalar in enumerate(portre(True)):
        ic = "".join(f'<tspan fill="{r}">{escape(m)}</tspan>' if r else escape(m) for r, m in parcalar)
        p.append(f'<text class="s" style="animation-delay:{gecikme + i*adim*0.6:.2f}s" x="{px}" y="{taban - 4 + i*PLH:.1f}" '
                 f'font-size="{PF}px" xml:space="preserve">{ic}</text>')

    # bilgi paneli
    for i, satir in enumerate(BILGI):
        tur = satir[0]
        y = taban + i * LH
        d = f'style="animation-delay:{gecikme + i*adim:.2f}s"'
        if tur == "baslik":
            ic = (f'<tspan fill="{t["komut"]}" font-weight="700">emre</tspan>'
                  f'<tspan fill="{t["yazi"]}">@</tspan>'
                  f'<tspan fill="{t["komut"]}" font-weight="700">yildirim</tspan>')
        elif tur == "cizgi":
            ic = f'<tspan fill="{t["nokta"]}">{"—" * GENIS}</tspan>'
        elif tur == "bolum":
            baslik = f"- {satir[1]} "
            ic = (f'<tspan fill="{t["yazi"]}" font-weight="700">{escape(baslik)}</tspan>'
                  f'<tspan fill="{t["nokta"]}">{"—" * (GENIS - len(baslik))}</tspan>')
        elif tur == "kv":
            ic = kv_satir(t, satir[1], satir[2])
        elif tur == "devam":
            bosluk = GENIS - len(satir[1])
            ic = f'<tspan fill="{t["deger"]}">{" " * bosluk}{escape(satir[1])}</tspan>'
        else:
            continue
        p.append(f'<text class="s" {d} x="{sag_x}" y="{y}" xml:space="preserve">{ic}</text>')

    # en altta yanıp sönen imleç
    son = gecikme + satir_sayisi * adim
    yc = taban + satir_sayisi * LH
    p.append(f'<text class="s" style="animation-delay:{son:.2f}s" x="{px}" y="{yc}" xml:space="preserve">'
             f'<tspan fill="{t["komut"]}">~</tspan><tspan fill="{t["yazi"]}"> $ </tspan>'
             f'<tspan class="imlec" fill="{t["yazi"]}">█</tspan></text>')
    p.append("</svg>")
    return "\n".join(p)


if __name__ == "__main__":
    for ad, t in TEMA.items():
        (KOK / "assets" / f"kart-{ad}.svg").write_text(svg(ad, t), encoding="utf-8")
