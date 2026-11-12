# slides - 슬라이드 생성

`practice/day2_slides/`, `practice/day3_slides/`의 pptx는 이 폴더의 스크립트로 만든다.
1일차 슬라이드(`practice/day1_slides/`)의 원본 31장은 PowerPoint로 직접 만든 파일이라 `extend_day1.py`가 이 위에 21장을 삽입하고 전체 발표 대본을 넣는다.

| 파일 | 내용 |
|---|---|
| `build_day2.js` | 2일차 슬라이드 25장 (내용 포함). 발표 대본은 `day2_notes.json` |
| `build_day3.js` | 3일차 슬라이드 10장 (내용 포함). 발표 대본은 `day3_notes.json` |
| `extend_day1.py` | 1일차 슬라이드 확장 (사전 지식 · 보충 자료 · 휴식 · 결과 · 정리 슬라이드 삽입, 학습목표·용어 수정, 66장 전체에 발표자 노트). 재실행 가능 |
| `day1_notes.py` | 1일차 발표 대본 (소요 시간은 글자 수에서 자동 계산) |
| `check_script_length.py` | 대본 분량 점검: 분당 300자 기준으로 글자 수와 표기 시간을 비교 |
| `figures_day1.py` | 1일차 설명 그림 24종 → `fig_day1/*.png` (matplotlib, 논문 수치는 Table 1, Extended Data Table 2·3·4) |
| `postprocess_pptx.py` | 후처리: 한글 줄바꿈을 단어 단위로, 박스 안 텍스트 세로 가운데 정렬, 노트 페이지 배치. `npm run day2·day3`와 `extend_day1.py`가 자동 실행 |
| `export_pdf.py` | pptx → pdf (한글·영문 자동 간격 끔). `--notes`를 붙이면 슬라이드 + 대본 노트 보기 PDF |
| `package.json` · `package-lock.json` | pptxgenjs 4.0.1 고정 |

## 다시 만들기

```bash
cd archive/slides
npm install
npm run day2      # ../../practice/day2_slides/day2_practice_slides.pptx 덮어씀
npm run day3
python3 export_pdf.py ../../practice/day2_slides/day2_practice_slides.pptx ../../practice/day2_slides/day2_practice_slides.pdf
python3 export_pdf.py ../../practice/day3_slides/day3_practice_slides.pptx ../../practice/day3_slides/day3_practice_slides.pdf
# 대본 PDF (슬라이드 + 발표자 노트, 일차별로 *_notes.pdf)
python3 export_pdf.py ../../practice/day2_slides/day2_practice_slides.pptx ../../practice/day2_slides/day2_practice_slides_notes.pdf --notes
```

1일차는 그림을 만든 뒤 삽입 스크립트를 실행함. 추가 슬라이드는 cSld 이름이 `added:`로 시작하며, 다시 실행하면 지우고 새로 만듦.

```bash
pip install python-pptx pillow matplotlib
python3 figures_day1.py
python3 extend_day1.py     # ../../practice/day1_slides/day1_theory_slides.pptx 갱신
python3 export_pdf.py ../../practice/day1_slides/day1_theory_slides.pptx ../../practice/day1_slides/day1_theory_slides.pdf
```
- 슬라이드는 cSld 이름으로 식별함: `orig:N` 원본 N번, `user:*` PowerPoint에서 직접 만든 슬라이드, `added:*` 이 스크립트가 만든 슬라이드. 이름이 없는 새 슬라이드는 `user:autoN`으로 이름을 붙이고 앞 슬라이드 뒤에 둠
- 대본 시간: 분당 300자(공백 포함) 기준으로 표기하며, 1일차는 휴식 전 약 50분, 전체 약 123분(휴식 제외). 실제 강의는 설명을 덧붙이므로 더 길어짐
- 용어: VQC = variational quantum circuit, PQC = parameterized quantum circuit. QGAN 논문은 PQC, MediQ-GAN 논문은 VQC로 부름. 슬라이드를 옮기면 2·3일차 대본의 "1일차 슬라이드 N" 참조도 맞춤

- 폰트는 Noto Sans KR. 설치되지 않은 PC에서는 줄바꿈이 달라질 수 있음
- `export_pdf.py`는 LibreOffice와 python3-uno가 필요함. 기본 설정으로 내보내면 "2일차"가 "2 일차"처럼 벌어져서 이 스크립트를 씀
- 다시 빌드하면 PowerPoint 테마 색 목록만 기본값이 되고, 화면의 색은 같음
