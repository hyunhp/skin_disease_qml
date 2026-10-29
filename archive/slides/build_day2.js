const pptxgen = require("pptxgenjs");

const OUT = process.argv[2] || "day2_practice_slides.pptx";

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
pres.title = "2일차 실습 설명 자료";
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

// =====================================================================
newSection("표지");
{
  const s = slide("TITLE_DARK", "QML Lecture · 2일차", "실습 설명 자료", "segmentation 전처리 → 양자 회로 → QGAN 학습",
    "2일차 노트북(practice/day2_practice.ipynb)의 내용을 설명하는 자료.\n- 코드 중심으로 구성함. 각 PART 첫 장에 해당 노트북 섹션을 표시함.\n- PART 0은 1일차 내용 복습임.");
  s.addShape(pres.shapes.OVAL, { x: 10.55, y: 0.85, w: 1.55, h: 1.55, fill: { color: C.text2 }, line: { color: C.accent1, width: 1.25 } });
  s.addShape(pres.shapes.OVAL, { x: 11.0, y: 1.3, w: 0.65, h: 0.65, fill: { color: C.accent1 }, line: { type: "none" } });
}

// ---------- 진행 ----------
newSection("진행");
{
  const s = slide("CONTENT", "오리엔테이션", "2일차 진행 순서", "노트북 섹션과 이 자료의 PART 대응",
    "- 학습 셀(§5)은 Colab 무료 CPU에서 400 step 약 35분 걸림(실측).\n- §3 segmentation은 1장당 수 초라 5장만 직접 처리하고, 학습은 저장소의 전처리 자산(DF 115장)으로 함.");
  const hl = (t) => ({ text: t, options: { bold: true, color: C.accent1 } });
  table(s, [
    ["노트북", "내용", "설명 자료"],
    ["§0 – §2", "Colab 설정, HAM10000 다운로드와 EDA", "PART 0 · 1"],
    ["§3", "segmentation 전처리 (K-means + FCM), 16×16 축소. 1장당 수 초라 5장만 직접 처리", "PART 1"],
    ["§4", "sub-generator 회로 1개를 만들고 출력 확인", "PART 2"],
    [hl("§5"), hl("QGAN 학습 400 step - Colab CPU 약 35분"), hl("PART 3")],
    ["§6", "생성 이미지 평가 (지표 4종)", "PART 4"],
    ["§7", "checkpoint를 Google Drive에 저장", "-"],
  ], 0.6, 2.25, 12.1, [1.6, 8.5, 2.0], { fontSize: 13, rowH: 0.55 });
}

// =====================================================================
newSection("PART 0 · 1일차 복습");
{
  const s = slide("SECTION_DARK", "PART 0", "1일차 복습", "오늘 구현하는 QGAN의 구조와 논문 대비 축소 범위",
    "1일차에서 다룬 QGAN 논문(Andra et al.)의 구조를 코드 관점에서 다시 정리함.\n- 오늘은 1일차 그림을 PennyLane·PyTorch 코드로 옮기는 날이라는 점을 먼저 짚음.");
  const rows = [["오늘 구현하는 것", "논문 ① QGAN의 patch 방식 생성자 - sub-generator 4개 + 고전 판별자"],
    ["입력 데이터", "HAM10000 DF 115장 → segmentation → 16×16 그레이스케일"],
    ["오늘의 결과물", "직접 학습한 생성자 checkpoint + 생성품질 지표 4종 표 (3일차 비교 기준)"]];
  rows.forEach((r, i) => {
    text(s, r[0], 0.9, 3.25 + i * 0.95, 2.6, 0.4, { fontSize: 14, bold: true, color: C.accent3 });
    text(s, r[1], 3.6, 3.25 + i * 0.95, 8.8, 0.4, { fontSize: 15, color: C.background1 });
  });
}
{
  const s = slide("CONTENT", "PART 0 · 1일차 복습", "QGAN 구조 : 생성자만 양자회로", "patch 방식: sub-generator마다 이미지 조각(patch)을 하나씩 만들고 이어붙임",
    "1일차 슬라이드 7~10 복습.\n- 생성자 = 변분 양자회로(PQC) 여러 개, 판별자 = 고전 신경망(논문 Table 4)인 비대칭 구조.\n- 학습 대상은 회전 게이트 각도 θ. 판별 결과의 손실을 θ까지 역전파해 갱신함.\n- 오늘 코드에서는 PatchQuantumGenerator 클래스가 왼쪽 상자 전체에 해당함.");
  // noise
  box(s, "노이즈 z\n(무작위 각도)", 0.6, 3.35, 1.6, 1.0, HEX.card2, C.text1, { fontSize: 12 });
  // generator container
  card(s, 2.6, 2.2, 3.9, 3.9, HEX.mint, { line: HEX.green });
  text(s, "생성자 = PatchQuantumGenerator", 2.8, 2.32, 3.6, 0.3, { fontSize: 12, bold: true, color: C.accent1 });
  for (let g = 0; g < 4; g++) {
    box(s, `sub-generator ${g + 1}  (7큐빗 PQC)`, 2.85, 2.8 + g * 0.78, 2.4, 0.58, C.accent1, C.background1, { fontSize: 11 });
    box(s, `patch ${g + 1}`, 5.45, 2.8 + g * 0.78, 0.85, 0.58, HEX.white, C.text1, { fontSize: 11, line: HEX.line });
    arrow(s, 5.27, 3.09 + g * 0.78, 5.43, 3.09 + g * 0.78);
  }
  arrow(s, 2.22, 3.85, 2.58, 3.85);
  // concat image
  box(s, "이어붙인 이미지\n16×16 = 256픽셀", 7.0, 3.35, 1.9, 1.0, HEX.card2, C.text1, { fontSize: 12 });
  arrow(s, 6.52, 3.85, 6.98, 3.85);
  box(s, "판별자\n고전 5층 FC\n(논문 Table 4)", 9.4, 3.2, 1.8, 1.3, C.accent2, C.background1, { fontSize: 12 });
  arrow(s, 8.92, 3.85, 9.38, 3.85);
  box(s, "진짜일\n확률", 11.65, 3.45, 1.05, 0.8, HEX.lav, C.text1, { fontSize: 12 });
  arrow(s, 11.22, 3.85, 11.63, 3.85);
  box(s, "실제 DF 이미지", 9.4, 5.35, 1.8, 0.6, HEX.card2, C.text1, { fontSize: 12 });
  arrow(s, 10.3, 5.33, 10.3, 4.52);
  // feedback
  s.addShape(pres.shapes.LINE, { x: 4.55, y: 6.4, w: 7.6, h: 0, line: { color: C.accent4, width: 1.5, dashType: "dash" } });
  s.addShape(pres.shapes.LINE, { x: 12.15, y: 4.27, w: 0, h: 2.13, line: { color: C.accent4, width: 1.5, dashType: "dash" } });
  s.addShape(pres.shapes.LINE, { x: 4.55, y: 6.12, w: 0, h: 0.28, line: { color: C.accent4, width: 1.5, dashType: "dash", beginArrowType: "triangle" } });
  text(s, "손실 → 역전파 → 회전각 θ 갱신", 6.2, 6.47, 4.5, 0.32, { fontSize: 12, bold: true, color: C.accent4, align: "center" });
}
{
  const s = slide("CONTENT", "PART 0 · 1일차 복습", "논문과 오늘 실습의 차이", "회로의 형태(RY encoding + RY·CZ 변분층 + post-selection)는 같고, 규모와 학습량을 줄임",
    "README '원 논문과 다른 점' 표와 같은 내용.\n- sub-generator 수는 처음에 논문과 큐빗 수가 가까운 2개로 정했다가, 2·4·8·16개를 같은 조건(600 step, depth 10)으로 실측해 품질이 가장 좋은 4개로 바꿈(README 실험 표).\n- 16개(논문 설정)는 판별자가 이겨 loss_d가 0.003까지 떨어짐.\n- 실습은 exact 상태벡터 시뮬레이션이라 shot noise와 하드웨어 오류가 없음.");
  table(s, [
    ["항목", "논문 (Andra et al.)", "2일차 실습", "이유"],
    ["sub-generator", "16개", "4개", "2·4·8·16개 실측 중 품질 최고"],
    ["큐빗 (sub-generator당)", "데이터 7 + ancilla 1", "데이터 6 + ancilla 1", "256 = 4 × 2⁶"],
    ["회로 depth", "10", "10", "논문과 동일"],
    ["판별자", "5층 FC (Table 4)", "5층 FC (Table 4)", "논문과 동일"],
    ["학습량", "2,000 epoch (1 ~ 1.5시간)", "400 step (Colab 약 35분)", "수업 시간 안에 완료"],
    ["실행 환경", "GPU", "Colab CPU, exact 시뮬레이션", "설치·계정 불필요"],
  ], 0.6, 2.25, 12.1, [2.6, 3.0, 3.2, 3.3], { fontSize: 13, rowH: 0.5 });
  text(s, "논문 설정인 sub-generator 16개로 학습하면 판별자가 이겨 loss_d가 0.003까지 떨어짐. 용량을 늘려도 품질이 오르지 않았음.", 0.6, 5.85, 12.1, 0.4, { fontSize: 12.5, color: C.accent6 });
  source(s, "논문 값: Andra et al. 프리프린트 Table 3 · 실습 값: README sub-generator 실험");
}

