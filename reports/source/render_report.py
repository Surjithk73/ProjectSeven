"""Native Word pagination and raster review on Windows without LibreOffice."""
from pathlib import Path
import argparse
import json
import time
import win32com.client
import pythoncom
import fitz
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--template',action='store_true')
parser.add_argument('--iteration',default='v1')
args=parser.parse_args()
target=Path(r'C:\Users\surji\Downloads\BCE497J PROJECT REPORT TEMPLATE_V1.docx') if args.template else ROOT/'reports/APIShield_Project_Report.docx'
out=ROOT/'reports/.qa'/('template' if args.template else args.iteration)
out.mkdir(parents=True,exist_ok=True)
pdf=out/'rendered.pdf'
pythoncom.CoInitialize()
word=win32com.client.DispatchEx('Word.Application')
word.Visible=False;word.DisplayAlerts=0;word.AutomationSecurity=3
document=None
try:
    document=word.Documents.Open(str(target),ConfirmConversions=False,ReadOnly=args.template,AddToRecentFiles=False,Visible=False)
    if not args.template:
        document.Repaginate()
        for _ in range(2):
            document.Fields.Update()
            for s in document.Sections:
                for f in s.Footers:f.Range.Fields.Update()
            document.Repaginate()
        document.Save()
    print('Native Word pages:',document.ComputeStatistics(2),flush=True)
    document.ExportAsFixedFormat(str(pdf),17,OpenAfterExport=False)
finally:
    if document is not None:document.Close(False)
    word.Quit()
    pythoncom.CoUninitialize()

pdfdoc=fitz.open(pdf)
info=[]
for i,page in enumerate(pdfdoc):
    pix=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
    pix.save(out/f'page-{i+1}.png')
    blocks=page.get_text('blocks')
    nonfooter=[b for b in blocks if b[1]<page.rect.height-48 and b[4].strip()]
    info.append({'page':i+1,'words':len(page.get_text().split()),'bottom':round(max([b[3] for b in nonfooter],default=0),1),
                 'first':page.get_text().strip().splitlines()[:3],
                 'text':page.get_text()})
(out/'page_audit.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
# Four-page sheets support a complete layout pass; individual PNGs remain full resolution.
for start in range(0,len(pdfdoc),4):
    canvas=Image.new('RGB',(1800,2600),'#dddddd');draw=ImageDraw.Draw(canvas)
    for offset in range(4):
        index=start+offset
        if index>=len(pdfdoc):break
        im=Image.open(out/f'page-{index+1}.png').convert('RGB');im.thumbnail((870,1230))
        x=(offset%2)*900+15;y=(offset//2)*1300+40
        canvas.paste(im,(x,y));draw.text((x,y-25),f'PAGE {index+1}',fill='black')
    canvas.save(out/f'sheet-{start//4+1:02}.jpg',quality=92)
print(json.dumps({'pages':len(pdfdoc),'out':str(out),'sparse':[x['page'] for x in info if x['words']<65],
                  'last_lines':[{'page':x['page'],'first':x['first']} for x in info if x['words']<65]},indent=2))
