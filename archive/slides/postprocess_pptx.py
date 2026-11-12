"""pptx 후처리: (1) 한글 줄바꿈을 단어 단위로, (2) 박스 안 텍스트를 가운데 정렬, (3) 노트 페이지 배치.

사용법: python3 postprocess_pptx.py <pptx> [<pptx> ...]   (제자리 덮어쓰기, 여러 번 실행해도 결과가 같음)
- (1) 모든 문단에 eaLnBrk="0"을 지정함. PowerPoint가 글자 단위가 아니라 공백(어절) 단위로 줄을 바꿈.
- (2) 채워진 사각형 안에 텍스트 상자만 들어 있으면, 텍스트를 상자의 세로 가운데에 놓음.
      텍스트 상자 1개: 상자 높이를 컨테이너에 맞추고 세로 가운데 정렬. 2개 이상(제목 + 본문): 묶음 전체를 컨테이너 가운데로 이동.
      원, 그림, 표, 다른 도형이 함께 들어 있는 컨테이너(다이어그램 틀 등)는 건드리지 않음.
- (3) 노트 페이지: 위쪽에 슬라이드 그림, 아래에 대본(Noto Sans KR 10.5pt). PDF의 notes 보기 품질용.
"""
import sys

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE, PP_PLACEHOLDER
from pptx.enum.text import MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
MIN_H, MIN_W = Inches(0.75), Inches(1.5)
TOL = Inches(0.06)


def wrap_by_word(slide):
    n = 0
    for p in slide._element.iter(qn("a:p")):
        pPr = p.find(qn("a:pPr"))
        if pPr is None:
            pPr = p.makeelement(qn("a:pPr"), {})
            p.insert(0, pPr)
        pPr.set("eaLnBrk", "0")
        n += 1
    return n


def _is_container(sh):
    if sh.shape_type != MSO_SHAPE_TYPE.AUTO_SHAPE:
        return False
    try:
        if sh.auto_shape_type not in (MSO_SHAPE.RECTANGLE, MSO_SHAPE.ROUNDED_RECTANGLE):
            return False
    except Exception:
        return False
    if sh.height < MIN_H or sh.width < MIN_W:
        return False
    if sh.has_text_frame and sh.text_frame.text.strip():
        return False
    spPr = sh._element.spPr
    return spPr.find(qn("a:solidFill")) is not None or spPr.find(qn("a:ln")) is not None


def _inside(c, sh):
    return (sh.left >= c.left - TOL and sh.top >= c.top - TOL and
            sh.left + sh.width <= c.left + c.width + TOL and sh.top + sh.height <= c.top + c.height + TOL)


def _intersects(c, sh):
    return (sh.left < c.left + c.width and sh.left + sh.width > c.left and
            sh.top < c.top + c.height and sh.top + sh.height > c.top)


def _has_text(sh):
    return sh.shape_type == MSO_SHAPE_TYPE.TEXT_BOX and sh.has_text_frame and sh.text_frame.text.strip()


def _pt(emu):
    return emu / 12700


