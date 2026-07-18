#!/usr/bin/env python3
"""Compare direct-build PDFs with active reference snapshots after rendering."""

from __future__ import annotations

import csv
import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image


PKG_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = PKG_ROOT / "docs/figure_asset_registry.csv"
OUT = PKG_ROOT / "reproduced/checks/exact_build_render_comparison.csv"


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def render(path: Path, stem: Path) -> Path:
    subprocess.run(
        ["pdftoppm", "-f", "1", "-singlefile", "-r", "150", "-png", str(path), str(stem)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return stem.with_suffix(".png")


def main() -> None:
    if shutil.which("pdftoppm") is None:
        raise RuntimeError("pdftoppm is required for exact-build rendered-pixel checks")
    with REGISTRY.open(newline="") as handle:
        rows = [r for r in csv.DictReader(handle) if r["reproduction_class"] == "exact_reproducible_build"]

    results = []
    with tempfile.TemporaryDirectory(prefix="atlas-render-check-") as tmp:
        tmp = Path(tmp)
        for row in rows:
            ref = PKG_ROOT / "outputs/figures" / row["manuscript_figure"]
            built = PKG_ROOT / "reproduced/figures" / row["rebuilt_file"]
            a = np.asarray(Image.open(render(ref, tmp / f"{ref.stem}-ref")).convert("RGB"), dtype=np.int16)
            b = np.asarray(Image.open(render(built, tmp / f"{ref.stem}-built")).convert("RGB"), dtype=np.int16)
            same_shape = a.shape == b.shape
            if same_shape:
                delta = np.abs(a - b)
                mae = float(delta.mean())
                changed = float(np.any(delta > 8, axis=2).mean())
                pixel_exact = bool(np.array_equal(a, b))
            else:
                mae = float("nan")
                changed = 1.0
                pixel_exact = False
            results.append(
                {
                    "manuscript_figure": row["manuscript_figure"],
                    "reference_md5": md5(ref),
                    "rebuilt_md5": md5(built),
                    "byte_exact": md5(ref) == md5(built),
                    "same_render_shape": same_shape,
                    "pixel_mae_150dpi": mae,
                    "changed_pixel_share_gt8": changed,
                    "pixel_exact_150dpi": pixel_exact,
                    "comparison_result": "pixel_exact_pdf_metadata_only" if pixel_exact else "rendering_difference",
                }
            )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    if not all(r["pixel_exact_150dpi"] for r in results):
        raise RuntimeError("One or more exact-build figures differ after 150-dpi rendering")
    print(f"Pixel-exact rendered comparison passed for {len(results)} direct builds")


if __name__ == "__main__":
    main()
