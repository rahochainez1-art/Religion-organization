"""Ajoute un cours à l'espace chiffré (espace.js) et met à jour index.html.
Usage : CARNET_MDP=... python3 outils/espace.py ajouter dossier_du_cours/
Le dossier contient : cours.json (avec "id"), lecons/*.json (avec "id"), lexique/*.json, textes/*.json,
et fiches.html (les fiches carnet). Tout est fusionné (remplace les entrées de même id).
Autres commandes : lister (affiche les cours présents), verifier (déchiffre et compte)."""
import json,os,re,sys,glob,base64,hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EJ=os.path.join(R,'espace.js')
def load():
  E=json.loads(open(EJ).read().split('=',1)[1].rstrip().rstrip(';'))
  b=lambda s: base64.b64decode(s)
  key=PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=b(E['salt']),iterations=E['it']).derive(os.environ['CARNET_MDP'].encode())
  P=json.loads(AESGCM(key).decrypt(b(E['iv']),b(E['ct']),None)); return E,key,P
def save(E,key,P):
  iv=os.urandom(12); ct=AESGCM(key).encrypt(iv,json.dumps(P,ensure_ascii=False).encode(),None)
  b=lambda x: base64.b64encode(x).decode()
  txt="window.ESPACE="+json.dumps({"v":1,"it":E['it'],"salt":E['salt'],"iv":b(iv),"ct":b(ct)})+";\n"
  open(EJ,'w').write(txt)
  ix=os.path.join(R,'index.html'); h=open(ix).read()
  h=re.sub(r'espace\.js\?v=\w+','espace.js?v='+hashlib.sha1(txt.encode()).hexdigest()[:8],h); open(ix,'w').write(h)
def upsert(lst,doc):
  for i,x in enumerate(lst):
    if x.get('id')==doc['id']: lst[i]=doc; return
  lst.append(doc)
cmd=sys.argv[1]
E,key,P=load()
if cmd=='lister':
  for c in sorted(P['cours'],key=lambda c:(c['matiere'],c.get('numero',0))): print(c['id'],c['matiere'],c.get('numero'),c.get('titre'))
elif cmd=='verifier':
  print({k:len(v) for k,v in P.items()})
elif cmd=='ajouter':
  d=sys.argv[2]; c=json.load(open(os.path.join(d,'cours.json')))
  if os.path.exists(os.path.join(d,'fiches.html')):
    P.setdefault('docs',{})['fiches-'+c['id']]=open(os.path.join(d,'fiches.html')).read(); c['fiches']='doc:fiches-'+c['id']
  upsert(P['cours'],c)
  for col in ['lecons','lexique','textes']:
    for f in sorted(glob.glob(os.path.join(d,col,'*.json'))): upsert(P[col],json.load(open(f)))
  save(E,key,P); print('ok',c['id'],{k:len(v) for k,v in P.items()})
