"""pptx -> pdf (LibreOffice UNO). 모든 문단의 한글·영문 자동 간격을 끄고 내보냄.

LibreOffice 기본 설정으로 내보내면 "2일차"가 "2 일차"처럼 숫자·영문과 한글 사이가 벌어짐.
사용법: python3 export_pdf.py <입력.pptx> <출력.pdf>   (LibreOffice와 python3-uno 필요)
"""
import sys, os, subprocess, time, tempfile, uno
from com.sun.star.beans import PropertyValue
src, dst = map(os.path.abspath, sys.argv[1:3])
prof = tempfile.mkdtemp(prefix="lo_prof_")
port = 2083
p = subprocess.Popen(["soffice", f"-env:UserInstallation=file://{prof}", "--headless", "--invisible", "--norestore",
                      f"--accept=socket,host=127.0.0.1,port={port};urp;"], env=dict(os.environ, SAL_USE_VCLPLUGIN="svp"),
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
ctx = None
local = uno.getComponentContext()
resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
for _ in range(60):
    try:
        ctx = resolver.resolve(f"uno:socket,host=127.0.0.1,port={port};urp;StarOffice.ComponentContext"); break
    except Exception: time.sleep(1)
def pv(n, v):
    x = PropertyValue(); x.Name = n; x.Value = v; return x
desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(src), "_blank", 0, (pv("Hidden", True),))
count = [0]
def fix_text(t):
    en = t.getText().createEnumeration() if hasattr(t, "getText") else None
    if en is None: return
    while en.hasMoreElements():
        par = en.nextElement()
        try:
            par.setPropertyValue("ParaIsCharacterDistance", False); count[0] += 1
        except Exception: pass
def walk(shape):
    st = shape.getShapeType()
    if st == "com.sun.star.drawing.GroupShape":
        for i in range(shape.getCount()): walk(shape.getByIndex(i))
        return
    if st == "com.sun.star.drawing.TableShape":
        model = shape.getPropertyValue("Model")
        for r in range(model.getRows().getCount()):
            for c in range(model.getColumns().getCount()):
                fix_text(model.getCellByPosition(c, r))
        return
    try: fix_text(shape)
    except Exception: pass
pages = doc.getDrawPages()
for i in range(pages.getCount()):
    pg = pages.getByIndex(i)
    for j in range(pg.getCount()): walk(pg.getByIndex(j))
for i in range(doc.getMasterPages().getCount()):
    pg = doc.getMasterPages().getByIndex(i)
    for j in range(pg.getCount()): walk(pg.getByIndex(j))
doc.storeToURL(uno.systemPathToFileUrl(dst), (pv("FilterName", "impress_pdf_Export"),))
doc.close(True)
try: desktop.terminate()
except Exception: pass
p.wait(timeout=30)
print("paragraphs fixed:", count[0], "->", dst)
