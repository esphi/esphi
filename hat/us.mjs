// Profil figürü 2: "turning ideas into real products" bir fırlatma üssü olarak.
// Her proje aynı roket, farklı tamamlanmışlıkta. Çalıştır: node hat/us.mjs → assets/us.svg
import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as k from "./kit/iso-kit.mjs";
import * as G from "./kit/lathe.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const W = 1200, H = 860, TAU = Math.PI * 2;

// ── gerçek durum (tasarim.py'deki PIPELINE ile aynı tutulur) ─────────────────
const EN = 62;
const ASAMA = [
  { ad: "IDEA", not: "just a sketch", y: [0, 1] },
  { ad: "PROTOTYPE", not: "rough first version", y: [1, 4] },
  { ad: "WORKING", not: "runs, unfinished", y: [4, 5] },
  { ad: "BUILT", not: "finished, not released", y: [5, 7] },
  { ad: "REVIEW", not: "App Store check", y: [7, 8] },
  { ad: "LIVE", not: "in your hands", y: [8, 9] },
];
const PROJE = [
  { ad: ["Odanda Gör"], y: 1 }, { ad: ["BİİİP"], y: 2 }, { ad: ["ZIP RUSH"], y: 3, soluk: true },
  { ad: ["VeriPilot"], y: 4 }, { ad: ["Pass"], y: 5 }, { ad: ["Veri", "Temizleyici"], y: 6 }, { ad: ["KESEN"], y: 7, lit: true },
];
const C = (i) => EN * i + EN / 2;
const MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace";

const w = (s, t, z) => [t, -s, z];
const plan = (s, t, ls, lt, r = 1) => ({ x: t, y: -(s + ls), w: lt, d: ls, r });
const ZB = -58, TON = 66, TAR = -78;
const TABAN = plan(-22, TAR, EN * 9 + 44, TON - TAR, 8);
const P0 = k.fitProjection([...k.boxCorners(TABAN, ZB - 8, 0)], W, H, { pad: 26, headroom: 0, azimuth: 13, elevation: 23 });
const ALTY = Math.max(...k.boxCorners(TABAN, ZB - 8, 0).map((p) => k.iso(p, P0)[1]));
const P = { ...P0, origin: [P0.origin[0], P0.origin[1] + (H - 34 - ALTY)] };
const K = G.scaleOf(P), V = G.viewOf(P);
const at = (s, t, z) => k.iso(w(s, t, z), P);

const S = (paths, st) => k.solidSvg(paths, st);
const L = (d, st) => (d ? k.lineSvg(d, st) : "");
const D = (pts, st) => k.dotsSvg(pts, st);
const mt = (ad, ...svg) => `<g class="mt-${ad}">${svg.join("")}</g>`;
const kutu = (s, t, ls, lt, z, h, st = {}, r = 1, bevel = 0, steps = 3) => S(k.slabOf(plan(s, t, ls, lt, r), z, h, P, steps, bevel), { tone: "mid", ...st });
const sil = (s, t, r, z, h, st = {}, steps = 28, bevel = 0) => S(k.cylinder(t, -s, r, z, h, P, steps, bevel), { tone: "mid", ...st });
const poli = (pts, kapali = false) => k.pathOf(pts.map((p) => at(...p)), kapali);
const cizgi = (a, b, st) => L(poli([a, b]), st);
const halka = (s, t, r, z, st = { tone: "lo" }, n = 32) => L(k.ring(t, -s, r, z, P, n), st);
const ustC = (s, t, ls, lt, z, r, st = { tone: "faint" }) => L(k.planOutline(plan(s, t, ls, lt, r), z, P, 3), st);
const nokta = (pts, st) => D(pts.map((p) => at(...p)), st);
const X = (s, t, z) => G.frameOf(w(s, t, z), [1, 0, 0], [0, -1, 0], [0, 0, 1]); // eksen +t
const SA = (s, t, z) => G.frameOf(w(s, t, z), [0, -1, 0], [1, 0, 0], [0, 0, 1]); // eksen +s
const ZA = (s, t, z, yon = 1) => G.frameOf(w(s, t, z), [0, 0, yon], [1, 0, 0], [0, 1, 0]);
const daire = (s, t, z, r) => G.circleOf(X(s, t, z), 0, r, P, 24); // +t yüzünde
const kay = (ds, dt, dz) => { const [x, y] = k.axisVector(P, [dt, -ds, dz]); return `${x.toFixed(2)}px,${y.toFixed(2)}px`; };
const onM = (s, t, z) => k.sideMatrix([t, -s], z, P, "right");
const ustM = (s, t, z) => k.topMatrix([t, -s], z, P, "y");
const yaziOn = (s, t, z, m, st) => k.faceTextSvg(onM(s, t, z), m, st);
const yaziUst = (s, t, z, m, st) => k.faceTextSvg(ustM(s, t, z), m, st);
const dolu = (d, cls) => `<path class="${cls}" d="${d}"/>`;
const uzak = (l) => [...l].sort((a, b) => b.s - a.s);
const dikis = (s, t, ls, lt, zs, r = 1, tone = "faint") => L(zs.map((z) => k.sideSeam(plan(s, t, ls, lt, r), z, P, 3)).join(""), { tone });
const tirtil = (s, t, r, z0, z1, n) => L(k.knurl(t, -s, r, z0, z1, n, P, 0.3) + k.sideArc(t, -s, r, z0, P, 32) + k.sideArc(t, -s, r, z1, P, 32), { tone: "lo" });
// +t yüzünde yuvarlak köşeli çerçeve
const onC = (s0, s1, z0, z1, t, r = 1.5) => {
  const pts = [];
  for (const [cs, cz, a] of [[s1 - r, z1 - r, 0], [s0 + r, z1 - r, 90], [s0 + r, z0 + r, 180], [s1 - r, z0 + r, 270]])
    for (let i = 0; i <= 4; i++) { const q = ((a + i * 22.5) * Math.PI) / 180; pts.push([cs + Math.cos(q) * r, t, cz + Math.sin(q) * r]); }
  return poli(pts, true);
};
const civata = (s, t, z, r = 1.1) => { const c = at(s, t, z); return `${L(daire(s, t, z, r), { tone: "lo" })}${D([c], { size: 0.5 })}`; };
let kimlik = 0;
const kes = (d, ...svg) => { const id = `c${++kimlik}`; return `<clipPath id="${id}"><path d="${d}"/></clipPath><g clip-path="url(#${id})">${svg.join("")}</g>`; };
// düşen gölge: ışık kitin ışığıyla aynı yönden (ekranda soldan)
const GS = 0.62 * 0.819, GT = 0.62 * 0.574;
const golge = (halkaPts, z0, h, zp) => {
  const u = [];
  for (const [x, y] of halkaPts) for (const z of [z0, z0 + h]) { const d = z - zp; u.push(k.iso([x + GT * d, y - GS * d, zp], P)); }
  return k.pathOf(G.hullOf(u), true);
};
const gKutu = (s, t, ls, lt, z0, h, zp, r = 1) => golge(k.ringOf(plan(s, t, ls, lt, r), 3), z0, h, zp);
const gSil = (s, t, r, z0, h, zp) => golge(k.circleRing(t, -s, r, 20), z0, h, zp);
const golgeler = (yollar, cls = "golge") => `<path class="${cls}" d="${yollar.join("")}"/>`;
// küre kapağı: üst yarı, taban halkasıyla birleşir
const kubbe = (s, t, z, rr, st = { tone: "hi" }) => { const [x, y] = at(s, t, z), u = []; for (let i = 0; i < 60; i++) u.push(k.iso([t + Math.cos((i / 60) * TAU) * rr, -s + Math.sin((i / 60) * TAU) * rr, z], P)); for (let i = 0; i <= 40; i++) { const q = Math.PI + (i / 40) * Math.PI; u.push([x + Math.cos(q) * rr * K, y + Math.sin(q) * rr * K]); } const d = k.pathOf(G.hullOf(u), true); return kes(d, S(G.sphereOf(w(s, t, z), rr, P), st)) + `<path class="iso-line" data-tone="hi" d="${d}"/>`; };
// kablo/hortum: dünya noktaları, dolgu yarıçapı
const kablo = (pts, r = 1, cls = "", bukum = 5) => {
  const d = k.pathOf(G.fillet(pts.map((p) => w(...p)), bukum, 6).map((p) => k.iso(p, P)));
  const b = 2 * r * K;
  return `<g class="kb ${cls}"><path class="kb0" d="${d}" style="stroke-width:${(b + 1.1).toFixed(2)}"/><path class="kb1" d="${d}" style="stroke-width:${b.toFixed(2)}"/><path class="kb2" d="${d}" style="stroke-width:${(b * 0.28).toFixed(2)}" transform="translate(${(-b * 0.12).toFixed(2)} ${(-b * 0.2).toFixed(2)})"/></g>`;
};
const led = (s, t, z, cls, r = 1.1) => `${dolu(daire(s, t, z, r + 0.5), "ledy")}${dolu(daire(s, t, z, r), "led " + cls)}`;
const ledUst = (s, t, z, cls, r = 1.1) => `${dolu(k.ring(t, -s, r + 0.5, z, P, 18), "ledy")}${dolu(k.ring(t, -s, r, z, P, 18), "led " + cls)}`;

