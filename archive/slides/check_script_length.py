"""발표 대본 분량 점검: 슬라이드별 대본 글자 수와 표기된 소요 시간이 분당 300자 기준에 맞는지 확인함.

사용법: python3 check_script_length.py [pptx ...]   (기본: 1·2·3일차 pptx)
표기 시간은 글자 수에서 자동 계산되므로(extend_day1.py, build_day2·3.js) 어긋나면 대본을 고친 뒤 다시 빌드하면 됨.
"""
import os, re, sys
from pptx import Presentation

CPM = 300
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = [os.path.join(HERE, "..", "..", "practice", f"day{n}_slides", f) for n, f in
           ((1, "day1_theory_slides.pptx"), (2, "day2_practice_slides.pptx"), (3, "day3_practice_slides.pptx"))]


def main(paths):
    for path in paths:
        total_c = total_m = 0
        bad = []
        for i, s in enumerate(Presentation(path).slides, 1):
            note = s.notes_slide.notes_text_frame.text if s.has_notes_slide else ""
            m = re.match(r"\[약 (\d+)분\]\n", note)
            body = note[m.end():] if m else note
            chars = len(body.replace("\n", ""))
            label = int(m.group(1)) if m else 0
            total_c += chars
            total_m += label
            if m and abs(chars / CPM - label) > 0.5 + 1e-9 and not (label == 1 and chars < CPM):
                bad.append((i, chars, label))
        print(f"{os.path.basename(path)}: 슬라이드 {i}장, 대본 {total_c:,}자, 표기 합계 {total_m}분, 글자 기준 {total_c / CPM:.0f}분")
        for i, c, l in bad:
            print(f"  불일치: {i}번 {c}자 (표기 {l}분, 글자 기준 {c / CPM:.1f}분)")


if __name__ == "__main__":
    main(sys.argv[1:] or DEFAULT)
