"""Profil kapağını (açık + koyu SVG) üretir. Çalıştır: python3 kapak.py"""
from pathlib import Path

KARE = [[2, 7, 6], [9, 5, 1], [4, 3, 8]]  # sihirli kare, her toplam 15
TEMA = {
    "acik": dict(yazi="#1f2328", ikinci="#59636e", cizgi="#d1d9e0", hucre="#f6f8fa",
                 vurgu="#2f6f4f", vurgu_zemin="#e3efe8", toplam="#2f6f4f"),
    "koyu": dict(yazi="#e6edf3", ikinci="#9198a1", cizgi="#3d444d", hucre="#151b23",
                 vurgu="#8cc7a3", vurgu_zemin="#1c2e25", toplam="#8cc7a3"),
}
W, H = 880, 250
GX, GY, C, G = 610, 26, 52, 6   # ızgara başı, hücre, aralık
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def svg(t):
    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Emre Yıldırım">')
    p.append(f"""<style>
.ad{{font:700 42px {SANS};fill:{t['yazi']};letter-spacing:-0.5px}}
.alt{{font:500 17px {SANS};fill:{t['ikinci']}}}
.n{{font:600 22px {MONO};fill:{t['yazi']};text-anchor:middle;dominant-baseline:central}}
.n5{{fill:{t['vurgu']}}}
.s{{font:600 14px {MONO};fill:{t['toplam']};text-anchor:middle;dominant-baseline:central}}
.g{{opacity:0;animation:gel .45s ease-out forwards}}
.t{{opacity:0;animation:gel .5s ease-out forwards}}
@keyframes gel{{from{{opacity:0;transform:translateY(4px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion:reduce){{.g,.t{{animation:none;opacity:1}}}}
</style>""")
    # sol: isim
    p.append(f'<text class="ad" x="40" y="112">Emre Yıldırım</text>')
    p.append(f'<text class="alt" x="42" y="150">Büyük Veri Analistliği öğrencisi · SUBÜ</text>')
    p.append(f'<text class="alt" x="42" y="178">Veriyle panel, kodla oyun ve uygulama yapıyorum.</text>')
    # sağ: ızgara
    for r in range(3):
        for c in range(3):
            v = KARE[r][c]
            x, y = GX + c * (C + G), GY + r * (C + G)
            orta = v == 5
            zemin = t["vurgu_zemin"] if orta else t["hucre"]
            kenar = t["vurgu"] if orta else t["cizgi"]
            p.append(f'<rect x="{x}" y="{y}" width="{C}" height="{C}" rx="8" fill="{zemin}" stroke="{kenar}"/>')
            gecikme = 0.3 + 0.2 * v
            cls = "n n5" if orta else "n"
            p.append(f'<text class="{cls} g" style="animation-delay:{gecikme:.2f}s" x="{x + C/2}" y="{y + C/2 + 1}">{v}</text>')
    son = 0.3 + 0.2 * 9 + 0.35
    boy = 3 * C + 2 * G
    for i in range(3):  # satır toplamları sağda, sütun toplamları altta
        p.append(f'<text class="s t" style="animation-delay:{son + i*0.08:.2f}s" x="{GX + boy + 22}" y="{GY + i*(C+G) + C/2}">15</text>')
        p.append(f'<text class="s t" style="animation-delay:{son + 0.24 + i*0.08:.2f}s" x="{GX + i*(C+G) + C/2}" y="{GY + boy + 18}">15</text>')
    p.append(f'<text class="s t" style="animation-delay:{son + 0.5:.2f}s" x="{GX + boy + 22}" y="{GY + boy + 18}">15</text>')
    p.append("</svg>")
    return "\n".join(p)


for ad, t in TEMA.items():
    Path(__file__).with_name("assets").joinpath(f"kapak-{ad}.svg").write_text(svg(t), encoding="utf-8")
print("tamam")
