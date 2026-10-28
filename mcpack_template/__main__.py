import sys
import tomllib
from pathlib import Path

from jinja2 import BaseLoader, DictLoader, Environment, FileSystemLoader
from jinja2.runtime import Undefined

src = Path(sys.argv[1])
dest = Path(sys.argv[2])
with Path(sys.argv[3]).open('rb') as fp:
    vals = tomllib.load(fp)

dest.mkdir(exist_ok=True)

def required(x):
    if isinstance(x, Undefined):
        raise RuntimeError('Required value')
    return x

fileloader = BaseLoader()
loader = FileSystemLoader(src)
env = Environment()
env.filters['required'] = required

for file in src.glob('**/*'):
    rel = file.relative_to(src)
    if file.is_dir():
        (dest / rel).mkdir(exist_ok=True, parents=True)

        meta_toml = (file / 'meta.toml')
        if meta_toml.is_file():
            with meta_toml.open('rb') as fp:
                meta = tomllib.load(fp)
                iter = meta['iterator']
                impl = meta['impl']
                out_tpl = meta['out_tpl']

            for item in vals[iter]:
                out = DictLoader({'tpl': out_tpl}).load(env, 'tpl').render({'item': item, 'v': vals})
                print(f'Rendering {rel / out}')
                with (dest / rel / out).open('w') as fpo:
                    tpl = loader.load(env, (rel / impl).as_posix())
                    fpo.write(tpl.render({'v': vals, 'item': item}))
    elif file.is_file() and file.suffix != '.toml':
        if (file.parent / 'meta.toml').is_file():
            continue
        else:
            print(f'Rendering {rel}')
            with (dest / rel).open('w') as fpo:
                tpl = loader.load(env, rel.as_posix())
                fpo.write(tpl.render({
                    'v': vals,
                    'range': range,
                    'round': round,
                    'smoothstep': lambda x: x * x * (3.0 - 2.0 * x),
                    'mix': lambda x, y, a: x * (1 - a) + y * a,
                }))