// =====================================================================
newSection("PART 1 · 데이터와 전처리");
{
  const s = slide("SECTION_DARK", "PART 1 · 노트북 §2 – §3", "데이터와 segmentation 전처리", "HAM10000에서 DF·NV를 고르고, 병변만 남겨 16×16으로 줄이는 과정");
  sectionRows(s, [["노트북 범위", "§2 EDA, §3 segmentation 전처리"],
    ["다루는 코드", "segment_fcm_kmeans · resize_for_encoding · preprocess_class"],
    ["논문 근거", "Andra et al. Section 3.1 (K-means + Fuzzy C-means), Table 10"]]);
}
{
  const s = slide("CONTENT", "PART 1 · 노트북 §2", "범위 축소 : DF vs NV", "7개 클래스 중 가장 적은 DF를 증강 대상으로, 가장 많은 NV를 비교 대상으로 둠",
    "- DF 115장 대 NV 6,705장, 약 1:58 불균형.\n- 증강 대상은 DF. NV는 3일차까지 '클래스 평균 상관계수' 지표에서 비교용으로만 씀(345장 사용).\n- 코드의 value_counts()는 진단명(dx)별 이미지 수를 많은 순으로 반환함.");
  table(s, [
    ["클래스", "이미지 수", "비율", "실습에서의 역할"],
    [{ text: "DF (피부섬유종)", options: { bold: true, color: C.accent1 } }, { text: "115", options: { bold: true, color: C.accent1 } }, "1.1%", "증강 대상 - 생성자 학습 데이터"],
    ["NV (모반)", "6,705", "66.9%", "비교 대상 - 지표 ② 기준 (345장 사용)"],
    ["전체 7개 클래스", "10,015", "100%", "DF : NV = 1 : 58"],
  ], 0.6, 2.25, 12.1, [3.0, 1.8, 1.4, 5.9], { fontSize: 13, rowH: 0.5 });
  code(s, [
    'metadata = pd.read_csv(f"{DATA_DIR}/HAM10000_metadata.csv")',
    { t: 'counts = metadata["dx"].value_counts()', hl: true },
    "",
    "# df     115   <- 증강 대상",
    "# nv    6705   <- 비교 대상",
  ], 0.6, 4.55, 7.0, 2.0, 13);
  text(s, [
    { text: "metadata는 image_id와 진단명(dx)을 연결하는 표임", options: { bullet: true, breakLine: true } },
    { text: "이미지 파일은 part_1·part_2 두 폴더에 나뉘어 있어 find_image_path가 양쪽을 확인함", options: { bullet: true } },
  ], 7.9, 4.65, 4.8, 1.6, { fontSize: 13, paraSpaceAfter: 8, color: C.accent6 });
  source(s, "HAM10000 메타데이터 (Tschandl et al., Scientific Data 5, 180161, 2018)");
}
{
  const s = slide("CONTENT", "PART 1 · 노트북 §3", "전처리 pipeline", "원본 → 병변만 남긴 64×64 → 16×16, 0 ~ 1. 저장소 자산(df_preprocessed.npy)도 같은 조건으로 만들어짐",
    "- 64×64로 먼저 줄이는 이유: 600×450 원본(27만 픽셀)으로 FCM을 돌리면 1장에 수십 초가 걸림. 64×64(4,096픽셀)면 수 초.\n- 가장 어두운 cluster를 병변으로 봄: 피부경 이미지에서 병변이 주변 피부보다 어둡다는 가정. 털·그림자가 많은 이미지에서는 틀릴 수 있음(한계).\n- 마지막 /255로 0 ~ 1 척도가 됨. 이 척도가 '전처리 데이터 = unit 척도'의 기준임.");
  const flow = [["원본", "600×450 RGB"], ["그레이 + 축소", "64×64\nINTER_AREA"], ["K-means", "k = 4\n사전 cluster"], ["FCM", "m = 2\n소속도 정제"],
    ["mask", "가장 어두운\ncluster = 병변"], ["축소 + 정규화", "16×16\n/255 → 0 ~ 1"]];
  const w = 1.75, gap = 0.32, y = 2.5;
  flow.forEach((f, i) => {
    const x = 0.6 + i * (w + gap);
    const hl = i === 2 || i === 3;
    card(s, x, y, w, 1.75, hl ? HEX.mint : HEX.card, { line: hl ? HEX.green : undefined });
    text(s, f[0], x + 0.15, y + 0.2, w - 0.3, 0.4, { fontSize: 15, bold: true, align: "center", color: hl ? C.accent1 : C.text1 });
    text(s, f[1], x + 0.15, y + 0.7, w - 0.3, 0.9, { fontSize: 12, color: C.accent6, align: "center" });
    if (i < flow.length - 1) arrow(s, x + w + 0.03, y + 0.88, x + w + gap - 0.03, y + 0.88);
  });
  text(s, "논문 Section 3.1의 K-means + Fuzzy C-means hybrid segmentation", 2.4, 4.35, 4.75, 0.4, { fontSize: 12, color: C.accent1, align: "center" });
  // why segmentation
  barList(s, [["병변만 남기는 이유", "논문 Table 10: raw 이미지로 증강하면 분류 성능이 오히려 떨어지고, segmentation을 거친 이미지에서만 개선됨"]], 0.6, 5.1, 5.9, 1.4);
  barList(s, [["64×64를 거치는 이유", "FCM 비용이 픽셀 수에 비례함. 원본 27만 픽셀 대신 4,096픽셀로 clustering해 1장당 수 초로 줄임"]], 6.8, 5.1, 5.9, 1.4);
}
{
  const s = slide("CONTENT", "PART 1 · 노트북 §3 코드", "segment_fcm_kmeans 코드", "밝기 1채널만 써서 4개 cluster로 나누고, 가장 어두운 cluster를 남김",
    "- ① 위치 정보 없이 밝기만으로 clustering함. pixels 모양은 (픽셀 수, 1).\n- ② sklearn KMeans 기본 초기화는 k-means++. n_init=4는 초기화를 4번 바꿔 inertia가 가장 낮은 결과를 씀.\n- ③ K-means 중심까지 거리의 역제곱으로 FCM 초기 소속도를 만듦(m=2일 때 FCM 소속도 공식과 같은 형태). 무작위 시작보다 빨리 수렴하고 결과가 매번 같음.\n- ④ FCM 결과 소속도가 가장 큰 cluster로 hard 라벨을 정한 뒤, 중심 밝기가 가장 낮은 cluster를 병변으로 봄.\n- ⑤ bitwise_and(gray, gray, mask)는 x & x = x라 연산 효과는 없고 mask 효과만 남음.");
  code(s, [
    "gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)",
    "gray = cv2.resize(gray, (64, 64), interpolation=cv2.INTER_AREA)",
    { t: "pixels = gray.reshape(-1, 1).astype(np.float32)      # 1", hl: true },
    "",
    { t: "km = KMeans(n_clusters=4, n_init=4, random_state=0)  # 2", hl: true },
    "km = km.fit(pixels)",
    "dist = np.abs(pixels - km.cluster_centers_.reshape(1, -1))",
    { t: "u_init = 1.0 / (dist + 1e-6) ** 2                    # 3", hl: true },
    "u_init = (u_init / u_init.sum(axis=1, keepdims=True)).T",
    "",
    "cntr, u, *_ = fuzz.cluster.cmeans(pixels.T, c=4, m=2.0,",
    "                 error=1e-4, maxiter=100, init=u_init)",
    { t: "membership = np.argmax(u, axis=0)                    # 4", hl: true },
    "lesion = np.argmin(cntr.flatten())",
    "mask = ((membership == lesion).reshape(64, 64) * 255).astype(np.uint8)",
    { t: "return cv2.bitwise_and(gray, gray, mask=mask)        # 5", hl: true },
  ], 0.6, 2.2, 7.6, 4.45, 11.5);
  barList(s, [
    ["① 밝기만 사용", "위치 정보 없이 (픽셀 수, 1)로 clustering"],
    ["② K-means 사전 cluster", "k-means++ 초기화 4회 중 최선 채택"],
    ["③ FCM 초기 소속도", "중심 거리의 역제곱 - 수렴이 빠르고 재현 가능"],
    ["④ 병변 cluster 선택", "중심이 가장 어두운 cluster = 병변"],
    ["⑤ mask 적용", "병변은 원래 밝기 유지, 배경은 0"],
  ], 8.5, 2.2, 4.2, 0.9, C.accent4);
}
{
  const s = slide("CONTENT", "PART 1 · 노트북 §3", "K-means와 Fuzzy C-means", "K-means는 픽셀마다 cluster 하나, FCM은 cluster별 소속도를 나눠 가짐",
    "- 경계 픽셀(병변 가장자리)은 어느 한쪽으로 딱 나누기 어려움. FCM은 '병변 60%, 피부 40%'처럼 표현해 경계가 덜 거칠어짐.\n- 이 코드는 마지막에 argmax로 hard 라벨을 다시 만들기 때문에, FCM의 이점은 '경계 픽셀의 배정이 더 안정적'이라는 데 있음.\n- fpc는 분할 선명도(1에 가까울수록 명확). 이미지별 품질 점검에 쓸 수 있음.");
  table(s, [
    ["", "K-means", "Fuzzy C-means (FCM)"],
    ["배정 방식", "hard - 픽셀마다 cluster 1개", "soft - 소속도 u (픽셀별 합 = 1)"],
    ["중심 갱신", "배정된 픽셀의 평균", "소속도^m 가중 평균"],
    ["주요 파라미터", "n_clusters, n_init", "c, m (fuzziness), error, maxiter, init"],
    ["이 코드에서의 역할", "FCM 초기값을 만드는 사전 cluster", "소속도 정제 → argmax로 최종 라벨"],
    ["출력", "cluster_centers_, labels_", "cntr, u, u0, d, jm, p, fpc"],
  ], 0.6, 2.25, 7.4, [2.0, 2.6, 2.8], { fontSize: 13, rowH: 0.55 });
  card(s, 8.3, 2.25, 4.4, 4.0, HEX.lav);
  text(s, "m (fuzziness)", 8.55, 2.45, 3.9, 0.35, { fontSize: 15, bold: true, color: C.accent2 });
  text(s, [
    { text: "m → 1: K-means처럼 딱 잘라 나뉨", options: { bullet: true, breakLine: true } },
    { text: "m이 클수록 소속이 여러 cluster로 퍼짐", options: { bullet: true, breakLine: true } },
    { text: "보통 2를 씀 (이 코드도 2)", options: { bullet: true } },
  ], 8.55, 2.95, 3.9, 1.5, { fontSize: 13, paraSpaceAfter: 6 });
  text(s, "fpc (0 ~ 1)", 8.55, 4.55, 3.9, 0.35, { fontSize: 15, bold: true, color: C.accent2 });
  text(s, "분할 선명도. 1에 가까울수록 명확하고, 1/c(여기서는 0.25)에 가까울수록 모호함", 8.55, 5.0, 3.9, 1.0, { fontSize: 13 });
}
{
  const s = slide("CONTENT", "PART 1 · 노트북 §3", "16×16 해상도와 축소 방법", "픽셀 수가 큐빗 수를 정함. 256픽셀 = sub-generator 4개 × 2⁶",
    "- 측정 결과(basis state) 2^n개가 픽셀 n개에 대응하므로 patch 픽셀 수의 log2가 데이터 큐빗 수가 됨.\n- 생성자 출력 256개는 patch 순서대로 이어붙이므로, 16×16으로 reshape하면 patch 하나가 가로 16 × 세로 4 띠가 됨.\n- INTER_AREA: 출력 픽셀이 덮는 원본 영역의 평균. 크게 줄일 때 정보가 고르게 반영됨. LINEAR는 주변 2×2만 참조해 축소 폭이 크면 작은 병변이 사라지거나 앨리어싱이 생김.");
  // 16x16 grid with 4 bands
  const gx = 0.9, gy = 2.3, cell = 0.235;
  const fills = [HEX.mint, HEX.lav, HEX.cream, HEX.card2];
  for (let p = 0; p < 4; p++) {
    s.addShape(pres.shapes.RECTANGLE, { x: gx, y: gy + p * 4 * cell, w: 16 * cell, h: 4 * cell, fill: { color: fills[p] }, line: { color: HEX.line, width: 0.75 } });
    text(s, `patch ${p + 1}  ·  64픽셀 (16 × 4)`, gx, gy + p * 4 * cell, 16 * cell, 4 * cell, { fontSize: 13, bold: true, align: "center", valign: "middle", color: C.text1 });
  }
  for (let i = 1; i < 16; i++) {
    s.addShape(pres.shapes.LINE, { x: gx + i * cell, y: gy, w: 0, h: 16 * cell, line: { color: "FFFFFF", width: 0.5, transparency: 40 } });
  }
  text(s, "16 × 16 = 256픽셀", gx, gy + 16 * cell + 0.1, 16 * cell, 0.35, { fontSize: 12, color: C.accent6, align: "center" });
  // formula
  card(s, 5.2, 2.3, 7.5, 1.6, HEX.card);
  text(s, "큐빗 수 계산", 5.45, 2.45, 7.0, 0.35, { fontSize: 14, bold: true, color: C.accent1 });
  text(s, "256 ÷ 4 = 64픽셀/patch  →  log₂ 64 = 6 데이터 큐빗  →  + ancilla 1 = 7큐빗", 5.45, 2.9, 7.0, 0.8, { fontSize: 14, bold: true });
  table(s, [
    ["보간법", "방식", "16×16 축소에서"],
    ["INTER_AREA", "출력 픽셀이 덮는 영역의 평균", "사용 - 저장소 자산과 같은 조건"],
    ["INTER_LINEAR", "주변 2×2 선형 보간 (기본값)", "큰 축소에서 앨리어싱"],
    ["INTER_NEAREST", "가장 가까운 픽셀 1개 복사", "마스크용, 밝기 정보 손실"],
  ], 5.2, 4.15, 7.5, [2.0, 2.9, 2.6], { fontSize: 12, rowH: 0.48 });
}

