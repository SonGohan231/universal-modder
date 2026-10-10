"""Version-fingerprinted, read-only PvZ/Titan adapter reconnaissance.

Never loads game libraries. Export discovery is not an engine binding.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from zipfile import ZipFile

PROFILES = {
    'pvz': {'package': 'com.ea.game.pvzfree_row', 'libraries': ['libpvz.so'],
            'candidate_pattern': r'(Board|LawnApp|Plant|Zombie).*(Update|Draw|AddPlant|AddZombie|Mouse|Touch)'},
    'clash': {'package': 'com.supercell.clashroyale',
              'libraries': ['libg.so', 'libsupercell_clashroyale.so'],
              'candidate_pattern': r'(Battle|Logic|Game|Titan|JNI_OnLoad)'},
}

def parse_symbols(text):
    symbols=[]
    for line in text.splitlines():
        cols=line.split()
        if len(cols)>=8 and cols[0].endswith(':') and cols[4] in ('GLOBAL','WEAK') and cols[6]!='UND':
            symbols.append({'name':cols[7], 'type':cols[3], 'visibility':cols[5]})
    return symbols

def inspect_native(profile, apks, readelf='readelf'):
    spec=PROFILES[profile]
    reports=[]
    for apk in apks:
        with ZipFile(apk) as archive:
            for entry in archive.infolist():
                parts=entry.filename.split('/')
                if len(parts)!=3 or parts[:2]!=['lib','arm64-v8a'] or parts[2] not in spec['libraries']:
                    continue
                if entry.file_size>256*1024*1024:
                    raise ValueError('native library exceeds 256 MiB limit')
                digest=hashlib.sha256()
                with tempfile.NamedTemporaryFile(suffix='.so') as temp:
                    with archive.open(entry) as source:
                        total=0
                        while chunk:=source.read(1024*1024):
                            total+=len(chunk)
                            if total>256*1024*1024: raise ValueError('decompressed limit')
                            digest.update(chunk);temp.write(chunk)
                    temp.flush()
                    def run(*args):
                        return subprocess.check_output([readelf,*args,temp.name],text=True,stderr=subprocess.PIPE,timeout=30,env={**os.environ,'LC_ALL':'C'})
                    header=run('-h')
                    if 'AArch64' not in header or 'ELF64' not in header:
                        raise ValueError('library is not ELF64 AArch64')
                    symbols=parse_symbols(run('--dyn-syms','--wide'))
                    deps=re.findall(r'\(NEEDED\).*?\[(.*?)\]',run('-d'))
                reports.append({'apk':Path(apk).name,'entry':entry.filename,'sha256':digest.hexdigest(),
                                'exports':len(symbols),'needed':deps,
                                'candidate_functions':[s['name'] for s in symbols if s['type']=='FUNC' and re.search(spec['candidate_pattern'],s['name'])][:100]})
    found={r['entry'].split('/')[-1] for r in reports}
    return {'profile':profile,'expected_package':spec['package'],'package_identity_verified':False,
            'libraries':reports,'missing':sorted(set(spec['libraries'])-found),
            'engine_binding':'unimplemented','playable':False,
            'next_required':['verified calling conventions and object lifetimes','engine lifecycle and rendering integration','offline gameplay test on original engines']}

def command(args):
    print(json.dumps(inspect_native(args.profile,args.apks,args.readelf),indent=2))