def _text_extent(sh):
    """텍스트가 실제로 차지하는 세로 범위(EMU)를 글자 크기·줄 수로 추정함. 위쪽 정렬 상자는 위에서, 가운데 정렬 상자는 중앙에서 계산."""
    body = sh.text_frame._txBody.find(qn("a:bodyPr"))
    lI = int(body.get("lIns", 91440)); rI = int(body.get("rIns", 91440))
    tI = int(body.get("tIns", 45720)); bI = int(body.get("bIns", 45720))
    avail = _pt(sh.width - lI - rI)
    total = 0.0
    for p in sh.text_frame.paragraphs:
        runs = p._p.findall(qn("a:r"))
        sz = 18.0
        for r in runs:
            rPr = r.find(qn("a:rPr"))
            if rPr is not None and rPr.get("sz"):
                sz = int(rPr.get("sz")) / 100
                break
        text = "".join((r.find(qn("a:t")).text or "") for r in runs)
        width = sum((1.0 if ord(ch) > 0x2E7F else 0.56) for ch in text) * sz
        lines = max(1, -(-int(width) // max(int(avail), 1)))
        pPr = p._p.find(qn("a:pPr"))
        ls = 1.0
        before = after = 0.0
        if pPr is not None:
            sp = pPr.find(qn("a:lnSpc"))
            if sp is not None and sp.find(qn("a:spcPct")) is not None:
                ls = int(sp.find(qn("a:spcPct")).get("val")) / 100000
            for tag, name in (("a:spcBef", "b"), ("a:spcAft", "a")):
                e = pPr.find(qn(tag))
                if e is not None and e.find(qn("a:spcPts")) is not None:
                    v = int(e.find(qn("a:spcPts")).get("val")) / 100
                    if name == "b":
                        before = v
                    else:
                        after = v
        total += lines * sz * 1.2 * ls + before + after
    h = int(total * 12700)
    anchor = body.get("anchor", "t")
    if anchor == "ctr":
        mid = sh.top + sh.height // 2
        return mid - h // 2, mid + h // 2
    if anchor == "b":
        return sh.top + sh.height - bI - h, sh.top + sh.height - bI
    return sh.top + tI, sh.top + tI + h


def center_text_in_boxes(slide):
    shapes = list(slide.shapes)
    moved = 0
    for c in shapes:
        if not _is_container(c):
            continue
        straddle = [s for s in shapes if s is not c and _intersects(c, s) and not _inside(c, s)
                    and not (s.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE and s.width * s.height >= c.width * c.height)]
        if any(_has_text(s) for s in straddle):
            continue  # 박스 밖으로 걸친 텍스트가 있으면(제목이 밖에 있는 경우 등) 건드리지 않음
        inner = [s for s in shapes if s is not c and _inside(c, s)]
        if not inner or any(not (s.shape_type == MSO_SHAPE_TYPE.TEXT_BOX) for s in inner):
            continue  # 도형·그림·표가 함께 있으면 건드리지 않음
        texts = [s for s in inner if _has_text(s)]
        if not texts:
            continue
        if len(texts) == 1:
            t = texts[0]
            pad = Inches(0.12)
            t.top = c.top + pad
            t.height = c.height - 2 * pad
            tf = t.text_frame
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            bodyPr = tf._txBody.find(qn("a:bodyPr"))
            for tag in ("a:spAutoFit", "a:normAutofit", "a:noAutofit"):
                for e in bodyPr.findall(qn(tag)):
                    bodyPr.remove(e)
            bodyPr.append(bodyPr.makeelement(qn("a:noAutofit"), {}))
            moved += 1
        else:
            ext = [_text_extent(s) for s in texts]
            top = min(e[0] for e in ext)
            bottom = max(e[1] for e in ext)
            dy = (c.top + c.height // 2) - (top + bottom) // 2
            if abs(dy) > Inches(0.02):
                for s in texts:
                    s.top = s.top + dy
                moved += 1
    return moved


def style_notes(slide, font="Noto Sans KR", size=10.5):
    if not slide.has_notes_slide:
        return
    ns = slide.notes_slide
    for ph in ns.placeholders:
        t = ph.placeholder_format.type
        if t == PP_PLACEHOLDER.SLIDE_IMAGE:
            ph.left, ph.top, ph.width, ph.height = Inches(0.6), Inches(0.5), Inches(6.3), Inches(3.54)
        elif t == PP_PLACEHOLDER.BODY:
            ph.left, ph.top, ph.width, ph.height = Inches(0.6), Inches(4.25), Inches(6.3), Inches(5.3)
            tf = ph.text_frame
            tf.word_wrap = True
            for p in tf.paragraphs:
                p.space_after = Pt(5)
                for r in p.runs:
                    r.font.size = Pt(size)
                    rPr = r._r.get_or_add_rPr()
                    for tag in ("a:latin", "a:ea", "a:cs"):
                        for e in rPr.findall(qn(tag)):
                            rPr.remove(e)
                        rPr.append(rPr.makeelement(qn(tag), {"typeface": font}))


def fix_duplicate_ids(slide):
    """슬라이드 안에서 같은 도형 ID가 겹치면 PowerPoint가 복구 경고를 띄울 수 있어, 뒤의 중복에 새 ID를 줌."""
    P = "http://schemas.openxmlformats.org/presentationml/2006/main"
    els = list(slide._element.iter("{%s}cNvPr" % P))
    seen, nxt = set(), max([int(e.get("id", 0)) for e in els] + [1]) + 1
    n = 0
    for e in els:
        i = int(e.get("id", 0))
        if i in seen:
            e.set("id", str(nxt))
            seen.add(nxt)
            nxt += 1
            n += 1
        else:
            seen.add(i)
    return n


def process(prs):
    notesSz = prs.part._element.find(qn("p:notesSz"))
    if notesSz is not None:  # 노트 페이지 크기를 7.5 x 10인치로 통일
        notesSz.set("cx", "6858000")
        notesSz.set("cy", "9144000")
    stats = {"paragraphs": 0, "centered": 0}
    for s in prs.slides:
        stats["paragraphs"] += wrap_by_word(s)
        stats["centered"] += center_text_in_boxes(s)
        stats["ids"] = stats.get("ids", 0) + fix_duplicate_ids(s)
        style_notes(s)
    return stats


def process_file(path):
    prs = Presentation(path)
    st = process(prs)
    prs.save(path)
    return st


if __name__ == "__main__":
    for f in sys.argv[1:]:
        print(f, process_file(f))