// =====================================================================
newSection("PART 2 · 양자 회로");
{
  const s = slide("SECTION_DARK", "PART 2 · 노트북 §4 – §5", "양자 회로 : sub-generator 하나", "노이즈 encoding → 변분층 반복 → 측정 → post-selection",
    "§4는 학습 없이 회로 출력만 확인하는 섹션임. §5 앞부분에서 생성자·판별자를 정의함.");
  sectionRows(s, [["노트북 범위", "§4 회로 1개 출력 확인, §5 생성자·판별자 정의"],
    ["다루는 코드", "sub_generator_circuit · probs_all[::2] · PatchQuantumGenerator"]]);
}
{
  const s = slide("CONTENT", "PART 2 · 노트북 §4 코드", "sub-generator 회로", "RY로 노이즈를 넣고, [학습 RY + 인접 CZ]를 10번 반복한 뒤 7큐빗 전체를 측정",
    "- 노이즈 encoding: 샘플마다 0 ~ π 난수 각도. 같은 가중치에서 다른 이미지가 나오는 원천.\n- RY는 상태 진폭을 실수로 유지한 채 회전시켜 측정 확률을 직접 바꿈. 확률 = 픽셀 밝기이므로 RY만으로 충분함.\n- CZ는 인접 큐빗을 얽어 픽셀 사이 상관을 만듦. CZ가 없으면 각 큐빗이 독립이라 확률 분포가 곱 형태로 제한됨.\n- qml.probs는 2^7 = 128개 basis state의 확률을 반환함.");
  code(s, [
    "@qml.qnode(dev)",
    "def sub_generator_circuit(noise, weights):",
    { t: "    for i in range(N_QUBITS):           # 1 encoding", hl: true },
    "        qml.RY(noise[i], wires=i)",
    { t: "    for layer in range(Q_DEPTH):        # 2 x 10", hl: true },
    "        for i in range(N_QUBITS):",
    "            qml.RY(weights[layer, i], wires=i)",
    "        for i in range(N_QUBITS - 1):",
    "            qml.CZ(wires=[i, i + 1])",
    { t: "    return qml.probs(wires=range(N_QUBITS))  # 3", hl: true },
  ], 0.6, 2.2, 6.4, 3.6, 12);
  text(s, "weights 모양 (10, 7) - sub-generator 하나당 학습 파라미터 70개", 0.6, 6.0, 6.4, 0.5, { fontSize: 12.5, color: C.accent6 });
  // circuit diagram
  const dx = 7.4, wy0 = 2.45, sp = 0.5;
  const labels = ["q0", "q1", "q2", "q3", "q4", "q5", "anc"];
  card(s, dx, 2.2, 5.3, 4.4, HEX.card);
  labels.forEach((l, i) => {
    const y = wy0 + 0.15 + i * sp;
    text(s, l, dx + 0.15, y - 0.15, 0.45, 0.3, { fontSize: 11, bold: true, color: i === 6 ? C.accent4 : C.text1, valign: "middle" });
    s.addShape(pres.shapes.LINE, { x: dx + 0.6, y, w: 4.5, h: 0, line: { color: C.accent6, width: 0.75 } });
    box(s, "RY(z)", dx + 0.75, y - 0.17, 0.75, 0.34, C.accent1, C.background1, { fontSize: 9 });
    box(s, "RY(θ)", dx + 2.0, y - 0.17, 0.75, 0.34, C.accent1, C.background1, { fontSize: 9 });
    box(s, "M", dx + 4.45, y - 0.17, 0.45, 0.34, C.accent4, C.background1, { fontSize: 10 });
    if (i < 6) {
      const xx = dx + 3.05 + (i % 3) * 0.32;
      s.addShape(pres.shapes.OVAL, { x: xx - 0.06, y: y - 0.06, w: 0.12, h: 0.12, fill: { color: C.text1 }, line: { type: "none" } });
      s.addShape(pres.shapes.OVAL, { x: xx - 0.06, y: y + sp - 0.06, w: 0.12, h: 0.12, fill: { color: C.text1 }, line: { type: "none" } });
      s.addShape(pres.shapes.LINE, { x: xx, y, w: 0, h: sp, line: { color: C.text1, width: 1.25 } });
    }
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: dx + 1.85, y: wy0 - 0.1, w: 2.35, h: 3.55, fill: { type: "none" }, rectRadius: 0.1, line: { color: C.accent1, width: 1.25, dashType: "dash" } });
  text(s, "① encoding", dx + 0.6, 6.05, 1.2, 0.3, { fontSize: 11, bold: true, color: C.accent1, align: "center" });
  text(s, "② × 10 (RY + CZ 사슬)", dx + 1.85, 6.05, 2.35, 0.3, { fontSize: 11, bold: true, color: C.accent1, align: "center" });
  text(s, "③ 측정", dx + 4.2, 6.05, 0.95, 0.3, { fontSize: 11, bold: true, color: C.accent4, align: "center" });
}
{
  const s = slide("CONTENT", "PART 2 · 노트북 §4 코드", "ancilla qubit과 post-selection", "128개 확률 중 ancilla qubit = 0인 64개만 patch로 씀. 코드로는 probs_all[::2]",
    "- PennyLane은 wire 0을 최상위 비트, 마지막 wire를 최하위 비트로 둠. 마지막 wire가 ancilla이므로 인덱스가 짝수일 때 ancilla = 0.\n- 데이터 큐빗만 측정하면 64개 확률의 합은 항상 1. 배경이 대부분인 patch(합이 0에 가까워야 함)를 표현할 수 없음.\n- ancilla = 0인 항목만 쓰면 합이 0 ~ 1 사이에서 자유로워지고, 이 '밝기 총합'도 학습 대상이 됨.\n- 3일차 노트북 §6 ①: 이 측정 방식으로 바꾸자 생성 이미지 평균과 실제 평균의 상관계수가 0.00에서 0.49로 올랐음(8×8 단계 사전 실험).\n- 일반적인 ancilla 용도(오류 정정 신드롬 측정 등)와는 목적이 다름.");
  table(s, [
    ["인덱스", "q0 … q5 (데이터)", "anc", "사용"],
    ["0", "000000", "0", { text: "patch 픽셀 0", options: { bold: true, color: C.accent1 } }],
    ["1", "000000", "1", { text: "버림", options: { color: C.accent6 } }],
    ["2", "000001", "0", { text: "patch 픽셀 1", options: { bold: true, color: C.accent1 } }],
    ["3", "000001", "1", { text: "버림", options: { color: C.accent6 } }],
    ["…", "…", "…", "…"],
    ["126", "111111", "0", { text: "patch 픽셀 63", options: { bold: true, color: C.accent1 } }],
    ["127", "111111", "1", { text: "버림", options: { color: C.accent6 } }],
  ], 0.6, 2.25, 6.3, [1.1, 2.3, 0.9, 2.0], { fontSize: 13, rowH: 0.43 });
  code(s, [
    "probs_all = sub_generator_circuit(noise, weights)",
    "output = probs_all[::2]   # even index = anc 0",
  ], 0.6, 5.95, 6.3, 0.75, 11.5);
  card(s, 7.2, 2.25, 5.5, 2.15, HEX.card);
  text(s, "ancilla 없이 측정하면", 7.45, 2.4, 5.0, 0.35, { fontSize: 15, bold: true, color: C.accent6 });
  text(s, [
    { text: "64개 확률의 합 = 항상 1", options: { bullet: true, breakLine: true } },
    { text: "배경 patch(합 ≈ 0)와 병변 patch(합이 큼)를 구분해 표현할 수 없음", options: { bullet: true } },
  ], 7.45, 2.85, 5.0, 1.4, { fontSize: 13, paraSpaceAfter: 6 });
  card(s, 7.2, 4.6, 5.5, 2.1, HEX.mint, { line: HEX.green });
  text(s, "ancilla = 0만 선택하면", 7.45, 4.75, 5.0, 0.35, { fontSize: 15, bold: true, color: C.accent1 });
  text(s, [
    { text: "64개 확률의 합 = 0 ~ 1 사이에서 자유로움", options: { bullet: true, breakLine: true } },
    { text: "patch별 밝기 총합도 학습 대상이 됨", options: { bullet: true, breakLine: true } },
    { text: "회로는 그대로, 측정·해석만 바꾼 것", options: { bullet: true } },
  ], 7.45, 5.2, 5.0, 1.6, { fontSize: 13, paraSpaceAfter: 6 });
}
{
  const s = slide("CONTENT", "PART 2 · 노트북 §5 코드", "PatchQuantumGenerator : patch 4개를 이어 한 장으로", "sub-generator별로 batch 크기만큼 회로를 실행하고, patch를 가로로 이어붙임",
    "- §4의 회로와 같지만 device가 default.qubit, diff_method가 backprop임. PyTorch 자동미분으로 회전각까지 기울기를 계산하기 위함(lightning.qubit은 backprop 미지원).\n- forward의 이중 루프가 비용의 핵심: sub-generator 4 × batch 8 = 회로 32번 실행.\n- torch.cat(dim=1)로 이어붙이면 (batch, 256). 이미지로 볼 때 reshape(16, 16).");
  code(s, [
    "class PatchQuantumGenerator(nn.Module):",
    "    def __init__(self, n_generators, n_data_qubits, ...):",
    { t: '        q_dev = qml.device("default.qubit", ...)', hl: true },
    { t: '        @qml.qnode(q_dev, interface="torch",', hl: true },
    { t: '                   diff_method="backprop")', hl: true },
    "        def circuit(noise, weights): ...   # same as §4",
    "        self.q_params = nn.ParameterList([",
    "            nn.Parameter(torch.rand(q_depth, n_qubits) * pi)",
    "            for _ in range(n_generators)])",
    "",
    "    def forward(self, batch_size):",
    "        patches = []",
    { t: "        for g in range(self.n_generators):      # 4", hl: true },
    { t: "            rows = [self.circuit(torch.rand(7) * pi,", hl: true },
    { t: "                     self.q_params[g])[::2]", hl: true },
    { t: "                    for _ in range(batch_size)] # 8", hl: true },
    "            patches.append(torch.stack(rows))",
    "        return torch.cat(patches, dim=1)   # (batch, 256)",
  ], 0.6, 2.2, 7.4, 4.5, 11);
  // diagram
  card(s, 8.3, 2.2, 4.4, 4.5, HEX.card);
  text(s, "gen(8) 한 번의 실행", 8.55, 2.35, 3.9, 0.35, { fontSize: 14, bold: true, color: C.accent1 });
  for (let g = 0; g < 4; g++) {
    const y = 2.85 + g * 0.72;
    box(s, `sub-gen ${g + 1}`, 8.55, y, 1.15, 0.52, C.accent1, C.background1, { fontSize: 11 });
    box(s, "× 8 샘플", 9.85, y, 1.0, 0.52, HEX.white, C.text1, { fontSize: 11, line: HEX.line });
    box(s, "(8, 64)", 11.0, y, 1.45, 0.52, HEX.lav, C.text1, { fontSize: 11 });
  }
  text(s, "torch.cat(dim=1) → (8, 256)", 8.55, 5.8, 3.9, 0.35, { fontSize: 13, bold: true, align: "center" });
  text(s, "회로 실행 4 × 8 = 32번", 8.55, 6.25, 3.9, 0.4, { fontSize: 13, bold: true, align: "center" });
}
{
  const s = slide("CONTENT", "PART 2 · 노트북 §5 코드", "파라미터 수 : 생성자 280개, 판별자 19,201개", "약 70배 차이가 나서 학습률을 다르게 둠 (생성자 0.05, 판별자 0.001)",
    "- 생성자 파라미터 = sub-generator 4 × depth 10 × 큐빗 7 = 280. noise encoding의 RY는 학습 대상이 아님.\n- 판별자는 256→64→32→16→8→1 완전연결. 첫 층 하나가 16,448개로 대부분을 차지함.\n- 판별자가 훨씬 크고 빨리 배우므로, 생성자 학습률을 크게(0.05), 판별자는 작게(0.001) 둬 균형을 맞춤.\n- 3일차 MediQ-GAN은 Adam betas (0.5, 0.999), lr 2e-4라는 GAN 관례값을 씀. 두 모델의 학습 설정이 다르다는 점도 비교 대상임.");
  const g = (t) => ({ text: t, options: { bold: true, color: C.accent1 } });
  table(s, [
    ["구성", "모양", "파라미터"],
    [g("생성자: 회전각 RY(θ)"), g("sub-generator 4 × depth 10 × 큐빗 7"), g("280")],
    ["판별자 Linear 1", "256 → 64", "16,448"],
    ["판별자 Linear 2", "64 → 32", "2,080"],
    ["판별자 Linear 3", "32 → 16", "528"],
    ["판별자 Linear 4", "16 → 8", "136"],
    ["판별자 Linear 5 + Sigmoid", "8 → 1", "9"],
    [{ text: "판별자 합계", options: { bold: true } }, "", { text: "19,201", options: { bold: true } }],
  ], 0.6, 2.25, 8.0, [3.0, 3.6, 1.4], { fontSize: 13, rowH: 0.5 });
  code(s, ["opt_g: lr=0.05", "opt_d: lr=0.001"], 8.9, 2.25, 3.8, 0.95, 12);
  text(s, "판별자가 약 70배 크고 빨리 배우므로, 생성자 학습률을 크게, 판별자는 작게 둬 균형을 맞춤.", 8.9, 3.45, 3.8, 1.4, { fontSize: 13, color: C.accent6 });
}

