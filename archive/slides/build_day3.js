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
function slide(master, kicker, title, sub, notes) {
  const s = pres.addSlide({ masterName: master, sectionTitle: section });
  if (kicker) s.addText(kicker, { placeholder: "kicker" });
  s.addText(title, { placeholder: "title" });
  if (sub) s.addText(sub, { placeholder: "sub" });
  if (notes) s.addNotes(notes);
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
// 1일차 슬라이드 10의 왼쪽 막대 + 제목 + 설명 목록
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
  const s = slide("TITLE_DARK", "QML Lecture · 3일차", "실습 설명 자료", "MediQ-GAN 미세조정 → QGAN과 같은 지표로 비교",
    "3일차 노트북(practice/day3_practice.ipynb)의 내용을 설명하는 자료.\n- 2일차 자료와 같은 구성: 코드 중심, 각 PART 첫 장에 해당 노트북 섹션을 표시함.");
  s.addShape(pres.shapes.OVAL, { x: 10.55, y: 0.85, w: 1.55, h: 1.55, fill: { color: C.text2 }, line: { color: C.accent1, width: 1.25 } });
  s.addShape(pres.shapes.OVAL, { x: 11.0, y: 1.3, w: 0.65, h: 0.65, fill: { color: C.accent1 }, line: { type: "none" } });
}

newSection("진행");
{
  const s = slide("CONTENT", "오리엔테이션", "3일차 진행 순서", "노트북 섹션과 이 자료의 PART 대응",
    "- 3일차는 학습 없이 checkpoint를 불러오는 셀이 대부분이라 수 초 안에 끝남.\n- 시간이 걸리는 셀: §3 구조 확인(16큐빗 회로 5개 forward, 십여 초), §4 미세조정 20 step(로컬 실측 약 7분, Colab은 더 걸림).\n- 진행 로그의 '남은 예상' 시간을 보고 step 수를 줄여도 됨.");
  const hl = (t) => ({ text: t, options: { bold: true, color: C.accent1 } });
  table(s, [
    ["노트북", "내용", "실행 시간", "설명 자료"],
    ["§0 – §1", "Colab 설정, 저장소 clone, 실습 자산 로드", "1분 이내", "PART 0"],
    ["§2", "QGAN checkpoint(600 step) 생성·평가 - 비교 기준선", "수 초", "PART 0"],
    ["§3", "MediQ-GAN 구조: dual-stream, 16큐빗 회로 × 5", "십여 초", "PART 1"],
    [hl("§4"), hl("10 epoch checkpoint에서 20 step 미세조정"), hl("약 7분 (로컬 CPU)"), hl("PART 2")],
    ["§5", "QGAN과 MediQ-GAN을 같은 지표 4종으로 비교", "수 초", "PART 3"],
    ["§6", "이미지 생성에서 양자컴퓨팅의 한계와 방향", "-", "PART 4"],
  ], 0.6, 2.25, 12.1, [1.6, 6.3, 2.4, 1.8], { fontSize: 13, rowH: 0.55 });
}

