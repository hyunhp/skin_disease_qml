# slides - 2·3일차 실습 설명 슬라이드 생성

`practice/day2_slides/`, `practice/day3_slides/`의 pptx는 이 폴더의 스크립트로 만든다.
1일차 슬라이드(`practice/day1_slides/`)는 PowerPoint로 직접 만든 파일이라 생성 스크립트가 없다.

| 파일 | 내용 |
|---|---|
| `build_day2.js` | 2일차 슬라이드 25장 (내용·발표자 노트 포함) |
| `build_day3.js` | 3일차 슬라이드 11장 |
| `export_pdf.py` | pptx → pdf (한글·영문 자동 간격 끔) |
| `package.json` · `package-lock.json` | pptxgenjs 4.0.1 고정 |

## 다시 만들기

```bash
cd archive/slides
npm install
npm run day2      # ../../practice/day2_slides/day2_practice_slides.pptx 덮어씀
npm run day3
python3 export_pdf.py ../../practice/day2_slides/day2_practice_slides.pptx ../../practice/day2_slides/day2_practice_slides.pdf
python3 export_pdf.py ../../practice/day3_slides/day3_practice_slides.pptx ../../practice/day3_slides/day3_practice_slides.pdf
```

- 폰트는 Noto Sans KR. 설치되지 않은 PC에서는 줄바꿈이 달라질 수 있음
- `export_pdf.py`는 LibreOffice와 python3-uno가 필요함. 기본 설정으로 내보내면 "2일차"가 "2 일차"처럼 벌어져서 이 스크립트를 씀
- 다시 빌드하면 PowerPoint 테마 색 목록만 기본값이 되고, 화면의 색은 같음