// =====================================================================
newSection("PART 3 · QGAN 학습");
{
  const s = slide("SECTION_DARK", "PART 3 · 노트북 §5", "QGAN 학습", "학습 루프, 손실 읽는 법, 계산 비용과 한계",
    "진행 로그는 20 step마다 출력됨. 로그 숫자를 읽는 기준은 이 PART의 '손실 기준값' 장.");
  sectionRows(s, [["노트북 범위", "§5 학습 셀 (400 step)"],
    ["다루는 코드", "학습 루프 (판별자 step · 생성자 step) · BCE 손실"],
    ["소요 시간", "Colab CPU 약 35분, 진행 로그는 20 step마다"]]);
}
{
  const s = slide("CONTENT", "PART 3 · 노트북 §5 코드", "학습 루프 : 한 step에 두 번 갱신", "판별자를 먼저 갱신하고, 같은 step에서 생성자를 갱신함",
    "- 판별자 step: 실제 batch는 1, 생성 이미지는 0으로 맞히도록 학습. gen(BATCH).detach()로 생성자 쪽 계산 그래프를 끊어 판별자만 갱신함.\n- 생성자 step: 생성 이미지에 정답 라벨 1을 붙여 손실을 계산함(non-saturating loss). 판별자를 속이는 방향으로 회전각이 갱신됨.\n- 실제 이미지는 복원추출로 8장씩 뽑음. 115장이라 1 epoch ≈ 14 step.");
  code(s, [
    "for step in range(STEPS):                    # 400",
    "    batch = real_flat[torch.randint(0, 115, (8,))]",
    "",
    { t: "    # discriminator: real -> 1, fake -> 0", hl: true },
    "    opt_d.zero_grad()",
    "    loss_d = bce(disc(batch), ones) \\",
    { t: "           + bce(disc(gen(8).detach()), zeros)", hl: true },
    "    loss_d.backward(); opt_d.step()",
    "",
    { t: "    # generator: make disc say 1 for fakes", hl: true },
    "    opt_g.zero_grad()",
    { t: "    loss_g = bce(disc(gen(8)), ones)", hl: true },
    "    loss_g.backward(); opt_g.step()",
  ], 0.6, 2.2, 7.2, 4.45, 12);
  barList(s, [
    ["① 판별자 step", "실제 → 1, 생성 → 0. detach로 생성자 쪽 기울기는 계산하지 않음", C.accent2],
    ["② 생성자 step", "생성 이미지에 라벨 1을 붙여 손실 계산. 판별자를 속이는 방향으로 θ 갱신", C.accent1],
    ["③ gen() 호출 2번", "판별자용 1번 + 생성자용 1번. step당 회로 64번 실행", C.accent4],
  ], 8.1, 2.3, 4.6, 1.3);
}
{
  const s = slide("CONTENT", "PART 3 · 진행 로그 읽기", "손실 기준값 : 1.386과 0.693", "판별자가 진짜·가짜를 구분하지 못할 때(D = 0.5)의 BCE 값이 기준선",
    "- loss_d = −[log D(x) + log(1 − D(G(z)))]. D가 모두 0.5면 2 ln 2 ≈ 1.386.\n- loss_g = −log D(G(z)). D(G(z)) = 0.5면 ln 2 ≈ 0.693. 거꾸로 D(G(z)) ≈ exp(−loss_g).\n- 차트는 Colab 실행 로그(step 20 ~ 180). loss_g가 0.57 → 0.85로 오름 = 판별자가 생성 이미지를 진짜로 볼 확률이 0.57 → 0.43으로 떨어짐. 판별자가 조금씩 우세해지는 흐름.\n- loss_d가 0으로 가면 판별자 완승(생성자 학습 신호 소실). README '학습 안정성' 사례 참고.");
  const steps = ["20", "40", "60", "80", "100", "120", "140", "160", "180"];
  const lg = [0.5651, 0.5864, 0.6169, 0.6624, 0.7102, 0.7095, 0.7226, 0.8258, 0.8515];
  const ld = [1.4052, 1.3990, 1.3929, 1.3842, 1.3775, 1.3764, 1.3996, 1.2880, 1.3529];
  s.addChart(pres.charts.LINE, [
    { name: "loss_d", labels: steps, values: ld },
    { name: "2 ln 2 = 1.386", labels: steps, values: steps.map(() => 1.386) },
    { name: "loss_g", labels: steps, values: lg },
    { name: "ln 2 = 0.693", labels: steps, values: steps.map(() => 0.693) },
  ], {
    x: 0.6, y: 2.15, w: 7.4, h: 4.6, chartColors: [THEME.colors.accent2, "B9B3D6", THEME.colors.accent1, "9FCFB8"],
    lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 6,
    showLegend: true, legendPos: "b", legendFontSize: 11, legendFontFace: "+mn-lt", legendColor: THEME.colors.dk1,
    showTitle: true, title: "Colab 실측 로그 (400 step 중 step 20 ~ 180)", titleFontSize: 13, titleFontFace: "+mn-lt", titleColor: THEME.colors.dk1,
    valAxisMinVal: 0.4, valAxisMaxVal: 1.6, valAxisMajorUnit: 0.2, valAxisLabelFormatCode: "0.0",
    catAxisLabelColor: THEME.colors.accent6, valAxisLabelColor: THEME.colors.accent6, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    catAxisLabelFontSize: 11, valAxisLabelFontSize: 11, valGridLine: { color: "E5E2DC", size: 0.5 }, catGridLine: { style: "none" },
    showCatAxisTitle: true, catAxisTitle: "step", catAxisTitleFontSize: 11, catAxisTitleColor: THEME.colors.accent6,
  });
  table(s, [
    ["값", "의미"],
    ["loss_d ≈ 1.386", "구분 불가 - 경쟁 유지"],
    ["loss_d → 0", "판별자 완승, 생성자 신호 소실"],
    ["loss_g ≈ 0.693", "생성 이미지를 반반으로 판정"],
    ["loss_g = 0.85", "D(G(z)) ≈ e^−0.85 ≈ 0.43"],
  ], 8.3, 2.25, 4.4, [1.75, 2.65], { fontSize: 12, rowH: 0.5 });
  text(s, "GAN 손실은 단조 감소하지 않음. 손실이 균형처럼 보여도 품질은 낮을 수 있어 §6 지표로 따로 평가함.", 8.3, 5.0, 4.4, 1.3, { fontSize: 12.5, color: C.accent6 });
}
{
  const s = slide("CONTENT", "PART 3 · 계산 비용", "계산 비용 : 학습에 35분이 걸리는 이유", "회로 하나는 작지만(2⁷ = 128차원) 실행 횟수가 많음",
    "- 25,600번 = 32(gen 1회) × 2(step당 호출) × 400 step.\n- backprop은 상태벡터 전체를 미분하므로 시뮬레이터에서만 가능함.\n- 실제 하드웨어는 parameter-shift: 회전각마다 θ ± π/2로 회로를 두 번 더 실행해 기울기를 얻음. 생성자 280개면 샘플 하나의 기울기에 560번, 게다가 각 실행은 확률 추정을 위해 수천 shot이 필요함.\n- 3일차 MediQ-GAN은 16큐빗이라 lightning.qubit + adjoint 미분을 씀(backprop 미지원, 메모리 효율).\n- README 실험: sub-generator가 적을수록 빠른 이유도 회로 호출 횟수(sub-generator 수 × batch)가 비용을 지배하기 때문.");
  card(s, 0.6, 2.3, 12.1, 0.9, HEX.white, { line: HEX.green });
  text(s, "회로 실행 수 = sub-generator 4 × batch 8 × step당 gen() 2회 × 400 step = 25,600회", 0.6, 2.3, 12.1, 0.9, { fontSize: 17, bold: true, color: C.accent1, align: "center", valign: "middle" });
  text(s, "회로 하나는 7큐빗(상태벡터 128차원)으로 작지만, 이 횟수만큼 forward와 backprop을 반복함.", 0.6, 3.4, 12.1, 0.4, { fontSize: 13, color: C.accent6 });
  table(s, [
    ["미분 방식", "어디서", "샘플 하나의 생성자 기울기 비용", "사용처"],
    ["backprop", "시뮬레이터만", "forward 1번 + 역전파 (상태벡터 직접 미분)", "2일차 QGAN (default.qubit)"],
    ["adjoint", "시뮬레이터만", "forward 1번 + 역방향 1번, 메모리 적음", "3일차 MediQ-GAN (lightning)"],
    ["parameter-shift", "하드웨어 가능", "파라미터당 2번 → 280 × 2 = 560번 (× shot 수)", "실제 양자 장치"],
  ], 0.6, 4.45, 12.1, [2.0, 1.8, 4.9, 3.4], { fontSize: 12, rowH: 0.5 });
}
{
  const s = slide("CONTENT", "PART 3 · 한계", "한계 : 실제와 생성 이미지의 픽셀 합 불일치", "정규화 단위가 달라, 판별자가 형태가 아닌 밝기 총합만으로도 구분할 수 있음",
    "- real_flat은 이미지 한 장의 합을 1로 나눔. 생성 이미지는 patch마다 ancilla = 0 확률이라 patch 합이 0 ~ 1, 4개를 이으면 0 ~ 4.\n- Colab 실행에서 생성 이미지의 장당 픽셀 합은 약 1.63(지표 표의 '픽셀합/장').\n- 6번 섹션 지표는 to_unit_scale이 이미지별 min-max로 다시 맞추므로 지표 값에는 직접 섞이지 않음. 영향을 받는 것은 학습 과정임.\n- 공개된 수치(README, 강사 checkpoint)는 현재 방식 그대로 학습한 결과임. 고친 방식으로 다시 학습해 비교하는 것은 실습 후 과제로 적합함.");
  table(s, [
    ["", "정규화 단위", "이미지 한 장의 픽셀 합"],
    ["실제 이미지 (real_flat)", "이미지 전체", "항상 1"],
    ["생성 이미지 (gen(...))", "patch 단위 (ancilla = 0 확률)", "0 ~ 4  (Colab 실측 약 1.63)"],
  ], 0.6, 2.3, 12.1, [3.4, 4.2, 4.5], { fontSize: 14, rowH: 0.55 });
  code(s, [
    "real_flat = real_flat / real_flat.sum(dim=1, keepdim=True)   # sum = 1",
    "fake      = gen(8)            # each of 4 patches sums to 0..1",
  ], 0.6, 4.2, 12.1, 0.95, 12);
  text(s, "수정 방법 (실습 후 과제)", 0.6, 5.3, 12.1, 0.35, { fontSize: 14, bold: true, color: C.accent1 });
  barList(s, [["실제 이미지도 patch별로 정규화", "patch마다 합 1로 맞춰 생성 쪽과 단위를 맞춤"]], 0.6, 5.75, 5.9, 1.0, C.accent4);
  barList(s, [["생성 patch를 최댓값으로 나눔", "0 ~ 1 척도로 맞추고 실제 이미지는 그대로 둠 (PennyLane QGAN 튜토리얼 방식)"]], 6.8, 5.75, 5.9, 1.0, C.accent4);
}

