const pptxgen = require("pptxgenjs");

const OUT = process.argv[2] || "day3_practice_slides.pptx";

// 1일차 슬라이드와 같은 팔레트·폰트
const THEME = {
  name: "QML Lecture",
  headFontFace: "Noto Sans KR",
  bodyFontFace: "Noto Sans KR",
  colors: {
    dk1: "212121", lt1: "FFFFFF", dk2: "1E3932", lt2: "F2F0EB",
    accent1: "00754A", accent2: "5B3E8C", accent3: "DFC49D", accent4: "9C5000",
    accent5: "006241", accent6: "6B6B6B", hlink: "00754A", folHlink: "5B3E8C",
  },
};
const HEX = { dark: "1E3932", green: "00754A", green2: "006241", purple: "5B3E8C", lav: "EDE7F5",
  gold: "DFC49D", brown: "9C5000", text: "212121", muted: "6B6B6B", card: "F2F0EB", card2: "EDEBE9",
  line: "C9C5BE", mint: "DDF2E6", cream: "FAF6EE", white: "FFFFFF", code: "F2F0EB" };
const MONO = "Courier New";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "3일차 실습 설명 자료";
pres.author = "QML Lecture";
// 테마 색 이름 → hex. 테마 XML을 따로 고치지 않고 모든 도형에 hex로 직접 지정함
const C = {
  text1: THEME.colors.dk1, text2: THEME.colors.dk2, background1: THEME.colors.lt1, background2: THEME.colors.lt2,
  accent1: THEME.colors.accent1, accent2: THEME.colors.accent2, accent3: THEME.colors.accent3,
  accent4: THEME.colors.accent4, accent5: THEME.colors.accent5, accent6: THEME.colors.accent6,
};

// ---------- layouts ----------
pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: 0.9, y: 1.95, w: 8, h: 0.4, fontSize: 13, bold: true, color: C.background1, charSpacing: 1 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.9, y: 2.4, w: 9.5, h: 0.9, fontSize: 40, bold: true, color: C.background1, align: "left" }, text: "" } },
    { placeholder: { options: { name: "sub", type: "body", x: 0.9, y: 3.3, w: 11.5, h: 0.9, fontSize: 28, bold: true, color: C.accent3, align: "left" }, text: "" } },
  ],
  slideNumber: { x: 6.42, y: 6.95, w: 0.5, h: 0.3, fontSize: 10, color: C.accent6, align: "center" },
});
pres.defineSlideMaster({
  title: "SECTION_DARK",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: 0.9, y: 0.75, w: 8, h: 0.4, fontSize: 12, bold: true, color: C.accent3, charSpacing: 1 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.9, y: 1.15, w: 11.5, h: 0.9, fontSize: 36, bold: true, color: C.background1, align: "left" }, text: "" } },
    { placeholder: { options: { name: "sub", type: "body", x: 0.9, y: 2.0, w: 11.5, h: 0.5, fontSize: 15, color: C.background2 }, text: "" } },
  ],
  slideNumber: { x: 6.42, y: 6.95, w: 0.5, h: 0.3, fontSize: 10, color: C.accent6, align: "center" },
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: 0.6, y: 0.4, w: 9, h: 0.35, fontSize: 12, bold: true, color: C.accent1, charSpacing: 1, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.75, w: 12.1, h: 0.75, fontSize: 30, bold: true, color: C.text1, margin: 0, align: "left" }, text: "" } },
    { placeholder: { options: { name: "sub", type: "body", x: 0.6, y: 1.5, w: 12.1, h: 0.45, fontSize: 14, color: C.accent6, margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 6.42, y: 6.95, w: 0.5, h: 0.3, fontSize: 10, color: C.accent6, align: "center" },
});