// =====================================================================
newSection("PART 0 · 2일차 복습과 기준선");
{
  const s = slide("SECTION_DARK", "PART 0 · 노트북 §1 – §2", "2일차 복습과 QGAN 기준선", "2일차에 만든 QGAN을 checkpoint로 불러와 오늘 비교의 기준선으로 씀");
  sectionRows(s, [["노트북 범위", "§1 실습 자산 로드, §2 QGAN 생성·평가"],
    ["다루는 코드", "torch.load · PatchQuantumGenerator(**config) · gm.evaluate"]]);
}
{
  const s = slide("CONTENT", "PART 0 · 2일차 복습", "2일차 구성과 3일차에서 바뀌는 부분", "생성자만 MediQ-GAN으로 바꾸고, 데이터·판별자·지표는 2일차 그대로 씀",
    "- 데이터, 판별자 구조(논문 Table 4), 지표 4종은 2일차와 동일함. 바뀌는 것은 생성자 하나뿐이라 비교가 공정함.\n- 2일차 생성자는 '전체가 양자'(model-level hybrid), 오늘 생성자는 '일부만 양자'(layer-level hybrid).\n- 2일차 수업 중 학습은 400 step, 오늘 쓰는 강사 checkpoint는 같은 구조로 600 step 학습한 것.");
  const same = { text: "2일차와 같음", options: { color: C.accent6 } };
  table(s, [
    ["항목", "2일차 (QGAN)", "3일차 (MediQ-GAN)"],
    ["데이터", "DF 115장, segmentation 후 16×16, 0 ~ 1", same],
    [{ text: "생성자", options: { bold: true } }, { text: "sub-generator 4개 × 7큐빗, depth 10 - 생성자 전체가 양자회로", options: { bold: true } },
      { text: "고전 stream + 양자 stream(16큐빗 × 5, depth 8)", options: { bold: true, color: C.accent2 } }],
    ["출력 척도", "측정 확률 (patch별 합 0 ~ 1)", "Tanh (-1 ~ 1)"],
    ["판별자", "5층 FC (논문 Table 4)", same],
    ["지표", "상관 · 최근접 거리 · 다양성 · 픽셀 분포", same],
    ["학습량", "수업 중 400 step, 강사 checkpoint 600 step", "사전학습 25 epoch, 수업 중 20 step 미세조정"],
  ], 0.6, 2.25, 12.1, [2.0, 5.05, 5.05], { fontSize: 13, rowH: 0.55 });
}
{
  const s = slide("CONTENT", "PART 0 · 노트북 §2 코드", "checkpoint 불러오기", "config로 같은 구조를 먼저 만들고, 학습된 가중치를 덮어씀",
    "- checkpoint는 가중치(state_dict)만 저장하므로, 불러오기 전에 같은 모양의 모델을 먼저 만들어야 함. 모양이 다르면 load_state_dict가 오류를 냄.\n- 그래서 학습 스크립트가 config(sub-generator 수, 큐빗 수, depth 등)를 함께 저장함. 클래스의 인자 기본값은 쓰이지 않음.\n- map_location='cpu': GPU에서 저장한 파일도 CPU에서 열 수 있게 함.\n- 강사 checkpoint(QGAN·MediQ-GAN)에는 판별자 가중치도 들어 있음. 2일차 §7에서 각자 저장한 파일에는 없음. MediQ-GAN을 미세조정할 때 판별자도 같은 시점 상태로 불러와야 균형이 유지됨.");
  code(s, [
    'ckpt_path = f"{ASSET_DIR}/qgan_df_{IMG_SIZE}px.pt"',
    { t: 'checkpoint = torch.load(ckpt_path, map_location="cpu")', hl: true },
    'cfg = checkpoint["config"]',
    "",
    { t: "gen = PatchQuantumGenerator(", hl: true },
    '    n_generators=cfg["n_generators"],',
    '    n_data_qubits=cfg["n_data_qubits"],',
    '    n_ancillas=cfg["n_ancillas"], q_depth=cfg["q_depth"])',
    { t: 'gen.load_state_dict(checkpoint["generator_state_dict"])', hl: true },
    "gen.eval()",
  ], 0.6, 2.2, 6.9, 3.9, 12);
  table(s, [
    ["checkpoint 키", "내용"],
    ["generator_state_dict", "생성자 가중치 (회전각 등)"],
    ["discriminator_state_dict", "판별자 가중치"],
    ["config", "모델 재구성에 필요한 설정"],
    ["history", "step별 loss_g · loss_d"],
    ["epoch", "학습한 epoch 수 (MediQ-GAN)"],
  ], 7.8, 2.2, 4.9, [2.4, 2.5], { fontSize: 12, rowH: 0.5 });
  text(s, "이 파일의 config: sub-generator 4, 데이터 6 + ancilla 1, depth 10, 600 step", 7.8, 5.45, 4.9, 0.7, { fontSize: 12, color: C.accent6 });
}
{
  const s = slide("CONTENT", "PART 0 · 노트북 §2", "QGAN 기준선", "강사 checkpoint(600 step)를 지표 4종으로 평가한 값. PART 3에서 MediQ-GAN과 같은 표에 놓음",
    "- README 결과표의 수치(로컬 CPU 실측). 상관계수는 64장 × 10개 시드 평균 ± 표준편차.\n- 생성은 호출마다 새 난수를 쓰므로 노트북을 실행할 때마다 값이 조금씩 다름(예: 이 자료 작성 중 실행 결과는 상관 0.222, 최근접 1.66, 다양성 1.97). 소수점보다 모델 간 격차를 봄.\n- QGAN은 64장, MediQ-GAN은 16장으로 평가함. 16큐빗 시뮬레이션이 비싸기 때문. 상관계수는 표본 수에 민감해 8 ~ 16장이면 0.05 ~ 0.17까지 흔들렸음.");
  table(s, [
    ["지표", "QGAN 600 step", "비교 기준", "해석"],
    ["② 클래스 평균 상관 ↑", { text: "0.195 ± 0.012", options: { bold: true } }, "높을수록 DF 평균 형태에 가까움", "64장 × 10시드 평균 ± 표준편차"],
    ["③ 최근접 실제 거리", { text: "1.64", options: { bold: true } }, "0에 가까우면 학습 이미지 암기", "암기는 아님"],
    ["④ 샘플 간 거리", { text: "1.92", options: { bold: true } }, "실제 DF 2.505", "실제의 약 77%"],
  ], 0.6, 2.25, 12.1, [2.8, 2.2, 3.7, 3.4], { fontSize: 13, rowH: 0.55 });
  code(s, [
    "with torch.no_grad():",
    "    qgan_fake = gen(batch_size=64).numpy().reshape(64, 16, 16)",
    { t: 'qgan_scores = gm.evaluate(qgan_fake, df_imgs, "prob")', hl: true },
  ], 0.6, 4.75, 7.6, 1.3, 12);
  text(s, "생성할 때마다 새 난수를 쓰므로 노트북 실행 결과는 표와 조금씩 다름. 소수점 자리보다 모델 간 격차를 봄.", 8.5, 4.8, 4.2, 1.2, { fontSize: 12.5, color: C.accent6 });
  source(s, "수치: README 결과표 (로컬 CPU, PennyLane exact 시뮬레이션)");
}

