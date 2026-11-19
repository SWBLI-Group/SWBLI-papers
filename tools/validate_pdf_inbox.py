# -*- coding: utf-8 -*-
"""Check a pdf-inbox PR only adds genuinely new PDF files.

Usage (in GitHub Actions):
    python tools/validate_pdf_inbox.py \
      --base origin/pdf-inbox \
      --library /tmp/library_hashes.json

The check compares SHA-256 digests against:
- pdfs/library_hashes.json from the new branch (local library);
- PDFs already present on the pdf-inbox branch.

PDF contents are not tracked on new; the hash manifest is the bridge.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDFS_DIR = ROOT / "pdfs"
MAX_BYTES = 100 * 1024 * 1024
WARN_BYTES = 50 * 1024 * 1024


def run_git(*args):
    return subprocess.run(
        ["git", "-c", "core.quotePath=false", *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    ).stdout


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="origin/pdf-inbox")
    parser.add_argument("--library", default="pdfs/library_hashes.json")
    args = parser.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    errors = []
    warnings = []
    try:
        diff = run_git("diff", "--name-status", "--diff-filter=ACMRD", f"{args.base}...HEAD")
    except subprocess.CalledProcessError as exc:
        print(exc.stderr, file=sys.stderr)
        return 1

    changes = []
    for line in diff.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, path = parts[0], parts[-1]
        changes.append((status, path))

    if not changes:
        errors.append("PR 没有新增 PDF；pdf-inbox 只接收新 PDF")

    added = []
    for status, path in changes:
        if status != "A":
            errors.append(f"只允许新增 PDF，禁止修改/删除已有文件：{status} {path}")
            continue
        if not path.startswith("pdfs/") or path.count("/") != 1:
            errors.append(f"PDF 必须直接放在 pdfs/ 下：{path}")
            continue
        if not path.lower().endswith(".pdf"):
            errors.append(f"不是 PDF 文件：{path}")
            continue
        if " " in path:
            errors.append(f"文件名不要包含空格：{path}")
            continue
        local = ROOT / path
        if not local.is_file():
            errors.append(f"文件不存在：{path}")
            continue
        size = local.stat().st_size
        if size == 0:
            errors.append(f"空文件：{path}")
            continue
        if size > MAX_BYTES:
            errors.append(f"文件超过 100 MB：{path} ({size / 1024 / 1024:.1f} MB)")
            continue
        if size > WARN_BYTES:
            warnings.append(f"文件较大，建议压到 50 MB 以下：{path} ({size / 1024 / 1024:.1f} MB)")
        with local.open("rb") as handle:
            head = handle.read(1024)
        if b"%PDF-" not in head:
            errors.append(f"文件头不是 PDF：{path}")
            continue
        added.append((path, local, sha256_file(local), size))

    library_hashes = {}
    library_path = Path(args.library)
    if not library_path.is_file():
        errors.append(f"找不到本地库哈希清单：{library_path}")
    else:
        try:
            entries = json.loads(library_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"哈希清单不是合法 JSON：{exc}")
            entries = []
        for entry in entries:
            digest = entry.get("sha256", "")
            if digest:
                library_hashes[digest] = entry

    seen_hashes = {}
    for path, local, digest, size in added:
        if digest in seen_hashes:
            errors.append(f"同一 PR 内重复 PDF：{seen_hashes[digest]} / {path}")
        seen_hashes[digest] = path

        known = library_hashes.get(digest)
        if known:
            ident = f"id={known.get('id')}" if known.get("id") is not None else "未关联条目"
            errors.append(
                f"PDF 已存在于本地文献库（{ident}，{known.get('file', '')}）：{path}"
            )

    added_paths = {path for path, _local, _digest, _size in added}
    existing = [
        path
        for path in PDFS_DIR.glob("*.pdf")
        if path.is_file() and f"pdfs/{path.name}" not in added_paths
    ]
    by_size = {}
    for path in existing:
        by_size.setdefault(path.stat().st_size, []).append(path)

    for path, local, digest, size in added:
        for other in by_size.get(size, []):
            if sha256_file(other) == digest:
                errors.append(
                    f"PDF 已存在于 pdf-inbox（{other.name}），内容相同：{path}"
                )
                break

    print(f"checked {len(added)} new PDF(s), {len(changes)} changed file(s)")
    for warning in warnings:
        print("WARN", warning)
    for error in errors:
        print("ERROR", error)
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: all uploaded PDFs are new")
    return 0


if __name__ == "__main__":
    sys.exit(main())
