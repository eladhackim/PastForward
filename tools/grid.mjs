import fs from "fs";
import { feature } from "topojson-client";
import { geoNaturalEarth1, geoPath, geoContains, geoBounds, geoGraticule } from "d3-geo";

const topo = JSON.parse(fs.readFileSync(new URL("./node_modules/world-atlas/countries-50m.json", import.meta.url)));
const all = feature(topo, topo.objects.countries).features;
const countries = all.filter(f => f.id !== "010"); // drop Antarctica

const R = {
  u: [840],
  l: [484, 320, 84, 340, 222, 558, 188, 591, 192, 332, 214, 388, 630, 44, 780, 170, 862, 328, 740, 218, 604, 68, 76, 600, 152, 32, 858, 238, 52, 28, 659, 662, 670, 308, 533, 531, 535, 796, 92, 850, 660, 500, 312, 474, 652, 663, 534],
  e: [352, 578, 752, 246, 208, 826, 372, 250, 724, 620, 56, 528, 442, 276, 756, 40, 380, 616, 203, 703, 348, 705, 191, 70, 688, 499, 8, 807, 300, 100, 642, 498, 804, 112, 440, 428, 233, 196, 470, 492, 674, 336, 20, 438, 234, 831, 832, 833, 248],
  r: [643],
  m: [792, 760, 422, 376, 275, 400, 368, 364, 682, 414, 634, 784, 512, 887, 48, 818, 434, 788, 12, 504, 732],
  a: [478, 466, 562, 148, 729, 728, 232, 231, 262, 706, 686, 270, 624, 324, 694, 430, 384, 854, 288, 768, 204, 566, 120, 140, 226, 266, 178, 180, 800, 404, 646, 108, 834, 24, 894, 454, 508, 716, 72, 516, 710, 426, 748, 450, 132, 678, 174, 480, 690],
  i: [356, 586, 50, 524, 64, 144, 4, 462],
  c: [156, 158, 496, 408, 410, 392, 344, 446, 104, 764, 418, 116, 704, 458, 702, 360, 608, 96, 626]
};
const code = {};
for (const [k, ids] of Object.entries(R)) ids.forEach(n => { code[String(n).padStart(3, "0")] = k; });
function regionOf(f, lon, lat) {
  let k = code[f.id];
  const name = f.properties && f.properties.name;
  if (!k) {
    if (name === "Kosovo" || name === "N. Cyprus") k = "e";
    else if (name === "Somaliland") k = "a";
    else k = "o";
  }
  if (f.id === "250" && lon < -30) k = "l";              // French Guiana etc.
  if (f.id === "208" && lon < -10) k = "o";              // Greenland / Faroe handled as other
  if (f.id === "840" && lon < -140) k = "u";
  return k;
}

const land = { type: "FeatureCollection", features: countries };
const proj = geoNaturalEarth1().fitWidth(1400, land);
const [[x0, y0], [x1, y1]] = geoPath(proj).bounds(land);
const COLS = 150;
const cell = (x1 - x0) / COLS;
const ROWS = Math.ceil((y1 - y0) / cell);
const boxes = countries.map(f => ({ f, b: geoBounds(f) }));
const inBox = (b, lon, lat) => {
  const [[w, s], [e, n]] = b;
  if (lat < s || lat > n) return false;
  return w <= e ? lon >= w && lon <= e : lon >= w || lon <= e;
};
const rows = [];
const acc = {};
for (let r = 0; r < ROWS; r++) {
  let s = "";
  for (let c = 0; c < COLS; c++) {
    const x = x0 + (c + .5 + (r % 2 ? .5 : 0)) * cell, y = y0 + (r + .5) * cell;
    const ll = proj.invert([x, y]);
    let ch = ".";
    const back = ll && proj(ll);
    if (ll && isFinite(ll[0]) && Math.abs(ll[0]) <= 180 && back && Math.hypot(back[0] - x, back[1] - y) < .5) {
      const [lon, lat] = ll;
      for (const { f, b } of boxes) {
        if (!inBox(b, lon, lat)) continue;
        if (geoContains(f, ll)) { ch = regionOf(f, lon, lat); break; }
      }
      if (ch !== "." && ch !== "o") {
        if (!(ch === "u" && lon < -130)) { (acc[ch] = acc[ch] || [0, 0, 0]); acc[ch][0] += c; acc[ch][1] += r; acc[ch][2]++; }
      }
    }
    s += ch;
  }
  rows.push(s);
}
const cent = {};
for (const [k, [sx, sy, n]] of Object.entries(acc)) cent[k] = [+(sx / n).toFixed(1), +(sy / n).toFixed(1)];
const PINS = { u: [-98, 39], l: [-60, -12], e: [12, 50], r: [92, 60], m: [44, 28], a: [22, -2], i: [79, 22], c: [108, 33] };
const pins = {};
for (const [k, ll] of Object.entries(PINS)) { const [px, py] = proj(ll); pins[k] = [+((px - x0) / cell - .5).toFixed(2), +((py - y0) / cell - .5).toFixed(2)]; }
const toG = ([lon, lat]) => { const [px, py] = proj([lon, lat]); return [+((px - x0) / cell).toFixed(1), +((py - y0) / cell).toFixed(1)]; };
const lines = [];
for (let lon = -180; lon <= 180; lon += 30) { const pts = []; for (let lat = -60; lat <= 85; lat += 5) pts.push(toG([Math.max(-179.9, Math.min(179.9, lon)), lat])); lines.push({ k: lon === -180 || lon === 180 ? "edge" : "m", pts }); }
for (let lat = -60; lat <= 60; lat += 30) { const pts = []; for (let lon = -180; lon <= 180; lon += 5) pts.push(toG([Math.max(-179.9, Math.min(179.9, lon)), lat])); lines.push({ k: lat === 0 ? "eq" : "p", pts }); }
for (const lat of [23.44, -23.44]) { const pts = []; for (let lon = -180; lon <= 180; lon += 5) pts.push(toG([Math.max(-179.9, Math.min(179.9, lon)), lat])); lines.push({ k: "tropic", pts }); }
const out = { cols: COLS, rows: ROWS, grid: rows.join("\n"), pins, lines };
fs.writeFileSync(new URL("../data/map.json", import.meta.url), JSON.stringify(out));
console.log(rows.join("\n"));
console.log(COLS, ROWS, pins);
