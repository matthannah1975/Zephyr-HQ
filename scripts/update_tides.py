import csv, io, json, re, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

SOURCES = {
 "interval": "https://www.data.qld.gov.au/dataset/2417a8c3-eb88-4632-bbf0-637192fa223a/resource/1542ee15-6f50-414f-bc15-66732f1f7eae/download/p012023a_noosa-head_2026_10min.csv",
 "hilo": "https://www.data.qld.gov.au/dataset/dca61f49-0a97-4999-9348-42f83417eacc/resource/1977d083-3119-41aa-8758-3980f3eb8a3f/download/q012023a_noosa-head_2026_hilo.csv"
}
TZ = timezone(timedelta(hours=10))
def parse_date(s):
 s=s.strip()
 for f in ("%d/%m/%Y","%Y-%m-%d","%d-%m-%Y","%d/%m/%y","%d-%b-%Y"):
  try:return datetime.strptime(s,f).date()
  except ValueError:pass
 return None
def parse_time(s):
 s=s.strip().replace(":", "")
 if re.fullmatch(r"\d{3,4}",s):
  s=s.zfill(4)
  if int(s[:2])<24 and int(s[2:])<60:return int(s[:2]),int(s[2:])
 return None
def parse(text):
 out=[]
 for row in csv.reader(io.StringIO(text)):
  if len(row)<4:continue
  day=parse_date(row[0]);tm=parse_time(row[1])
  if not day or not tm:continue
  try:height=float(row[3].strip())
  except ValueError:continue
  stamp=datetime(day.year,day.month,day.day,tm[0],tm[1],tzinfo=TZ).isoformat()
  out.append([stamp,round(height,3),row[2].strip()])
 return sorted(out,key=lambda p:p[0])
def download(url):
 req=urllib.request.Request(url,headers={"User-Agent":"ZephyrHQ-TideDashboard/1.0","Accept":"text/csv"})
 with urllib.request.urlopen(req,timeout=45) as r:return r.read().decode("utf-8-sig")
data={}
for name,url in SOURCES.items():
 data[name]=parse(download(url))
 if len(data[name])<100:raise RuntimeError(f"Too few {name} tide records: {len(data[name])}")
Path("data").mkdir(exist_ok=True)
Path("data/noosa-tides-2026.json").write_text(json.dumps({"station":"Noosa Head","timezone":"Australia/Brisbane","source":"Maritime Safety Queensland / Queensland Government, CC BY 4.0","interval":data["interval"],"hilo":data["hilo"]},separators=(",",":")))
print("Tide points:",{k:len(v) for k,v in data.items()})