// =====================================================================
newSection("PART 4 · 생성과 평가");
{
  const s = slide("SECTION_DARK", "PART 4 · 노트북 §6", "생성과 평가", "생성 이미지를 지표 4종으로 평가함. 3일차 MediQ-GAN에도 같은 지표를 씀");
  sectionRows(s, [["노트북 범위", "§6 생성 이미지 확인과 지표 4종"],
    ["다루는 코드", "gm.to_unit_scale · mean_image_correlation · nearest_neighbor_distance · sample_diversity"]]);
}
{
  const s = slide("CONTENT", "PART 4 · 노트북 §6", "생성품질 지표 4종", "16×16 저해상도라 FID 대신 해석 가능한 지표를 씀 (practice/gen_metrics.py)",
    "- FID는 Inception 특징을 쓰는데 16×16에서는 특징이 의미를 갖지 못하고, 표본도 수백 장 수준이라 쓰지 않음.\n- 모든 지표는 to_unit_scale로 0 ~ 1로 맞춘 뒤 계산함. QGAN은 'prob'(이미지별 min-max), MediQ-GAN은 'tanh'((x+1)/2), 전처리 데이터는 'unit'(그대로).\n- ②는 평균 형태만 봄. 모든 샘플이 같은 평균 이미지여도 높게 나오므로 ④와 함께 봐야 함.\n- ③이 0에 가까우면 학습 데이터를 복사한 것이라 증강 가치가 없음.");
  table(s, [
    ["지표", "보는 것", "함수", "읽는 법"],
    ["① 픽셀 강도 분포", "밝기 분포가 실제와 맞는가", "plot_pixel_histogram", "척도 변환 전 값도 함께 봄"],
    ["② 클래스 평균 상관", "병변의 전체 형태를 재현했는가", "mean_image_correlation", "높을수록 좋음. DF > NV여야 함"],
    ["③ 최근접 실제 거리", "학습 데이터를 외웠는가", "nearest_neighbor_distance", "0에 가까우면 암기"],
    ["④ 샘플 간 거리", "같은 그림만 반복하는가", "sample_diversity", "0에 가까우면 mode collapse"],
  ], 0.6, 2.25, 12.1, [2.4, 3.3, 3.2, 3.2], { fontSize: 13, rowH: 0.48 });
  text(s, "to_unit_scale(x, mode) - 세 척도를 0 ~ 1로 맞춘 뒤 지표를 계산함", 0.6, 4.85, 12.1, 0.35, { fontSize: 14, bold: true, color: C.accent1 });
  table(s, [
    ["mode", "대상", "변환"],
    ["prob", "QGAN 출력 (patch별 합 0 ~ 1인 확률)", "이미지별 min-max"],
    ["tanh", "MediQ-GAN 출력 (-1 ~ 1)", "(x + 1) / 2"],
    ["unit", "전처리 데이터 (0 ~ 1)", "그대로"],
  ], 0.6, 5.25, 12.1, [1.6, 6.0, 4.5], { fontSize: 12, rowH: 0.34 });
}
{
  const s = slide("CONTENT", "PART 4 · 결과 읽기", "Colab 실행 결과", "형태는 어느 정도 재현했지만 DF와 NV의 상관 차이는 작음. 실행마다 값이 조금씩 다름",
    "- 수치는 Colab에서 노트북을 끝까지 실행한 결과임. README의 600 step 결과(상관 0.195, 최근접 1.64, 다양성 1.92)와 실행마다 차이가 있음.\n- DF 0.297 대 NV 0.284: 노트북 출력 기준으로는 'DF 특징을 잡았다'고 말하기 어려움. 토론 포인트: 16×16 그레이에서는 DF와 NV의 평균 형태(가운데 어두운 덩어리)가 원래 비슷할 수 있음 → 클래스 평균 이미지 두 장을 직접 비교해 보게 함.\n- 최근접 거리 최솟값 0.956 > 0이므로 암기는 아님.\n- 다양성 1.731은 실제 DF 2.505의 약 70%. mode collapse는 아님.");
  s.addChart(pres.charts.BAR, [{ name: "상관계수", labels: ["DF 평균 대비", "NV 평균 대비"], values: [0.297, 0.284] }], {
    x: 0.6, y: 2.15, w: 4.6, h: 4.55, barDir: "col", chartColors: [THEME.colors.accent1, THEME.colors.accent6],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 12, dataLabelFontFace: "+mn-lt", dataLabelColor: THEME.colors.dk1, dataLabelFormatCode: "0.000",
    showLegend: false, showTitle: true, title: "② 클래스 평균 상관계수", titleFontSize: 13, titleFontFace: "+mn-lt", titleColor: THEME.colors.dk1,
    valAxisMinVal: 0, valAxisMaxVal: 0.4, valAxisMajorUnit: 0.1, valAxisLabelFormatCode: "0.0",
    catAxisLabelColor: THEME.colors.accent6, valAxisLabelColor: THEME.colors.accent6, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, valGridLine: { color: "E5E2DC", size: 0.5 }, catGridLine: { style: "none" },
    varyColors: true,
  });
  table(s, [
    ["지표", "결과", "해석"],
    ["② 상관 (DF / NV 평균 대비)", "0.297 / 0.284", "DF와 NV 차이가 작음"],
    ["③ 최근접 실제 거리", "평균 1.579, 최솟값 0.956", "0보다 충분히 커서 암기는 아님"],
    ["④ 샘플 간 거리", "1.731", "실제 DF 2.505의 약 70% - mode collapse 아님"],
  ], 5.6, 2.3, 7.1, [2.4, 2.0, 2.7], { fontSize: 12.5, rowH: 0.6 });
  text(s, "DF와 NV 상관이 거의 같음. 생성자가 DF 고유의 특징을 잡았는지, 16×16 그레이스케일에서 두 클래스의 평균 형태가 원래 비슷한지는 이 결과만으로 구분할 수 없음.", 5.6, 4.95, 7.1, 1.4, { fontSize: 13, color: C.accent6 });
  source(s, "Colab에서 노트북을 끝까지 실행한 결과 (400 step, 생성 64장)");
}

