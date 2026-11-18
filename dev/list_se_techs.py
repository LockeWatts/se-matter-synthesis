"""Lists Space Exploration technologies and their prerequisite closure from SE's source.
Usage: python3 list_se_techs.py SE_PROTOTYPES_DIR TECH_NAME [look-for ...]"""
import re, sys, glob
root, target, look = sys.argv[1], sys.argv[2], sys.argv[3:]
def norm(s): return re.sub(r'data_util\.mod_prefix\s*\.\.\s*"', '"se-', s)
techs = {}
for f in glob.glob(root + "/**/*.lua", recursive=True):
    txt = norm(re.sub(r'--[^\n]*', '', open(f, errors="replace").read()))
    for m in re.finditer(r'type\s*=\s*"technology"', txt):
        # walk out to the enclosing braces
        depth, i = 0, m.start()
        while i > 0:
            if txt[i] == '}': depth += 1
            elif txt[i] == '{':
                if depth == 0: break
                depth -= 1
            i -= 1
        depth, j = 0, i
        while j < len(txt):
            if txt[j] == '{': depth += 1
            elif txt[j] == '}':
                depth -= 1
                if depth == 0: break
            j += 1
        block = txt[i:j + 1]
        name = re.search(r'\bname\s*=\s*"([^"]+)"', block)
        pre = re.search(r'prerequisites\s*=\s*\{([^}]*)\}', block)
        unlocks = re.findall(r'recipe\s*=\s*"([^"]+)"', block)
        packs = re.findall(r'\{\s*"([a-z0-9-]+science-pack[a-z0-9-]*)"\s*,\s*1', block)
        if name:
            techs[name.group(1)] = dict(pre=set(re.findall(r'"([^"]+)"', pre.group(1))) if pre else set(), unlocks=unlocks, packs=packs, file=f.replace(root, ""))
    # later additions:  tech_add_prerequisites("tech", {"a", "b"})
    for m in re.finditer(r'tech_add_prerequisites\(\s*"([^"]+)"\s*,\s*\{([^}]*)\}', txt):
        techs.setdefault(m.group(1), dict(pre=set(), unlocks=[], packs=[], file="(added)"))["pre"] |= set(re.findall(r'"([^"]+)"', m.group(2)))
def closure(t, seen=None):
    seen = seen if seen is not None else set()
    for p in techs.get(t, {}).get("pre", ()):
        if p not in seen:
            seen.add(p); closure(p, seen)
    return seen
c = closure(target)
print(f"{target}: direct prerequisites {sorted(techs[target]['pre'])}")
print(f"closure size {len(c)}; not defined in SE's files (vanilla or generated): {sorted(x for x in c if x not in techs)}")
for l in look:
    hits = sorted(x for x in c if l in x)
    print(f"  in closure matching '{l}': {hits}")
    for t, d in techs.items():
        if any(l in u for u in d['unlocks']) and l not in t:
            print(f"    recipe matching '{l}' unlocked by {t} (pre {sorted(d['pre'])}, packs {d['packs']}) in closure: {t in c}")
