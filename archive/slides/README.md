# slides - 2·3일차 실습 설명 슬라이드 생성

`practice/day2_slides/`, `practice/day3_slides/`의 pptx는 이 폴더의 스크립트로 만든다.
1일차 슬라이드(`practice/day1_slides/`)는 PowerPoint로 직접 만든 파일이라 생성 스크립트가 없다.

| 파일 | 내용 |
|---|---|
| `build_day2.js` | 2일차 슬라이드 25장 (pptxgenjs). 슬라이드 내용·발표자 노트가 모두 이 파일 안에 있음 |
| `build_day3.js` | 3일차 슬라이드 23장 |
| `export_pdf.py` | pptx → pdf. LibreOffice로 내보내되 모든 문단의 한글·영문 자동 간격을 끔 |
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

- 색·폰트는 1일차 슬라이드와 같은 팔레트(`THEME`)와 Noto Sans KR을 씀. 폰트가 설치되지 않은 PC에서는 다른 글꼴로 대체되어 줄바꿈이 달라질 수 있음.
- `export_pdf.py`는 LibreOffice와 python3-uno가 필요함(Linux: `libreoffice-impress`, `python3-uno` 패키지).
  LibreOffice 기본 설정으로 내보내면 "2일차"가 "2 일차"처럼 숫자·영문과 한글 사이가 벌어지기 때문에 이 스크립트를 씀.
- 저장소의 pptx는 스크립트 출력에 테마 색을 추가로 넣은 것이라, 다시 만들면 PowerPoint의 테마 색 목록만 기본값으로 바뀜. 슬라이드에 보이는 색은 같음(모든 도형에 hex로 지정).
- 수치를 바꿀 때는 노트북·README·checkpoint와 같은 값인지 확인함(CLAUDE.md "근거를 함께 쓴다").