// ---------- helpers ----------
let section = "";
const NOTES = require("./day3_notes.json"); // 발표 대본(슬라이드 번호 -> 대본). 없으면 인라인 notes를 씀
let slideNo = 0;
function slide(master, kicker, title, sub, notes) {
  const s = pres.addSlide({ masterName: master, sectionTitle: section });
  slideNo += 1;
  if (kicker) s.addText(kicker, { placeholder: "kicker" });
  s.addText(title, { placeholder: "title" });
  if (sub) s.addText(sub, { placeholder: "sub" });
  const script = NOTES[String(slideNo)];
  if (script) s.addNotes(`[약 ${Math.max(1, Math.round(script.replace(/\n/g, "").length / 300))}분]\n` + script);
  else if (notes) s.addNotes(notes);
  return s;
}
function newSection(t) { section = t; pres.addSection({ title: t }); }

function shadow() { return { type: "outer", color: "000000", opacity: 0.12, blur: 6, offset: 2, angle: 90 }; }

function card(s, x, y, w, h, fill, opts = {}) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, rectRadius: 0.12,
    line: opts.line ? { color: opts.line, width: 1.25 } : { type: "none" }, shadow: opts.shadow ? shadow() : undefined });
}
function text(s, t, x, y, w, h, o = {}) {
  s.addText(t, Object.assign({ x, y, w, h, isTextBox: true, fontSize: 14, color: C.text1, valign: "top", margin: 0 }, o));
}
function numCircle(s, n, x, y, d = 0.42, fill = C.accent1) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { type: "none" } });
  s.addText(String(n), { x, y, w: d, h: d, isTextBox: true, fontSize: 14, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0 });
}
// 코드 블록: lines = [string | {t, hl}] - hl이면 금색으로 강조
function code(s, lines, x, y, w, h, fontSize = 12) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: C.text2 }, rectRadius: 0.1, line: { type: "none" } });
  const runs = lines.map((l, i) => {
    const o = typeof l === "string" ? { t: l } : l;
    const isComment = o.t.trim().startsWith("#");
    return { text: o.t === "" ? " " : o.t, options: { fontFace: MONO, fontSize, color: o.hl ? C.accent3 : (isComment ? "9FBFB0" : C.background2),
      bold: !!o.hl, breakLine: i < lines.length - 1 } };
  });
  s.addText(runs, { x: x + 0.25, y: y + 0.2, w: w - 0.5, h: h - 0.4, isTextBox: true, valign: "top", margin: 0, paraSpaceAfter: 2 });
}
function table(s, rows, x, y, w, colW, o = {}) {
  const fs = o.fontSize || 12;
  const data = rows.map((r, ri) => r.map((c) => {
    const cell = typeof c === "object" && c !== null && c.text !== undefined ? c : { text: String(c) };
    const base = ri === 0
      ? { bold: true, color: C.background1, fill: { color: C.text2 }, fontSize: fs }
      : { color: C.text1, fill: { color: ri % 2 === 0 ? C.background2 : C.background1 }, fontSize: fs };
    return { text: cell.text, options: Object.assign(base, cell.options || {}) };
  }));
  s.addTable(data, { x, y, w, colW, border: { type: "solid", pt: 0.5, color: HEX.line }, valign: "middle",
    margin: [0.06, 0.1, 0.06, 0.1], rowH: o.rowH || 0.38, autoPage: false });
}
function arrow(s, x1, y1, x2, y2, color = C.accent6) {
  s.addShape(pres.shapes.LINE, { x: x1, y: y1, w: x2 - x1, h: y2 - y1, line: { color, width: 1.75, endArrowType: "triangle" } });
}
function box(s, t, x, y, w, h, fill, color, o = {}) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, rectRadius: 0.08,
    line: o.line ? { color: o.line, width: 1 } : { type: "none" } });
  s.addText(t, { x, y, w, h, isTextBox: true, fontSize: o.fontSize || 12, color, bold: o.bold !== false, align: "center", valign: "middle", margin: 0.05 });
}

