"""Build editable translation drafts with local OPUS/Argos CTranslate2 models.
Dependencies are isolated under .local/translator. Models are build-time only.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import urlopen, Request
import json
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / '.local/translation-models'
OUTPUT = ROOT / 'data/locales'
OUTPUT.mkdir(exist_ok=True)
SOURCES = json.loads((ROOT / 'data/source-strings.json').read_text(encoding='utf-8'))
REPOS = {code: 'etenszyn/argos-opus-mt-en-' + code + '-ct2' for code in ['fr','de','es','it','pt','nl']}
REPOS.update({code:'jiangzhuo9357/opus-mt-en-'+code+'-ct2' for code in ['ar','ru','zh']})


def download(code):
    repo = REPOS[code]
    folder = MODELS / code
    folder.mkdir(parents=True, exist_ok=True)
    metadata = json.load(urlopen('https://huggingface.co/api/models/' + repo, timeout=30))
    for item in metadata['siblings']:
        name = item['rfilename']
        if name not in {'config.json','model.bin','sentencepiece.model','shared_vocabulary.json','source_vocabulary.json','target_vocabulary.json','shared_vocabulary.txt','source_vocabulary.txt','target_vocabulary.txt','source.spm','target.spm'}:
            continue
        target = folder / name
        if target.is_file():
            continue
        url = 'https://huggingface.co/' + repo + '/resolve/main/' + name
        for attempt in range(3):
            try:
                with urlopen(Request(url, headers={'User-Agent':'DesertGate-local-copy-build'}), timeout=60) as response, target.with_suffix(target.suffix+'.part').open('wb') as output:
                    while block := response.read(1024*1024):
                        output.write(block)
                target.with_suffix(target.suffix+'.part').replace(target)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(3)
    print('MODEL READY', code, flush=True)
    return code


def compile(code):
    import ctranslate2
    import sentencepiece as spm
    folder = MODELS / code
    source_spm = folder / ('source.spm' if (folder/'source.spm').exists() else 'sentencepiece.model')
    target_spm = folder / ('target.spm' if (folder/'target.spm').exists() else 'sentencepiece.model')
    encoder = spm.SentencePieceProcessor(model_file=str(source_spm))
    decoder = spm.SentencePieceProcessor(model_file=str(target_spm))
    translator = ctranslate2.Translator(str(folder), device='cpu', compute_type='int8', inter_threads=1, intra_threads=4)
    file = OUTPUT / (code+'.json')
    saved = json.loads(file.read_text(encoding='utf-8')) if file.exists() else {'strings':{},'reviewed':False,'origin':'local OPUS/Argos machine draft'}
    missing = [s for s in SOURCES if s not in saved['strings']]
    pieces, keys = [], []
    # Translate sentences separately, preserving original paragraph breaks and placeholders.
    for text in missing:
        chunks = re.split(r'(\n+|(?<=[.!?])\s+(?=[A-Z]))', text)
        refs = []
        for chunk in chunks:
            if not chunk or chunk.isspace():
                refs.append(chunk); continue
            if re.search(r'\{\w+\}',chunk):
                # UI templates receive reviewed manual wording after this build.
                refs.append(chunk); continue
            refs.append(len(pieces)); pieces.append(chunk)
        keys.append((text,refs))
    outputs=[]
    for start in range(0,len(pieces),32):
        batch = pieces[start:start+32]
        # In travel copy, quote means a price proposal, not a quotation or citation.
        tokens=[encoder.encode(re.sub(r'\bquote\b', 'price proposal', s, flags=re.I),out_type=str) + (['</s>'] if source_spm.name=='source.spm' else []) for s in batch]
        results=translator.translate_batch(tokens,beam_size=2,max_decoding_length=350,max_input_length=400)
        outputs.extend(decoder.decode(result.hypotheses[0]).replace('▁', ' ').strip() for result in results)
        if start%320==0:
            print(f'TRANSLATING {code}: {start}/{len(pieces)} sentences',flush=True)
    for text,refs in keys:
        saved['strings'][text]=''.join(outputs[r] if isinstance(r,int) else r for r in refs)
    file.write_text(json.dumps(saved,ensure_ascii=False,indent=2),encoding='utf-8')
    print('TRANSLATED',code,len(saved['strings']),flush=True)


if __name__=='__main__':
    if '--download' in sys.argv:
        with ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(download,REPOS))
    else:
        codes=[s for s in sys.argv[1:] if s in REPOS] or list(REPOS)
        for code in codes:
            compile(code)
