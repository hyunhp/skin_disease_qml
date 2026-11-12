"""1일차 슬라이드 확장: 사전 지식(GAN·양자회로), 휴식, 결과·정리 슬라이드를 추가하고 전체 발표 대본을 넣음.

1일차 pptx는 PowerPoint로 만든 원본이라, 이 스크립트가 원본 슬라이드를 그대로 두고 새 슬라이드만 삽입함.
추가 슬라이드는 cSld 이름이 'added:'로 시작하며, 다시 실행하면 이들을 지우고 새로 만듦(재실행 가능).
사용법: python3 figures_day1.py && python3 extend_day1.py [pptx 경로]
"""
import copy
import math
import os
import re
import sys

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

from day1_notes import NOTES

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "fig_day1")
IMG = os.path.join(HERE, "..", "..", "practice", "docs", "image")
DEFAULT_PPTX = os.path.join(HERE, "..", "..", "practice", "day1_slides", "day1_theory_slides.pptx")

FONT = "Noto Sans KR"
INK, GRAY, GREEN, GREEN2, DARK = "212121", "6B6B6B", "00754A", "006241", "1E3932"
ROW, CARD, CREAM, AMBER = "EDEBE9", "F2F0EB", "FAF6EE", "9C5000"
PURPLE_BG, PURPLE, GREEN_BG, SAND, MUTED = "ECE6F5", "5B3F8C", "E4F0EA", "DFC49D", "CFC9B8"
X0, W0 = 0.7, 11.93  # 본문 좌측 여백, 본문 폭 (인치)


# ----------------------------------------------------------------------------- 저수준 도우미
def rgb(h):
    return RGBColor.from_string(h)


def _set_font(run, size, color, bold):
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = rgb(color)
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:ea", "a:cs"):
        for e in rPr.findall(qn(tag)):
            rPr.remove(e)
        e = rPr.makeelement(qn(tag), {"typeface": FONT})
        rPr.append(e)


def _runs(text):
    """'**굵게**' 표기를 (텍스트, 굵게) 목록으로 분해."""
    out = []
    for i, part in enumerate(re.split(r"\*\*", text)):
        if part:
            out.append((part, i % 2 == 1))
    return out


