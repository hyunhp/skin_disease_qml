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
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

from day1_notes import NOTES
from postprocess_pptx import process as postprocess

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "fig_day1")
IMG = os.path.join(HERE, "..", "..", "practice", "docs", "image")
DEFAULT_PPTX = os.path.join(HERE, "..", "..", "practice", "day1_slides", "day1_theory_slides.pptx")

FONT = "Noto Sans KR"
INK, GRAY, GREEN, GREEN2, DARK = "212121", "6B6B6B", "00754A", "006241", "1E3932"
ROW, CARD, CREAM, AMBER = "EDEBE9", "F2F0EB", "FAF6EE", "9C5000"
PURPLE_BG, PURPLE, GREEN_BG, SAND, MUTED = "ECE6F5", "5B3F8C", "E4F0EA", "DFC49D", "CFC9B8"
X0, W0 = 0.7, 11.93  # 본문 좌측 여백, 본문 폭 (인치)
# PowerPoint로 넣었던 GAN 도입 3장. 캐릭터 그림·라벨 오류·'보상/페널티' 표현이 있어 템플릿 슬라이드 GAN1 ~ GAN3으로 대체하고 실행 시 지움
REPLACED_USER = {"user:gan1", "user:gan2", "user:gan3"}


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
        self.by_key, self.file_order = {}, []
        self._index_slides()
        self._drop_added()
        self.num_donor = None
        for sh in self.slide_of("O3").shapes:
            if sh.is_placeholder and "sldNum" in sh._element.xml:
                self.num_donor = sh._element
        self.blank = self.prs.slide_layouts.get_by_name("Blank")
        self.new = {}

    def _index_slides(self):
        """슬라이드를 cSld 이름으로 식별함. orig:N = 원본 N번, user:* = 사용자가 직접 넣은 슬라이드, added:* = 이 스크립트가 만든 슬라이드.
        이름이 없는 슬라이드(PowerPoint에서 새로 넣은 것)는 user:autoN으로 이름을 붙이고 앞 슬라이드 바로 뒤에 둠."""
        auto = 0
        for s in self.prs.slides:
            nm = s._element.cSld.get("name") or ""
            if nm in REPLACED_USER:
                continue
            m = re.fullmatch(r"orig:(\d+)", nm)
            if m:
                key = "O" + m.group(1)
            elif nm.startswith("user:"):
                key = nm
            elif nm.startswith("added:"):
                key = nm[len("added:"):]
            else:
                auto += 1
                key = f"user:auto{auto}"
                s._element.cSld.set("name", key)
            self.file_order.append(key)
            if not nm.startswith("added:"):
                self.by_key[key] = s

    def _drop_added(self):
        lst = self.prs.slides._sldIdLst
        for sid in list(lst):
            sl = self.prs.part.related_part(sid.rId).slide
            nm = sl._element.cSld.get("name") or ""
            if nm.startswith("added:") or nm in REPLACED_USER:
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
        """order에 있는 슬라이드는 그 순서대로, order에 없는 사용자 슬라이드는 파일에서 바로 앞이던 슬라이드 뒤에 둠."""
        known = set(order)
        attached, front, pred = {}, [], None
        for k in self.file_order:
            if k in known:
                pred = k
            elif pred is None:
                front.append(k)
            else:
                attached.setdefault(pred, []).append(k)
        final = list(front)
        for k in order:
            final.append(k)
            final += attached.get(k, [])
        lst = self.prs.slides._sldIdLst
        by_id = {sid.id: sid for sid in lst}
        objs = [by_id[self.slide_of(k).slide_id] for k in final]
        self.final = final
        for sid in list(lst):
            lst.remove(sid)
        for sid in objs:
            lst.append(sid)

    def slide_of(self, key):
        return self.by_key[key] if key in self.by_key else self.new[key]


def clear_text_runs(shape, text):
    """첫 문단의 첫 run 서식은 유지하고 텍스트만 교체."""
    p = shape.text_frame.paragraphs[0]
    runs = p.runs
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


# ----------------------------------------------------------------------------- 용어 정정
# 변분 양자회로 = variational quantum circuit(VQC). PQC = parameterized quantum circuit. 변분 layer = variational layer
TERM_FIXES = {
    "O7": [("변분 양자회로(PQC)", "parameterized quantum circuit(PQC)")],
    "O10": [("변분 양자회로(PQC)", "parameterized quantum circuit(PQC)"), ("변분 layer", "variational layer")],
}