// =====================================================================
newSection("PART 1 · MediQ-GAN 구조");
{
  const s = slide("SECTION_DARK", "PART 1 · 노트북 §3", "MediQ-GAN 구조", "생성자 안에서 고전 stream과 양자 stream이 병렬로 돌고 하나로 합쳐짐");
  sectionRows(s, [["노트북 범위", "§3 ToyDualStreamGenerator 정의와 forward 1회"],
    ["다루는 코드", "q_circuit · quantum_stream · forward"],
    ["비교 대상", "2일차 QGAN(생성자 전체가 양자회로)"]]);
}
{
  const s = slide("CONTENT", "PART 1 · 1일차 복습", "hybrid 수준 : model-level과 layer-level", "QGAN은 생성자 전체가 양자회로, MediQ-GAN은 생성자 안의 한 갈래만 양자회로",
    "- 1일차 슬라이드 18 'Hybrid 분류체계' 복습.\n- model-level hybrid: 판별자만 고전, 생성자는 처음부터 끝까지 양자회로. 출력이 측정 확률이라 척도가 확률(patch별 합 0 ~ 1).\n- layer-level hybrid: 생성자 안에서 고전 layer와 양자 layer가 함께 동작. 최종 출력은 고전 decoder가 만들고 Tanh(-1 ~ 1).\n- MediQ-GAN 논문의 주장: 전역 구조는 고전, 세부는 양자가 맡는 쪽이 더 높은 해상도로 확장됨.");
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
  const s = slide("CONTENT", "PART 1 · 노트북 §3 코드", "dual-stream의 데이터 흐름", "잠재벡터 256차원을 절반씩 나누고, 두 stream의 출력을 이어붙여 decoder로 보냄",
    "- forward 코드: z[:, :half]는 고전 stream, z[:, half:]는 양자 stream으로 감(논문 Fig.2 'feature map split').\n- 고전 stream은 128 → 32 → 128 MLP. 논문은 conv encoder지만 16×16 저해상도라 MLP로 단순화함.\n- 양자 stream 출력은 16채널 × 4×4 = 256차원. 고전 128과 concat하면 384차원.\n- decoder는 384 → 32 → 256 MLP + Tanh. 최종 이미지는 이 고전 decoder가 만듦 → Tanh가 포화되면 z와 무관한 상수 이미지가 나올 수 있음(PART 2 학습 안정성).");
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
  const s = slide("CONTENT", "PART 1 · 노트북 §3 코드", "양자 회로 : 16큐빗, depth 8", "같은 값으로 RY → RX encoding, [학습 RY + 인접 CZ] × 8, 큐빗별 PauliX 기댓값",
    "- 2일차 회로와 다른 점: ① 입력이 난수가 아니라 q_align이 만든 학습된 특징값, ② RY와 RX를 같은 값으로 연속 적용, ③ 확률 대신 PauliX 기댓값(-1 ~ 1, 큐빗당 1개)을 출력.\n- 기댓값 출력이라 ancilla qubit이나 post-selection이 필요 없음.\n- lightning.qubit(C++ 시뮬레이터)은 backprop을 지원하지 않아 adjoint 미분을 씀. 16큐빗 상태벡터는 2^16 = 65,536차원.\n- 공식 레포(mediq-gan.py의 quantum_circuit)와 같은 구성. depth는 논문 그림 기준 8(레포 CLI 기본값은 6).");
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
  const s = slide("CONTENT", "PART 1 · 노트북 §3 코드", "양자 stream : 16 site 중 5개만 회로로 처리", "양자 쪽 입력을 4×4 = 16 site로 보고, 고른 5개 site만 sub-generator 회로가 처리함",
    "- z_quantum 128차원을 16 site × 8차원으로 보고, q_align(Linear 8 → 16)으로 site마다 큐빗 수(16)에 맞춘 토큰을 만듦.\n- site_idx = linspace(0, 15, 5).round() = [0, 4, 8, 11, 15]. sub-generator g는 site_idx[g] 하나만 처리함.\n- 회로 출력 16개 기댓값의 평균 → 스칼라 1개 → 4×4 맵의 해당 칸. 나머지 11칸은 0.\n- proj_qexp(1×1 conv)가 5채널 맵을 16채널로 투영. 1×1이라 칸끼리 섞지 않음.\n- 회로 실행 수 = sub-generator 5 × batch. 이 부분이 MediQ-GAN에서 가장 느림.");
  // 4x4 grid
  const gx = 0.9, gy = 2.4, cs = 0.82;
  const sel = { 0: 1, 4: 2, 8: 3, 11: 4, 15: 5 };
  for (let k = 0; k < 16; k++) {
    const r = Math.floor(k / 4), c = k % 4;
    const on = sel[k] !== undefined;
    s.addShape(pres.shapes.RECTANGLE, { x: gx + c * cs, y: gy + r * cs, w: cs, h: cs, fill: { color: on ? HEX.purple : HEX.card }, line: { color: HEX.white, width: 2 } });
    text(s, on ? `site ${k}\ngen ${sel[k]}` : `site ${k}\n0`, gx + c * cs, gy + r * cs, cs, cs,
      { fontSize: 10, bold: on, color: on ? C.background1 : C.accent6, align: "center", valign: "middle" });
  }
  text(s, "4×4 site 맵 - 보라색 5칸만 회로 출력, 나머지는 0", gx - 0.2, gy + 4 * cs + 0.12, 4 * cs + 0.4, 0.5, { fontSize: 12, color: C.accent6, align: "center" });
  code(s, [
    "sites  = z_quantum.view(B, 16, self.site_dim)   # (B,16,8)",
    { t: "tokens = self.q_align(sites)                  # (B,16,16)", hl: true },
    "q_maps = torch.zeros(B, 5, 4, 4)",
    "for g, si in enumerate(self.site_idx):  # [0,4,8,11,15]",
    { t: "    outs = torch.stack([torch.stack(self.q_circuit(", hl: true },
    { t: "                tokens[b, si], self.q_weights[g]))", hl: true },
    "        for b in range(B)])           # (B, 16) expvals",
    "    y, x = divmod(si, 4)",
    { t: "    q_maps[:, g, y, x] = outs.mean(dim=1)  # scalar", hl: true },
    "return self.proj_qexp(q_maps).flatten(1)   # (B, 256)",
  ], 4.6, 2.2, 8.1, 3.95, 11.5);
  text(s, "forward 1회의 회로 실행 수 = 5 × batch. 회로 하나의 상태벡터는 2¹⁶ = 65,536차원.", 4.6, 6.3, 8.1, 0.45, { fontSize: 12.5, color: C.accent6, valign: "middle" });
}
{
  const s = slide("CONTENT", "PART 1 · 파라미터 분포", "생성자 파라미터 구성", "30,000개 중 양자 회전각은 640개(2.1%). 2일차 QGAN 생성자는 280개 전부가 양자 회전각임",
    "- 값은 노트북의 ToyDualStreamGenerator(in_dim 256)를 그대로 만들어 센 것.\n- 파라미터 수로는 양자 stream이 2.1%에 불과하지만, 학습 시간의 대부분은 16큐빗 회로 시뮬레이션에서 나옴.\n- 2일차 QGAN은 생성자 280개가 전부 양자 파라미터. '양자 비율'이 hybrid 수준의 차이를 수치로 보여줌.\n- parameter-shift로 실제 장치에서 학습한다면 640개 × 2 = 1,280회 회로 실행이 샘플 하나의 기울기에 필요함.");
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
  const s = slide("CONTENT", "PART 1 · 한계", "원 논문과 실습의 차이", "양자 stream은 원 논문 스펙 그대로, 고전 부분과 판별자·평가를 단순화함",
    "- 양자 stream을 줄이지 않은 이유: 줄이면 '논문이 말한 모델'이 아니게 됨. 대신 해상도와 학습 구간을 줄임(README 설계 원칙 1).\n- 판별자 차이가 가장 큼: 원 논문은 WGAN-GP critic(gradient penalty로 판별자를 제약). 실습은 QGAN과 같은 표준 BCE 판별자라 판별자가 쉽게 이김(다음 PART 학습 안정성).\n- 평가: 16×16에서는 FID가 의미 없어 지표 4종을 씀.");
  table(s, [
    ["항목", "원 논문 (Jiao et al.)", "3일차 실습", "비고"],
    ["양자 stream", "16큐빗 × 5, depth 8", { text: "동일", options: { bold: true, color: C.accent1 } }, "공식 레포와 같은 회로"],
    ["고전 encoder / decoder", "conv", "MLP", "16×16 저해상도라 단순화"],
    ["입력 · 출력", "64×64 RGB", "16×16 그레이스케일", "2일차 전처리 자산 사용"],
    ["판별자", "WGAN-GP critic", "표준 BCE 판별자 (Table 4)", "QGAN과 같은 판별자"],
    ["학습", "GPU, 전체 학습", "25 epoch 사전학습 + 수업 중 미세조정", "16큐빗 시뮬레이션 비용"],
    ["평가", "FID, 분류 성능", "지표 4종", "FID는 16×16에서 의미 없음"],
  ], 0.6, 2.25, 12.1, [2.6, 2.8, 3.6, 3.1], { fontSize: 13, rowH: 0.55 });
}