def tb(slide, x, y, w, h, paras, size=12.5, color=INK, bold=False, align="l", anchor="t", ls=1.2, after=4,
       name=None):
    """텍스트 상자. paras: 문자열 목록(줄마다 문단). '**굵게**' 지원."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        box.name = name
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    if isinstance(paras, str):
        paras = [paras]
    for i, t in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
        p.line_spacing = ls
        p.space_after = Pt(after)
        for txt, b in _runs(t):
            r = p.add_run()
            r.text = txt
            _set_font(r, size, color, bold or b)
    return box


def rect(slide, x, y, w, h, fill, line=None, lw=1.25, rounded=False):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
                                 Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = rgb(fill)
    if line:
        shp.line.color.rgb = rgb(line)
        shp.line.width = Pt(lw)
    else:
        shp.line.fill.background()
    spPr = shp._element.spPr
    spPr.append(spPr.makeelement(qn("a:effectLst"), {}))
    shp.text_frame.text = ""
    return shp


def text_width_pt(text, size):
    return sum((1.08 if ord(c) > 0x2E7F else 0.6) for c in text) * size


def n_lines(text, size, width_in):
    avail = width_in * 72
    total = 0
    for line in text.split("\n"):
        total += max(1, math.ceil(text_width_pt(line.replace("**", ""), size) / avail))
    return total


def table(slide, x, y, colw, rows, header=True, fs=11.5, hfs=11.5, first_bold=True, hl=(), min_rh=0.42,
          hh=0.42, pad=0.14, ls=1.2):
    """사각형 + 텍스트 상자로 만든 표(기존 슬라이드와 같은 방식). 행 높이는 줄 수에서 계산. 끝 y를 반환."""
    cy = y
    r0 = 0
    if header:
        rect(slide, x, cy, sum(colw), hh, DARK)
        cx = x
        for w, t in zip(colw, rows[0]):
            tb(slide, cx + pad, cy, w - 2 * pad, hh, t, size=hfs, color="FFFFFF", bold=True, anchor="m")
            cx += w
        cy += hh
        r0 = 1
    for i, row in enumerate(rows[r0:]):
        lines = max(n_lines(t, fs, w - 2 * pad) for w, t in zip(colw, row))
        rh = max(min_rh, lines * fs * 1.2 * ls / 72 + 0.2)
        rect(slide, x, cy, sum(colw), rh, "FFFFFF" if i % 2 == 0 else ROW)
        cx = x
        for j, (w, t) in enumerate(zip(colw, row)):
            green = i in hl
            tb(slide, cx + pad, cy, w - 2 * pad, rh, t.split("\n"), size=fs, color=GREEN if green else INK,
               bold=(first_bold and j == 0) or green, anchor="m", ls=ls, after=0)
            cx += w
        cy += rh
    return cy


def card(slide, x, y, w, h, title, lines, fill=CARD, line=None, tcolor=GREEN, fs=11.5, tfs=12, rounded=True,
         bullet="- "):
    rect(slide, x, y, w, h, fill, line=line, rounded=rounded)
    paras = []
    if title:
        paras.append(f"**{title}**")
    tbx = tb(slide, x + 0.22, y + 0.16, w - 0.44, h - 0.3, paras + [bullet + t if bullet else t for t in lines],
             size=fs, ls=1.22, after=4)
    if title:
        r = tbx.text_frame.paragraphs[0].runs[0]
        _set_font(r, tfs, tcolor, True)
    return tbx


def callout(slide, x, y, w, h, label, lines, fs=11.5):
    """기존 '핵심' 상자(크림 배경 + 갈색 라벨)."""
    rect(slide, x, y, w, h, CREAM, rounded=True)
    tbx = tb(slide, x + 0.28, y + 0.14, w - 0.56, h - 0.24, [f"**{label}**"] + lines, size=fs, ls=1.22, after=3)
    _set_font(tbx.text_frame.paragraphs[0].runs[0], 11.5, AMBER, True)


def picture(slide, path, x, y, w=None, h=None):
    iw, ih = Image.open(path).size
    if w is None:
        w = h * iw / ih
    h = w * ih / iw
    slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
    return w, h


def caption(slide, text):
    tb(slide, 6.63, 7.03, 6.0, 0.25, text, size=8.5, color="8A8A8A", align="r", anchor="m", ls=1.0, name="src_caption")


def header(slide, kicker, title, sub):
    tb(slide, X0, 0.55, 10.0, 0.35, kicker, size=11.5, color=GREEN, bold=True, anchor="m", ls=1.0)
    tb(slide, X0, 0.9, W0, 0.7, title, size=27, bold=True, anchor="m", ls=1.0)
    tb(slide, X0, 1.52, W0, 0.4, sub, size=13, color=GRAY, anchor="m", ls=1.15)


def divider_rows(slide, kicker, title, sub, rows, ty=1.25):
    tb(slide, X0, 0.7, 10.0, 0.35, kicker, size=11.5, color=MUTED, bold=True, anchor="m", ls=1.0)
    tb(slide, X0, ty, W0, 0.6, title, size=30, color="FFFFFF", bold=True, anchor="m", ls=1.0)
    tb(slide, X0, ty + 0.6, W0, 0.5, sub, size=14, color=MUTED, anchor="m", ls=1.0)
    y = 2.95
    for label, text in rows:
        tb(slide, X0, y, 2.6, 0.3, label, size=12, color=SAND, bold=True, ls=1.0)
        tb(slide, 3.5, y - 0.03, 9.1, 0.9, text, size=12.5, color="FFFFFF", ls=1.3)
        y += 1.0


# ----------------------------------------------------------------------------- 슬라이드 단위
class Deck:
    def __init__(self, path):
        self.prs = Presentation(path)
        self.path = path
        self._drop_added()
        self.orig = list(self.prs.slides)
        self.num_donor = None
        for sh in self.orig[2].shapes:
            if sh.is_placeholder and "sldNum" in sh._element.xml:
                self.num_donor = sh._element
        self.blank = self.prs.slide_layouts.get_by_name("Blank")
        self.new = {}

    def _drop_added(self):
        lst = self.prs.slides._sldIdLst
        for sid in list(lst):
            sl = self.prs.part.related_part(sid.rId).slide
            if (sl._element.cSld.get("name") or "").startswith("added:"):
                self.prs.part.drop_rel(sid.rId)
                lst.remove(sid)
        # 남은 슬라이드 파트 이름을 연속 번호로 되돌려, 새 슬라이드의 파트 이름과 충돌하지 않게 함
        self.prs.part.rename_slide_parts([sid.rId for sid in lst])

    def add(self, key, dark=False, bg="FFFFFF"):
        s = self.prs.slides.add_slide(self.blank)
        s._element.cSld.set("name", f"added:{key}")
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = rgb(DARK if dark else bg)
        for ph in list(s.placeholders):
            ph._element.getparent().remove(ph._element)
        self.new[key] = s
        return s

    def finish_slide(self, s):
        if self.num_donor is not None:
            s.shapes._spTree.append(copy.deepcopy(self.num_donor))

    def reorder(self, order):
        lst = self.prs.slides._sldIdLst
        by_id = {sid.id: sid for sid in lst}
        objs = []
        for k in order:
            s = self.orig[int(k[1:]) - 1] if re.fullmatch(r"O\d+", k) else self.new[k]
            objs.append(by_id[s.slide_id])
        for sid in list(lst):
            lst.remove(sid)
        for sid in objs:
            lst.append(sid)

    def slide_of(self, key):
        return self.orig[int(key[1:]) - 1] if re.fullmatch(r"O\d+", key) else self.new[key]


def clear_text_runs(shape, text):
    """첫 문단의 첫 run 서식은 유지하고 텍스트만 교체."""
    p = shape.text_frame.paragraphs[0]
    runs = p.runs
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


# ----------------------------------------------------------------------------- 기존 슬라이드 수정
def edit_originals(d):
    # 3번: 학습목표 5항목으로 재구성
    s = d.orig[2]
    for sh in list(s.shapes):
        if not (sh.is_placeholder and "sldNum" in sh._element.xml):
            sh._element.getparent().remove(sh._element)
    header(s, "오리엔테이션", "학습목표", "INDEX")
    goals = [
        "HAM10000 데이터셋 EDA와 클래스 불균형 문제",
        "GAN 학습 구조·평가 지표(FID, LPIPS)와 양자회로 기초(qubit, 게이트, 측정, PQC)",
        "QGAN과 고전 GAN의 차이 - patch 방식 아키텍처",
        "아키텍처 '전체가 양자'(QGAN)와 '일부만 양자'(MediQ-GAN, dual-stream) 차이 구분",
        "두 논문의 결과를 같은 기준(비교 대상, 지표, 실행 환경)으로 해석",
    ]
    y = 2.3
    for i, g in enumerate(goals, 1):
        c = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(X0), Inches(y), Inches(0.5), Inches(0.5))
        c.fill.solid()
        c.fill.fore_color.rgb = rgb(GREEN)
        c.line.fill.background()
        c._element.spPr.append(c._element.spPr.makeelement(qn("a:effectLst"), {}))
        c.text_frame.text = str(i)
        c.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        _set_font(c.text_frame.paragraphs[0].runs[0], 14, "FFFFFF", False)
        c.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        tb(s, 1.45, y, 11.0, 0.5, g, size=14, anchor="m", ls=1.1)
        y += 0.82
    # 24번: IBM 실기 결과를 수치로 정정 (논문 표현 '소폭'은 FID +19 ~ +79)
    for sh in d.orig[23].shapes:
        if sh.has_text_frame and "IBM Marrakesh 실기에 올려" in sh.text_frame.text:
            clear_text_runs(sh, "학습 완료된 회로를 IBM Marrakesh 실기에 올려 inference만 검증 (클래스별 FID +19 ~ +79 상승, 논문은 '비교 가능한 수준'으로 평가)")
    # 26번: 줄표 규칙(CLAUDE.md)에 맞춰 en dash를 하이픈으로
    for sh in d.orig[25].shapes:
        if sh.has_text_frame and "–" in sh.text_frame.text:
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    r.text = r.text.replace(" – ", " - ").replace("–", "-")


# ----------------------------------------------------------------------------- 신규 슬라이드
def build_new(d):
    f = lambda n: os.path.join(FIG, n)

    # --- 사전 지식 divider
    s = d.add("PRE", dark=True)
    divider_rows(s, "PRELIMINARY", "사전 지식", "두 논문을 읽는 데 필요한 GAN과 양자회로 기초", [
        ("GAN", "생성자·판별자의 minimax 학습, 학습 불안정성(mode collapse)과 WGAN-GP, 생성 품질 평가 지표(FID, LPIPS)"),
        ("양자회로", "qubit과 상태벡터, 회전·얽힘 게이트, 측정과 기댓값, 변분 양자회로(PQC)의 hybrid 학습 루프, 시뮬레이션의 한계"),
        ("이후 내용과의 관계", "이 장에서 정의한 용어(RY, CNOT, 기댓값, WGAN-GP, FID)를 QGAN·MediQ-GAN 설명에서 그대로 사용함"),
    ])

    # --- G1
    s = d.add("G1")
    header(s, "사전 지식 · GAN", "GAN의 구조와 학습 목표", "생성자와 판별자가 하나의 목적함수를 반대 방향으로 최적화하는 minimax 구조")
    w, h = picture(s, f("gan_game.png"), X0, 2.15, w=7.7)
    card(s, 8.7, 2.15, 3.93, 3.0, None, [
        "**Generator**: 노이즈 z를 샘플로 변환. D가 생성 샘플을 진짜로 판단하도록 갱신",
        "**Discriminator**: 실제와 생성 샘플을 구분. 판별 정확도를 최대화하도록 갱신",
        "**학습 순서**: D 갱신과 G 갱신을 번갈아 반복",
        "QGAN·MediQ-GAN은 이 구조에서 G만 양자회로를 포함함",
    ], fs=11.5)
    rect(s, X0, 5.45, W0, 1.2, "FFFFFF", line=GREEN, rounded=True)
    tb(s, X0, 5.55, W0, 0.5, "min_G max_D  V(D, G) = E[ log D(x) ] + E[ log( 1 − D(G(z)) ) ]", size=19, color=GREEN2,
       bold=True, align="c", anchor="m", ls=1.0)
    tb(s, X0, 6.08, W0, 0.45, "x ~ p_data(실제), z ~ p_z(노이즈). G의 손실은 학습 초반 gradient 소실을 피하려고 −log D(G(z))로 바꿔 쓰는 경우가 많음",
       size=11, color=GRAY, align="c", anchor="m", ls=1.0)
    d.finish_slide(s)

    # --- G2
    s = d.add("G2")
    header(s, "사전 지식 · GAN", "학습 불안정성과 WGAN-GP", "원 GAN의 손실은 학습이 불안정하고, 두 논문은 서로 다른 학습 목표를 사용함")
    table(s, X0, 2.2, [1.5, 2.1, 1.95], [
        ["문제", "현상", "원인"],
        ["Vanishing gradient", "D가 너무 잘 구분하면 G의 gradient가 0에 수렴", "두 분포의 support가 겹치지 않으면 JS divergence가 상수"],
        ["Mode collapse", "G가 일부 유형의 샘플만 반복 생성", "D가 다양성을 직접 평가하지 않음"],
        ["진동", "손실이 수렴하지 않고 진동", "두 모델을 동시에 최적화하는 min-max 구조"],
    ], fs=11, hfs=11.5)
    table(s, 6.95, 2.2, [1.2, 2.2, 2.28], [
        ["항목", "원 GAN (BCE)", "WGAN-GP"],
        ["D의 출력", "확률 (시그모이드)", "실수 점수 (critic)"],
        ["손실", "BCE: log D(x) + log(1 − D(G(z)))", "E[D(x)] − E[D(G(z))] + λ·GP"],
        ["거리", "Jensen-Shannon", "Wasserstein-1"],
        ["안정화", "없음", "critic gradient 노름을 1로 유도 (1-Lipschitz)"],
        ["사용 논문", "QGAN (Table 4)", "MediQ-GAN (식 (1)·(2))"],
    ], fs=11, hfs=11.5, hl={4})
    callout(s, X0, 5.75, W0, 0.95, "실습과의 연결", [
        "3일차: MediQ-GAN을 생성자 학습률 0.02로 학습하면 3 epoch 만에 mode collapse가 발생함. 원 논문이 WGAN-GP critic을 쓰는 이유에 해당함."])
    d.finish_slide(s)

    # --- G3
    s = d.add("G3")
    header(s, "사전 지식 · GAN", "생성 품질 평가: 지표별 측정 대상", "생성 이미지의 품질은 눈으로 판단하기 어려워 정량 지표를 병행함")
    table(s, X0, 2.2, [2.0, 3.55, 1.45], [
        ["지표", "측정 대상", "방향"],
        ["Downstream 분류 성능\n(AUC-ROC, 정확도)", "생성 이미지를 학습 데이터에 추가했을 때 분류기 성능 변화\nQGAN 논문, MediQ-GAN Table 1", "높을수록 좋음"],
        ["FID", "실제와 생성 이미지의 Inception 특징 분포(평균·공분산) 사이 Fréchet 거리\nMediQ-GAN 논문 (클래스별)", "낮을수록 좋음"],
        ["intra-class LPIPS", "같은 클래스 생성 이미지 쌍의 지각적 거리 평균. mode collapse 점검\nMediQ-GAN 논문", "높을수록 다양"],
        ["지표 4종 (실습)", "픽셀 분포, 클래스 평균 상관, 최근접 실제 거리, 샘플 다양성\n2·3일차 노트북 (16×16에서는 FID 사용 불가)", "지표별 상이"],
    ], fs=10.5, hfs=11.5)
    picture(s, f("fid_concept.png"), 8.05, 2.15, w=4.58)
    card(s, 8.05, 4.45, 4.58, 2.2, "해석 시 유의", [
        "FID가 낮아도 LPIPS가 낮으면 비슷한 이미지만 생성한 것이므로 두 지표를 함께 봄",
        "표본이 적은 클래스(df 115장)에서는 FID 공분산 추정이 불안정함",
        "분류 성능은 분류기와 증강 비율에 의존함",
    ], fs=10.5)
    d.finish_slide(s)

    # --- Q1
    s = d.add("Q1")
    header(s, "사전 지식 · 양자회로", "qubit과 상태벡터", "n큐빗 상태는 2ⁿ개의 복소 진폭이며, 측정 확률은 진폭 크기의 제곱")
    rect(s, X0, 2.2, 6.4, 1.15, "FFFFFF", line=GREEN, rounded=True)
    tb(s, X0, 2.3, 6.4, 0.95, ["|ψ⟩ = α|0⟩ + β|1⟩,   |α|² + |β|² = 1", "n큐빗:  |ψ⟩ = Σ c_x |x⟩,   P(x) = |c_x|²"],
       size=16, color=GREEN2, bold=True, align="c", anchor="m", ls=1.15, after=2)
    table(s, X0, 3.6, [1.2, 2.45, 2.75], [
        ["구분", "고전", "양자"],
        ["상태", "n bit = 문자열 하나", "n큐빗 = 2ⁿ 진폭 벡터"],
        ["갱신", "논리 연산", "유니터리 행렬 곱 (노름 보존)"],
        ["읽기", "값을 그대로 읽음", "측정 시 확률 P(x)로 bitstring 하나 결정"],
    ], fs=11, hfs=11.5)
    picture(s, f("state3_probs.png"), 7.4, 2.2, w=5.23)
    card(s, 7.4, 5.15, 5.23, 1.5, "이후 논문과의 연결", [
        "QGAN: 데이터 7큐빗 → 확률 128개 = patch 픽셀 128개",
        "MediQ-GAN: 16큐빗 → 상태벡터 65,536차원",
    ], fs=11)
    d.finish_slide(s)

    # --- Q2
    s = d.add("Q2")
    header(s, "사전 지식 · 양자회로", "게이트: 회전과 얽힘", "두 논문의 회로는 회전 게이트와 얽힘 게이트 두 종류로만 구성됨")
    end = table(s, X0, 2.2, [1.15, 3.65, 1.7], [
        ["게이트", "작용", "학습 대상"],
        ["RY(θ)", "|0⟩ → cos(θ/2)|0⟩ + sin(θ/2)|1⟩\nP(1) = sin²(θ/2)", "θ (학습)"],
        ["RX(θ)", "X축 회전. MediQ-GAN의 encoding에 사용", "입력값 (고정)"],
        ["CNOT", "제어 큐빗이 1이면 목표 큐빗 반전", "파라미터 없음"],
        ["CZ", "두 큐빗이 모두 1이면 위상에 −1", "파라미터 없음"],
    ], fs=11, hfs=11.5)
    card(s, X0, end + 0.2, 6.5, 6.7 - end - 0.2, "두 논문의 회로 구성", [
        "QGAN: RY(z) encoding → [RY(θ) + CZ 체인] × depth 10",
        "MediQ-GAN: RX, RY encoding → [RY(θ) + CNOT 체인] × 8",
    ], fs=11)
    picture(s, f("qubit_ry_curve.png"), 7.9, 2.15, w=3.4)
    picture(s, f("bell_bars.png"), 7.7, 4.6, w=4.93)
    d.finish_slide(s)

    # --- Q3
    s = d.add("Q3")
    header(s, "사전 지식 · 양자회로", "측정과 기댓값", "측정 한 번은 bitstring 하나이고, 모델이 쓰는 값은 반복 측정의 통계량")
    end = table(s, X0, 2.2, [1.75, 3.2, 1.55], [
        ["출력 방식", "정의와 출력 크기", "사용 논문"],
        ["확률 분포 P(x)", "2ⁿ개 basis state의 측정 확률\n출력 크기 2ⁿ (지수)", "QGAN"],
        ["기댓값 ⟨X_i⟩", "큐빗별 관측량의 평균, −1 ~ 1\n출력 크기 n (선형)", "MediQ-GAN"],
    ], fs=11, hfs=11.5, min_rh=0.8)
    rect(s, X0, end + 0.2, 6.5, 1.0, "FFFFFF", line=GREEN, rounded=True)
    tb(s, X0, end + 0.27, 6.5, 0.86, ["⟨Z⟩ = P(0) − P(1)  ∈ [−1, 1]", "shot N회 추정의 표준오차 = √((1 − ⟨Z⟩²) / N) ≤ 1/√N"],
       size=14, color=GREEN2, bold=True, align="c", anchor="m", ls=1.15, after=2)
    callout(s, X0, end + 1.4, 6.5, 6.7 - end - 1.4, "출력 구조의 차이", [
        "QGAN: 8큐빗 중 ancilla qubit = 0인 128개 확률을 patch 픽셀로 사용",
        "MediQ-GAN: 16큐빗 → 기댓값 16개를 특징으로 사용, 이미지는 고전 decoder가 생성",
    ], fs=10.5)
    picture(s, f("shots_convergence.png"), 7.5, 2.2, w=5.13)
    tb(s, 7.5, 5.6, 5.13, 1.2, ["정밀도를 10배 높이려면 shot이 100배 필요함. 이 비용이 뒤의 VQC 학습 비용 계산에 들어감",
                                 "시뮬레이터에서 shots를 지정하지 않으면 이 오차 없이 exact 기댓값을 계산함"], size=10.5, color=GRAY, ls=1.25)
    d.finish_slide(s)

    # --- Q4
    s = d.add("Q4")
    header(s, "사전 지식 · 양자회로", "변분 양자회로(PQC)와 hybrid 학습 루프", "양자회로는 미분 가능한 하나의 layer로 쓰이고, 파라미터 갱신은 고전 optimizer가 담당함")
    picture(s, f("pqc_hybrid_loop.png"), (13.333 - 9.2) / 2, 2.0, w=9.2)
    cw = (W0 - 2 * 0.2) / 3
    for i, (t, lines) in enumerate([
        ("encoding", ["입력을 회전각으로 변환 (angle encoding). 두 논문 모두 사용", "대안인 amplitude encoding은 2ⁿ개 값을 적재하나 상태 준비 회로가 깊어질 수 있음"]),
        ("ansatz", ["학습 가능한 회전 + 얽힘 게이트의 반복", "두 논문 모두 hardware-efficient 구조 (RY + CNOT 또는 CZ)"]),
        ("gradient", ["시뮬레이터: adjoint 또는 backpropagation", "실기: parameter-shift rule, 파라미터마다 회로 2회 추가 실행"]),
    ]):
        card(s, X0 + i * (cw + 0.2), 5.4, cw, 1.45, t, lines, fs=10.5)
    d.finish_slide(s)

    # --- Q5
    s = d.add("Q5")
    header(s, "사전 지식 · 양자회로", "시뮬레이션의 한계와 학습 가능성", "state vector 시뮬레이션은 큐빗 수에 지수적이고, 회로가 넓고 깊을수록 학습이 어려워짐")
    picture(s, f("statevector_memory.png"), X0, 2.25, w=5.6)
    table(s, 6.6, 2.2, [1.55, 4.48], [
        ["항목", "내용"],
        ["시뮬레이션 규모", "16큐빗은 1 MiB로 노트북에서 처리 가능. 30큐빗부터 16 GiB로 일반 PC 한계"],
        ["해석", "정확히 시뮬레이션되는 규모의 회로는 양자 우위의 근거가 아님. MediQ-GAN 논문도 quantum-inspired로 규정하고 양자 소자를 계산 가속 용도로 한정"],
        ["NISQ 실기", "게이트 오류와 decoherence로 얕은 회로만 신뢰 가능"],
        ["Barren plateau", "큐빗 수·깊이가 커질수록 gradient 분산이 지수적으로 감소하는 현상"],
        ["표현력 대 학습 가능성", "표현력이 큰 회로일수록 barren plateau 위험이 큼. MediQ-GAN은 DLA 분석으로 depth 8을 선택"],
    ], fs=11.5, hfs=11.5, min_rh=0.62)
    d.finish_slide(s)

    # --- 휴식
    s = d.add("BRK", dark=True)
    tb(s, X0, 0.7, 10, 0.35, "BREAK", size=11.5, color=MUTED, bold=True, anchor="m", ls=1.0)
    tb(s, X0, 1.25, W0, 0.7, "휴식", size=34, color="FFFFFF", bold=True, anchor="m", ls=1.0)
    tb(s, X0, 1.95, W0, 0.5, "10분 후 재개", size=16, color=MUTED, anchor="m", ls=1.0)
    y = 3.1
    for label, text in [
        ("여기까지", "HAM10000 클래스 불균형 → GAN 구조·학습 불안정성·평가 지표 → qubit, 게이트, 측정, PQC 학습 루프"),
        ("이어서", "Chapter 1 QGAN (patch 방식, 학습 step, 결과) → Chapter 2 MediQ-GAN (dual-stream, WGAN-GP, 결과) → Chapter 3 정리"),
    ]:
        tb(s, X0, y, 2.6, 0.3, label, size=12, color=SAND, bold=True, ls=1.0)
        tb(s, 3.5, y - 0.03, 9.1, 0.9, text, size=12.5, color="FFFFFF", ls=1.3)
        y += 1.1
    d.finish_slide(s)

    # --- T1 QGAN 학습 step
    s = d.add("T1")
    header(s, "01 · QGAN 논문", "QGAN 한 step의 학습 과정", "판별자와 생성자를 번갈아 갱신하며, 생성자의 gradient는 회로 파라미터 θ까지 전달됨")
    end = table(s, X0, 2.2, [0.9, 6.0, 5.03], [
        ["단계", "동작", "손실"],
        ["1  생성", "z → sub-generator 16개 → patch 결합 → 생성 이미지 x̃", "-"],
        ["2  D 갱신", "실제 x는 1, 생성 x̃는 0으로 분류하도록 D의 가중치 갱신", "L_D = −[ log D(x) + log(1 − D(x̃)) ]  (BCE)"],
        ["3  G 갱신", "D가 x̃를 1로 판단하도록 회로 각도 θ 갱신", "L_G = −log D(x̃)  (non-saturating)"],
        ["4  반복", "2,000 epoch (논문 Table 3·4)", "-"],
    ], fs=11.5, hfs=11.5, min_rh=0.62)
    callout(s, X0, end + 0.25, W0, 1.45, "설정에서 확인할 점", [
        "- 학습률: 생성자 0.1, 판별자 5×10⁻³ (Table 3·4). 생성자가 20배 큼",
        "- 논문은 손실을 Binary Cross Entropy로 표기함. G 손실 형태는 일반적인 non-saturating 형태로 적은 것임",
        "- 실습(2일차)은 sub-generator 4개, 600 step으로 줄인 설정을 사용함",
    ])
    d.finish_slide(s)

    # --- IMG QGAN 생성 이미지
    s = d.add("IMG")
    header(s, "01 · QGAN 논문 결과", "결과 0 - QGAN 생성 이미지", "논문 Fig. 21: 원본 유래 합성 이미지(A)와 합성 segmentation(B)")
    picture(s, os.path.join(IMG, "paper_qgan_fig21_samples.png"), X0, 2.35, w=6.9)
    card(s, 8.0, 2.35, 4.63, 3.0, "관찰", [
        "병변의 위치와 대략적인 경계는 재현됨",
        "해상도가 낮아 질감 같은 세부는 확인하기 어려움",
        "이 논문은 FID 같은 생성 품질 지표를 제시하지 않고(프리프린트 기준) 증강 후 분류 성능으로 간접 검증함",
        "따라서 우열 판단의 근거는 다음 슬라이드의 분류 성능임",
    ], fs=11.5)
    caption(s, "그림 출처: Andra et al., Fig. 21 (프리프린트 Research Square rs-5191116v1, CC BY 4.0)")
    d.finish_slide(s)

    # --- M1 입력 구성과 decoder
    s = d.add("M1")
    header(s, "02 · MEDIQ-GAN 논문", "입력 구성과 decoder", "class prototype을 노이즈에 결합하고, 양자 stream 출력은 decoder에서 64×64 RGB로 복원")
    picture(s, f("mediq_shape_flow.png"), (13.333 - 9.6) / 2, 2.0, w=9.6)
    hw = (W0 - 0.25) / 2
    card(s, X0, 5.4, hw, 1.45, "prototype conditioning", [
        "EfficientNet-B0(30 epoch 미세조정) 특징의 클래스별 평균 벡터를 노이즈에 결합",
        "centroid 간 거리를 최대화하는 regularization loss로 클래스 구분 유지",
    ], fs=10.5)
    card(s, X0 + hw + 0.25, 5.4, hw, 1.45, "decoder", [
        "3×3 conv → upsample-blur-conv 3단계 → 3×3 conv",
        "양자 stream 출력과 고전 stream 출력을 concat한 32×4×4를 3×64×64로 확대",
    ], fs=10.5)
    caption(s, "구조 출처: Jiao et al., arXiv:2506.21015 Method 절")
    d.finish_slide(s)

    # --- M2 critic과 학습 목표
    s = d.add("M2")
    header(s, "02 · MEDIQ-GAN 논문", "critic과 학습 목표", "critic은 고전 convolutional network로 유지하고, 학습 목표는 WGAN-GP를 사용")
    table(s, X0, 2.2, [2.5, 9.43], [
        ["항목", "내용"],
        ["학습 목표", "WGAN-GP: L = E[D(x)] − E[D(G(z))] + λ·E[(‖∇D(x̂)‖₂ − 1)²]  (논문 식 (1)·(2))"],
        ["critic 구조", "원 WGAN-GP 논문의 convolutional 구조, 입력 3×64×64"],
        ["critic을 고전으로 둔 이유\n(논문)", "1. 3×64×64 입력을 매 iteration 처리해야 하므로 NISQ 소자에서 구현이 비현실적\n2. 안정적이고 잘 알려진 critic을 두어 성능 향상을 양자 설계의 효과로 귀속"],
        ["QGAN과의 차이", "QGAN: 5층 완전연결 + BCE (Table 4)\nMediQ-GAN: convolution + WGAN-GP"],
        ["실습과의 차이", "3일차: MLP 판별자 + 표준 BCE, lr 2×10⁻⁴, betas (0.5, 0.999)로 25 epoch 완주 (README '원 논문과 다른 점')"],
    ], fs=11.5, hfs=11.5, min_rh=0.6)
    d.finish_slide(s)

    # --- R1 분류 성능
    s = d.add("R1")
    header(s, "02 · MEDIQ-GAN 논문 결과", "결과 ① - 분류 성능 (Table 1)", "baseline 대비 정확도는 3개 데이터셋 · 2개 분류기 모두에서 상승하나, 모든 행에서 최고는 아님")
    picture(s, f("mediq_acc_dots.png"), X0, 2.15, w=7.7)
    card(s, 8.65, 2.15, 3.98, 3.3, "읽는 법", [
        "EfficientNet-B0 정확도 상승: ISIC +3.75, ODIR +6.83, RetinaMNIST +9.25",
        "ViT-small 정확도 상승: +10.11, +3.44, +12.82",
        "RetinaMNIST ViT-small: FastGAN 64.37이 MediQ-GAN 63.75보다 높음",
        "ISIC ViT-small AUC: FastGAN 0.9549 > 0.9517",
        "MosaiQ는 baseline 이하 (ISIC ViT-small 50.25%)",
    ], fs=10.5)
    caption(s, "수치 출처: Jiao et al., arXiv:2506.21015 Table 1")
    d.finish_slide(s)

    # --- R2 FID, LPIPS
    s = d.add("R2")
    header(s, "02 · MEDIQ-GAN 논문 결과", "결과 ② - 생성 품질: FID와 LPIPS", "소수 클래스 FID는 ISIC·ODIR에서 MediQ-GAN이 가장 낮고, RetinaMNIST에서는 DiT가 더 낮음")
    picture(s, f("mediq_fid_minority.png"), X0, 2.05, w=6.4)
    card(s, 7.35, 2.15, 5.28, 2.6, "해석", [
        "DiT는 확산 모델로 용량이 훨씬 큼. 논문 서술은 'best or second-best'",
        "MosaiQ: FID 316 ~ 593, RetinaMNIST LPIPS 0.079로 거의 같은 이미지만 생성",
        "FID는 클래스당 표본이 적을수록 불안정함",
    ], fs=10.5)
    table(s, X0, 5.4, [3.4, 1.5, 1.5, 1.6, 1.9], [
        ["소수 클래스 평균 LPIPS (높을수록 다양)", "Real", "DiT", "FastGAN", "MediQ-GAN"],
        ["ISIC 2019", "0.457", "0.367", "0.422", "0.409"],
        ["ODIR-5k", "0.612", "0.609", "0.609", "0.601"],
        ["RetinaMNIST", "0.396", "0.321", "0.394", "0.384"],
    ], fs=10.5, hfs=10.5, min_rh=0.32, hh=0.34)
    caption(s, "수치 출처: Jiao et al., Extended Data Table 2·3")
    d.finish_slide(s)

    # --- R3 생성 이미지 비교
    s = d.add("R3")
    header(s, "02 · MEDIQ-GAN 논문 결과", "결과 ③ - 생성 이미지 비교 (Fig. 2)", "열은 데이터셋별 대표 클래스, 행은 방법, 마지막 행은 실제 이미지")
    picture(s, os.path.join(IMG, "paper_mediqgan_fig2_samples.png"), X0, 2.0, h=4.85)
    card(s, 6.75, 2.0, 5.88, 3.6, "논문의 정성 서술", [
        "DCGAN, Structure-preserving GAN: 흐린 dermoscopic 질감",
        "StyleGAN2-ADA: 다수 클래스는 개선, 희소 클래스에서 약함",
        "FastGAN, DiT: 데이터가 극히 적은 ISIC df에서 구조 손실",
        "MosaiQ: PCA 축소로 색과 구조가 사라진 흐린 패치",
        "MediQ-GAN: 클래스 특징 보존 (논문 서술)",
        "저자의 정성 평가이므로 FID, LPIPS와 함께 해석함",
    ], fs=11.5)
    caption(s, "그림 출처: Jiao et al., arXiv:2506.21015 Fig. 2 (CC BY 4.0)")
    d.finish_slide(s)

    # --- R4 IBM 실기
    s = d.add("R4")
    header(s, "02 · MEDIQ-GAN 논문 결과", "결과 ④ - IBM 실기 검증", "학습된 회로를 IBM Marrakesh에서 inference만 실행: 모든 클래스에서 FID 상승")
    picture(s, f("mediq_ibm_fid.png"), X0, 2.1, w=6.9)
    card(s, 7.8, 2.15, 4.83, 3.0, "읽는 법", [
        "범위: 데이터셋별 대표 클래스 9개, inference만 (학습은 시뮬레이션)",
        "FID 상승폭: +19 (RetinaMNIST GR0) ~ +79 (ISIC df)",
        "논문 평가: 시뮬레이션보다 약간 낮으나 비교 가능한 수준",
    ], fs=10.5)
    callout(s, X0, 5.75, W0, 1.0, "비교", [
        "ISIC df: 실기 FID 261.5는 FastGAN 225.0보다 나쁘고 DCGAN 272.6보다 좋음. 노이즈에 무너지지 않는다는 근거이며, 실기에서 고전 baseline보다 우위라는 근거는 아님"], fs=11)
    caption(s, "수치 출처: Jiao et al., Extended Data Table 4, Table 2")
    d.finish_slide(s)

    # --- R5 생성자 분석
    s = d.add("R5")
    header(s, "02 · MEDIQ-GAN 논문 결과", "결과 ⑤ - 생성자의 학습 가능성 분석", "Jacobian 특이값 분포와 DLA 분석으로 hybrid 생성자를 평가함")
    end = table(s, X0, 2.2, [2.7, 3.9, 5.33], [
        ["분석", "의미", "논문 결과"],
        ["effective rank,\nparticipation ratio", "잠재 방향 중 출력에 실제 영향을 주는 비율 (높을수록 좋음)", "특이값 감쇠가 고전 baseline보다 완만 (Extended Data Fig. 3)"],
        ["log10 condition number", "생성자 conditioning (낮을수록 좋음)", "MediQ-GAN 2.09 / 2.04 / 2.01 (ISIC / ODIR / Retina)\nDCGAN 2.54 / 2.54 / 2.44, StyleGAN2-ADA 5.78 / 6.25 / 6.58"],
        ["DLA 분석", "회로가 만드는 변환군의 차원으로 표현력과 barren plateau 위험을 판단", "depth 8에서 표현력이 충분하고 barren plateau를 피함"],
        ["ablation", "양자 채널 수, VQC 개수", "늘릴수록 성능과 effective rank 개선, 현 설정 이후 이득 감소. 16채널 · 5 VQC는 시뮬레이션 비용과 절충"],
    ], fs=11, hfs=11.5, min_rh=0.6)
    callout(s, X0, end + 0.25, W0, 6.75 - end - 0.25, "한계", [
        "논문 결론: MediQ-GAN은 모든 unconstrained benchmark에서 고전 생성모델을 넘어서지는 못함. 이 분석은 생성자의 수치적 성질에 대한 것임"], fs=11)
    caption(s, "수치 출처: Jiao et al., Extended Data Table 5, Discussion")
    d.finish_slide(s)

    # --- C1 점검 항목
    s = d.add("C1")
    header(s, "03 · 내용 정리", "두 논문을 읽을 때의 점검 항목", "양자 생성모델 논문의 주장을 평가할 때 적용하는 다섯 가지 기준")
    table(s, X0, 2.2, [2.4, 4.4, 5.13], [
        ["점검 항목", "QGAN", "MediQ-GAN"],
        ["비교 대상", "고전 vanilla GAN 1종", "고전 GAN 5종, 확산 모델 2종, MosaiQ"],
        ["평가 방식", "분류 성능 (AUC-ROC, 정확도)", "분류 성능 + FID + LPIPS"],
        ["양자 요소의 범위", "생성자 전체", "생성자 일부 (공식 코드 기준 16개 위치 중 5개)"],
        ["조건 의존성", "segmentation 입력에서만 증강 효과", "모든 지표에서 최고는 아님 (결과 ①, ②)"],
        ["한계의 명시", "개선 폭 AUC +0.017. 이 저장소 8×8 재현에서는 정확도 하락", "실기 검증은 inference에 한정. 고전 모델을 전 영역에서 넘지는 못함"],
    ], fs=12.5, hfs=12, min_rh=0.8)
    d.finish_slide(s)

    # --- C2 2·3일차 대응
    s = d.add("C2")
    header(s, "03 · 내용 정리", "2·3일차 실습과의 대응", "회로 사양은 유지하고 해상도와 학습량을 줄여 Colab 무료 CPU에서 끝까지 실행")
    end = table(s, X0, 2.2, [2.5, 4.9, 4.53], [
        ["이론 (1일차)", "실습 구현", "원 논문과의 차이"],
        ["QGAN patch 생성자", "2일차: sub-generator 4개 × 7큐빗(데이터 6 + ancilla 1), depth 10", "논문: 16개 × 8큐빗. 16×16 그레이스케일"],
        ["QGAN 판별자", "5층 완전연결 (2·3일차 공통)", "동일 (Table 4)"],
        ["MediQ-GAN dual-stream", "3일차: 양자 stream 16큐빗 × 5, depth 8. 25 epoch 미세조정", "고전 부분·판별자는 MLP + 표준 BCE (논문: conv + WGAN-GP)"],
        ["평가", "지표 4종 (16×16에서 FID 불가)", "논문: FID, LPIPS, 분류 성능"],
        ["실행 환경", "PennyLane exact 시뮬레이션, Colab CPU", "논문: GPU, IBM 실기는 inference"],
    ], fs=11.5, hfs=11.5, min_rh=0.62)
    callout(s, X0, end + 0.2, W0, 6.75 - end - 0.2, "실측 (로컬 CPU, README)", [
        "QGAN 600 step: 클래스 평균 상관 0.195. MediQ-GAN 25 epoch: 0.365, 단 다양성은 실제의 약 1/8. 두 모델의 평균 형태와 다양성 절충이 다르게 나타남"], fs=11)
    d.finish_slide(s)


ORDER = (
    ["O1", "O2", "O3", "O4", "O5", "PRE", "G1", "G2", "G3", "Q1", "Q2", "Q3", "Q4", "Q5", "BRK"]
    + ["O6", "O7", "O8", "O9", "O10", "T1", "O11", "IMG", "O12", "O13", "O14"]
    + ["O15", "O16", "M1", "O17", "O18", "O19", "M2", "O20", "O21", "O22", "O23", "O24", "O25", "O26"]
    + ["R1", "R2", "R3", "R4", "R5"]
    + ["O27", "O28", "C1", "C2", "O29", "O30", "O31"]
)


def main():
    path = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PPTX)
    d = Deck(path)
    edit_originals(d)
    build_new(d)
    d.reorder(ORDER)
    total = sum(NOTES[k][0] for k in ORDER)
    pre = sum(NOTES[k][0] for k in ORDER[: ORDER.index("BRK")])
    for i, k in enumerate(ORDER, 1):
        mins, text = NOTES[k]
        text = text.replace("{TOTAL}", str(total))
        head = f"[약 {mins}분]\n" if mins else ""
        d.slide_of(k).notes_slide.notes_text_frame.text = head + text
    d.prs.save(path)
    print(f"{len(ORDER)}장 저장: {path}")
    print(f"휴식 전 {pre}분, 전체 발표 {total}분(휴식 제외), 슬라이드 번호 {ORDER.index('BRK') + 1}번이 휴식")


if __name__ == "__main__":
    main()