def _walk(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from _walk(sh.shapes)


def _paragraphs(slide):
    paras = []
    for sh in _walk(slide.shapes):
        if sh.has_text_frame:
            paras += list(sh.text_frame.paragraphs)
        if getattr(sh, "has_table", False) and sh.has_table:
            for r in sh.table.rows:
                for c in r.cells:
                    paras += list(c.text_frame.paragraphs)
    return paras


def _set_runs(shape, par_idx, texts):
    """문단의 앞쪽 런 텍스트를 순서대로 교체하고 남는 런은 지움(서식은 첫 런 유지)."""
    runs = shape.text_frame.paragraphs[par_idx].runs
    for r, t in zip(runs, texts):
        r.text = t
    for r in runs[len(texts):]:
        r._r.getparent().remove(r._r)


def fix_o20(slide):
    """VQC·VQA·QAOA 슬라이드: PQC(parameterized)와 VQC(variational)의 관계를 표에 반영."""
    for sh in _walk(slide.shapes):
        if sh.name == "TextBox 9":
            _set_runs(sh, 0, ["parameterized quantum circuit(PQC) + 고전 최적화 루프를 사용하는 알고리즘 상위 범주"])
        elif sh.name == "TextBox 11":
            _set_runs(sh, 1, ["Circuit / Classifier)"])
        elif sh.name == "TextBox 12":
            _set_runs(sh, 0, ["PQC를 variational 방식으로 학습시키는 구현. 분류 등 지도학습에 쓰며 data encoding + 학습 가능한 ansatz로 구성 (MediQ-GAN의 양자 stream)"])
        elif sh.name == "TextBox 18":
            runs = sh.text_frame.paragraphs[0].runs
            runs[2].text = "PQC"
            runs[3].text = " → 측정 → 고전 "


def fix_terms(d):
    """런 단위로 치환하고, 문구가 여러 런에 걸쳐 있으면 문단의 첫 런으로 합쳐 치환함."""
    log = []
    for key, pairs in TERM_FIXES.items():
        paras = _paragraphs(d.slide_of(key))
        for old, new in pairs:
            for p in paras:
                if old not in "".join(r.text for r in p.runs):
                    continue
                hit = False
                for r in p.runs:
                    if old in r.text:
                        r.text = r.text.replace(old, new)
                        hit = True
                if not hit:
                    full = "".join(r.text for r in p.runs).replace(old, new)
                    p.runs[0].text = full
                    for r in p.runs[1:]:
                        r._r.getparent().remove(r._r)
                log.append((key, old))
    fix_o20(d.slide_of("O20"))
    return log


# ----------------------------------------------------------------------------- 기존 슬라이드 수정
def edit_originals(d):
    # 3번: 학습목표 5항목으로 재구성
    s = d.slide_of("O3")
    for sh in list(s.shapes):
        if not (sh.is_placeholder and "sldNum" in sh._element.xml):
            sh._element.getparent().remove(sh._element)
    header(s, "오리엔테이션", "학습목표", "INDEX")
    goals = [
        "HAM10000 데이터셋 EDA와 클래스 불균형 문제",
        "GAN 학습 구조·평가 지표(FID, LPIPS)와 양자회로 기초(qubit, 게이트, 측정, VQC)",
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
    for sh in d.slide_of("O24").shapes:
        if sh.has_text_frame and "IBM Marrakesh 실기에 올려" in sh.text_frame.text:
            clear_text_runs(sh, "학습 완료된 회로를 IBM Marrakesh 실기에 올려 inference만 검증 (클래스별 FID +19 ~ +79 상승, 논문은 '비교 가능한 수준'으로 평가)")
    # 26번: 줄표 규칙(CLAUDE.md)에 맞춰 en dash를 하이픈으로
    for sh in d.slide_of("O26").shapes:
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
        ("양자회로", "qubit과 상태벡터, 회전·얽힘 게이트, 측정과 기댓값, variational quantum circuit(VQC)의 hybrid 학습 루프, 시뮬레이션의 한계"),
        ("이후 내용과의 관계", "이 장에서 정의한 용어(RY, CNOT, 기댓값, WGAN-GP, FID)를 QGAN·MediQ-GAN 설명에서 그대로 사용함"),
    ])

    # --- GAN1 개요
    s = d.add("GAN1")
    header(s, "사전 지식 · GAN", "GAN: 적대적 학습으로 데이터 분포를 근사하는 생성모델",
           "Generative Adversarial Network(생성적 적대 신경망). Goodfellow et al., NeurIPS 2014")
    picture(s, f("gan_dist.png"), 1.2, 2.15, w=10.9)
    card(s, X0, 5.2, 6.85, 1.55, None, [
        "**목적**: 실제 분포 p_data를 근사하는 생성 분포 p_g를 학습해 새 샘플을 만듦",
        "**구성**: 생성자 G와 판별자 D, 두 신경망",
        "**학습 신호**: D의 판단이 G의 손실이 됨. 정답 이미지와 픽셀 단위로 비교하지 않음",
    ], fs=11)
    callout(s, 7.8, 5.2, 4.83, 1.55, "의료 이미지 증강에서의 용도", [
        "희귀 병변은 수집이 어렵고 개인정보 문제로 공유가 제한됨",
        "소수 클래스(df 115장)를 새 샘플로 보충. 유용성은 지표로 별도 검증",
    ], fs=11)
    caption(s, "그림: 개념도(1차원 예시). 수치 데이터가 아님")
    d.finish_slide(s)

    # --- GAN2 역할
    s = d.add("GAN2")
    header(s, "사전 지식 · GAN", "생성자와 판별자의 역할", "두 신경망은 입력·출력이 다르고 목표가 서로 반대임. 이 반대 관계가 '적대적'의 의미임")
    picture(s, f("gan_roles.png"), X0, 2.25, w=5.9)
    table(s, 6.85, 2.2, [1.15, 2.45, 2.18], [
        ["항목", "생성자 G", "판별자 D"],
        ["입력", "노이즈 벡터 z", "이미지 (실제 x 또는 생성 x̃)"],
        ["출력", "이미지 x̃ = G(z)", "진짜일 확률 (0 ~ 1)"],
        ["목표", "D(G(z))를 1에 가깝게", "D(x)는 1, D(G(z))는 0에 가깝게"],
        ["모델 유형", "생성모델", "이진 분류기"],
        ["2일차 구현", "양자회로 4개, 파라미터 280개", "5층 완전연결, 파라미터 19,201개"],
    ], fs=11, hfs=11.5, min_rh=0.5)
    callout(s, X0, 5.65, W0, 1.1, "실습과의 연결", [
        "QGAN·MediQ-GAN은 G에만 양자회로를 넣음. 2일차는 D가 G보다 약 70배 커서 학습률을 G 0.05, D 0.001로 다르게 둠 (2일차 노트북)"], fs=11)
    d.finish_slide(s)

    # --- GAN3 학습 과정
    s = d.add("GAN3")
    header(s, "사전 지식 · GAN", "학습 과정: 판별자와 생성자를 번갈아 갱신",
           "한 step 안에서 D를 먼저, G를 나중에 갱신함. 2·3일차 노트북의 학습 루프와 같은 순서임")
    picture(s, f("gan_step.png"), X0, 2.15, w=6.25)
    card(s, 7.3, 2.2, 5.33, 3.45, "종료와 손실 해석", [
        "보상이 아니라 손실의 gradient로 파라미터를 갱신함",
        "학습은 정해진 step 수에서 멈춤 (2일차 400 step). 생성 분포가 실제와 같아지는 시점을 손실로 알 수는 없음",
        "이론상 평형(p_g = p_data)에서 D = 1/2이고 이때 D 손실 2 ln 2 ≈ 1.386, G 손실 ln 2 ≈ 0.693. 2일차 로그의 기준값",
        "D 손실이 0에 가까우면 D가 압도해 G의 gradient가 약해짐",
        "품질은 손실이 아닌 평가 지표로 판단함 (이어지는 지표 슬라이드)",
    ], fs=11)
    callout(s, X0, 5.85, W0, 0.9, "코드 대응 (2일차 노트북)", [
        "loss_d = bce(disc(batch), 1) + bce(disc(gen(B).detach()), 0) → opt_d.step()   /   loss_g = bce(disc(gen(B)), 1) → opt_g.step()"], fs=10.5)
    d.finish_slide(s)

    # --- G1
    s = d.add("G1")
    header(s, "사전 지식 · GAN", "GAN의 목적함수(minimax)", "앞의 학습 과정을 하나의 목적함수와 갱신 방향으로 정식화함")
    w, h = picture(s, f("gan_game.png"), X0, 2.15, w=7.7)
    card(s, 8.7, 2.15, 3.93, 3.0, None, [
        "**D 갱신**: 실제 x는 1, 생성 x̃는 0으로 분류하도록 V를 최대화",
        "**G 갱신**: D가 x̃를 1로 판단하도록 V를 최소화",
        "**D의 최적해**: D*(x) = p_data(x) / (p_data(x) + p_g(x)). p_g = p_data이면 1/2",
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
    callout(s, X0, 5.6, W0, 1.2, "용어와 실습 연결", [
        "support: 분포가 0이 아닌 값을 갖는 영역. JS divergence, Wasserstein-1: 두 확률분포 사이의 거리 척도. 1-Lipschitz: 입력이 변할 때 출력 변화율이 1 이하인 함수",
        "3일차: MediQ-GAN을 생성자 학습률 0.02로 학습하면 3 epoch 만에 mode collapse가 발생함. 원 논문이 WGAN-GP critic을 쓰는 이유에 해당함"], fs=10.5)
    d.finish_slide(s)

    # --- G3
    s = d.add("G3")
    header(s, "사전 지식 · GAN", "생성 품질 평가: 지표별 측정 대상", "생성 이미지의 품질은 눈으로 판단하기 어려워 정량 지표를 병행함. 용어는 이어지는 세 장에서 풀어 설명함")
    table(s, X0, 2.2, [2.0, 3.55, 1.45], [
        ["지표", "측정 대상", "방향"],
        ["Downstream 분류 성능\n(AUC-ROC, 정확도)", "생성 이미지를 학습 데이터에 추가했을 때 분류기 성능 변화\nQGAN 논문, MediQ-GAN Table 1", "높을수록 좋음"],
        ["FID", "실제와 생성 이미지의 Inception 특징 분포(평균·공분산) 사이 Fréchet 거리\nMediQ-GAN 논문 (클래스별)", "낮을수록 좋음"],
        ["intra-class LPIPS", "같은 클래스 생성 이미지 쌍의 지각적 거리 평균. mode collapse 점검\nMediQ-GAN 논문", "높을수록 다양"],
        ["지표 4종 (실습)", "픽셀 분포, 클래스 평균 상관, 최근접 실제 거리, 샘플 다양성\n2·3일차 노트북 (16×16에서는 FID 사용 불가)", "지표별 상이"],
    ], fs=10.5, hfs=11.5)
    card(s, 8.05, 2.2, 4.58, 4.4, "해석 시 유의", [
        "FID가 낮아도 LPIPS가 낮으면 비슷한 이미지만 생성한 것이므로 두 지표를 함께 봄",
        "표본이 적은 클래스(df 115장)에서는 FID 공분산 추정이 불안정함",
        "분류 성능은 분류기와 증강 비율에 의존함",
        "정확도만으로는 불균형 데이터의 성능을 판단하기 어려워 AUC를 함께 봄",
    ], fs=11)
    d.finish_slide(s)

    # --- G4 지표 용어 1: 분류 성능
    s = d.add("G4")
    header(s, "사전 지식 · 평가 지표", "지표 용어 ① 분류 성능: 정확도, ROC, AUC", "증강 효과를 분류기 성능으로 확인할 때 쓰는 용어")
    table(s, X0, 2.2, [1.7, 5.4], [
        ["용어", "설명"],
        ["downstream 평가", "생성 이미지를 실제로 쓰는 후속 작업(여기서는 분류)의 성능으로 생성 품질을 간접 평가"],
        ["양성 / 음성", "찾으려는 클래스(df)를 양성, 비교 클래스(nv)를 음성으로 둠 (이진 분류)"],
        ["정확도", "전체 중 맞힌 비율, (TP + TN) / 전체. df 대 nv 분류에서 nv가 98.3%(6,705 / 6,820)이므로 모두 nv로 답해도 98.3%라서 불균형 데이터에서는 높게 나옴"],
        ["ROC 곡선", "판정 기준값(threshold)을 바꾸며 TPR(양성을 맞힌 비율)과 FPR(음성을 양성으로 잘못 판정한 비율)을 그린 곡선"],
        ["AUC", "ROC 곡선 아래 면적. 무작위 양성이 무작위 음성보다 높은 점수를 받을 확률. 0.5는 무작위, 1.0은 완벽. 기준값과 클래스 비율의 영향을 덜 받음"],
    ], fs=11, hfs=11.5, min_rh=0.6)
    picture(s, f("roc_example.png"), 8.45, 2.15, w=4.18)
    tb(s, 8.45, 5.95, 4.18, 0.6, "TP, TN: 양성, 음성을 맞힌 수. 곡선이 왼쪽 위로 휠수록 AUC가 큼", size=10, color=GRAY, ls=1.25)
    d.finish_slide(s)

    # --- G5 지표 용어 2: FID
    s = d.add("G5")
    header(s, "사전 지식 · 평가 지표", "지표 용어 ② FID: Inception 특징과 Fréchet 거리", "실제 이미지 집합과 생성 이미지 집합이 얼마나 비슷한 분포인지를 한 숫자로 나타냄")
    end = table(s, X0, 2.2, [1.85, 4.95], [
        ["용어", "설명"],
        ["Inception 특징", "ImageNet으로 사전학습한 Inception-v3의 마지막 pooling 출력(2,048차원). 이미지를 숫자 벡터로 바꾼 표현"],
        ["특징 분포", "이미지 집합을 특징 공간의 점 구름으로 보고 평균 μ와 공분산 Σ로 요약(가우시안 근사)"],
        ["Fréchet 거리", "두 가우시안 사이의 거리. 평균 차이와 분산 형태 차이를 함께 반영함"],
        ["FID 해석", "0에 가까울수록 두 분포가 비슷함. 클래스당 표본이 적으면 Σ 추정이 불안정함"],
    ], fs=11, hfs=11.5, min_rh=0.62)
    rect(s, X0, end + 0.25, 6.8, 0.85, "FFFFFF", line=GREEN, rounded=True)
    tb(s, X0, end + 0.25, 6.8, 0.85, "FID = ‖μ_r − μ_g‖² + Tr( Σ_r + Σ_g − 2(Σ_r Σ_g)^½ )", size=15, color=GREEN2, bold=True,
       align="c", anchor="m", ls=1.0)
    picture(s, f("fid_concept.png"), 7.85, 2.2, w=4.78)
    card(s, 7.85, 4.6, 4.78, 2.1, "읽는 법", [
        "r은 실제(real), g는 생성(generated) 이미지 집합",
        "왼쪽 그림: 분포가 겹쳐 FID 낮음. 오른쪽: 분포가 어긋나고 일부 영역만 덮어 FID 높음",
        "이 강의의 실습은 16×16이라 Inception 입력 크기에 맞지 않아 FID를 쓰지 않음",
    ], fs=10.5)
    d.finish_slide(s)

    # --- G6 지표 용어 3: LPIPS
    s = d.add("G6")
    header(s, "사전 지식 · 평가 지표", "지표 용어 ③ LPIPS: 지각적 거리와 다양성", "같은 클래스에서 만든 이미지끼리 얼마나 다른지로 mode collapse를 점검함")
    picture(s, f("lpips_flow.png"), (13.333 - 10.4) / 2, 2.0, w=10.4)
    hw = (W0 - 0.25) / 2
    card(s, X0, 5.2, hw, 1.65, "용어", [
        "**지각적 거리**: 픽셀 값 차이가 아니라 사전학습 CNN 특징으로 잰 이미지 간 차이. 사람의 유사성 판단과 더 잘 맞음",
        "**LPIPS**: Learned Perceptual Image Patch Similarity. layer별 특징 차이를 학습된 가중치로 합산한 거리",
    ], fs=10.5)
    card(s, X0 + hw + 0.25, 5.2, hw, 1.65, "intra-class LPIPS의 해석", [
        "**intra-class**: 같은 클래스 안의 생성 이미지 쌍만 비교함",
        "값이 실제 이미지 쌍의 값에 가까우면 다양성이 충분하고, 크게 낮으면 비슷한 이미지만 만드는 mode collapse",
    ], fs=10.5)
    caption(s, "정의 출처: Zhang et al., The Unreasonable Effectiveness of Deep Features as a Perceptual Metric (CVPR 2018)")
    d.finish_slide(s)

    # --- QI1 양자 컴퓨팅과 양자 머신러닝
    s = d.add("QI1")
    header(s, "사전 지식 · 양자 컴퓨팅", "양자 컴퓨팅과 양자 머신러닝", "양자회로를 머신러닝 모델의 일부로 쓰는 접근을 데이터와 알고리즘 종류로 분류함")
    picture(s, f("qml_taxonomy.png"), X0, 2.2, w=6.5)
    card(s, 7.55, 2.2, 5.08, 3.0, "정의", [
        "**양자 컴퓨팅**: 중첩, 얽힘, 간섭을 이용하는 계산 모델. 입력은 큐빗, 연산은 양자 게이트, 출력은 측정",
        "**양자 머신러닝(QML)**: 양자회로를 학습 가능한 모델의 일부로 사용함",
        "**hybrid**: 회로는 일부이고 입출력 처리, 손실 계산, optimizer는 고전 컴퓨터가 담당함",
    ], fs=11)
    callout(s, X0, 5.55, W0, 1.2, "이 강의의 범위", [
        "QGAN과 MediQ-GAN은 고전 데이터(이미지)를 각도로 바꿔 양자회로에 넣는 CQ 유형임. 양자 컴퓨터가 이미지를 직접 읽는다는 뜻이 아니라, 회로가 파라미터를 가진 함수로 쓰이는 것임"], fs=11)
    caption(s, "분류 출처: Schuld, Sinayskiy & Petruccione, Contemporary Physics 56 (2015)")
    d.finish_slide(s)

    # --- QI2 중첩, 얽힘, 간섭
    s = d.add("QI2")
    header(s, "사전 지식 · 양자 컴퓨팅", "양자 연산의 세 가지 성질: 중첩, 얽힘, 간섭", "세 성질이 회로 안에서 각각 어떤 역할을 하는지를 이 강의의 회로와 연결함")
    end = table(s, X0, 2.2, [1.4, 4.9, 5.63], [
        ["성질", "의미", "이 강의의 회로에서의 역할"],
        ["중첩", "큐빗이 |0⟩과 |1⟩의 진폭을 동시에 가짐. 측정하면 확률에 따라 하나로 정해짐", "RY(θ)로 각도를 조절해 측정 확률을 정함 (노이즈 encoding, 학습 파라미터)"],
        ["얽힘", "여러 큐빗의 측정 결과가 독립이 아니라 상관을 가짐", "CNOT, CZ로 픽셀 또는 특징 사이의 상관을 표현함"],
        ["간섭", "진폭이 더해지거나 상쇄되어 측정 확률이 달라짐", "variational layer가 진폭을 조합해 확률 분포를 만들고, 학습은 이 결과를 조절함"],
    ], fs=11, hfs=11.5, min_rh=0.62)
    picture(s, f("interference_amp.png"), X0, end + 0.2, w=6.4)
    card(s, 7.35, end + 0.2, 5.28, 6.8 - end - 0.2, "간섭 예시", [
        "RY(π/2)로 |0⟩과 |1⟩의 진폭이 각각 0.71로 나뉨 (중첩)",
        "RY(−π/2)를 이어 적용하면 |1⟩의 진폭이 0.71×0.71 − 0.71×0.71 = 0으로 상쇄되어 |0⟩만 남음 (간섭)",
    ], fs=10.5)
    d.finish_slide(s)

    # --- QI3 고전 layer와 VQC layer
    s = d.add("QI3")
    header(s, "사전 지식 · 양자 컴퓨팅", "고전 layer와 VQC layer", "VQC(variational quantum circuit)는 입력과 출력이 고전 값이므로 신경망의 layer 하나처럼 쓸 수 있음")
    picture(s, f("layer_compare.png"), (13.333 - 9.6) / 2, 2.0, w=9.6)
    cw = (W0 - 2 * 0.2) / 3
    for i, (t, lines) in enumerate([
        ("입력 표현", ["고전: 벡터를 그대로 사용", "VQC: 값을 회전각으로 변환(encoding)해 큐빗에 넣음"]),
        ("연산과 비선형성", ["고전: 행렬곱 + 활성화 함수", "VQC: 유니터리 연산(선형, 노름 보존). 비선형성은 encoding의 삼각함수와 측정 확률(진폭의 제곱)에서 생김"]),
        ("파라미터와 학습", ["고전: 가중치 행렬, backpropagation", "VQC: 회전각 θ, adjoint 또는 parameter-shift로 gradient 계산"]),
    ]):
        card(s, X0 + i * (cw + 0.2), 5.3, cw, 1.55, t, lines, fs=10)
    d.finish_slide(s)

    # --- G2B 학습 불안정성 시각화
    s = d.add("G2B")
    header(s, "사전 지식 · GAN", "학습 불안정성 시각화: mode collapse, JS 대 Wasserstein", "앞 슬라이드의 두 문제를 2차원 예시와 거리 척도 비교로 확인함")
    w1, h1 = picture(s, f("mode_collapse.png"), X0, 2.1, w=6.4)
    w2, h2 = picture(s, f("js_vs_wasserstein.png"), 7.55, 2.1, w=5.08)
    card(s, X0, 5.45, 6.4, 1.4, "mode collapse", [
        "실제 분포가 두 mode(예: 서로 다른 두 병변 형태)를 가져도 한 mode만 반복하면 판별자를 속일 수 있음",
        "다양성 지표(LPIPS, 샘플 간 거리)로 점검함",
    ], fs=10.5)
    card(s, 7.55, 5.45, 5.08, 1.4, "vanishing gradient와 WGAN", [
        "support가 겹치지 않으면 JS는 ln 2로 일정해 생성자에게 방향 정보가 없음",
        "Wasserstein-1은 거리에 비례해 gradient가 남음",
    ], fs=10.5)
    caption(s, "개념도(2차원 예시와 점질량 분포 가정). 수치 데이터가 아님")
    d.finish_slide(s)

    # --- Q1B Bloch 구
    s = d.add("Q1B")
    header(s, "사전 지식 · 양자회로", "1큐빗 상태의 시각화: Bloch 구 단면과 RY 회전", "RY(θ)는 상태를 x-z 평면의 원 위에서 θ만큼 회전시키고, 측정 확률은 z축 성분이 정함")
    picture(s, f("bloch_ry.png"), X0, 2.1, w=4.5)
    end = table(s, 5.5, 2.2, [1.5, 5.63], [
        ["항목", "설명"],
        ["Bloch 구", "1큐빗 순수 상태를 구 위의 한 점으로 나타냄. 북극이 |0⟩, 남극이 |1⟩"],
        ["RY(θ)", "y축 주위의 회전. 상태가 x-z 평면을 벗어나지 않아 이 슬라이드는 그 단면을 그림"],
        ["측정 확률", "z축 성분이 정함. 북극에 가까울수록 0이 나올 확률이 큼"],
        ["RX, RZ", "RX는 x축 주위, RZ는 z축 주위의 회전. RZ는 확률을 바꾸지 않고 위상만 바꿔 간섭에 영향을 줌"],
    ], fs=10.5, hfs=11.5, min_rh=0.6)
    callout(s, 5.5, end + 0.25, 7.13, 6.8 - end - 0.25, "읽는 법", [
        "θ = 0이면 |0⟩, θ = π이면 |1⟩, θ = π/2이면 x축 방향(50 : 50). 학습은 이 θ들을 조정해 확률 분포를 만드는 과정임"], fs=10.5)
    d.finish_slide(s)

    # --- ENC encoding 방식 비교
    s = d.add("ENC")
    header(s, "사전 지식 · 양자회로", "Encoding 방식 비교: angle encoding과 amplitude encoding", "같은 값 4개(실제 DF 이미지의 2×2 patch)를 두 방식으로 큐빗에 넣는 예")
    picture(s, f("encoding_compare.png"), (13.333 - 9.0) / 2, 1.95, w=9.0)
    end = table(s, X0, 5.15, [2.0, 4.9, 5.03], [
        ["비교", "angle encoding", "amplitude encoding"],
        ["큐빗 수", "값 n개 → 큐빗 n개", "값 2ⁿ개 → 큐빗 n개"],
        ["회로 깊이", "게이트 1층", "상태 준비 회로가 일반적으로 깊음"],
        ["두 논문", "QGAN RY(z), MediQ-GAN RX → RY", "사용하지 않음"],
    ], fs=10.5, hfs=10.5, min_rh=0.33, hh=0.33)
    tb(s, X0, end + 0.06, W0, 0.3, "두 논문에서 encoding되는 값은 이미지가 아니라 노이즈(QGAN)와 특징 벡터(MediQ-GAN)임. 위 이미지는 두 방식을 비교하기 위한 예시임",
       size=10, color=GRAY, ls=1.1)
    d.finish_slide(s)

    # --- PATCH patch 분할 예시
    s = d.add("PATCH")
    header(s, "01 · QGAN 논문", "patch 분할 예시: 16×16 = 4 patch × 64픽셀", "큐빗 수에 맞춰 이미지를 띠로 나누고, sub-generator마다 patch 하나를 생성함")
    picture(s, f("patch_split.png"), (13.333 - 11.0) / 2, 2.0, w=11.0)
    callout(s, X0, 5.95, W0, 0.9, "논문과 실습의 구성", [
        "논문: sub-generator 16개 × 데이터 큐빗 7개(patch당 128픽셀). 실습: 4개 × 6개(patch당 64픽셀). patch는 서로 독립인 회로가 만들어 경계가 어긋날 수 있음"], fs=10.5)
    d.finish_slide(s)

    # --- PS parameter-shift 예시
    s = d.add("PS")
    header(s, "02 · MEDIQ-GAN 논문 · 심화", "parameter-shift rule 예시: f(θ) = ⟨Z⟩ = cos θ", "shift한 회로 두 번의 기댓값 차이로 정확한 미분을 얻음")
    picture(s, f("param_shift.png"), X0, 2.1, w=6.9)
    card(s, 7.85, 2.1, 4.78, 3.7, "계산 순서 (θ₀ = π/3)", [
        "f(θ₀) = cos(π/3) = 0.500",
        "θ₀ + π/2 회로를 실행: f = −0.866",
        "θ₀ − π/2 회로를 실행: f = 0.866",
        "차이를 2로 나눔: (−0.866 − 0.866) / 2 = −0.866 = −sin θ₀ = f′(θ₀)",
    ], fs=11)
    callout(s, X0, 6.0, W0, 0.85, "유의점", [
        "파라미터마다 회로를 2번 더 실행해야 하고, shot 기반이면 각 기댓값에 통계 오차가 붙음. 시뮬레이터에서는 adjoint나 backpropagation으로 대체함"], fs=10.5)
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
    header(s, "사전 지식 · 양자회로", "PQC·VQC와 hybrid 학습 루프", "PQC(parameterized quantum circuit)를 variational 방식으로 학습시킨 것이 VQC(variational quantum circuit)임. QGAN 논문은 PQC, MediQ-GAN 논문은 VQC로 부름")
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
        ("여기까지", "HAM10000 클래스 불균형 → GAN 구조·학습 불안정성 → 평가 지표 용어(정확도, AUC, FID, LPIPS) → 양자 컴퓨팅·QML 개요, 상태벡터, 게이트, 측정, VQC 학습 루프, encoding 방식, 시뮬레이션 한계"),
        ("이어서", "Chapter 1 QGAN (구조, 학습 step, 결과) → Chapter 2 MediQ-GAN (dual-stream, WGAN-GP, 결과) → Chapter 3 정리"),
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
    ["O1", "O2", "O3", "O4", "O5", "PRE", "GAN1", "GAN2", "GAN3", "G1", "G2", "G2B", "G3", "G4", "G5", "G6",
     "QI1", "QI2", "QI3", "Q1", "Q1B", "Q2", "Q3", "Q4", "ENC", "Q5", "BRK"]
    + ["O6", "O7", "O8", "O9", "PATCH", "O10", "T1", "O11", "IMG", "O12", "O13", "O14"]
    + ["O15", "O16", "M1", "O17", "O18", "O19", "M2", "O20", "O21", "O22", "O23", "O24", "O25", "PS", "O26"]
    + ["R1", "R2", "R3", "R4", "R5"]
    + ["O27", "O28", "C1", "C2", "O29", "O30", "O31"]
)


SPEECH_CPM = 300  # 강의 발화 속도: 분당 글자 수(공백 포함, 줄바꿈 제외)


def speech_minutes(text):
    """대본 글자 수에서 소요 시간(분)을 계산함. 최소 1분."""
    return max(1, round(len(text.replace("\n", "")) / SPEECH_CPM))


def main():
    path = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PPTX)
    d = Deck(path)
    edit_originals(d)
    for key, old in fix_terms(d):
        print("용어 정정(런 병합):", key, old)
    build_new(d)
    d.reorder(ORDER)
    final = d.final
    mins = {k: speech_minutes(NOTES[k]) for k in final if k in NOTES}
    total = sum(mins.values())
    pre = sum(mins[k] for k in final[: final.index("BRK")] if k in mins)
    for k in final:
        if k not in NOTES:
            print("대본 없음(건드리지 않음):", k)
            continue
        head = f"[약 {mins[k]}분]\n" if k != "BRK" else ""
        d.slide_of(k).notes_slide.notes_text_frame.text = head + NOTES[k]
    postprocess(d.prs)  # 대본을 넣은 뒤에 실행: 줄바꿈, 박스 안 가운데 정렬, 노트 페이지 서식
    d.prs.save(path)
    print(f"{len(final)}장 저장: {path}")
    print(f"대본 분량 기준: 휴식 전 {pre}분, 전체 {total}분(휴식 제외), 슬라이드 번호 {final.index('BRK') + 1}번이 휴식 (분당 {SPEECH_CPM}자)")


if __name__ == "__main__":
    main()