// 1일차 슬라이드처럼 오른쪽 아래에 출처 한 줄
function source(s, t) {
  text(s, t, 6.9, 6.95, 5.8, 0.3, { fontSize: 9, color: C.accent6, align: "right", valign: "middle" });
}
// 1일차 슬라이드 20의 왼쪽 막대 + 제목 + 설명 목록
function barList(s, items, x, y, w, gap = 0.95, color = C.accent1) {
  items.forEach((it, i) => {
    const yy = y + i * gap;
    s.addShape(pres.shapes.RECTANGLE, { x, y: yy, w: 0.07, h: gap - 0.2, fill: { color: it[2] || color }, line: { type: "none" } });
    text(s, it[0], x + 0.25, yy, w - 0.25, 0.35, { fontSize: 15, bold: true });
    text(s, it[1], x + 0.25, yy + 0.38, w - 0.25, gap - 0.5, { fontSize: 12.5, color: C.accent6 });
  });
}
function summary(s, rows) {
  table(s, [["주제", "정리"], ...rows.map((r) => [{ text: r[0], options: { bold: true } }, r[1]])],
    0.6, 2.25, 12.1, [2.4, 9.7], { fontSize: 13, rowH: 0.55 });
}
function sectionRows(s, rows, y0 = 3.25, gap = 0.95) {
  rows.forEach((r, i) => {
    text(s, r[0], 0.9, y0 + i * gap, 2.6, 0.4, { fontSize: 14, bold: true, color: C.accent3 });
    text(s, r[1], 3.6, y0 + i * gap, 8.8, 0.6, { fontSize: 15, color: C.background1 });
  });
}
function chartStyle(extra) {
  return Object.assign({
    catAxisLabelColor: THEME.colors.accent6, valAxisLabelColor: THEME.colors.accent6,
    catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", catAxisLabelFontSize: 11, valAxisLabelFontSize: 11,
    valGridLine: { color: "E5E2DC", size: 0.5 }, catGridLine: { style: "none" },
    showTitle: true, titleFontSize: 13, titleFontFace: "+mn-lt", titleColor: THEME.colors.dk1,
  }, extra);
}