// ── roket parçaları ──────────────────────────────────────────────────────────
const R = 15, GOV0 = 18, GOV1 = 112, BURUN = 46;
const silG = (c, t, z0, z1, r = R) => { const u = []; for (const z of [z0, z1]) for (let i = 0; i < 48; i++) u.push(at(c + Math.cos((i / 48) * TAU) * r, t + Math.sin((i / 48) * TAU) * r, z)); return dolu(k.pathOf(G.hullOf(u), true), "silG"); };
const tup = (c, t, z0, z1, r, mat, st = {}, ustKapak = true) => mt(mat, sil(c, t, r, z0, z1 - z0, { tone: "hi", crease: "lo", ...st }, 64)) + (ustKapak ? "" : "");
const burR = (L, r) => (s) => r * Math.max(0, 1 - (s / L) ** 1.75) ** 0.78;
function burun(c, t, z, L, r, mat, st = {}) {
  const f = burR(L, r), g = (s) => Math.max(-6, (f(Math.min(L, s + 0.05)) - f(Math.max(0, s - 0.05))) / 0.1), F = ZA(c, t, z), n = [];
  for (let i = 0; i <= 30; i++) { const s = L * (1 - (1 - i / 30) ** 1.4); n.push([s, f(s), 1]); }
  const u = []; for (const [s, rr] of n) for (let i = 0; i < 24; i++) u.push(at(c + Math.cos((i / 24) * TAU) * rr, t + Math.sin((i / 24) * TAU) * rr, z + s));
  return mt(mat, S(G.lathe(n, F, P, { smooth: { slope: g, radius: f } }), { tone: "hi", ...st })) + dolu(k.pathOf(G.hullOf(u), true), "silG");
}
const lule = (c, t, z0, mat = "krom") => mt(mat, S(G.lathe(Array.from({ length: 9 }, (_, i) => [10 - i * 1.25, 4.6 + 5 * Math.sin((i / 8) * 1.45) ** 1.2, 1]).reverse(), ZA(c, t, z0), P, { smooth: true }), { tone: "hi" })) + dolu(k.ring(t, -c, 8.4, z0 + 0.01, P, 32), "lic");
function kanatlar(c, t, z0, mat, on) {
  const o = [];
  for (const d of [231, 335, 51, 155]) {
    const q = (d * Math.PI) / 180, u = [Math.sin(q), -Math.cos(q), 0], a = [Math.cos(q), Math.sin(q), 0];
    const arka = d > 180; if (arka === on) continue;
    const oo = G.add3(w(c, t, z0), G.mul3(a, -0.9));
    o.push(mt(mat, S(G.prismOf(G.frameOf(oo, a, u, [0, 0, 1]), [[R - 0.6, 12], [R + 10, 0], [R + 10, 9], [R + 6, 20], [R - 0.6, 42]], 0, 1.8, P), { tone: "hi" })));
  }
  return o.join("");
}
// proje amblemleri (roketin ön yüzünde)
const AMB = {
  "Odanda Gör": "M-6 1V-2.4A1.8 1.8 0 0 1 -2.6 -2.8V-5.4A1.4 1.4 0 0 1 -1.2 -6.8H1.2A1.4 1.4 0 0 1 2.6 -5.4V-2.8A1.8 1.8 0 0 1 6 -2.4V4.4H-6ZM-5 4.4V6.4M5 4.4V6.4M-2.6 .6H2.6",
  "BİİİP": "M-2.4 -6.4A2.4 2.4 0 0 1 2.4 -6.4V-1A2.4 2.4 0 0 1 -2.4 -1ZM-4.6 -1.6A4.6 4.6 0 0 0 4.6 -1.6M0 3V6.4M-3 6.4H3",
  "ZIP RUSH": "M-5.4 -5.4H5.4V-1.8H-5.4V1.8H5.4V5.4H-2",
  VeriPilot: "M-5.4 6V1.4H-2.6V6ZM-1.4 6V-2H1.4V6ZM2.6 6V-6H5.4V6Z",
  Pass: "M-6 4.6H6M-5 3.4A5 5 0 0 1 5 3.4ZM0 -1.6V-3.4M-1.4 -3.4H1.4",
  Veri: "M-6 -5.6H6L1.6 .4V6.2L-1.6 4.4V.4Z",
  KESEN: "M-6 -6H6V6H-6ZM-2 -6V6M2 -6V6M-6 -2H6M-6 2H6",
};
const amblem = (c, t, z, ad, cls = "", olcek = 1) => `<g transform="${onM(c, t + R + 0.4, z)} scale(${olcek})"><path class="amb ${cls}" d="${AMB[ad]}"/></g>`;
const pencere = (c, t, z, yan = true) => { const F = X(c, t + R - 1, z); return mt("krom", S(G.disc(0, 2, 4.2, F, P), { tone: "hi" })) + dolu(G.circleOf(F, 2, 3, P), yan ? "lumba" : "lumba sonuk"); };
// bitmiş roket
function raket(c, t, z0, ad, { mat = "beyaz", ek = "turuncu", aci = true } = {}) {
  const o = [golgeler([gSil(c, t, R, z0, 130, Math.max(0, z0 - 6) > 10 ? 14 : 0)])];
  o.push(kanatlar(c, t, z0, ek, false), lule(c, t, z0));
  o.push(tup(c, t, z0 + 10, z0 + GOV0, R - 1.6, "celik"), tup(c, t, z0 + GOV0, z0 + GOV1, R, mat, { inner: L([22, 46, 70, 100].map((z) => k.sideArc(t, -c, R, z0 + z, P, 40)).join(""), { tone: "faint" }) }));
  o.push(tup(c, t, z0 + 78, z0 + 84, R + 0.25, ek, { crease: "none" }), tup(c, t, z0 + 84, z0 + GOV1, R, mat, { inner: L([100, 106].map((z) => k.sideArc(t, -c, R, z0 + z, P, 40)).join(""), { tone: "faint" }) }));
  o.push(tup(c, t, z0 + GOV0, z0 + GOV0 + 3, R + 0.25, ek, { crease: "none" }), tup(c, t, z0 + GOV0 + 3, z0 + 78, R, mat, { crease: "none", inner: L([26, 46, 70].map((z) => k.sideArc(t, -c, R, z0 + z, P, 40)).join(""), { tone: "faint" }) }), tup(c, t, z0 + 78, z0 + 84, R + 0.25, ek, { crease: "none" }), tup(c, t, z0 + 84, z0 + GOV1, R, mat, { crease: "none", inner: L([104].map((z) => k.sideArc(t, -c, R, z0 + z, P, 40)).join(""), { tone: "faint" }) }));
  const pd = []; for (const z of [24, 48, 72, 88, 108]) for (let i = -4; i <= 4; i++) { const q = Math.PI / 2 + i * 0.33; pd.push([c + Math.cos(q) * R, t + Math.sin(q) * R, z0 + z]); } o.push(nokta(pd, { size: 0.5, tone: "lo" }));
  o.push(silG(c, t, z0 + GOV0, z0 + GOV1));
  o.push(burun(c, t, z0 + GOV1, BURUN, R, ek), pencere(c, t, z0 + 96), amblem(c, t, z0 + 56, ad, ek === "turuncu" ? "t" : "", 1.15), kanatlar(c, t, z0, ek, true));
  void aci; return o.join("");
}
// iskelet roket: halkalar + kirişler, alttan panelleniyor
function iskelet(c, t, z0, ad, { panel = 1, ust = 94, soluk = false } = {}) {
  const o = [golgeler([gSil(c, t, R, z0, ust, 0)]), kanatlar(c, t, z0, "celik", false)];
  const h = []; for (let z = 18; z <= ust; z += 12) h.push(z);
  const yay = (z, on) => { const p = []; for (let i = 0; i <= 30; i++) { const q = (on ? 0 : Math.PI) + (i / 30) * Math.PI; p.push([c + Math.cos(q + 0.23) * R, t + Math.sin(q + 0.23) * R, z0 + z]); } return poli(p); };
  const kirisA = [], kirisO = []; for (let i = 0; i < 16; i++) { const q = (i / 16) * TAU + 0.12, p = [c + Math.cos(q) * R, t + Math.sin(q) * R]; (Math.sin(q - 0.23) > 0 ? kirisO : kirisA).push(poli([[...p, z0 + 18], [...p, z0 + ust]])); }
  o.push(lule(c, t, z0, soluk ? "celik" : "pirinc"), tup(c, t, z0 + 10, z0 + 18, R - 1.6, "celik"));
  o.push(`<path class="isk a" d="${kirisA.join("")}${h.map((z) => yay(z, false)).join("")}"/>`);
  // içeride yakıt tankı
  const tk = Math.min(ust - 14, 62); o.push(mt(soluk ? "celik" : "pirinc", sil(c, t, 8.4, z0 + 22, tk - 22, { tone: "hi", crease: "none", inner: L([30, 40, 50].map((z) => k.sideArc(t, -c, 8.4, z0 + z, P, 24)).join(""), { tone: "lo" }) }, 40)), mt(soluk ? "celik" : "pirinc", ""), kubbeM(c, t, z0 + tk, 8.4, soluk ? "celik" : "pirinc"));
  o.push(`<path class="isk" d="${kirisO.join("")}${h.map((z) => yay(z, true)).join("")}"/>`);
  if (panel) {
    const z1 = 18 + panel * 12; o.push(tup(c, t, z0 + 18, z0 + z1, R + 0.2, soluk ? "celik" : "acik", { inner: L([24, 30, 36, 42].filter((z) => z < z1).map((z) => k.sideArc(t, -c, R, z0 + z, P, 40)).join(""), { tone: "faint" }) }), silG(c, t, z0 + 18, z0 + z1));
    // üst ağız: panelin içi görünür
    o.push(dolu(k.ring(t, -c, R - 0.6, z0 + z1, P, 48), "agiz"), `<path class="isk a" d="${kirisA.slice(0, 7).map((x) => x).join("")}" style="opacity:0"/>`);
    const ic = []; for (let i = 0; i < 16; i++) { const q = (i / 16) * TAU + 0.12, p = [c + Math.cos(q) * R, t + Math.sin(q) * R]; ic.push(poli([[...p, z0 + z1], [...p, z0 + ust]])); }
    o.push(mt(soluk ? "celik" : "pirinc", sil(c, t, 8.4, z0 + z1, Math.max(1, tk - z1), { tone: "hi", crease: "none", inner: L([30, 40, 50].filter((z) => z > z1).map((z) => k.sideArc(t, -c, 8.4, z0 + z, P, 24)).join(""), { tone: "lo" }) }, 40)), kubbeM(c, t, z0 + tk, 8.4, soluk ? "celik" : "pirinc"));
    o.push(`<path class="isk" d="${ic.filter((_, i) => Math.sin((i / 16) * TAU + 0.12 - 0.23) > 0).join("")}${h.filter((z) => z > z1).map((z) => yay(z, true)).join("")}"/>`);
  }
  o.push(kanatlar(c, t, z0, "celik", true));
  // amblem levhası iskelete asılı
  const az = z0 + Math.min(ust - 14, 18 + panel * 12 + 16); o.push(S(k.slabOf(plan(c - 8, t + R + 0.6, 16, 1, 0.2), az - 9, 18, P, 2), { tone: "hi" }), `<g transform="${onM(c, t + R + 1.6, az)}"><path class="amb ${soluk ? "s" : "k"}" d="${AMB[ad]}"/></g>`);
  return o.join("");
}
const kubbeM = (c, t, z, rr, mat) => mt(mat, kubbe(c, t, z, rr));
const kafes = (s, t, z0, z1, en, adim = 14) => {
  const o = [], h = en / 2, d = [];
  const dir = (a, b) => S(k.slabOf(plan(s + a - 0.9, t + b - 0.9, 1.8, 1.8, 0.2), z0, z1 - z0, P, 2), { tone: "mid", crease: "none" });
  o.push(dir(h, -h), dir(-h, -h));
  for (let z = z0; z < z1 - 1; z += adim) { const zz = Math.min(z1, z + adim); d.push(poli([[s - h, t - h, z], [s + h, t - h, zz]]), poli([[s + h, t - h, z], [s + h, t + h, zz]])); }
  o.push(L(d.join(""), { tone: "lo" }), dir(h, h));
  const d2 = []; for (let z = z0; z < z1 - 1; z += adim) { const zz = Math.min(z1, z + adim); d2.push(poli([[s - h, t + h, z], [s + h, t + h, zz]]), poli([[s - h, t + h, zz], [s + h, t + h, z]]), poli([[s - h, t - h, z], [s - h, t + h, zz]]), poli([[s - h, t + h, zz], [s + h, t + h, zz]]), poli([[s - h, t - h, zz], [s - h, t + h, zz]])); }
  o.push(L(d2.join(""), { tone: "mid" }), dir(-h, h)); return o.join("");
};
const direkY = (s, t, z0, z1, en = 4) => S(k.slabOf(plan(s - en / 2, t - en / 2, en, en, 0.5), z0, z1 - z0, P, 2), { tone: "hi", crease: "lo" });
const kiris = (s, t, ls, lt, z, h) => S(k.slabOf(plan(s, t, ls, lt, 0.4), z, h, P, 2), { tone: "hi", crease: "lo" });
// iskele: rocketin iki yanında boru + tahta
function iskele(c, t, ust, on) {
  const o = [], tt = on ? t + 19 : t - 19, zs = []; for (let z = 22; z < ust; z += 26) zs.push(z);
  if (!on) { for (const z of zs) o.push(kutu(c - 25, tt - 4, 50, 8, z, 1.4, { tone: "mid" }, 0.3)); o.push(L(zs.map((z) => poli([[c - 24, tt, z - 22], [c + 24, tt, z]])).join(""), { tone: "lo", free: true })); }
  else o.push(L(zs.map((z) => poli([[c - 24, tt, z], [c + 24, tt, z]])).join(""), { tone: "mid", free: true }));
  for (const s of [c + 24, c - 24]) o.push(mt("pirinc", sil(s, tt, 0.8, 0, ust + 6, { crease: "none" }, 8)));
  return o.join("");
}
const kaynak = (x, y, gec) => `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)})"><circle class="kayH m" style="animation-delay:${gec}s" r="15"/><path class="kayY m" style="animation-delay:${gec}s" d="M0 -8L1.4 -1.4L8 0L1.4 1.4L0 8L-1.4 1.4L-8 0L-1.4 -1.4Z"/>${[[-9, 20], [6, 26], [12, 16], [-4, 30], [2, 18], [-14, 12]].map(([dx, dy], i) => `<circle class="kiv m" style="--x:${dx}px;--y:${dy}px;animation-delay:${(gec - i * 0.13).toFixed(2)}s" r="1.2"/>`).join("")}</g>`;
const duman = (x, y, liste, cls = "") => `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)})">${liste.map(([dx, dy, r, g, s]) => `<circle class="dum m ${cls}" style="--x:${dx}px;--y:${dy}px;animation-delay:${g}s;animation-duration:${s}s" r="${r}"/>`).join("")}</g>`;

