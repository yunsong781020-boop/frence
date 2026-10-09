#!/usr/bin/env python3
from pathlib import Path
import json, csv, sys

ROOT=Path(__file__).resolve().parent
QF=ROOT/"app/src/main/assets/questions.json"
AF=ROOT/"app/src/main/assets/audio"
MF=ROOT/"audio_manifest_v05.csv"

bad_tokens=["�","Ã","Â","â€™","â€“","â€œ","â€"]
issues=[]

qs=json.loads(QF.read_text(encoding="utf-8"))
if len(qs)!=50:
    issues.append(f"题目数量应为50，当前{len(qs)}")

for q in qs:
    qid=q.get("id")
    if len(q.get("options",[]))!=4:
        issues.append(f"Q{qid}: 不是4个选项")
    a=q.get("answer")
    if not isinstance(a,int) or a<0 or a>3:
        issues.append(f"Q{qid}: answer索引非法")
    for field in ["question","text","analysis","correctWhy","tip"]:
        s=str(q.get(field,""))
        if not s.strip():
            issues.append(f"Q{qid}: {field}为空")
        if any(t in s for t in bad_tokens):
            issues.append(f"Q{qid}: {field}包含乱码")
    for opt in q.get("options",[]):
        if not opt.strip():
            issues.append(f"Q{qid}: 存在空选项")
        if any(t in opt for t in bad_tokens):
            issues.append(f"Q{qid}: 选项包含乱码")

manifest=list(csv.DictReader(MF.open(encoding="utf-8-sig")))
expected={row["audio_id"]+".mp3" for row in manifest}
if len(expected)!=45:
    issues.append(f"独立音频应为45，当前{len(expected)}")

for name in sorted(expected):
    p=AF/name
    if not p.exists():
        issues.append(f"缺少音频 {name}")
        continue
    if p.stat().st_size < 8000:
        issues.append(f"音频过小/可能无效 {name}")
    head=p.read_bytes()[:3]
    # MP3 may begin ID3 or frame sync
    if head != b"ID3" and not (len(head)>=2 and head[0]==0xFF and (head[1]&0xE0)==0xE0):
        issues.append(f"音频格式异常 {name}")

refs={q["audio_file"] for q in qs}
if refs != expected:
    issues.append(f"题库引用与音频清单不一致: refs={len(refs)}, expected={len(expected)}")

if issues:
    print("V0.5 发布检查失败：")
    for x in issues:
        print("-",x)
    sys.exit(1)

print("V0.5 发布检查通过：50题、4选1、编码正常、45段音频完整且题库引用一致。")
