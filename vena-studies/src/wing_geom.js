/* wing_geom.js v02 · Skillet Clubtail (Gomphurus ventricosus) wing outline and named venation
 * Source: C3-E1-A1 02_scripts/dragonfly_geom.py (constants, lerp) and dragonfly_geom_v02.py
 *         (wing_outline v02 petiolate, wing_veins_v2). Ported 2026-11-20.
 * Ported one way, do not edit upstream. Changes upstream are re-ported here, never the reverse.
 * Units mm. Wing-local frame: u along span from the hinge, v chord, v > 0 = leading (costal) side.
 * scale: multiplies every coordinate; 1.0 = source of record (forewing 30 mm, hindwing 28.5 mm).
 * The cell grid in wing_veins_v2 draws from Python random.Random(7); this file carries an MT19937
 * port so the numbers match a fresh Python process (one call per process). Each call here reseeds.
 */
(function (root) {
  'use strict';
  var FORE_L = 30.0, FORE_CH = 7.0, HIND_L = 28.5, HIND_CH = 9.5;
  var NODUS = 0.46, PTEROSTIGMA = [0.84, 0.92];
  function lerp(a, b, t) { return a + (b - a) * t; }

  /* MT19937, CPython random.random() compatible for an int seed */
  function MT(seed) {
    var mt = new Uint32Array(624), mti = 625;
    function initGen(s) { mt[0] = s >>> 0; for (mti = 1; mti < 624; mti++) { var p = mt[mti - 1] ^ (mt[mti - 1] >>> 30);
      mt[mti] = (((((p & 0xffff0000) >>> 16) * 1812433253) << 16) + (p & 0x0000ffff) * 1812433253 + mti) >>> 0; } }
    function initByArray(key) { initGen(19650218); var i = 1, j = 0, k = Math.max(624, key.length);
      for (; k; k--) { var p = mt[i - 1] ^ (mt[i - 1] >>> 30);
        mt[i] = ((mt[i] ^ (((((p & 0xffff0000) >>> 16) * 1664525) << 16) + ((p & 0x0000ffff) * 1664525))) + key[j] + j) >>> 0;
        i++; j++; if (i >= 624) { mt[0] = mt[623]; i = 1; } if (j >= key.length) j = 0; }
      for (k = 623; k; k--) { var q = mt[i - 1] ^ (mt[i - 1] >>> 30);
        mt[i] = ((mt[i] ^ (((((q & 0xffff0000) >>> 16) * 1566083941) << 16) + (q & 0x0000ffff) * 1566083941)) - i) >>> 0;
        i++; if (i >= 624) { mt[0] = mt[623]; i = 1; } }
      mt[0] = 0x80000000; }
    function genInt() { var y, kk, mag = [0, 0x9908b0df];
      if (mti >= 624) { for (kk = 0; kk < 624 - 397; kk++) { y = (mt[kk] & 0x80000000) | (mt[kk + 1] & 0x7fffffff); mt[kk] = mt[kk + 397] ^ (y >>> 1) ^ mag[y & 1]; }
        for (; kk < 623; kk++) { y = (mt[kk] & 0x80000000) | (mt[kk + 1] & 0x7fffffff); mt[kk] = mt[kk + (397 - 624)] ^ (y >>> 1) ^ mag[y & 1]; }
        y = (mt[623] & 0x80000000) | (mt[0] & 0x7fffffff); mt[623] = mt[396] ^ (y >>> 1) ^ mag[y & 1]; mti = 0; }
      y = mt[mti++]; y ^= (y >>> 11); y ^= (y << 7) & 0x9d2c5680; y ^= (y << 15) & 0xefc60000; y ^= (y >>> 18); return y >>> 0; }
    initByArray([seed >>> 0]);
    return function () { var a = genInt() >>> 5, b = genInt() >>> 6; return (a * 67108864.0 + b) * (1.0 / 9007199254740992.0); };
  }

  /* wing_outline v02: petiolate root. Returns [[u,v],...] lead (root to tip) then trail (tip to root). */
  function wingOutline(kind, n, scale) {
    kind = kind || 'fore'; n = n || 48; scale = scale == null ? 1.0 : scale;
    var fore = kind === 'fore';
    var L = fore ? FORE_L : HIND_L, C = fore ? FORE_CH : HIND_CH;
    var rootChord = fore ? 4.0 : 8.0, peak = fore ? 0.55 : 0.36;
    var lead = [], trail = [];
    for (var i = 0; i <= n; i++) {
      var t = i / n, u = t * L;
      var vl = 0.35 * Math.sin(Math.PI * t) - Math.pow(t, 6) * 1.2, c;
      if (t < peak) c = lerp(rootChord, C, Math.sin(0.5 * Math.PI * t / peak));
      else c = C * Math.pow(Math.cos(0.5 * Math.PI * (t - peak) / (1 - peak)), 0.85);
      var neck = fore ? 0.10 : 0.07;
      if (t < neck) c = lerp(fore ? 2.2 : 3.6, c, Math.pow(t / neck, 0.7));
      c = Math.max(c, 0.0);
      lead.push([u, vl]); trail.push([u, vl - c]);
    }
    var pts = lead.concat(trail.reverse());
    return scale === 1.0 ? pts : pts.map(function (p) { return [p[0] * scale, p[1] * scale]; });
  }

  function _at(p, u) {
    for (var i = 0; i < p.length - 1; i++) { var u0 = p[i][0], v0 = p[i][1], u1 = p[i + 1][0], v1 = p[i + 1][1];
      if (u0 <= u && u <= u1) return lerp(v0, v1, (u - u0) / (u1 - u0 + 1e-9)); }
    return null;
  }
  function or(a, b) { return a ? a : b; } /* Python `a or b` for numbers and None */

  /* wing_veins_v2: {name: [[u,v],...]}, 'cross': [[[u,v],[u,v]],...] */
  function wingVeins(kind, scale) {
    kind = kind || 'fore'; scale = scale == null ? 1.0 : scale;
    var RNG = MT(7);
    var hind = kind === 'hind';
    var L = hind ? HIND_L : FORE_L;
    var outline = wingOutline(kind, 96, 1.0), n = Math.floor(outline.length / 2);
    var lead = outline.slice(0, n), trail = outline.slice(n).reverse();
    function chordAt(t) { var i = Math.min(Math.max(Math.trunc(t * (n - 1)), 0), n - 1); return [lead[i][1], trail[i][1]]; }
    var V = {};
    function longit(name, t0, t1, f0, f1, curve, k) {
      curve = curve || 0.0; k = k || 33; var pts = [];
      for (var i = 0; i < k; i++) { var t = lerp(t0, t1, i / (k - 1)), tb = chordAt(t);
        var f = lerp(f0, f1, i / (k - 1)) + curve * Math.sin(Math.PI * i / (k - 1));
        pts.push([t * L, lerp(tb[0], tb[1], f)]); }
      V[name] = pts; return pts;
    }
    longit('C', 0.0, 1.0, 0.0, 0.0);
    longit('Sc', 0.0, NODUS, 0.075, 0.075);
    longit('R1', 0.0, 0.997, 0.13, 0.035);
    longit('R2', 0.30, 0.985, 0.19, 0.55, 0.01);
    longit('IR2', 0.52, 0.965, 0.245, 0.72, 0.0);
    longit('R3', 0.11, 0.935, 0.19, 0.86, 0.04);
    longit('IR3', 0.55, 0.90, 0.30, 0.90, 0.0);
    longit('R4+5', 0.12, 0.86, 0.26, 0.95, 0.06);
    longit('MA', 0.12, 0.80, 0.31, 0.97, 0.08);
    longit('MP', 0.10, hind ? 0.62 : 0.52, 0.42, 0.97, 0.05);
    longit('CuA', 0.09, hind ? 0.80 : 0.66, 0.55, 0.97, 0.04);
    longit('CuP', 0.07, hind ? 0.36 : 0.30, 0.66, 0.97, 0.0);
    longit('A1', 0.03, hind ? 0.45 : 0.24, 0.80, 0.97, 0.0);
    var r3 = _at(V['R3'], 0.12 * L);
    V['RM_stem'] = [[0, chordAt(0)[0] - 0.4], [0.12 * L, r3 !== null ? r3 : 0]];
    var t = 0.12, tb = chordAt(t), bot = tb[1];
    V['arculus'] = [[t * L, _at(V['R1'], t * L)], [t * L, _at(V['CuA'], t * L)]];
    var ta = 0.155, tbb = 0.235;
    V['triangle'] = [[ta * L, _at(V['MA'], ta * L)], [tbb * L, _at(V['MA'], tbb * L)], [tbb * L, _at(V['CuA'], tbb * L)], [ta * L, _at(V['CuA'], ta * L)]];
    V['tri_split'] = [[ta * L, _at(V['MA'], ta * L)], [tbb * L, _at(V['CuA'], tbb * L)]];
    V['subtriangle'] = [[ta * L, _at(V['CuA'], ta * L)], [tbb * L, _at(V['CuA'], tbb * L)], [(ta + 0.02) * L, or(_at(V['A1'], (ta + 0.02) * L), bot)]];
    var cN = chordAt(NODUS); V['nodus'] = [[NODUS * L, cN[0]], [NODUS * L, _at(V['R1'], NODUS * L)]];
    V['subnodus'] = [[NODUS * L, _at(V['R1'], NODUS * L)], [(NODUS + 0.012) * L, _at(V['R3'], (NODUS + 0.012) * L)]];
    var pa = PTEROSTIGMA[0], pb = PTEROSTIGMA[1], c1 = chordAt(pa), c2 = chordAt(pb);
    V['pterostigma'] = [[pa * L, c1[0]], [pb * L, c2[0]], [pb * L, _at(V['R1'], pb * L)], [pa * L, _at(V['R1'], pa * L)]];
    if (hind) { var al = [];
      for (var i = 0; i < 9; i++) { var tt = lerp(0.10, 0.34, i / 8);
        al.push([tt * L, lerp(or(_at(V['CuA'], tt * L), 0), or(_at(V['A1'], tt * L), 0), 0.5 + 0.35 * Math.sin(Math.PI * i / 8))]); }
      V['anal_loop'] = al; }
    /* crossveins */
    var cross = [], ant = hind ? 10 : 13, u, k;
    for (i = 1; i <= ant; i++) { t = NODUS * i / (ant + 0.5); u = t * L; var top = chordAt(t)[0];
      cross.push([[u, top], [u, _at(V['Sc'], u)]]); cross.push([[u, _at(V['Sc'], u)], [u, _at(V['R1'], u)]]); }
    var post = 12;
    for (i = 1; i <= post; i++) { t = NODUS + (pa - NODUS) * i / (post + 0.5); u = t * L;
      if (_at(V['R1'], u) !== null) cross.push([[u, chordAt(t)[0]], [u, _at(V['R1'], u)]]); }
    for (i = 1; i < 4; i++) { t = pb + (0.995 - pb) * i / 4; u = t * L;
      if (_at(V['R1'], u) !== null) cross.push([[u, chordAt(t)[0]], [u, _at(V['R1'], u)]]); }
    var pairs = [['R1', 'R2'], ['R1', 'R3'], ['R2', 'R3'], ['R2', 'IR2'], ['IR2', 'R3'], ['R3', 'IR3'], ['R3', 'R4+5'], ['IR3', 'R4+5'], ['R4+5', 'MA'], ['MA', 'MP'], ['MA', 'CuA'], ['MP', 'CuA'], ['CuA', 'CuP'], ['CuA', 'A1'], ['CuP', 'A1']];
    for (var q = 0; q < pairs.length; q++) {
      var a = pairs[q][0], b = pairs[q][1], pA = V[a], pB = V[b];
      var u0 = Math.max(pA[0][0], pB[0][0]), u1 = Math.min(pA[pA.length - 1][0], pB[pB.length - 1][0]);
      if (u1 - u0 < 1.0) continue;
      u = u0 + 0.6; k = 0;
      while (u < u1) {
        t = u / L;
        var step = lerp(1.1, 0.52, t) * (1 + 0.12 * (RNG() - 0.5));
        var va = _at(pA, u), vb = _at(pB, u);
        if (va === null || vb === null) { u += step; continue; }
        if (a === 'R1' && b === 'R3' && u > 0.30 * L) break;
        if (a === 'R2' && b === 'R3' && u > 0.52 * L) break;
        if (a === 'MA' && b === 'CuA' && u < (hind ? 0.62 : 0.52) * L) { u += step; continue; }
        if (a === 'R3' && b === 'R4+5' && u > 0.55 * L) break;
        if (a === 'CuA' && b === 'A1' && u < (hind ? 0.36 : 0.30) * L) { u += step; continue; }
        if (Math.abs(va - vb) < 0.35) { u += step; continue; }
        var du = 0.18 * step * (k % 2 ? 1 : -1);
        var vb2 = or(_at(pB, Math.min(u + du, u1)), vb);
        cross.push([[u, va], [u + du, vb2]]);
        u += step; k += 1;
      }
    }
    var marg = ['A1', 'CuA', 'MA', 'R4+5', 'IR3', 'R3', 'IR2', 'R2'];
    for (q = 0; q < marg.length; q++) { var p = V[marg[q]];
      for (i = 0; i < p.length; i += 3) { u = p[i][0]; var v = p[i][1]; var cb = chordAt(u / L)[1];
        if (cb < v - 0.25 && (v - cb) < 2.2) cross.push([[u, v], [u + 0.25, cb]]); } }
    V['cross'] = cross;
    if (scale !== 1.0) {
      var sc = function (pt) { return [pt[0] * scale, pt[1] === null ? null : pt[1] * scale]; };
      Object.keys(V).forEach(function (key) { V[key] = key === 'cross' ? V[key].map(function (s) { return s.map(sc); }) : V[key].map(sc); });
    }
    return V;
  }

  var LONGITUDINALS = ['C', 'Sc', 'R1', 'R2', 'IR2', 'R3', 'IR3', 'R4+5', 'MA', 'MP', 'CuA', 'CuP', 'A1'];
  var api = { FORE_L: FORE_L, FORE_CH: FORE_CH, HIND_L: HIND_L, HIND_CH: HIND_CH, NODUS: NODUS, PTEROSTIGMA: PTEROSTIGMA,
    LONGITUDINALS: LONGITUDINALS, wingOutline: wingOutline, wingVeins: wingVeins, MT: MT };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.WingGeom = api;
})(this);