// ── sahne ────────────────────────────────────────────────────────────────────
const PX = 1062, PY = 138, YR = 178, YB = 40, YT = -0.26, YQ = 3.24; // gezegen, yörünge, boş yuvanın açısı
const yor = (q) => { const x = Math.cos(q) * YR, y = Math.sin(q) * YB; return [PX + x * Math.cos(YT) - y * Math.sin(YT), PY + x * Math.sin(YT) + y * Math.cos(YT)]; };
function gok() {
  const o = []; let sd = 7; const rnd = () => ((sd = (sd * 16807) % 2147483647) / 2147483647);
  const yl = ["", "", ""]; for (let i = 0; i < 190; i++) { const x = rnd() * W, y = rnd() * 560; if (x < 720 && y < 140 && y > 30) continue; yl[i % 3] += `M${x.toFixed(1)} ${y.toFixed(1)}h.01`; }
  yl.forEach((d, i) => o.push(`<path class="yildiz y${i}${i ? " m" : ""}" d="${d}"/>`));
  // gezegen + yörünge: LIVE
  const px = PX, py = PY, pr = 98;
  o.push(`<circle cx="${px}" cy="${py}" r="170" fill="url(#gezH)"/>`);
  o.push(`<g transform="translate(${px} ${py}) rotate(${((YT * 180) / Math.PI).toFixed(1)})"><path class="yorA" d="M${-YR} 0A${YR} ${YB} 0 0 1 ${YR} 0"/></g>`);
  o.push(`<circle cx="${px}" cy="${py}" r="${pr}" fill="url(#gez)"/>`);
  const kt = kes(`M${px - pr} ${py}A${pr} ${pr} 0 1 1 ${px + pr} ${py}A${pr} ${pr} 0 1 1 ${px - pr} ${py}Z`, `<path class="kita" d="M${px - 78} ${py - 46}c26 -22 54 -16 66 -2s34 2 30 24s-34 12 -44 30s-34 22 -46 4s-22 -40 -6 -56ZM${px + 18} ${py + 18}c18 -10 44 -2 50 14s-16 38 -36 36s-30 -38 -14 -50ZM${px + 26} ${py - 70}c16 -4 36 8 34 18s-24 8 -32 2s-12 -18 -2 -20Z"/><path class="bulut" d="M${px - 90} ${py + 6}c40 -10 70 8 112 0s50 -6 80 2M${px - 80} ${py - 26}c34 8 60 -8 100 -2s40 6 70 0M${px - 60} ${py + 48}c30 -6 60 6 110 -2"/><g fill="#ffd58a">${Array.from({ length: 42 }, () => `<circle cx="${(px - 60 + rnd() * 110).toFixed(1)}" cy="${(py - 50 + rnd() * 104).toFixed(1)}" r="${(0.6 + rnd() * 0.9).toFixed(1)}" opacity="${(0.25 + rnd() * 0.6).toFixed(2)}"/>`).join("")}</g><circle cx="${px}" cy="${py}" r="${pr}" fill="url(#gezG)"/>`);
  const [sx, sy] = yor(YQ), [ux, uy] = yor(0.5);
  o.push(kt, `<g transform="translate(${px} ${py}) rotate(${((YT * 180) / Math.PI).toFixed(1)})"><path class="yorO" d="M${-YR} 0A${YR} ${YB} 0 0 0 ${YR} 0"/></g>`);
  o.push(`<g transform="translate(${sx.toFixed(1)} ${sy.toFixed(1)}) rotate(16) scale(1.5)"><circle r="24" fill="#0A0F1C" opacity=".75"/><circle class="yuvC" r="24"/><g class="m yuva0"><path class="bosR" d="M0 -17C5 -11 6 -5 6 2V12H-6V2C-6 -5 -5 -11 0 -17ZM-6 5L-11 13V16L-6 12M6 5L11 13V16L6 12"/></g></g>`);
  o.push(`<text x="${(sx - 46).toFixed(0)}" y="${(sy - 6).toFixed(0)}" text-anchor="end" font-family="${MONO}" font-size="17" font-weight="700" fill="#F47735">LIVE</text><text x="${(sx - 46).toFixed(0)}" y="${(sy + 14).toFixed(0)}" text-anchor="end" font-family="${MONO}" font-size="14" fill="#8C95A8">0 in orbit</text>`); void ux; void uy;
  return o.join("");
}
function ufuk() {
  const tepe = (y0, seed, g, cls) => { let sd = seed; const rnd = () => ((sd = (sd * 16807) % 2147483647) / 2147483647); const p = [[0, H]]; for (let x = 0; x <= W; x += 60) p.push([x, y0 - rnd() * g]); p.push([W, H]); return `<path class="${cls}" d="M${p.map(([x, y]) => `${x} ${y.toFixed(0)}`).join("L")}Z"/>`; };
  const o = [tepe(470, 11, 70, "tepe1"), tepe(520, 29, 60, "tepe2")]; let d = ""; let sd = 5; const rnd = () => ((sd = (sd * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < 46; i++) d += `M${(rnd() * W).toFixed(0)} ${(500 + rnd() * 40).toFixed(0)}h.01`;
  o.push(`<path class="uzakI" d="${d}"/>`); return o.join("");
}
const isildak = (s, t, gec, sure) => { const [x, y] = at(s, t, 10); return `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)})"><g class="m isl" style="animation-delay:${gec}s;animation-duration:${sure}s"><path fill="url(#isl)" d="M-3 0L-58 -520H58L3 0Z"/></g></g>`; };
function taban() {
  const o = [`<path class="iso-halo" d="${k.haloOf(TABAN, ZB - 8, 6, P)}"/>`];
  const ek = [-2.4, -29.2, ZB + 3].map((z) => L(k.sideSeam(TABAN, z, P, 6), { tone: "faint" })).join("");
  o.push(S(k.slabOf(TABAN, ZB, -ZB, P, 6, 1.4), { tone: "hi", crease: "lo", inner: ek }));
  o.push(L(k.planOutline(k.insetPlan(TABAN, 4), 0, P, 6), { tone: "faint" }));
  // zemin karoları + aşama alanları
  const d = []; for (let s = -18; s < 580; s += 31) d.push(poli([[s, TAR + 4, 0], [s, 30, 0]])); for (let t = TAR + 24; t < 32; t += 27) d.push(poli([[-18, t, 0], [576, t, 0]]));
  o.push(L(d.join(""), { tone: "faint", free: true }));
  ASAMA.forEach(({ ad, y: [a, b] }) => { const s0 = a * EN + 2, s1 = b * EN - 2; o.push(`<path class="alan0 ${ad === "REVIEW" ? "r" : ad === "LIVE" ? "l" : ""}" d="${k.planOutline(plan(s0, -32, s1 - s0, 64, 4), 0, P, 4)}"/>`); });
  // ön yol: tırtıl aracının rayı
  o.push(dolu(poli([[-18, 37, 0], [576, 37, 0], [576, 61, 0], [-18, 61, 0]], true), "yolZ"));
  for (const t of [41, 55]) { let tr = ""; for (let s = -16; s < 574; s += 7) tr += poli([[s, t - 2, 0], [s + 3.6, t - 2, 0], [s + 3.6, t + 4, 0], [s, t + 4, 0]], true); o.push(dolu(tr, "travers")); o.push(L(poli([[-18, t, 0.4], [576, t, 0.4]]) + poli([[-18, t + 2, 0.4], [576, t + 2, 0.4]]), { tone: "mid" })); }
  let ok = ""; for (let i = 0; i < 9; i++) { const s = C(i) + EN / 2 - 6; ok += poli([[s, 46, 0], [s + 4, 46, 0], [s + 8, 49, 0], [s + 4, 52, 0], [s, 52, 0], [s + 4, 49, 0]], true); } o.push(dolu(ok, "okz"));
  // ön yüz
  const T = TON;
  ASAMA.forEach(({ ad, not, y: [a, b] }, i) => {
    const s0 = a * EN + 2, s1 = b * EN - 2, c = (s0 + s1) / 2, canli = ad === "LIVE", rev = ad === "REVIEW";
    o.push(S(k.slabOf(plan(s0, T, s1 - s0, 1.2, 0.2), ZB + 4.6, 23.4, P, 2), { tone: "mid" }));
    o.push(dolu(onC(s0, s1, ZB + 4.6, ZB + 6.6, T + 1.2, 0.1), `serit${i}`));
    const uz = s1 - s0, p1 = Math.min(12, (uz - 6) / (ad.length * 0.61)), p2 = Math.min(6.6, (uz - 4) / (not.length * 0.605));
    o.push(yaziOn(c, T + 1.2, -41.4, ad, { size: +p1.toFixed(2), tone: canli || rev ? "lit" : "hi", anchor: "middle" }), `<g class="acik2">${yaziOn(c, T + 1.2, -49.6, not, { size: +p2.toFixed(2), anchor: "middle" })}</g>`);
  });
  // proje levhaları + 6 dilimli ilerleme
  for (let y = 0; y < 9; y++) {
    const p = PROJE.find((q) => q.y === y), s = C(y), a = ASAMA.findIndex(({ y: [m, n] }) => y >= m && y < n);
    if (p) {
      o.push(mt(p.lit ? "levhaT" : p.soluk ? "celik" : "levha", S(k.slabOf(plan(s - 28, T, 56, 1.4, 0.2), -18.6, 15.4, P, 2), { tone: "hi" })));
      const yz = (z, m, size) => o.push(`<g class="etk ${p.soluk ? "hi" : "kara"}">${yaziOn(s, T + 1.4, z, m, { size, anchor: "middle" })}</g>`);
      const ad = p.ad.join(" "); if (p.ad.length === 1) yz(-14, ad, Math.min(9.4, 50 / (ad.length * 0.61))); else { yz(-9.9, p.ad[0], 6.6); yz(-16.6, p.ad[1], 6.6); }
    } else o.push(`<path class="bosL" d="${onC(s - 28, s + 28, -18.6, -3.2, T, 1)}"/>`, `<g class="acik2">${yaziOn(s, T, -13.2, y ? "nothing yet" : "next?", { size: 6.6, anchor: "middle" })}</g>`);
    for (let j = 0; j < 6; j++) { const x = s - 28 + j * 9.5; o.push(dolu(onC(x, x + 8.5, -26.8, -21.8, T, 0.8), `dil ${j <= a && (p || y === 0) ? (p?.lit ? "t" : p?.soluk || !p ? "s" : "d") : ""}${p && j === a ? " m ucD" : ""}`)); }
  }
  return o.join("");
}
// IDEA: hologram masası
function idea() {
  const c = C(0), o = [golgeler([gSil(c, 0, 24, 0, 12, 0)])];
  o.push(sil(c, 0, 25, 0, 4, { tone: "mid" }, 64, 0.5), mt("acik", sil(c, 0, 20, 4, 8, { tone: "hi", crease: "lo", inner: tirtil(c, 0, 20, 6, 10, 80) }, 64, 0.5)), dolu(k.ring(0, -c, 16, 12.05, P, 48), "holoZ"), halka(c, 0, 18, 12, { tone: "lo" }, 48));
  const [x0, y0] = at(c, 0, 12), [x1, y1] = at(c, 0, 150); void x1; const yh = y0 - y1;
  o.push(`<path fill="url(#holo)" d="M${(x0 - 16 * K).toFixed(1)} ${y0.toFixed(1)}L${(x0 - 27 * K).toFixed(1)} ${y1.toFixed(1)}H${(x0 + 27 * K).toFixed(1)}L${(x0 + 16 * K).toFixed(1)} ${y0.toFixed(1)}Z"/>`);
  // hologram roket: tel çizim, kendi ekseninde dönüyor (boylam çizgileri kayar)
  const g = [], z0 = 22; const f = burR(BURUN, R);
  const rr = (z) => (z < GOV1 ? R : f(z - GOV1));
  const halkaH = (z, r) => { const p = []; for (let i = 0; i < 40; i++) { const q = (i / 40) * TAU; p.push([c + Math.cos(q) * r, Math.sin(q) * r, z0 + z]); } return poli(p, true); };
  for (const z of [12, 18, 40, 62, 84, 112, 126, 138]) g.push(halkaH(z * 0.86, rr(z)));
  o.push(`<path class="holo" d="${g.join("")}"/>`);
  const KARE = 8; for (let j = 0; j < KARE; j++) { let d = ""; for (let i = 0; i < 8; i++) { const q = ((i + j / KARE) / 8) * TAU, p = []; for (const z of [18, 40, 62, 84, 100, 112, 120, 128, 136, 143, 149, 154, 157.6]) p.push([c + Math.cos(q) * rr(z), Math.sin(q) * rr(z), z0 + z * 0.86]); d += poli(p); } o.push(`<path class="holo k m" style="animation-delay:${((j * 1.2) / KARE - 1.2).toFixed(2)}s" d="${d}"/>`); }
  const sil2 = (sg) => { const p = []; for (const z of [18, 112, 120, 128, 136, 143, 149, 154, 158]) { const [x, y] = at(c, 0, z0 + z * 0.86); p.push([x + sg * rr(z) * K, y]); } return k.pathOf(p); };
  o.push(`<path class="holo d" d="${sil2(1)}${sil2(-1)}"/>`);
  o.push(`<g class="m tarH"><path class="holoT" d="${k.ring(0, -c, 24, 20, P, 48)}"/></g>`); void yh;
  // çizim masası
  return o.join("");
}
function proto(y, ad, opt) {
  const c = C(y), o = [];
  o.push(golgeler([gKutu(c - 25, -23, 50, 8, 0, 30, 0)]), iskele(c, 0, opt.ust, false));
  o.push(kutu(c - 20, -20, 40, 40, 0, 3, { tone: "mid" }, 4), golgeler([gSil(c, 0, 18, 3, 20, 3)]));
  for (const [a, b] of [[12, -12], [-12, -12], [12, 12], [-12, 12]]) o.push(direkY(c + a, b, 3, 9, 3));
  o.push(iskelet(c, 0, 7, ad, opt), iskele(c, 0, opt.ust, true));
  if (opt.kol) { const [ka, kz] = opt.kol, hx = c + ka, ht = Math.sqrt(Math.max(0, R * R - ka * ka)) + 2, bs = c + 25, bt = 24; o.push(golgeler([gSil(bs, bt, 6, 0, 10, 0)]), sil(bs, bt, 6, 0, 4, { tone: "hi", crease: "lo" }, 28), mt("turuncu", sil(bs, bt, 4.4, 4, 5, { tone: "hi" }, 24)), kablo([[bs, bt, 8], [bs + 4, bt, 8 + (kz + 7) * 0.62]], 2.3, "kolT", 2), kablo([[bs + 4, bt, 8 + (kz + 7) * 0.62], [hx + 12, ht + 6, kz + 18]], 1.8, "kolT", 2), kablo([[hx + 12, ht + 6, kz + 18], [hx + 3, ht + 1, kz + 8]], 1, "", 2)); for (const q of [[bs + 4, bt, 8 + (kz + 7) * 0.62, 3], [hx + 12, ht + 6, kz + 18, 2.4]]) o.push(mt("krom", S(G.sphereOf(w(q[0], q[1], q[2]), q[3], P), { tone: "hi" }))); }
  if (opt.kay) opt.kay.forEach(([a, z, g]) => { const [x, yy] = at(c + a, Math.sqrt(Math.max(0, R * R - a * a)), 7 + z); o.push(kaynak(x, yy, g)); });
  return o.join("");
}
// WORKING: ateşleme standı
function working() {
  const c = C(4), o = [], z0 = 48, SZ = 42;
  o.push(golgeler([gKutu(c - 24, -22, 48, 44, 40, 8, 0)]));
  o.push(sil(c, 0, 24, 0, 2, { tone: "mid" }, 56), dolu(k.ring(0, -c, 19, 2.05, P, 48), "cukur"), dolu(k.ring(0, -c, 14, 2.1, P, 48), "cukurI"));
  const ayak = (a, b) => direkY(c + a, b, 0, SZ, 5) + mt("pirinc", sil(c + a, b, 3.6, 0, 2, {}, 14));
  o.push(ayak(22, -20), ayak(-22, -20), L(poli([[c - 22, -20, 4], [c + 22, -20, 38]]) + poli([[c + 22, -20, 4], [c - 22, -20, 38]]), { tone: "lo" }));
  const [fx, fy] = at(c, 0, z0 + 1);
  o.push(duman(fx, fy + 38 * K, [[-92, -20, 13, 0, 2.6], [-70, -44, 16, -0.6, 2.8], [-104, -2, 11, -1.3, 2.4], [-58, -24, 14, -1.9, 2.7], [88, -24, 13, -0.3, 2.6], [70, -50, 16, -0.9, 2.9], [104, -6, 11, -1.6, 2.4], [58, -28, 14, -2.1, 2.7], [-84, -62, 15, -2.4, 3], [82, -66, 15, -0.1, 3]]));
  o.push(`<g transform="translate(${fx.toFixed(1)} ${fy.toFixed(1)}) scale(${K.toFixed(2)})"><circle class="m alevH" r="46" cy="26" fill="url(#hale)"/><path class="m alev a1" d="M-8.4 -1C-12 12 -11 24 -13 34C-18 38 -24 39 -27 42C-18 44 18 44 27 42C24 39 18 38 13 34C11 24 12 12 8.4 -1Z"/><path class="m alev a2" d="M-6.4 -1C-8.8 11 -7.4 22 -8 32C-11 36 -15 37.4 -17 40C-10 41.6 10 41.6 17 40C15 37.4 11 36 8 32C7.4 22 8.8 11 6.4 -1Z"/><path class="m alev a3" d="M-4 -1C-5.4 8 -4 18 -3.4 28C-5 33 -7 35 -8 38C-4 39.4 4 39.4 8 38C7 35 5 33 3.4 28C4 18 5.4 8 4 -1Z"/><path class="sok" d="M-2.6 6L0 9L2.6 6L0 3ZM-2.2 14L0 17L2.2 14L0 11ZM-1.8 22L0 24.6L1.8 22L0 19.4Z"/></g>`);
  o.push(lule(c, 0, z0));
  o.push(S(k.slabOf(plan(c - 26, -24, 52, 48, 3), SZ, 5, P, 4, 0.4), { tone: "hi", crease: "lo", inner: dikis(c - 26, -24, 52, 48, [SZ + 2.4], 3) }));
  o.push(dolu(k.ring(0, -c, 17, SZ + 5.05, P, 48), "cukur"));
  o.push(tup(c, 0, z0 + 2, z0 + 10, R - 1.6, "celik"), kanatlar(c, 0, z0 - 2, "acik", false));
  o.push(tup(c, 0, z0 + 10, z0 + 70, R, "acik", { inner: L([22, 34, 46, 58].map((z) => k.sideArc(0, -c, R, z0 + z, P, 40)).join(""), { tone: "faint" }) }), silG(c, 0, z0 + 10, z0 + 70));
  // sökük panel: içi görünüyor
  const pc = poli([0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => { const q = Math.PI / 2 - 0.15 + (i / 8) * 1.1; return [c + Math.cos(q) * R, Math.sin(q) * R, z0 + 44]; }).concat([8, 7, 6, 5, 4, 3, 2, 1, 0].map((i) => { const q = Math.PI / 2 - 0.15 + (i / 8) * 1.1; return [c + Math.cos(q) * R, Math.sin(q) * R, z0 + 22]; })), true);
  o.push(dolu(pc, "agiz"), kes(pc, kablo([[c - 12, 12, z0 + 24], [c - 8, 13, z0 + 34], [c - 11, 12, z0 + 44]], 0.8, "hava", 3), kablo([[c - 6, 13, z0 + 20], [c - 4, 14, z0 + 36], [c - 8, 13, z0 + 48]], 0.8, "ptfe", 3), `<path class="m led acik bl1" d="${daire(c - 6, 14, z0 + 28, 1)}"/><path class="m led acik bl2" d="${daire(c - 6, 14, z0 + 32, 1)}"/>`), L(pc, { tone: "hi" }));
  // açık tepe: elektronik bölümü
  o.push(dolu(k.ring(0, -c, R - 1.2, z0 + 70.05, P, 48), "agiz"), L(k.ring(0, -c, R - 1.2, z0 + 70, P, 48), { tone: "lo" }), mt("pirinc", sil(c, 0, 5, z0 + 67, 8, { tone: "hi" }, 28)), mt("krom", sil(c - 7, 3, 2, z0 + 68, 6, { tone: "hi" }, 14), sil(c + 7, 2, 2, z0 + 68, 5, { tone: "hi" }, 14)), ledUst(c, 0, z0 + 75, "acik", 1.2));
  o.push(amblem(c + 3, 0, z0 + 56, "VeriPilot", "w", 1));
  o.push(ayak(22, 20), ayak(-22, 20)); o.push(S(k.slabOf(plan(c - 26, 20, 52, 4, 0.6), SZ, 5, P, 2), { tone: "hi", crease: "lo" }), dolu([0, 1, 2, 3, 4, 5].map((i) => poli([[c - 24 + i * 8.4, 24, SZ], [c - 20 + i * 8.4, 24, SZ], [c - 17 + i * 8.4, 24, SZ + 5], [c - 21 + i * 8.4, 24, SZ + 5]], true)).join(""), "ikaz2"));
  o.push(kanatlar(c, 0, z0 - 2, "acik", true));
  return o.join("");
}
// BUILT: ışıklı hangar
function hangarArka() {
  const s0 = 5 * EN + 2, s1 = 7 * EN - 2, t = -44, o = [];
  o.push(golgeler([gKutu(s0, t - 2, s1 - s0, 4, 0, 120, 0)]));
  o.push(S(k.slabOf(plan(s0, t - 3, s1 - s0, 3, 0.4), 0, 172, P, 2), { tone: "mid" }), dolu(poli([[s0 + 2, t, 0], [s1 - 2, t, 0], [s1 - 2, t, 170], [s0 + 2, t, 170]], true), "hangar"));
  const d = []; for (let s = s0 + 12; s < s1; s += 12) d.push(poli([[s, t, 0], [s, t, 172]])); for (const z of [40, 84, 128]) d.push(poli([[s0, t, z], [s1, t, z]])); o.push(L(d.join(""), { tone: "faint" }));
  o.push(S(k.slabOf(plan(s1 - 2, t, 2, 62, 0.4), 0, 172, P, 2), { tone: "mid" }));
  for (const y of [5, 6]) o.push(`<ellipse cx="${at(C(y), t, 96)[0].toFixed(1)}" cy="${at(C(y), t, 96)[1].toFixed(1)}" rx="86" ry="150" fill="url(#hangI)"/>`);
  return o.join("");
}
function hangarUst() {
  const s0 = 5 * EN + 2, s1 = 7 * EN - 2, o = [];
  o.push(direkY(s0 + 2.4, 18, 0, 172, 4.4), S(k.slabOf(plan(s0 - 3, -50, s1 - s0 + 6, 72, 1), 172, 6, P, 3, 0.4), { tone: "hi", crease: "lo", inner: dikis(s0 - 3, -50, s1 - s0 + 6, 72, [174.4], 1) }));
  const d = []; for (let s = s0 + 8; s < s1; s += 14) d.push(poli([[s, -50, 178], [s, 22, 178]])); o.push(L(d.join(""), { tone: "faint", free: true }));
  o.push(dolu(poli([[s0 + 6, 22, 172.8], [s1 - 6, 22, 172.8], [s1 - 6, 22, 174.4], [s0 + 6, 22, 174.4]], true), "tup"), `<path class="tup g" d="${poli([[s0 + 6, 22, 173.6], [s1 - 6, 22, 173.6]])}"/>`);
  return o.join("");
}
function built(y, ad, ek) {
  const c = C(y), o = [];
  o.push(golgeler([gSil(c, 0, 20, 0, 8, 0)]), sil(c, 0, 22, 0, 3, { tone: "mid" }, 56, 0.4));
  for (const [a, b] of [[13, -13], [-13, -13], [13, 13], [-13, 13]].sort((m, n) => k.depthOf(w(m[0], m[1], 0), P) - k.depthOf(w(n[0], n[1], 0), P))) o.push(mt("pirinc", sil(c + a * 0.7, b * 0.7, 1.6, 3, 9, { crease: "none" }, 12)));
  o.push(raket(c, 0, 5, ad, { mat: "beyaz", ek }));
  // "uçuştan önce çıkar" kurdelesi
  const r0 = [c - R - 1, 8, 5 + 80], [rx, ry] = at(...r0); o.push(`<g transform="translate(${rx.toFixed(1)} ${ry.toFixed(1)})"><g class="m kurd"><path class="kurdele" d="M0 0L-5 1L-7 36L-3.5 32L0 36Z"/></g></g>`);
  return o.join("");
}
// REVIEW: rampa
function review() {
  const c = C(7), o = [];
  o.push(golgeler([gSil(c, 0, 30, 0, 10, 0), gKutu(c + 18, -34, 14, 14, 0, 120, 0)]));
  o.push(sil(c, 0, 30, 0, 6, { tone: "hi", crease: "lo" }, 72, 0.6), mt("turuncuK", sil(c, 0, 30.2, 2, 2, { crease: "none" }, 72)), sil(c, 0, 30, 4, 2, { tone: "hi", crease: "lo" }, 72), sil(c, 0, 25, 6, 6, { tone: "hi", crease: "lo" }, 64, 0.5), dolu(k.ring(0, -c, 25, 12.05, P, 64), "parlaR"), halka(c, 0, 21, 12, { tone: "lo" }, 48), D(G.dotsOf(ZA(c, 0, 0), 12, 23, 24, P, { all: true }), { size: 0.8 }));
  // kule
  o.push(kafes(c + 24, -26, 0, 154, 13, 14)); o.push(kutu(c + 16, -34, 16, 16, 154, 2, { tone: "hi" }, 0.6), sil(c + 24, -26, 0.8, 156, 14, { crease: "none" }, 8));
  const [bx, by] = at(c + 24, -26, 171); o.push(`<circle class="hale m fener" cx="${bx.toFixed(1)}" cy="${by.toFixed(1)}" r="26"/><circle class="m fener" cx="${bx.toFixed(1)}" cy="${by.toFixed(1)}" r="4" fill="#ff9a62"/>`);
  for (const z of [64, 118]) o.push(kutu(c + 12, -22, 14, 5, z, 5, { tone: "hi", crease: "lo" }, 0.6), kutu(c + 15, -18, 9, 12, z + 0.6, 3.6, { tone: "mid" }, 0.6));
  for (const z of [28, 56, 84, 112, 140]) o.push(kutu(c + 16.4, -33.6, 15, 15, z, 1.4, { tone: "mid" }, 0.4));
  // buhar (arkada)
  const [vx, vy] = at(c - 4, 6, 16);
  o.push(raket(c, 0, 14, "KESEN", { mat: "beyaz", ek: "turuncu" }));
  for (const [a, b] of [[-17, 12], [15, 14]]) o.push(kutu(c + a - 2, b - 2, 4, 4, 12, 13, { tone: "hi", crease: "lo" }, 0.6), mt("pirinc", kutu(c + a * 0.86 - 1.4, b * 0.8 - 1.4, 2.8, 2.8, 23, 2.4, {}, 0.4)));
  o.push(duman(vx, vy, [[-44, -14, 7, 0, 4], [-60, -4, 9, -1.1, 4.4], [-36, -26, 6, -2.2, 4], [40, -16, 7, -0.6, 4.2], [58, -4, 9, -1.8, 4.4], [34, -30, 6, -3, 4]], "buh"));
  // tahliye: gövdeden yana
  const [ex, ey] = at(c - R, 4, 14 + 92); o.push(duman(ex, ey, [[-40, -8, 3.4, 0, 3], [-48, 2, 4, -0.9, 3.2], [-34, -16, 3, -1.8, 3]], "buh"));
  // geri sayım tabelası
  const ts = c - 30, tt = 24; o.push(direkY(ts + 5, tt, 0, 30, 2.4), direkY(ts + 25, tt, 0, 30, 2.4), S(k.slabOf(plan(ts, tt - 1, 30, 3, 0.6), 24, 19, P, 2), { tone: "hi", crease: "lo" }), dolu(onC(ts + 1.4, ts + 28.6, 25.4, 41.6, tt + 2, 0.6), "ekr"), `<g class="say">${yaziOn(ts + 15, tt + 2, 34, "T-10", { size: 7.4, anchor: "middle" })}</g><g class="say h m fener">${yaziOn(ts + 15, tt + 2, 27.4, "HOLD", { size: 5.4, anchor: "middle" })}</g>`);
  return o.join("");
}
// LIVE: boş rampa, gökyüzünü dinleyen çanak
function live() {
  const c = C(8), o = [];
  o.push(golgeler([gSil(c, 0, 27, 0, 4, 0), gSil(c + 8, -22, 8, 0, 34, 0)]));
  o.push(sil(c, 0, 27, 0, 4, { tone: "mid" }, 72, 0.5), halka(c, 0, 23, 4, { tone: "lo" }, 56), `<path class="bos m" d="${k.ring(0, -c, 16, 4, P, 48)}"/>`, L(poli([[c - 23, 0, 4], [c + 23, 0, 4]]) + poli([[c, -23, 4], [c, 23, 4]]), { tone: "faint" }));
  for (let i = 0; i < 4; i++) { const q = (i / 4) * TAU + 0.6; o.push(mt("pirinc", sil(c + Math.cos(q) * 20, Math.sin(q) * 20, 1.2, 4, 4, { crease: "none" }, 10))); }
  o.push(dolu(k.ring(0, -c, 12, 4.05, P, 40), "holoZ t"));
  // çanak
  const ds = c + 12, dt = -36; o.push(sil(ds, dt, 8, 0, 14, { tone: "hi", crease: "lo" }, 32, 0.4), sil(ds, dt, 2.4, 14, 14, { tone: "mid", crease: "none" }, 16));
  const [x, y] = at(ds, dt, 36); o.push(`<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(-24)"><g class="m canak"><path class="cnk" d="M-34 -8A34 34 0 0 0 34 -8A34 10 0 0 1 -34 -8Z"/><ellipse class="cnkI" cx="0" cy="-8" rx="34" ry="9.4"/><path class="cnkC" d="M-20 -8L0 -34L20 -8M0 -6L0 -34"/><circle cx="0" cy="-35" r="3" fill="#F47735"/></g></g>`);
  return o.join("");
}
// KESEN'den yörüngeye: henüz uçulmamış rota
function rota() {
  const [x0, y0] = at(C(7), 0, 180), [x1, y1] = yor(YQ);
  return `<path class="rota m" d="M${x0.toFixed(1)} ${y0.toFixed(1)}Q${(x0 + 3).toFixed(1)} ${(y0 - 46).toFixed(1)} ${(x1 + 20).toFixed(1)} ${(y1 + 34).toFixed(1)}"/>`;
}
// vinç: burnu VeriPilot'a taşıyor
function vincArka() {
  const o = [golgeler([60, 308].map((s) => gKutu(s - 3, -49, 6, 6, 0, 70, 0)))];
  for (const s of [308, 60]) o.push(kafes(s, -46, 0, 188, 9, 14), kiris(s - 3, -46, 6, 52, 188, 6));
  return o.join("");
}
function vinc() {
  const o = [S(k.slabOf(plan(52, -4, 264, 8, 0.6), 194, 8, P, 2, 0.4), { tone: "hi", crease: "lo", inner: dikis(52, -4, 264, 8, [196.4, 199.6], 0.6) })];
  let st = ""; for (let i = 0; i < 18; i++) { const s = 56 + i * 14.6; st += poli([[s, 4, 196.4], [s + 7, 4, 196.4], [s + 9, 4, 199.6], [s + 2, 4, 199.6]], true); } o.push(dolu(st, "ikaz2"));
  const c = C(4), g = [];
  g.push(S(k.slabOf(plan(c - 10, -7, 20, 14, 1), 188, 18, P, 3, 0.4), { tone: "hi", crease: "lo", inner: dikis(c - 10, -7, 20, 14, [192, 203], 1) }), mt("pirinc", S(G.disc(0, 2, 5, X(c, 7, 197), P), { tone: "hi" })), `<g class="mt-pirinc"><g transform="${onM(c, 9, 197)}"><g class="m don"><path class="dc2" d="M0 -4V4M-4 0H4"/></g></g></g>`);
  const [x0, y0] = at(c, 0, 188), [, y1] = at(c, 0, 178); g.push(`<path class="halat" d="M${x0.toFixed(1)} ${y0.toFixed(1)}V${y1.toFixed(1)}"/>`, mt("pirinc", sil(c, 0, 1.6, 174, 4, {}, 14)));
  g.push(`<path class="halat" d="${poli([[c, 0, 174], [c - 10, 3, 140]])}${poli([[c, 0, 174], [c + 10, 3, 140]])}"/>`);
  g.push(burun(c, 0, 128, 42, R, "turuncu"), mt("celik", sil(c, 0, R + 0.2, 126, 3, { tone: "hi", crease: "none" }, 56)));
  o.push(`<g class="m vinc">${g.join("")}</g>`);
  return o.join("");
}
// kontrol binası ve yakıt küreleri (arka sıra)
function arkaTesis() {
  const o = [golgeler([gKutu(78, -74, 96, 20, 0, 24, 0), gSil(224, -62, 12, 0, 24, 0), gSil(254, -62, 12, 0, 24, 0), gSil(520, -62, 10, 0, 30, 0)])];
  o.push(S(k.slabOf(plan(78, -74, 96, 20, 1), 0, 24, P, 3, 0.4), { tone: "hi", crease: "lo", inner: dikis(78, -74, 96, 20, [4, 20], 1) }));
  for (let i = 0; i < 9; i++) o.push(dolu(onC(82 + i * 10, 90 + i * 10, 8, 16, -54, 0.5), i % 4 === 2 ? "lumba sonuk" : "lumba m cam"));
  o.push(kutu(96, -70, 30, 12, 24, 8, { tone: "mid" }, 0.8), sil(150, -64, 0.7, 24, 22, { crease: "none" }, 8), sil(158, -66, 0.7, 24, 14, { crease: "none" }, 8));
  for (const s of [254, 224]) { for (const [a, b] of [[8, -8], [-8, -8], [8, 8], [-8, 8]]) o.push(direkY(s + a, -62 + b, 0, 14, 2)); o.push(mt("acik", S(G.sphereOf(w(s, -62, 20), 12, P), { tone: "hi", inner: L(G.arcOf(ZA(s, -62, 0), 20, 12, P), { tone: "lo" }) }))); }
  o.push(kablo([[236, -50, 3], [300, -50, 3], [300, -34, 3], [C(4) + 22, -34, 3]], 1.2, "ptfe", 5));
  o.push(kablo([[440, -54, 3], [480, -54, 3], [480, -30, 3], [C(7) + 26, -30, 3]], 1.2, "hava", 5));
  // projektör direkleri
  for (const [s, yon] of [[436, 1], [500, -1]]) { o.push(direkY(s, -60, 0, 92, 3), S(k.slabOf(plan(s - 8, -62, 16, 3, 0.6), 92, 11, P, 2), { tone: "hi", crease: "lo" })); for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) o.push(dolu(daire(s - 3.8 + i * 7.6, -59, 95 + j * 5.2, 2), "prj")); const [x, y] = at(s, -59, 97); o.push(`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="40" fill="url(#prjH)"/>`); void yon; }
  return o.join("");
}
function drone() {
  const [x, y] = at(C(8) + 2, 6, 118);
  return `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)})"><g class="m drone"><path class="drI" d="M0 6L-34 92H34Z"/><path class="drK" d="M-22 -2H22M-22 -2V-7M22 -2V-7"/><path class="drG" d="M-9 -5H9L7 6H-7Z"/><circle class="m fener" cx="0" cy="3" r="2.2" fill="#F47735"/><ellipse class="drP m" cx="-22" cy="-8" rx="13" ry="2.4"/><ellipse class="drP m" cx="22" cy="-8" rx="13" ry="2.4"/></g></g>`;
}
// tırtıl araç: parça taşıyarak bütün hattı geçer
function arac() {
  const s = 0, t = 48, g = [];
  g.push(golgeler([gKutu(s - 17, t - 9, 34, 18, 0, 14, 0)]));
  for (const tt of [t - 8.5, t + 4.5]) g.push(mt("kaucuk", S(G.prismOf(X(s, tt, 4), G.stadium(3.8, 3.8, 24, 18).map(([x, y]) => [x - 12, y]), 0, 4, P), { tone: "hi" })));
  for (const a of [-12, -4, 4, 12]) g.push(L(daire(s + a, t + 8.5, 4, 2.4), { tone: "mid" }), dolu(daire(s + a, t + 8.5, 4, 0.9), "led bekle"));
  g.push(S(k.slabOf(plan(s - 17, t - 9, 34, 18, 1.4), 7, 4, P, 3, 0.4), { tone: "hi", crease: "lo" }), mt("turuncuK", S(k.slabOf(plan(s + 8, t - 7, 9, 14, 1), 11, 9, P, 3, 0.4), { tone: "hi", crease: "lo" })), dolu(onC(s + 9.4, s + 15.6, 14, 18.6, t + 7, 0.6), "lumba"));
  g.push(mt("acik", S(G.disc(0, 22, 7, SA(s - 15, t, 18), P), { tone: "hi", inner: L([4, 11, 18].map((z) => G.arcOf(SA(s - 15, t, 18), z, 7, P)).join(""), { tone: "lo" }) })), mt("krom", S(G.disc(-0.4, 0, 5.4, SA(s - 15, t, 18), P), { tone: "hi" })));
  const [bx, by] = at(s + 12.5, t, 22); g.push(`<circle class="hale m fener" cx="${bx.toFixed(1)}" cy="${by.toFixed(1)}" r="13"/><circle class="m fener" cx="${bx.toFixed(1)}" cy="${by.toFixed(1)}" r="2.4" fill="#ffb07e"/>`);
  const a = [-2, 558].map((q) => at(q, 64, 0)[0]); return kes(`M${a[0].toFixed(1)} 0H${a[1].toFixed(1)}V${H}H${a[0].toFixed(1)}Z`, `<g class="m arac">${g.join("")}</g>`);
}
function tuneller() {
  const o = [];
  for (const s of [-20, 556]) { o.push(S(k.slabOf(plan(s, 35, 22, 29, 1.4), 0, 34, P, 3, 0.5), { tone: "hi", crease: "lo", inner: dikis(s, 35, 22, 29, [8, 28], 1.4) })); o.push(dolu([0, 1, 2].map((i) => poli([[s + 2 + i * 6.6, 64, 28.6], [s + 5.4 + i * 6.6, 64, 28.6], [s + 7.4 + i * 6.6, 64, 33], [s + 4 + i * 6.6, 64, 33]], true)).join(""), "ikaz2")); for (let i = 0; i < 4; i++) o.push(L(onC(s + 4, s + 18, 10 + i * 4, 12 + i * 4, 64, 0.6), { tone: "lo" })); }
  o.push(dolu(poli([[556, 38, 1], [556, 61, 1], [556, 61, 26], [556, 38, 26]], true), "cukur"));
  return o.join("");
}
function esya() {
  const o = [];
  // çelik halka yığını, variller, kablo
  const var1 = (s, t, mat) => o.push(golgeler([gSil(s, t, 4, 0, 10, 0)]), mt(mat, sil(s, t, 4, 0, 11, { tone: "hi", crease: "lo", inner: L(k.sideArc(t, -s, 4, 3.6, P, 18) + k.sideArc(t, -s, 4, 7.4, P, 18), { tone: "lo" }) }, 28)));
  var1(250, 30, "turuncuK"); var1(242, 33, "acik"); var1(246, 26, "celik");
  o.push(golgeler([gKutu(116, 24, 14, 9, 0, 8, 0), gKutu(176, 25, 14, 9, 0, 8, 0)]));
  for (const s of [116, 180]) o.push(S(k.slabOf(plan(s, 25, 14, 8, 0.8), 0, 8, P, 2, 0.3), { tone: "hi", crease: "lo", inner: dikis(s, 25, 14, 8, [5], 0.8) }), mt("pirinc", kutu(s + 5, 33, 4, 0.8, 4.4, 1.4, {}, 0.2)));
  o.push(guv(C(8) - 16, 22, 4));
  return o.join("");
}
// güvercin
function guv(s, t, z) { const [x, y] = at(s, t, z); return `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) scale(1.25)"><path class="ayakk" d="M-2 -6V0M2 -6V0M-4.4 0H-1M-.4 0H3"/><path class="gvd" d="M-9 -17C-7 -19 -3 -17 -1.4 -14C4 -14 10 -11 17 -7C14 -4 6 -3 1 -4.4C-5 -5 -8.4 -10 -9 -17Z"/><path class="kanat" d="M-1 -12C4 -13 10 -9 15 -6.6C9 -5 2 -6 -1 -12Z"/><g class="m bas2"><circle class="gvd" cx="-8.6" cy="-18.6" r="4"/><path class="gaga" d="M-12 -19.4L-16 -17.6L-12 -16.8Z"/><circle class="goz" cx="-9.8" cy="-19.6" r=".9"/></g></g>`; }

// ── kart ─────────────────────────────────────────────────────────────────────
const SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif";
const mal = (ad, top, s0, s1, s2, s3, hi, mid, lo, faint) => `.mt-${ad}{--anatomy-paper:${s2};--anatomy-top:${top};--anatomy-shade-0:${s0};--anatomy-shade-1:${s1};--anatomy-shade-2:${s2};--anatomy-shade-3:${s3};--anatomy-hi:${hi};--anatomy-mid:${mid};--anatomy-lo:${lo};--anatomy-faint:${faint}}`;
const CSS = `
.iso{--anatomy-paper:#141f34;--anatomy-face:#1a2740;--anatomy-top:#26375a;
--anatomy-shade-0:#0c1424;--anatomy-shade-1:#111b2e;--anatomy-shade-2:#172339;--anatomy-shade-3:#1c2a45;
--anatomy-hi:#b9c4da;--anatomy-mid:#7c8aa8;--anatomy-lo:#4c5c7e;--anatomy-faint:#34446a;--anatomy-lit:#F47735;
--anatomy-halo:#02050b;--anatomy-dot:#e9e4dc;--anatomy-weight:.7px;--anatomy-mono:${MONO}}
${mal("zemin", "#101a2d", "#080e1a", "#0a1120", "#0c1526", "#0e182b", "#6a7896", "#4a5876", "#33415f", "#1d2a44")}
${mal("acik", "#5f7399", "#22304c", "#2b3b5b", "#384a70", "#46598a", "#e8e6e2", "#a9b6cf", "#8294b8", "#6f83ab")}
${mal("krem", "#efe8da", "#8c857a", "#a9a194", "#c6beb0", "#ddd5c6", "#fffaf0", "#5f5a52", "#8a8378", "#a79f92")}
${mal("levha", "#fffaf0", "#d6cebf", "#dcd4c6", "#e6dfd1", "#f0eadd", "#fffaf0", "#5f5a52", "#8a8378", "#a79f92")}
${mal("levhaT", "#ffb07e", "#F47735", "#f5803f", "#f78c50", "#ff9a62", "#ffd9c0", "#8a3d17", "#8a3d17", "#c85f27")}
${mal("pirinc", "#d8ac62", "#4c3820", "#6b5029", "#8d6b38", "#b08848", "#ffe0a3", "#e2bd7b", "#7a5c31", "#9c7a44")}
${mal("krom", "#c9d4e6", "#1f2b45", "#41537a", "#7386ab", "#a4b3cd", "#ffffff", "#cdd7e8", "#42537a", "#8292b3")}
${mal("kaucuk", "#1a2233", "#070b13", "#0a0f19", "#0e1522", "#121a2a", "#56637f", "#48557a", "#2b364d", "#222c41")}
${mal("celik", "#3a4c70", "#131d31", "#1a273f", "#223150", "#2b3c60", "#93a2c0", "#73829f", "#4c5c7e", "#3a4a6c")}
${mal("kumas", "#7d8fb6", "#2c3a5a", "#3a4b72", "#4c5f8c", "#6074a3", "#f3efe7", "#c3cde0", "#93a4c6", "#8294b8")}
${mal("turuncu", "#ff8a45", "#7d3513", "#a1481b", "#c85f27", "#e6702f", "#ffd0ad", "#ffb07e", "#8a3d17", "#b4541f")}
${mal("turuncuK", "#8c431f", "#34190f", "#472213", "#5f2e17", "#75391b", "#ffa06a", "#d9713a", "#a8532a", "#6d351a")}
${mal("kartus", "#3b2b2c", "#1a1216", "#241a1e", "#2f2226", "#38292c", "#F47735", "#F47735", "#a8532a", "#5d3a2e")}
${mal("kirmizi", "#ff6a4d", "#6e1f14", "#8f2a1c", "#b63a27", "#d94a33", "#ffc2b5", "#ff9a86", "#8f2a1c", "#b63a27")}
${mal("guv", "#f6f3ec", "#9aa0ad", "#b5bac4", "#d0d2d6", "#e6e4df", "#ffffff", "#8a90a0", "#9aa0ad", "#b5bac4")}
${mal("mavi", "#6f93c9", "#22375e", "#2f4b7c", "#3f629c", "#5079b4", "#d6e4fb", "#a9c3ea", "#5f83bd", "#4a6ba3")}
${mal("beyaz", "#f7f2e8", "#a39d92", "#bcb6aa", "#d6d0c4", "#ece6da", "#fffdf8", "#6d685f", "#97918a", "#b5afa4")}
.iso-svg path:not([class^="iso"]){vector-effect:none}
.iso-face-text{font-weight:700;letter-spacing:0}.iso-face-text[data-tone="lit"]{fill:#F47735}
.etk .iso-face-text{fill:#e9e4dc}.etk.kara .iso-face-text{fill:#14100c}.acik2 .iso-face-text{fill:#93a2c0;font-weight:500}
.say .iso-face-text{fill:#ffd58a}.say.h .iso-face-text{fill:#F47735}
.golge{fill:#01040a;opacity:.4}
.yildiz{fill:none;stroke:#e9e4dc;stroke-linecap:round;stroke-width:1.5px;opacity:.5}.yildiz.y1{stroke-width:2.2px}.yildiz.y2{stroke-width:1.8px}
.kita{fill:#2f4a7a;opacity:.75}.bulut{fill:none;stroke:#9fb4dc;stroke-width:5px;opacity:.16;stroke-linecap:round}
.yorA{fill:none;stroke:#F47735;stroke-width:1.2px;opacity:.28;stroke-dasharray:3 5}.yorO{fill:none;stroke:#F47735;stroke-width:1.6px;opacity:.8;stroke-dasharray:5 5}
.bosR{fill:#0A0F1C;fill-opacity:.6;stroke:#F47735;stroke-width:1.6px;stroke-dasharray:3 2.4;stroke-linejoin:round}
.rota{fill:none;stroke:#F47735;stroke-width:2px;stroke-dasharray:2 9;stroke-linecap:round;opacity:.9}
.tepe1{fill:#0e1830}.tepe2{fill:#0b1325}.uzakI{fill:none;stroke:#ffd58a;stroke-width:1.8px;stroke-linecap:round;opacity:.35}
.alan0{fill:#2c4070;fill-opacity:.16;stroke:#5d6c8c;stroke-width:1px;stroke-dasharray:6 4}.alan0.r{fill:#F47735;fill-opacity:.12;stroke:#F47735}.alan0.l{fill:none;stroke:#F47735;stroke-opacity:.5}
.yolZ{fill:#131d33}.travers{fill:#0b1222}.okz{fill:#F47735;opacity:.28}
.serit0,.serit1,.serit2,.serit3{fill:#4c5c7e}.serit4,.serit5{fill:#F47735}
.bosL{fill:none;stroke:#5d6c8c;stroke-width:1px;stroke-dasharray:4 3}
.dil{fill:#0a101d;stroke:#33446a;stroke-width:.8px}.dil.d{fill:#e6dfd1;stroke:none}.dil.s{fill:#73829f;stroke:none}.dil.t{fill:#F47735;stroke:none}
.sok{fill:#fff;opacity:.85}.yuvC{fill:none;stroke:#F47735;stroke-width:1px;opacity:.55}.amb.w{stroke:#f3efe7}.prj{fill:#fff6e2}.drK{fill:none;stroke:#b9c4da;stroke-width:2px;stroke-linecap:round}.drG{fill:#46598a;stroke:#e8e6e2;stroke-width:1px}.drP{fill:#b9c4da;opacity:.5}.drI{fill:url(#drI)}.kolT .kb0{stroke:#ffd0ad}.kolT .kb1{stroke:#c85f27}.kolT .kb2{stroke:#ff9a62}
.silG{fill:url(#silG)}.lic{fill:#0a0d14}.agiz{fill:#070b14}.cukur{fill:#05080f}.cukurI{fill:url(#kor)}.lumba{fill:#ffd58a}.lumba.sonuk{fill:#1c2a45}
.amb{fill:none;stroke:#2b3c60;stroke-width:1.1px;stroke-linecap:round;stroke-linejoin:round}.amb.t{stroke:#c8501c}.amb.k{stroke:#ffe0a3}.amb.s{stroke:#93a2c0}
.isk{fill:none;stroke:#b9c4da;stroke-width:1.7px;stroke-linejoin:round}.isk.a{stroke:#4c5c7e;stroke-width:1.2px}
.holoZ{fill:#7fd6f0;opacity:.28}.holoZ.t{fill:#F47735;opacity:.07}.holo{fill:none;stroke:#8fe3fa;stroke-width:1px;opacity:.65}.holo.d{stroke-width:1.5px;opacity:.95}.holo.k{opacity:0}.holoT{fill:none;stroke:#d8f7ff;stroke-width:1.6px;opacity:.7}
.kayH{fill:url(#kayG);opacity:0}.kayY{fill:#fff;opacity:0}.kiv{fill:#ffe0a3;opacity:0}
.dum{fill:#8d9bb8;opacity:0}.dum.buh{fill:#dfe6f2}
.a1{fill:#F47735}.a2{fill:#ffb347}.a3{fill:#fff6e2}.led{fill:#8fe0c0}.ledy{fill:#05080f}.led.bekle{fill:#F47735}
.ikaz2{fill:#F47735;opacity:.8}.hangar{fill:#0f182b}.kurdele{fill:#e6402a}
.tup{fill:#fff6e2}.tup.g{fill:none;stroke:#ffe9c4;stroke-width:13px;opacity:.14;stroke-linecap:round}
.parlaR{fill:url(#korR)}.hale{fill:url(#hale)}.ekr{fill:#060d18}
.bos{fill:none;stroke:#F47735;stroke-width:1.6px;stroke-dasharray:5 4}
.cnk{fill:#46598a;stroke:#e8e6e2;stroke-width:1px}.cnkI{fill:#8294b8;stroke:#e8e6e2;stroke-width:1px}.cnkC{fill:none;stroke:#e8e6e2;stroke-width:1.2px}
.halat{fill:none;stroke:#b9c4da;stroke-width:1.2px}.dc2{stroke:#3a2d1e;stroke-width:1px;fill:none}
.kb0,.kb1,.kb2{fill:none;stroke-linecap:round;stroke-linejoin:round}.kb0{stroke:#5d6c8c}.kb1{stroke:#0b111d}.kb2{stroke:#33425f}.hava .kb0{stroke:#7f98bd}.hava .kb1{stroke:#23406b}.hava .kb2{stroke:#6f9ad0}.ptfe .kb0{stroke:#b9b2a5}.ptfe .kb1{stroke:#6d6a66}.ptfe .kb2{stroke:#d8d2c6}
.gvd{fill:#f1ede4;stroke:#fff;stroke-width:.8px}.kanat{fill:#c9ccd4;stroke:#8a90a0;stroke-width:.7px}.gaga{fill:#F47735}.goz{fill:#14100c}.ayakk{fill:none;stroke:#F47735;stroke-width:1.2px}
.m{transform-box:view-box}
.don{transform-origin:0 0;animation:don 5s linear infinite}
.y1{animation:goz 3.6s ease-in-out infinite}.y2{animation:goz 5s ease-in-out -2s infinite}
.isl{transform-origin:0 0;animation:isl 11s ease-in-out infinite alternate}
.holo.k{animation:kare 1.2s steps(1) infinite}.tarH{animation:tarH 3.4s ease-in-out infinite alternate}
.kayH,.kayY{animation:kayn 2.6s linear infinite}.kiv{animation:kiv 2.6s ease-in infinite}
.alev{transform-origin:0 0;animation:alev .22s ease-in-out infinite alternate}.a2{animation-duration:.17s}.a3{animation-duration:.13s}.alevH{animation:alevH .3s ease-in-out infinite alternate}
.dum{transform-origin:0 0;animation:dum 2.6s ease-out infinite}
.fener{animation:fener 2s ease-in-out infinite}.ucD{animation:fener 2.4s ease-in-out infinite}.bl1{animation:fener 1.1s steps(1) infinite}.bl2{animation:fener 1.7s steps(1) infinite}
.vinc{animation:vinc 16s cubic-bezier(.45,0,.3,1) infinite}.arac{animation:arac 26s linear infinite}
.drone{animation:drone 7s ease-in-out infinite alternate}.drP{animation:fener .18s linear infinite}.cam{animation:cam 9s steps(1) infinite}
.kurd{transform-origin:0 0;animation:kurd 2.4s ease-in-out infinite alternate}.canak{transform-origin:0 0;animation:canak 8s ease-in-out infinite alternate}
.rota{animation:rota 1.6s linear infinite}.yuva0{animation:bosa 2.6s ease-in-out infinite}.bos{animation:bosa 2.6s ease-in-out infinite}.bas2{animation:basg 5s ease-in-out infinite}
@keyframes drone{0%{transform:translate(-26px,8px)}50%{transform:translate(6px,-8px)}100%{transform:translate(30px,6px)}}
@keyframes cam{0%,100%{opacity:1}}
@keyframes don{to{transform:rotate(360deg)}}
@keyframes goz{0%,100%{opacity:.6}50%{opacity:.12}}
@keyframes isl{from{transform:rotate(-24deg)}to{transform:rotate(20deg)}}
@keyframes kare{0%{opacity:.8}12.5%,100%{opacity:0}}
@keyframes tarH{from{transform:translateY(0)}to{transform:translateY(${(-128 * K * 0.92).toFixed(1)}px)}}
@keyframes kayn{0%,3%,6%,9%,13%,100%{opacity:0}1.5%,4.5%,7.5%,11%{opacity:1}}
@keyframes kiv{0%{opacity:0;transform:translate(0,0)}2%{opacity:1}22%{opacity:.9}30%,100%{opacity:0;transform:translate(var(--x),var(--y))}}
@keyframes alev{from{transform:scale(1,.9)}to{transform:scale(.94,1.1)}}
@keyframes alevH{from{opacity:.65}to{opacity:1}}
@keyframes dum{0%{opacity:0;transform:translate(0,0) scale(.4)}18%{opacity:.5}100%{opacity:0;transform:translate(var(--x),var(--y)) scale(2.1)}}
@keyframes fener{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes vinc{0%,8%{transform:translate(${kay(-190, 0, 0)})}46%,78%{transform:translate(0,0)}100%{transform:translate(${kay(-190, 0, 0)})}}
@keyframes arac{from{transform:translate(${kay(-24, 0, 0)})}to{transform:translate(${kay(590, 0, 0)})}}
@keyframes kurd{from{transform:rotate(-5deg)}to{transform:rotate(9deg)}}
@keyframes canak{from{transform:scaleX(1) rotate(-6deg)}to{transform:scaleX(.82) rotate(16deg)}}
@keyframes rota{from{stroke-dashoffset:22}to{stroke-dashoffset:0}}
@keyframes bosa{0%,100%{opacity:.35}50%{opacity:1}}
@keyframes basg{0%,62%,78%,100%{transform:translate(0,0)}68%{transform:translate(-1.4px,1.6px)}}
@media (max-width:520px){.iso{--anatomy-weight:.42px}}
@media (prefers-reduced-motion:reduce){.m{animation:none!important}.holo.k:first-of-type{opacity:.7}}
`;
const DEFS = `<defs>
<linearGradient id="gok" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#080d1a"/><stop offset=".5" stop-color="#101c38"/><stop offset=".72" stop-color="#0d1528"/><stop offset="1" stop-color="#0A0F1C"/></linearGradient>
<linearGradient id="silG" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#fff" stop-opacity=".1"/><stop offset=".26" stop-color="#fff" stop-opacity=".16"/><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#02050f" stop-opacity=".5"/></linearGradient>
<radialGradient id="gez" cx=".3" cy=".3" r=".85"><stop offset="0" stop-color="#3d5c96"/><stop offset=".5" stop-color="#1f3461"/><stop offset="1" stop-color="#0a1226"/></radialGradient>
<radialGradient id="gezG" cx=".24" cy=".24" r=".95"><stop offset=".45" stop-color="#050a17" stop-opacity="0"/><stop offset="1" stop-color="#050a17" stop-opacity=".88"/></radialGradient>
<radialGradient id="gezH"><stop offset=".5" stop-color="#5f8fe0" stop-opacity=".3"/><stop offset="1" stop-color="#5f8fe0" stop-opacity="0"/></radialGradient>
<linearGradient id="isl" x1="0" x2="0" y1="1" y2="0"><stop offset="0" stop-color="#cfe0ff" stop-opacity=".26"/><stop offset="1" stop-color="#cfe0ff" stop-opacity="0"/></linearGradient>
<linearGradient id="holo" x1="0" x2="0" y1="1" y2="0"><stop offset="0" stop-color="#7fd6f0" stop-opacity=".3"/><stop offset="1" stop-color="#7fd6f0" stop-opacity="0"/></linearGradient>
<radialGradient id="kayG"><stop offset="0" stop-color="#dff3ff" stop-opacity=".9"/><stop offset="1" stop-color="#8fd0ff" stop-opacity="0"/></radialGradient>
<radialGradient id="hale"><stop offset="0" stop-color="#F47735" stop-opacity=".6"/><stop offset="1" stop-color="#F47735" stop-opacity="0"/></radialGradient>
<radialGradient id="kor"><stop offset="0" stop-color="#ffd58a"/><stop offset=".5" stop-color="#F47735" stop-opacity=".8"/><stop offset="1" stop-color="#F47735" stop-opacity="0"/></radialGradient>
<radialGradient id="korR"><stop offset="0" stop-color="#F47735" stop-opacity=".5"/><stop offset="1" stop-color="#F47735" stop-opacity=".02"/></radialGradient>
<radialGradient id="prjH"><stop offset="0" stop-color="#fff1d6" stop-opacity=".5"/><stop offset="1" stop-color="#fff1d6" stop-opacity="0"/></radialGradient>
<linearGradient id="drI" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#cfe0ff" stop-opacity=".3"/><stop offset="1" stop-color="#cfe0ff" stop-opacity="0"/></linearGradient>
<radialGradient id="hangI"><stop offset="0" stop-color="#ffe9c4" stop-opacity=".3"/><stop offset="1" stop-color="#ffe9c4" stop-opacity="0"/></radialGradient>
</defs>`;
const kac = ({ y: [a, b] }) => PROJE.filter((p) => p.y >= a && p.y < b).length; void kac;
const etiket = "A rocket base at night: every project is a rocket at its true stage. A hologram at Idea; Odanda Gör, BİİİP and ZIP RUSH are bare frames at Prototype; VeriPilot fires its engine at Working without a nose; Pass and Veri Temizleyici stand finished in the Built hangar; KESEN holds at T-10 on the Review pad; Live is an empty orbit.";
const katman = [gok(), isildak(128, -70, 0, 11), isildak(470, -70, -5, 13), ufuk(), taban(), arkaTesis(), vincArka(), hangarArka(), rota(), live(), review(), built(6, "Veri", "mavi"), built(5, "Pass", "pirinc"), hangarUst(), working(), proto(3, "ZIP RUSH", { panel: 0, ust: 78, soluk: true, kay: [[-4, 42, -1.7]] }), proto(2, "BİİİP", { panel: 1, ust: 90, kol: [7, 72], kay: [[7, 72, 0], [-9, 30, -1.3]] }), proto(1, "Odanda Gör", { panel: 2, ust: 102, kol: [8, 84], kay: [[8, 84, -0.7], [-8, 42, -2]] }), idea(), vinc(), drone(), esya(), arac(), tuneller()].join("");
const svg = k.figureSvg({ width: W, height: H, label: etiket, standalone: "dark", body: [
  `<style>${CSS}</style>`, DEFS,
  `<clipPath id="kart"><rect width="${W}" height="${H}" rx="20"/></clipPath><g clip-path="url(#kart)"><rect width="${W}" height="${H}" fill="url(#gok)"/>${katman}</g>`,
  `<rect x=".5" y=".5" width="${W - 1}" height="${H - 1}" rx="20" fill="none" stroke="#1C2638"/>`,
  `<text x="52" y="62" font-family="${MONO}" font-size="18" letter-spacing="1" fill="#F47735">$ launch --status</text>`,
  `<text x="52" y="93" font-family="${SANS}" font-size="20" fill="#B6BDCC">Every project is a rocket. The more complete it looks, the closer it is.</text>`,
  `<text x="52" y="119" font-family="${SANS}" font-size="20" fill="#8C95A8">Nothing is in orbit yet — KESEN is on the pad.</text>`,
] });
writeFileSync(join(HERE, "..", "assets", "us.svg"), svg);
console.log("us.svg", Math.round(svg.length / 1024), "KB ·", (svg.match(/class="iso-solid/g) || []).length, "parça ·", (svg.match(/<path/g) || []).length, "yol · ölçek", K.toFixed(2));
