from um.android_native import parse_symbols, inspect_native
from zipfile import ZipFile

def test_exports_exclude_undefined_and_local():
    text=''' 1: 0000 4 FUNC GLOBAL DEFAULT 12 BoardUpdate
 2: 0000 0 FUNC GLOBAL DEFAULT UND malloc
 3: 0000 4 FUNC WEAK DEFAULT 12 WeakExport
 4: 0000 4 FUNC LOCAL DEFAULT 12 private
 5: 0000 4 OBJECT GLOBAL DEFAULT 12 data'''
    assert [s['name'] for s in parse_symbols(text)]==['BoardUpdate','WeakExport','data']

def test_missing_does_not_claim_ready(tmp_path):
    p=tmp_path/'empty.apk'
    with ZipFile(p,'w') as z:z.writestr('AndroidManifest.xml','test')
    r=inspect_native('clash',[p])
    assert r['missing']==['libg.so','libsupercell_clashroyale.so']
    assert r['playable'] is False and r['engine_binding']=='unimplemented'