// =====================================================================
newSection("PART 2 · 라이브 미세조정");
{
  const s = slide("SECTION_DARK", "PART 2 · 노트북 §4", "라이브 미세조정", "덜 학습된 10 epoch checkpoint에서 출발해 20 step을 더 학습함",
    "1 step 약 20초라 20 step이면 로컬 기준 약 7분.");
  sectionRows(s, [["노트북 범위", "§4 미세조정과 전후 비교"],
    ["다루는 코드", "mediqgan_e010.pt · sample_z · real_tanh · Adam(betas=(0.5, 0.999))"],
    ["소요 시간", "20 step 약 7분 (로컬 CPU), Colab은 더 걸림"]]);
}
{
  const s = slide("CONTENT", "PART 2 · 노트북 §4 코드", "미세조정 코드와 2일차 설정 비교", "루프 구조는 2일차와 같고, 출력 척도·잠재벡터·optimizer 설정이 다름",
    "- real_tanh: 실제 이미지(0 ~ 1)를 2x - 1로 옮겨 생성자 출력(Tanh, -1 ~ 1)과 척도를 맞춤.\n- sample_z: checkpoint config의 z_dist를 따름(normal). 강사 학습과 같은 조건이어야 비교가 됨.\n- 판별자도 checkpoint에서 불러옴. 새 판별자로 시작하면 균형이 처음부터 깨짐.\n- 10 epoch에서 출발하는 이유: 완전히 수렴한 모델에서 시작하면 손실이 거의 움직이지 않아 학습 과정이 보이지 않음.");
  code(s, [
    'mq_ckpt = torch.load(f"{ASSET_DIR}/mediqgan_e010.pt")',
    { t: 'mq_disc.load_state_dict(mq_ckpt["discriminator_state_dict"])', hl: true },
    "",
    { t: "real_tanh = torch.tensor(df_imgs.reshape(115, -1) * 2 - 1)", hl: true },
    "def sample_z(n): return torch.randn(n, 256)   # z ~ N(0, 1)",
    "",
    { t: "opt_g = Adam(mq_gen.parameters(),  lr=2e-4, betas=(0.5, 0.999))", hl: true },
    "opt_d = Adam(mq_disc.parameters(), lr=2e-4, betas=(0.5, 0.999))",
    "",
    "for step in range(20):       # batch 4, same D/G loop as day 2",
    "    ...",
  ], 0.6, 2.2, 7.4, 4.45, 11.5);
  table(s, [
    ["설정", "2일차 QGAN", "3일차 MediQ"],
    ["출력 척도", "확률 (prob)", "Tanh (-1 ~ 1)"],
    ["실제 이미지", "이미지 합 = 1", "2x - 1"],
    ["잠재벡터", "U(0, π) 각도", "N(0, 1)"],
    ["학습률 G / D", "0.05 / 0.001", "2e-4 / 2e-4"],
    ["Adam betas", "(0.9, 0.999)", "(0.5, 0.999)"],
    ["batch · step", "8 · 400", "4 · 20 (미세조정)"],
  ], 8.3, 2.2, 4.4, [1.3, 1.55, 1.55], { fontSize: 11.5, rowH: 0.48 });
  text(s, "lr 2e-4, beta1 0.5는 DCGAN 논문(Radford et al., 2016)의 설정값", 8.3, 5.75, 4.4, 0.6, { fontSize: 11.5, color: C.accent6 });
}
{
  const s = slide("CONTENT", "PART 2 · 학습 안정성", "사전학습 손실 기록 (25 epoch)", "강사 checkpoint의 학습 기록(epoch별 평균). 15 ~ 21 epoch에서 판별자가 우세해졌다가 22 epoch부터 회복함",
    "- 차트는 mediqgan_final.pt의 history(700 step = 25 epoch × 28 step)를 epoch별로 평균한 값.\n- 10 epoch까지는 균형 근처(loss_d 1.2 ~ 1.4). 이후 loss_d가 0.74까지 떨어지고 loss_g가 3.37까지 오름 - 판별자 우세 구간. 22 epoch부터 다시 균형으로 돌아옴.\n- 사전 실험에서 lr_g 0.02(큰 학습률)로 시작했을 때는 3 epoch 만에 loss_d 0.0027, 다양성 0.000(완전 mode collapse). GAN 관례값으로 바꿔 25 epoch을 완주함(README 학습 안정성).\n- 원 논문이 WGAN-GP critic을 쓰는 이유가 이 불안정성임. 판별자 설계가 결과를 좌우한다는 점을 토론 소재로 씀.");
  const ep = Array.from({ length: 25 }, (_, i) => String(i + 1));
  const g = [0.827, 0.828, 0.839, 0.855, 0.869, 0.891, 0.899, 0.918, 0.944, 0.981, 1.08, 1.245, 1.423, 1.731, 1.989, 2.411, 2.761, 2.967, 3.368, 3.195, 3.055, 1.899, 0.718, 0.74, 0.772];
  const d = [1.39, 1.356, 1.332, 1.318, 1.304, 1.286, 1.279, 1.262, 1.243, 1.217, 1.162, 1.087, 1.022, 0.935, 0.88, 0.818, 0.78, 0.763, 0.738, 0.747, 0.778, 1.093, 1.357, 1.341, 1.313];
  s.addChart(pres.charts.LINE, [
    { name: "loss_g", labels: ep, values: g },
    { name: "loss_d", labels: ep, values: d },
    { name: "2 ln 2 = 1.386", labels: ep, values: ep.map(() => 1.386) },
  ], chartStyle({
    x: 0.6, y: 2.15, w: 8.0, h: 4.6, chartColors: [THEME.colors.accent1, THEME.colors.accent2, "B9B3D6"],
    lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 5,
    showLegend: true, legendPos: "b", legendFontSize: 11, legendFontFace: "+mn-lt", legendColor: THEME.colors.dk1,
    title: "MediQ-GAN 사전학습 손실 (epoch별 평균, 로컬 CPU)", valAxisMinVal: 0, valAxisMaxVal: 3.5, valAxisMajorUnit: 0.5, valAxisLabelFormatCode: "0.0",
    showCatAxisTitle: true, catAxisTitle: "epoch", catAxisTitleFontSize: 11, catAxisTitleColor: THEME.colors.accent6,
  }));
  barList(s, [
    ["10 epoch까지", "loss_d 1.39 → 1.22, 2 ln 2 근처의 균형 상태", C.accent1],
    ["11 ~ 21 epoch", "loss_d 최저 0.74 (19 epoch), loss_g 최고 3.37 - 판별자 우세", C.accent2],
    ["22 epoch 이후", "loss_d 1.3 부근으로 회복", C.accent6],
    ["lr_g 0.02 사전 실험", "3 epoch 만에 loss_d 0.0027, 다양성 0.000 (완전 mode collapse)", C.accent4],
  ], 9.0, 2.3, 3.7, 1.05);
  source(s, "mediqgan_final.pt history, 700 step = 25 epoch × 28 step");
}
{
  const s = slide("CONTENT", "PART 2 · 계산 비용", "계산 비용 : 수업에서 미세조정만 하는 이유", "16큐빗 회로 시뮬레이션이 비싸 25 epoch 사전학습에 196분(약 3시간 15분)이 걸림",
    "- 1 epoch = DF 115장을 batch 4로 28 step. checkpoint 기록상 epoch당 평균 7.8분(453 ~ 487초).\n- 1 step 약 20초: batch 4 × 샘플당 약 3초(판별자 step + 생성자 step).\n- 큐빗 수에 따른 비용: 16큐빗은 12큐빗 대비 상태벡터가 16배(2^16 vs 2^12), 실측 소요시간은 약 20배였음(3일차 노트북 §6 ④).\n- 그래서 수업에서는 10 epoch checkpoint(약 80분 학습분)에서 출발해 20 step만 더 돌림.");
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
newSection("PART 3 · 비교");
{
  const s = slide("SECTION_DARK", "PART 3 · 노트북 §5", "QGAN vs MediQ-GAN", "두 모델의 출력을 0 ~ 1로 되돌린 뒤 같은 지표 4종으로 비교함");
  sectionRows(s, [["노트북 범위", "§5 지표 비교표, 상관계수·픽셀 분포 그림"],
    ["다루는 코드", "gm.comparison_table · to_unit_scale(x, 'prob' / 'tanh')"]]);
}
{
  const s = slide("CONTENT", "PART 3 · 노트북 §5", "지표 비교 : 형태 재현과 다양성", "상관은 MediQ-GAN이 높고, 샘플 간 거리는 QGAN이 실제 DF에 가까움",
    "- MediQ-GAN 25 epoch: 클래스 평균 상관 0.365로 QGAN(0.195)보다 높음 - 평균적인 병변 형태를 더 잘 맞춤.\n- 그러나 샘플 간 거리 0.30은 실제 DF(2.505)의 약 1/8 - 비슷한 이미지를 반복 생성(mode collapse 경향).\n- QGAN은 상관이 낮지만 다양성 1.92로 실제 분포에 가까움.\n- 10 epoch(0.018)과 25 epoch(0.365) 차이로 학습량이 결과를 크게 바꾼다는 점도 확인함.\n- 이 자료 작성 중 노트북 실행 결과: MediQ-GAN 25 epoch 상관 0.366, 다양성 0.285 - README와 일치.");
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
  source(s, "수치: README 결과표 (로컬 CPU). MediQ-GAN은 16장, QGAN은 64장으로 평가");
}
{
  const s = slide("CONTENT", "PART 3 · 결과 해석", "결과 해석 : 두 모델의 한계", "QGAN은 형태 재현이 약하고, MediQ-GAN은 평균 이미지에 가까운 그림을 반복함",
    "- MediQ-GAN의 최근접 실제 거리 3.44는 QGAN(1.64)의 두 배. 생성 이미지가 어떤 실제 이미지와도 가깝지 않음 → 개별 병변이 아니라 평균적인 형태를 반복해 그린다는 해석과 맞음(상관은 높고 다양성은 낮음).\n- 클래스 평균 상관(②)은 평균 형태만 보므로, 같은 평균 이미지를 반복해도 높게 나옴. ②만 보면 MediQ-GAN이 낫다고 잘못 결론 내리게 됨.\n- 토론: 데이터 증강이 목적이라면 어느 쪽이 더 쓸모 있는가 / 지표 하나로 순위를 매길 수 있는가.");
  table(s, [
    ["지표", "QGAN 600 step", "MediQ-GAN 25 epoch", "의미"],
    ["② 클래스 평균 상관 ↑", "0.195", { text: "0.365", options: { bold: true, color: C.accent2 } }, "평균 형태는 MediQ-GAN이 더 가까움"],
    ["③ 최근접 실제 거리", "1.64", "3.44", "MediQ-GAN은 실제 이미지 어느 것과도 멂"],
    ["④ 샘플 간 거리 (실제 2.505)", { text: "1.92", options: { bold: true, color: C.accent1 } }, "0.30", "MediQ-GAN은 비슷한 그림을 반복"],
  ], 0.6, 2.25, 12.1, [3.2, 2.2, 2.4, 4.3], { fontSize: 13, rowH: 0.55 });
  text(s, "해석", 0.6, 4.6, 12.1, 0.35, { fontSize: 14, bold: true, color: C.accent1 });
  text(s, [
    { text: "QGAN: 다양성은 실제에 가깝지만 병변 형태 재현이 약함. patch를 서로 독립적으로 만들어 이미지 전체 구조를 잡기 어려움.", options: { breakLine: true } },
    { text: "MediQ-GAN: 평균 형태는 잘 맞추지만 다양성이 실제의 1/8. 최종 출력을 고전 decoder가 만들기 때문에 Tanh가 포화되면 z와 무관한 이미지가 나옴.", options: { breakLine: true } },
    { text: "②만 보면 MediQ-GAN이 낫다고 결론 내리게 됨. ②는 평균 형태만 보므로 같은 이미지를 반복해도 높게 나옴." },
  ], 0.6, 5.0, 12.1, 1.6, { fontSize: 13, paraSpaceAfter: 6 });
}

// =====================================================================
newSection("PART 4 · 토론");
{
  const s = slide("CONTENT", "PART 4 · 노트북 §6", "이미지 생성에서 양자컴퓨팅의 한계", "3일 동안의 실습에서 확인한 내용 (노트북 §6)",
    "노트북 §6 내용 요약.\n① 2일차 QGAN: ancilla qubit 없이 측정하면 patch 합이 1로 고정되어 학습이 무너졌음(8×8 단계 사전 실험).\n② 두 모델 모두 exact 상태벡터 시뮬레이터로 학습함(shot 없음). 실제 장치는 parameter-shift가 필요함.\n③ 16×16에서는 FID가 의미 없음 - '어떤 지표로 좋다고 할 것인가'가 아직 열린 문제.\n④ 16큐빗은 12큐빗 대비 상태 16배, 시간 약 20배.\n⑤ 원 논문은 WGAN-GP critic으로 판별자를 제약함. 고전 쪽 학습 안정화가 결과를 좌우함.\n⑥ 양자 생성모델은 양자 데이터·해밀토니안 상태 생성에서 먼저 의미를 가짐. 고전 데이터 영역의 우위는 아직 검증 단계.");
  table(s, [
    ["", "관찰", "실습에서 확인한 근거"],
    ["①", "측정 방식이 학습 성패를 가름", "ancilla qubit = 0만 쓰도록 바꾸자 생성 평균과 실제 평균의 상관 0.00 → 0.49 (8×8 사전 실험)"],
    ["②", "현재 학습은 시뮬레이터에서만 가능한 규모", "두 모델 모두 exact 상태벡터 시뮬레이션. 실제 장치는 parameter-shift로 파라미터당 회로 2회 × shot"],
    ["③", "해상도 한계가 평가 한계로 이어짐", "16×16에서는 FID를 쓸 수 없어 지표 4종으로 대신함"],
    ["④", "큐빗 수에 지수적으로 늘어나는 비용", "16큐빗은 12큐빗 대비 상태벡터 16배, 실측 시간 약 20배"],
    ["⑤", "고전 쪽 학습 안정화가 결과를 좌우", "BCE 판별자가 쉽게 이김. 원 논문은 WGAN-GP critic으로 판별자를 제약"],
    ["⑥", "고전 이미지 생성에서의 우위는 미검증", "양자 생성모델은 양자 데이터·해밀토니안 상태 생성에서 먼저 의미를 가짐"],
  ], 0.6, 2.25, 12.1, [0.5, 4.0, 7.6], { fontSize: 12.5, rowH: 0.58 });
}
{
  const s = slide("CONTENT", "PART 4 · 참고", "MediQ-GAN 원 논문 결과", "논문 수치 인용 - 실습의 16×16 결과와 직접 비교하지 않음",
    "- 세 데이터셋 모두 클래스별 FID가 최고 또는 차상위(논문 Table 2). ODIR-5k 행만 FID가 아니라 증강 후 분류 성능(Table 1)임.\n- 원 논문은 64×64 RGB, WGAN-GP critic, GPU 학습 조건. 실습 결과와 같은 선상에서 비교하지 않음.\n- 비교 대상에 diffusion 모델(DiT)까지 포함되어 있다는 점, IBM 실기기(ibm_marrakesh)에서 추론을 검증했다는 점을 짚음.\n- 시사점: '생성자 전체를 양자로'보다 '전역 구조는 고전, 세부는 양자'인 layer-level hybrid가 더 높은 해상도로 확장되고 있음.");
  table(s, [
    ["데이터셋", "내용", "결과"],
    ["ISIC 2019", "피부경검사 8클래스", "소수클래스(df, vasc, scc)에서 모든 고전 baseline보다 낮은 FID"],
    ["ODIR-5k", "안저사진", "증강 후 분류: 두 backbone(EfficientNet-B0, ViT-small) 모두 최고 성능"],
    ["RetinaMNIST", "다운샘플 안저사진", "5개 클래스 중 4개에서 최저(최고품질) FID"],
  ], 0.6, 2.25, 12.1, [2.2, 2.6, 7.3], { fontSize: 13, rowH: 0.6 });
  text(s, [
    { text: "비교 대상  ", options: { bold: true, color: C.accent1 } },
    { text: "DCGAN, WGAN-GP, Structure-Preserving GAN, StyleGAN2-ADA, FastGAN, DiT · Stable Diffusion 3(LoRA 미세조정), 이전 세대 hybrid 모델 MosaiQ", options: { breakLine: true } },
    { text: "실기기 검증  ", options: { bold: true, color: C.accent2 } },
    { text: "IBM 양자 장치(ibm_marrakesh)에서 대표 클래스의 추론만 검증 (대기열·shot 제한)" },
  ], 0.6, 4.95, 12.1, 1.3, { fontSize: 13, paraSpaceAfter: 10 });
  source(s, "출처: Jiao et al., MediQ-GAN, arXiv:2506.21015v2, Table 1 · 2");
}

// =====================================================================
newSection("정리");
{
  const s = slide("CONTENT", "정리", "3일차 정리", "MediQ-GAN 구조와 미세조정, QGAN과의 비교",
    "오늘 다룬 내용을 PART 순서대로 정리함.");
  summary(s, [
    ["hybrid 수준", "QGAN은 생성자 전체가 양자회로(model-level), MediQ-GAN은 생성자 안의 양자 stream만 양자회로(layer-level)"],
    ["dual-stream", "잠재벡터 256차원을 절반씩 고전 MLP와 양자 stream으로 나눠 처리한 뒤 concat → decoder → Tanh"],
    ["양자 stream", "16큐빗 × depth 8 회로 5개가 16 site 중 5개만 처리. PauliX 기댓값 출력이라 ancilla qubit이 필요 없음"],
    ["파라미터와 비용", "30,000개 중 양자 회전각은 640개(2.1%)지만 학습 시간 대부분이 16큐빗 시뮬레이션 (25 epoch 196분)"],
    ["checkpoint와 미세조정", "config로 같은 구조를 만든 뒤 가중치를 불러옴. 판별자도 같은 시점 상태로 불러와 20 step 추가 학습"],
    ["학습 안정성", "BCE 판별자가 쉽게 이김 (lr_g 0.02에서 3 epoch 만에 mode collapse). 원 논문은 WGAN-GP critic을 씀"],
    ["비교 결과", "상관은 MediQ-GAN 0.365 > QGAN 0.195, 다양성은 QGAN 1.92 > MediQ-GAN 0.30. 지표 하나로 순위를 정하지 않음"],
  ]);
}

(async () => {
  // pptxgenjs 4.0.1의 writeFile은 Node에서 compression 옵션을 무시해 zip이 비압축(약 6배 크기)으로 저장됨 - STREAM으로 받아 직접 씀
  const buf = await pres.write({ outputType: "STREAM", compression: true });
  require("fs").writeFileSync(OUT, buf);
  console.log("wrote", OUT);
})();