// =====================================================================
newSection("정리");
{
  const s = slide("CONTENT", "정리", "2일차 정리", "segmentation 전처리부터 QGAN 학습·평가까지",
    "오늘 다룬 내용을 PART 순서대로 정리함.");
  summary(s, [
    ["데이터와 전처리", "DF 115장을 증강 대상으로 둠. K-means + FCM segmentation으로 병변만 남기고 16×16, 0 ~ 1로 축소 (INTER_AREA)"],
    ["sub-generator 회로", "7큐빗(데이터 6 + ancilla 1), RY encoding 후 [학습 RY + 인접 CZ] × 10. ancilla = 0인 확률 64개가 patch 하나"],
    ["post-selection", "ancilla = 0 항목만 쓰면 patch 밝기 총합이 0 ~ 1에서 자유로워져 배경 patch도 표현 가능"],
    ["생성자·판별자", "생성자 280개(양자 회전각) vs 판별자 19,201개. 학습률 0.05 / 0.001로 균형을 맞춤"],
    ["학습과 손실", "step마다 판별자 → 생성자 순서로 갱신. 기준값 loss_d 1.386, loss_g 0.693, loss_d → 0이면 판별자 완승"],
    ["계산 비용", "400 step에 회로 25,600회. backprop은 시뮬레이터 전용, 실제 장치는 parameter-shift(파라미터당 2회 × shot)"],
    ["평가와 한계", "지표 4종을 함께 봄. 실제(합 1)와 생성(patch별 합) 이미지의 픽셀 합 불일치, 16×16, shot noise 없음"],
  ]);
}

(async () => {
  // pptxgenjs 4.0.1의 writeFile은 Node에서 compression 옵션을 무시해 zip이 비압축(약 6배 크기)으로 저장됨 - STREAM으로 받아 직접 씀
  const buf = await pres.write({ outputType: "STREAM", compression: true });
  require("fs").writeFileSync(OUT, buf);
  console.log("wrote", OUT);
})();