// =====================================================================
newSection("표지");
{
  const s = slide("TITLE_DARK", "QML Lecture · 3일차", "실습 설명 자료", "MediQ-GAN 미세조정 → QGAN과 같은 지표로 비교");
  s.addShape(pres.shapes.OVAL, { x: 10.55, y: 0.85, w: 1.55, h: 1.55, fill: { color: C.text2 }, line: { color: C.accent1, width: 1.25 } });
  s.addShape(pres.shapes.OVAL, { x: 11.0, y: 1.3, w: 0.65, h: 0.65, fill: { color: C.accent1 }, line: { type: "none" } });
}
// =====================================================================
newSection("MediQ-GAN 구조");
{
  const s = slide("CONTENT", "MediQ-GAN 구조 · 1일차 복습", "hybrid 수준 : model-level과 layer-level", "QGAN은 생성자 전체가 양자회로, MediQ-GAN은 생성자 안의 한 갈래만 양자회로");
  card(s, 0.6, 2.3, 5.9, 4.3, HEX.mint, { line: HEX.green });
  text(s, "QGAN - model-level hybrid", 0.85, 2.5, 5.4, 0.4, { fontSize: 17, bold: true, color: C.accent1 });
  text(s, "Andra et al., 2025 · 2일차 실습", 0.85, 2.9, 5.4, 0.35, { fontSize: 12, color: C.accent6 });
  text(s, [
    { text: "생성자 = 양자회로 (sub-generator 4개)", options: { bullet: true, breakLine: true } },
    { text: "patch를 나눠 만들고 이어붙임", options: { bullet: true, breakLine: true } },
    { text: "출력 = 측정 확률 (patch별 합 0 ~ 1)", options: { bullet: true, breakLine: true } },
    { text: "판별자만 고전", options: { bullet: true } },
  ], 0.85, 3.45, 5.4, 2.0, { fontSize: 14, paraSpaceAfter: 8 });
  box(s, "z → [양자회로 × 4] → 이미지", 0.85, 5.65, 5.4, 0.6, C.accent1, C.background1, { fontSize: 13 });
  card(s, 6.8, 2.3, 5.9, 4.3, HEX.lav, { line: "B9B3D6" });
  text(s, "MediQ-GAN - layer-level hybrid", 7.05, 2.5, 5.4, 0.4, { fontSize: 17, bold: true, color: C.accent2 });
  text(s, "Jiao et al., 2025 · 3일차 실습", 7.05, 2.9, 5.4, 0.35, { fontSize: 12, color: C.accent6 });
  text(s, [
    { text: "생성자 = 고전 stream + 양자 stream", options: { bullet: true, breakLine: true } },
    { text: "입력을 절반씩 나눠 병렬 처리 후 concat", options: { bullet: true, breakLine: true } },
    { text: "출력 = 고전 decoder → Tanh (-1 ~ 1)", options: { bullet: true, breakLine: true } },
    { text: "양자 stream은 원 논문 스펙(16큐빗 × 5, depth 8)", options: { bullet: true } },
  ], 7.05, 3.45, 5.4, 2.0, { fontSize: 14, paraSpaceAfter: 8 });
  box(s, "z → [고전 ∥ 양자] → concat → decoder", 7.05, 5.65, 5.4, 0.6, C.accent2, C.background1, { fontSize: 13 });
}
{
  const s = slide("CONTENT", "MediQ-GAN 구조 · 노트북 §3 코드", "dual-stream의 데이터 흐름", "잠재벡터 256차원을 절반씩 나누고, 두 stream의 출력을 이어붙여 decoder로 보냄");
  box(s, "잠재벡터 z\n256차원\nN(0, 1)", 0.6, 3.25, 1.5, 1.2, HEX.card2, C.text1, { fontSize: 12 });
  // classical row
  box(s, "z[:, :128]", 2.55, 2.25, 1.5, 0.7, HEX.white, C.text1, { fontSize: 12, line: HEX.line });
  box(s, "고전 stream\nMLP 128→32→128", 4.45, 2.15, 2.3, 0.9, C.text2, C.background1, { fontSize: 12 });
  box(s, "128", 7.15, 2.25, 0.9, 0.7, HEX.white, C.text1, { fontSize: 12, line: HEX.line });
  // quantum row
  box(s, "z[:, 128:]", 2.55, 4.75, 1.5, 0.7, HEX.white, C.text1, { fontSize: 12, line: HEX.line });
  box(s, "양자 stream\n16 site → 회로 5개\n→ 1×1 conv", 4.45, 4.55, 2.3, 1.1, C.accent2, C.background1, { fontSize: 12 });
  box(s, "16 × 4×4\n= 256", 7.15, 4.65, 0.9, 0.9, HEX.white, C.text1, { fontSize: 11, line: HEX.line });
  arrow(s, 2.12, 3.65, 2.53, 2.65); arrow(s, 2.12, 4.05, 2.53, 5.05);
  arrow(s, 4.07, 2.60, 4.43, 2.60); arrow(s, 6.77, 2.60, 7.13, 2.60);
  arrow(s, 4.07, 5.10, 4.43, 5.10); arrow(s, 6.77, 5.10, 7.13, 5.10);
  box(s, "concat\n128 + 256\n= 384", 8.5, 3.25, 1.35, 1.2, HEX.mint, C.text1, { fontSize: 12, line: HEX.green });
  arrow(s, 8.07, 2.60, 8.6, 3.23); arrow(s, 8.07, 5.10, 8.6, 4.47);
  box(s, "decoder\nMLP 384→32→256\nTanh", 10.25, 3.20, 1.6, 1.3, C.text2, C.background1, { fontSize: 12 });
  arrow(s, 9.87, 3.85, 10.23, 3.85);
  box(s, "16×16\n-1 ~ 1", 12.05, 3.45, 0.75, 0.8, HEX.card2, C.text1, { fontSize: 11 });
  arrow(s, 11.87, 3.85, 12.03, 3.85);
  code(s, [
    "z_c, z_q = z[:, :self.half], z[:, self.half:]",
    "fused = torch.cat([self.classical_stream(z_c),",
    "                   self.quantum_stream(z_q)], dim=1)",
    "return self.decoder(fused)",
  ], 0.6, 5.72, 12.1, 1.1, 10.5);
}
{
  const s = slide("CONTENT", "MediQ-GAN 구조 · 노트북 §3 코드", "양자 회로 : 16큐빗, depth 8", "같은 값으로 RY → RX encoding, [학습 RY + 인접 CZ] × 8, 큐빗별 PauliX 기댓값");
  code(s, [
    '@qml.qnode(dev, interface="torch", diff_method="adjoint")',
    "def q_circuit(x, weights):",
    { t: "    for i in range(n_qubits):         # 1 encoding", hl: true },
    "        qml.RY(x[i], wires=i)",
    "        qml.RX(x[i], wires=i)",
    { t: "    for layer in range(q_depth):      # 2 x 8", hl: true },
    "        for i in range(n_qubits):",
    "            qml.RY(weights[layer, i], wires=i)",
    "        for i in range(n_qubits - 1):",
    "            qml.CZ(wires=[i, i + 1])",
    { t: "    return [qml.expval(qml.PauliX(i))  # 3", hl: true },
    { t: "            for i in range(n_qubits)]", hl: true },
  ], 0.6, 2.2, 6.6, 4.4, 12);
  // circuit diagram
  const dx = 7.5, sp = 0.5, wy0 = 2.55;
  card(s, dx, 2.2, 5.2, 4.4, HEX.card);
  const labels = ["q0", "q1", "q2", "⋮", "q14", "q15"];
  labels.forEach((l, i) => {
    const y = wy0 + 0.15 + i * sp;
    text(s, l, dx + 0.12, y - 0.15, 0.5, 0.3, { fontSize: 11, bold: true, valign: "middle" });
    if (l === "⋮") return;
    s.addShape(pres.shapes.LINE, { x: dx + 0.6, y, w: 4.45, h: 0, line: { color: C.accent6, width: 0.75 } });
    box(s, "RY(x)", dx + 0.7, y - 0.17, 0.65, 0.34, C.accent2, C.background1, { fontSize: 9 });
    box(s, "RX(x)", dx + 1.42, y - 0.17, 0.65, 0.34, C.accent2, C.background1, { fontSize: 9 });
    box(s, "RY(θ)", dx + 2.4, y - 0.17, 0.7, 0.34, C.accent1, C.background1, { fontSize: 9 });
    box(s, "⟨X⟩", dx + 4.5, y - 0.17, 0.5, 0.34, C.accent4, C.background1, { fontSize: 10 });
  });
  [[0, 1], [1, 2], [4, 5]].forEach(([a, b], k) => {
    const xx = dx + 3.35 + k * 0.32, ya = wy0 + 0.15 + a * sp, yb = wy0 + 0.15 + b * sp;
    s.addShape(pres.shapes.OVAL, { x: xx - 0.06, y: ya - 0.06, w: 0.12, h: 0.12, fill: { color: C.text1 }, line: { type: "none" } });
    s.addShape(pres.shapes.OVAL, { x: xx - 0.06, y: yb - 0.06, w: 0.12, h: 0.12, fill: { color: C.text1 }, line: { type: "none" } });
    s.addShape(pres.shapes.LINE, { x: xx, y: ya, w: 0, h: yb - ya, line: { color: C.text1, width: 1.25 } });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: dx + 2.25, y: wy0 - 0.1, w: 2.1, h: 3.1, fill: { type: "none" }, rectRadius: 0.1, line: { color: C.accent1, width: 1.25, dashType: "dash" } });
  text(s, "① encoding", dx + 0.6, 5.75, 1.6, 0.3, { fontSize: 11, bold: true, color: C.accent2, align: "center" });
  text(s, "② × 8 (RY + CZ 사슬)", dx + 2.25, 5.75, 2.1, 0.3, { fontSize: 11, bold: true, color: C.accent1, align: "center" });
  text(s, "③ 측정", dx + 4.35, 5.75, 0.8, 0.3, { fontSize: 11, bold: true, color: C.accent4, align: "center" });
  text(s, "출력: 큐빗 16개의 기댓값 → 평균 → site당 스칼라 1개", dx + 0.25, 6.12, 4.7, 0.35, { fontSize: 12, align: "center" });
}
{
  const s = slide("CONTENT", "MediQ-GAN 구조 · 파라미터 분포", "생성자 파라미터 구성", "30,000개 중 양자 회전각은 640개(2.1%). 2일차 QGAN 생성자는 280개 전부가 양자 회전각임");
  const q = (t) => ({ text: t, options: { bold: true, color: C.accent2 } });
  table(s, [
    ["모듈", "구성", "파라미터", "비율"],
    ["decoder", "Linear 384 → 32 → 256 + Tanh", "20,768", "69.2%"],
    ["고전 stream", "Linear 128 → 32 → 128", "8,352", "27.8%"],
    [q("양자 회전각"), q("sub-generator 5 × 8층 × 16큐빗"), q("640"), q("2.1%")],
    ["q_align", "Linear 8 → 16 (site 벡터를 큐빗 수에 맞춤)", "144", "0.5%"],
    ["proj_qexp", "1×1 conv, 5 → 16채널", "96", "0.3%"],
    [{ text: "합계", options: { bold: true } }, "", { text: "30,000", options: { bold: true } }, "100%"],
  ], 0.6, 2.25, 12.1, [2.4, 5.9, 2.0, 1.8], { fontSize: 13, rowH: 0.52 });
  text(s, "파라미터 수로는 2%지만, 학습 시간의 대부분은 이 640개가 들어 있는 16큐빗 회로의 시뮬레이션에서 나옴.", 0.6, 6.0, 12.1, 0.4, { fontSize: 13, color: C.accent6 });
  source(s, "노트북 ToyDualStreamGenerator(in_dim 256)에서 직접 센 값");
}
{
  const s = slide("CONTENT", "MediQ-GAN 구조 · 한계", "원 논문과 실습의 차이", "양자 stream은 원 논문 스펙 그대로, 고전 부분과 판별자·평가를 단순화함");
  table(s, [
    ["항목", "원 논문 (Jiao et al.)", "3일차 실습", "비고"],
    ["양자 stream", "16큐빗 × 5, depth 8", { text: "동일", options: { bold: true, color: C.accent1 } }, "공식 레포와 같은 회로"],
    ["고전 encoder / decoder", "conv", "MLP", "16×16 저해상도라 단순화"],
    ["입력 · 출력", "64×64 RGB", "16×16 그레이스케일", "2일차 전처리 자산 사용"],
    ["판별자", "WGAN-GP critic", "표준 BCE 판별자 (Table 4)", "QGAN과 같은 판별자"],
    ["학습", "GPU, 전체 학습", "25 epoch 사전학습. 수업에서는 10 epoch checkpoint + 20 step", "16큐빗 시뮬레이션 비용"],
    ["평가", "FID, 분류 성능", "지표 4종", "FID는 16×16에서 의미 없음"],
  ], 0.6, 2.25, 12.1, [2.6, 2.8, 3.6, 3.1], { fontSize: 13, rowH: 0.55 });
}
// =====================================================================
newSection("미세조정");
{
  const s = slide("CONTENT", "미세조정 · 계산 비용", "계산 비용 : 수업에서 미세조정만 하는 이유", "16큐빗 회로 시뮬레이션이 비싸 25 epoch 사전학습에 196분(약 3시간 15분)이 걸림");
  const b = (t) => ({ text: t, options: { bold: true } });
  table(s, [
    ["", "2일차 QGAN", "3일차 MediQ-GAN"],
    ["큐빗 (회로 하나)", "7", "16"],
    ["상태벡터 차원", "2⁷ = 128", "2¹⁶ = 65,536"],
    ["미분 방식", "backprop (default.qubit)", "adjoint (lightning.qubit)"],
    ["1 step", "약 2.2초 (batch 8)", b("약 20초 (batch 4)")],
    ["전체 학습", "600 step 약 22분", b("25 epoch 196분 (epoch당 7.8분)")],
    ["수업 중 학습", "처음부터 400 step (Colab 약 35분)", "10 epoch checkpoint에서 20 step"],
  ], 0.6, 2.25, 12.1, [3.0, 4.55, 4.55], { fontSize: 13, rowH: 0.52 });
  text(s, "16큐빗은 12큐빗보다 상태벡터가 16배 크고(2¹⁶ vs 2¹²), 실측 소요 시간은 약 20배였음.", 0.6, 6.0, 12.1, 0.4, { fontSize: 13, color: C.accent6 });
  source(s, "로컬 CPU 실측. epoch 시간은 checkpoint epoch_sec 평균");
}
// =====================================================================
newSection("비교");
{
  const s = slide("CONTENT", "비교 · 노트북 §5", "지표 비교 : 형태 재현과 다양성", "상관은 MediQ-GAN이 높고, 샘플 간 거리는 QGAN이 실제 DF에 가까움");
  s.addChart(pres.charts.BAR, [{ name: "상관", labels: ["QGAN 600 step", "MediQ 10 epoch", "MediQ 25 epoch"], values: [0.195, 0.018, 0.365] }], chartStyle({
    x: 0.6, y: 2.15, w: 6.0, h: 4.6, barDir: "col", chartColors: [THEME.colors.accent1, "B9B3D6", THEME.colors.accent2], varyColors: true,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 12, dataLabelFontFace: "+mn-lt", dataLabelColor: THEME.colors.dk1, dataLabelFormatCode: "0.000",
    showLegend: false, title: "② 클래스 평균 상관 (높을수록 형태 재현)", valAxisMinVal: 0, valAxisMaxVal: 0.4, valAxisMajorUnit: 0.1, valAxisLabelFormatCode: "0.0",
  }));
  s.addChart(pres.charts.BAR, [{ name: "다양성", labels: ["QGAN 600 step", "MediQ 25 epoch", "실제 DF"], values: [1.92, 0.30, 2.505] }], chartStyle({
    x: 6.8, y: 2.15, w: 5.9, h: 4.6, barDir: "col", chartColors: [THEME.colors.accent1, THEME.colors.accent2, THEME.colors.accent6], varyColors: true,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 12, dataLabelFontFace: "+mn-lt", dataLabelColor: THEME.colors.dk1, dataLabelFormatCode: "0.00",
    showLegend: false, title: "④ 샘플 간 거리 (0에 가까우면 mode collapse)", valAxisMinVal: 0, valAxisMaxVal: 3, valAxisMajorUnit: 0.5, valAxisLabelFormatCode: "0.0",
  }));
  source(s, "수치: README 결과표(로컬 CPU), MediQ-GAN 16장, QGAN 64장 평가. 지표 정의는 2일차 참고");
}
{
  const s = slide("CONTENT", "비교 · 결과 해석", "결과 해석 : 두 모델의 한계", "QGAN은 형태 재현이 약하고, MediQ-GAN은 평균 이미지에 가까운 그림을 반복함");
  table(s, [
    ["지표", "QGAN 600 step", "MediQ-GAN 25 epoch", "의미"],
    ["② 클래스 평균 상관 ↑\n(평균 이미지와의 Pearson 상관)", "0.195", { text: "0.365", options: { bold: true, color: C.accent2 } }, "평균 형태는 MediQ-GAN이 더 가까움"],
    ["③ 최근접 실제 거리\n(가장 가까운 실제 이미지까지 L2)", "1.64", "3.44", "MediQ-GAN은 실제 이미지 어느 것과도 멂"],
    ["④ 샘플 간 거리 (실제 2.505)\n(생성 이미지 쌍 L2 평균)", { text: "1.92", options: { bold: true, color: C.accent1 } }, "0.30", "MediQ-GAN은 비슷한 그림을 반복"],
  ], 0.6, 2.25, 12.1, [3.4, 2.1, 2.4, 4.2], { fontSize: 13, rowH: 0.62 });
  text(s, "해석", 0.6, 4.95, 12.1, 0.35, { fontSize: 14, bold: true, color: C.accent1 });
  text(s, [
    { text: "QGAN: 다양성은 실제에 가깝지만 병변 형태 재현이 약함. patch를 서로 독립적으로 만들어 이미지 전체 구조를 잡기 어려움.", options: { breakLine: true } },
    { text: "MediQ-GAN: 평균 형태는 잘 맞추지만 다양성이 실제의 1/8. 최종 출력을 고전 decoder가 만들기 때문에 Tanh가 포화되면 z와 무관한 이미지가 나옴.", options: { breakLine: true } },
    { text: "②만 보면 MediQ-GAN이 낫다고 결론 내리게 됨. ②는 평균 형태만 보므로 같은 이미지를 반복해도 높게 나옴." },
  ], 0.6, 5.3, 12.1, 1.5, { fontSize: 12, paraSpaceAfter: 4 });
}
// =====================================================================
newSection("정리");
{
  const s = slide("CONTENT", "정리", "3일차 정리", "MediQ-GAN 구조와 미세조정, QGAN과의 비교");
  summary(s, [
    ["hybrid 수준", "QGAN은 생성자 전체가 양자회로(model-level), MediQ-GAN은 생성자 안의 양자 stream만 양자회로(layer-level)"],
    ["dual-stream", "잠재벡터 256차원을 절반씩 고전 MLP와 양자 stream으로 나눠 처리한 뒤 concat → decoder → Tanh"],
    ["양자 stream", "16큐빗 × depth 8 회로 5개가 16 site 중 5개만 처리. PauliX 기댓값 출력이라 ancilla qubit이 필요 없음"],
    ["파라미터와 비용", "30,000개 중 양자 회전각은 640개(2.1%)지만 학습 시간 대부분이 16큐빗 시뮬레이션 (25 epoch 196분)"],
    ["checkpoint와 미세조정", "config로 같은 구조를 만든 뒤 가중치를 불러옴. 판별자도 같은 시점 상태로 불러와 20 step 추가 학습"],
    ["학습 안정성", "BCE 판별자가 우세함 (lr_g 0.02에서 3 epoch 만에 mode collapse). 원 논문은 WGAN-GP critic을 씀"],
    ["비교 결과", "상관은 MediQ-GAN 0.365 > QGAN 0.195, 다양성은 QGAN 1.92 > MediQ-GAN 0.30. 지표 하나로 순위를 정하지 않음"],
  ]);
}

(async () => {
  // pptxgenjs 4.0.1의 writeFile은 Node에서 compression 옵션을 무시해 zip이 비압축(약 6배 크기)으로 저장됨 - STREAM으로 받아 직접 씀
  const buf = await pres.write({ outputType: "STREAM", compression: true });
  require("fs").writeFileSync(OUT, buf);
  console.log("wrote", OUT);
})();
