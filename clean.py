from glob import glob
import subprocess
import re
from tqdm import tqdm

buildDir = "/home/supa/lin_storage/random_git_repos/tiletest/build/"
srcDir   = "/home/supa/lin_storage/random_git_repos/tiletest/src/"
incDir   = "/home/supa/lin_storage/random_git_repos/tiletest/include/"

def checkIfBuilds(buildDir):
    subprocess.run(['ninja', 'clean'], cwd=buildDir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out = subprocess.run(['ninja', '-j 10'], cwd=buildDir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out.returncode == 0

def getFiles(dirs):
    headers, cpp = [], []
    for dir_ in dirs:
        headers.extend(glob(dir_ + '/**/*.hpp', recursive=True))
        cpp.extend(glob(dir_ + '/**/*.cpp', recursive=True))
    
    return headers, cpp

def getIncludes(files):
    out = []
    for fname in files:
        with open(fname, 'r') as f:
            txt = f.read()
    
        out.append((fname, re.findall(r"^#include\s*[<\"].*[>\"]", txt, re.M)))
    return out

def tryReplace(fname, include):
    with open(fname, 'r') as f:
        orig = f.read()

    new = orig.replace(include, f"//{include}")
    with open(fname, 'w') as f:
        f.write(new)
    if checkIfBuilds(buildDir):
        return True
    else:
        with open(fname, 'w') as f:
            f.write(orig)
        return False 

def main():
    headers, cpp = getFiles([srcDir, incDir])

    hdrIncs = sorted(getIncludes(headers), key=lambda tup: len(tup[1]))
    srcIncs = sorted(getIncludes(cpp),     key=lambda tup: len(tup[1]))

    files = hdrIncs + srcIncs

    for fname, headers in tqdm(files, desc="File"):
        for inc in tqdm(headers, leave=False, desc="Include"):
            tryReplace(fname, inc)

if __name__ == "__main__":
    main()