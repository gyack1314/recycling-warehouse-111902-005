"""流式生成原始称重文件；不计算净重和业务有效性。"""
import argparse,csv,json,hashlib
from pathlib import Path
def generate(out,rows):
    if rows<2:raise ValueError("rows至少为2")
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    paths=[out/"a.csv",out/"b.csv"]
    files=[paths[0].open("w",encoding="utf-8",newline=""),paths[1].open("w",encoding="gb18030",newline="")]
    writers=[csv.writer(x) for x in files]
    header=["row_id","revision","vehicle","trip","side","weight","at","ref"]
    for w in writers:w.writerow(header)
    repeated=0
    for i in range(rows//2):
        vehicle="V-heavy" if i%10 else "V-"+str(i%97)
        gross=[str(i*2+1),1,vehicle,"T-"+str(i),"gross","100.000","2026-10-01T08:00:00+08:00",str(i*2+2)]
        tare=[str(i*2+2),1,vehicle,"T-"+str(i),"tare","10.000","2026-10-01T08:30:00+08:00",""]
        writers[0].writerow(gross);writers[1].writerow(tare)
        if i%1000==0:
            writers[1].writerow(gross);repeated+=1
        if i%5000==0: writers[0].writerow(["bad","record"])
    for f in files:f.close()
    inventory=[]
    for path,encoding in zip(paths,["utf-8","gb18030"]):
        digest=hashlib.sha256()
        with path.open("rb") as f:
            for block in iter(lambda:f.read(65536),b""):digest.update(block)
        inventory.append({"file":path.name,"encoding":encoding,"device":"A","boot":"B1","sha256":digest.hexdigest()})
    (out/"files.json").write_text(json.dumps(inventory,indent=2),encoding="utf-8")
    (out/"generation.json").write_text(json.dumps({"base_rows":2*(rows//2),"repeated":repeated,"requested_rows":rows},indent=2),encoding="utf-8")
    return inventory
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);p.add_argument("--rows",type=int,default=1000000)
    a=p.parse_args();print(json.dumps(generate(a.out,a.rows),ensure_ascii=False))
