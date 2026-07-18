#!/usr/bin/env python3
"""Full fixed-concept appendix figures for the rationale-concept exercise.

The concise paper-facing display pools related concepts. These appendix
figures instead show the full fixed set of 20 concepts per target, including
concepts that are not Bonferroni-significant, so readers can inspect the
complete heldout audit trail.
"""

from __future__ import annotations

import csv
import math
import textwrap
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


PKG_ROOT = Path(__file__).resolve().parents[2]
INPUT = (
    PKG_ROOT
    / "outputs/source_data/rationale_concepts/current_paper"
    / "full_fixed_concept_appendix_figure_source.csv"
)
OUTDIR = PKG_ROOT / "reproduced/figures"
CHECKDIR = PKG_ROOT / "reproduced/checks"

ARIAL = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
ARIAL_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")

TARGETS = [
    {
        "target_name": "same_task_exposed_vs_non_exposed",
        "slug": "exposure",
        "title": "Exposure: non-exposed (-); exposed (+)",
        "subtitle": "Same task, exposed versus non-exposed country contexts",
        "xlabel": "Exposed minus non-exposed (pp)",
        "source": "country",
        "xlim": (-60, 60),
        "tick_step": 20,
    },
    {
        "target_name": "same_task_substitution_vs_other_exposed",
        "slug": "substitution",
        "title": "Substitution: other exposed (-); substitution-only (+)",
        "subtitle": "Same task, within exposed task-country observations",
        "xlabel": "Heldout difference in concept presence (pp)",
        "source": "margin",
        "xlim": (-34, 18),
        "tick_step": 10,
    },
    {
        "target_name": "same_task_augmentation_vs_other_exposed",
        "slug": "augmentation",
        "title": "Augmentation: other exposed (-); augmentation-only (+)",
        "subtitle": "Same task, within exposed task-country observations",
        "xlabel": "Heldout difference in concept presence (pp)",
        "source": "margin",
        "xlim": (-22, 16),
        "tick_step": 5,
    },
]

TEXT = "#172232"
MUTED = "#607086"
MUTED_LIGHT = "#8B99AA"
GRID = "#E8EEF5"
ZERO = "#9DAABA"
AXIS = "#AEB8C4"

CATEGORY_DISPLAY = {
    "country_context_condition": "Country context",
    "task_specific_condition": "Task-specific",
    "country_context_task_interaction": "Country/task interaction",
    "mixed_or_ambiguous": "Mixed/ambiguous",
    "generic_margin_wording": "Generic margin wording",
    "mixed": "Mixed/ambiguous",
    "Country-context": "Country context",
    "Task-specific": "Task-specific",
    "Country/task interaction": "Country/task interaction",
    "Mixed/unclear": "Mixed/ambiguous",
}

CATEGORY_COLORS = {
    "Country context": "#2B78B8",
    "Task-specific": "#D99023",
    "Country/task interaction": "#009E73",
    "Mixed/ambiguous": "#5E6A78",
    "Generic margin wording": "#9A6A9E",
    "Unclassified": "#7A8794",
}

CATEGORY_MARKERS = {
    "Country context": "circle",
    "Task-specific": "triangle",
    "Country/task interaction": "diamond",
    "Mixed/ambiguous": "square",
    "Generic margin wording": "plus",
    "Unclassified": "circle",
}


def setup_fonts() -> None:
    if ARIAL.exists():
        pdfmetrics.registerFont(TTFont("Arial", str(ARIAL)))
    if ARIAL_BOLD.exists():
        pdfmetrics.registerFont(TTFont("Arial-Bold", str(ARIAL_BOLD)))


def font_name(bold: bool = False) -> str:
    return "Arial-Bold" if bold and ARIAL_BOLD.exists() else "Arial"


def pil_font(size: float, bold: bool = False, scale: int = 3) -> ImageFont.FreeTypeFont:
    path = ARIAL_BOLD if bold and ARIAL_BOLD.exists() else ARIAL
    return ImageFont.truetype(str(path), int(round(size * scale)))


def hex_color(value: str) -> colors.Color:
    return colors.HexColor(value)


def rgb(value: str) -> tuple[int, int, int]:
    h = value.strip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def blend(value: str, alpha: float, background: str = "#FFFFFF") -> str:
    fg = np.array(rgb(value), dtype=float)
    bg = np.array(rgb(background), dtype=float)
    out = alpha * fg + (1 - alpha) * bg
    return "#" + "".join(f"{int(round(x)):02X}" for x in out)


def clean_category(value: object) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "Unclassified"
    raw = str(value).strip()
    return CATEGORY_DISPLAY.get(raw, raw or "Unclassified")


def sentence_case(value: object) -> str:
    text = str(value).strip()
    return text[:1].upper() + text[1:] if text else ""


def wrap_text_points(text: str, width_pt: float, size: float, bold: bool = False) -> list[str]:
    words = sentence_case(text).split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if pdfmetrics.stringWidth(candidate, font_name(bold), size) <= width_pt:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_right_multiline_pdf(
    c: canvas.Canvas,
    x: float,
    y_center: float,
    lines: list[str],
    size: float,
    color: str,
    line_height: float,
    bold: bool = False,
) -> None:
    c.setFillColor(hex_color(color))
    c.setFont(font_name(bold), size)
    total = line_height * (len(lines) - 1)
    y0 = y_center + total / 2
    for i, line in enumerate(lines):
        c.drawRightString(x, y0 - i * line_height - size * 0.33, line)


def draw_right_multiline_png(
    draw: ImageDraw.ImageDraw,
    x: float,
    y_center: float,
    lines: list[str],
    size: float,
    color: str,
    line_height: float,
    bold: bool,
    scale: int,
) -> None:
    font = pil_font(size, bold=bold, scale=scale)
    total = line_height * scale * (len(lines) - 1)
    y0 = y_center * scale - total / 2
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        draw.text(
            (x * scale - (bbox[2] - bbox[0]), y0 + i * line_height * scale - size * scale * 0.58),
            line,
            fill=rgb(color),
            font=font,
        )


def marker_polygon(marker: str, x: float, y: float, r: float) -> list[tuple[float, float]]:
    if marker == "triangle":
        return [(x, y + r), (x - r * 0.92, y - r * 0.72), (x + r * 0.92, y - r * 0.72)]
    if marker == "diamond":
        return [(x, y + r), (x - r, y), (x, y - r), (x + r, y)]
    if marker == "square":
        return [(x - r, y - r), (x + r, y - r), (x + r, y + r), (x - r, y + r)]
    return []


def draw_marker_pdf(
    c: canvas.Canvas,
    x: float,
    y: float,
    marker: str,
    color: str,
    significant: bool,
    size: float = 4.0,
) -> None:
    fill = hex_color(color if significant else "#FFFFFF")
    stroke = hex_color(TEXT if significant else color)
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.45 if significant else 0.8)
    if marker == "circle":
        c.circle(x, y, size, stroke=1, fill=1)
    elif marker in {"triangle", "diamond", "square"}:
        path = c.beginPath()
        pts = marker_polygon(marker, x, y, size * (1.05 if marker == "triangle" else 1.0))
        path.moveTo(*pts[0])
        for pt in pts[1:]:
            path.lineTo(*pt)
        path.close()
        c.drawPath(path, stroke=1, fill=1)
    elif marker == "plus":
        c.roundRect(x - size, y - size, 2 * size, 2 * size, 1.2, stroke=1, fill=1)
        c.setStrokeColor(stroke)
        c.setLineWidth(0.65)
        c.line(x - size * 0.55, y, x + size * 0.55, y)
        c.line(x, y - size * 0.55, x, y + size * 0.55)
    else:
        c.circle(x, y, size, stroke=1, fill=1)


def draw_marker_png(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    marker: str,
    color: str,
    significant: bool,
    size: float,
    scale: int,
) -> None:
    xs, ys, rs = x * scale, y * scale, size * scale
    fill = rgb(color if significant else "#FFFFFF")
    outline = rgb(TEXT if significant else color)
    width = max(1, int((0.55 if significant else 0.9) * scale))
    if marker == "circle":
        draw.ellipse([xs - rs, ys - rs, xs + rs, ys + rs], fill=fill, outline=outline, width=width)
    elif marker in {"triangle", "diamond", "square"}:
        pts = [(px * scale, py * scale) for px, py in marker_polygon(marker, x, y, size * (1.05 if marker == "triangle" else 1.0))]
        draw.polygon(pts, fill=fill, outline=outline)
        draw.line(pts + [pts[0]], fill=outline, width=width)
    elif marker == "plus":
        draw.rounded_rectangle([xs - rs, ys - rs, xs + rs, ys + rs], radius=1.2 * scale, fill=fill, outline=outline, width=width)
        draw.line([xs - rs * 0.55, ys, xs + rs * 0.55, ys], fill=outline, width=width)
        draw.line([xs, ys - rs * 0.55, xs, ys + rs * 0.55], fill=outline, width=width)
    else:
        draw.ellipse([xs - rs, ys - rs, xs + rs, ys + rs], fill=fill, outline=outline, width=width)


def load_data() -> pd.DataFrame:
    data = pd.read_csv(INPUT)
    required = {
        "target_name", "hypothesis_id", "hypothesis_rank", "effect_pp",
        "se_pp", "ci_low_pp", "ci_high_pp", "category_display",
        "is_significant", "display_label", "discovery_target_separation",
        "fidelity_gap", "n_pairs",
    }
    missing = sorted(required.difference(data.columns))
    if missing:
        raise RuntimeError(f"Public fixed-concept source is missing columns: {missing}")
    if len(data) != 60 or data["target_name"].nunique() != 3:
        raise RuntimeError("Public fixed-concept source must contain 60 rows across three targets")
    return data


def prepare_layout(sub: pd.DataFrame, label_width: float) -> tuple[pd.DataFrame, float]:
    sub = sub.sort_values(["effect_pp", "hypothesis_rank"], ascending=[False, True]).reset_index(drop=True)
    labels = [
        wrap_text_points(text, width_pt=label_width, size=6.6, bold=False)
        for text in sub["display_label"]
    ]
    line_counts = np.array([len(x) for x in labels])
    row_heights = 12.2 + np.maximum(0, line_counts - 1) * 6.5
    top = 52.0
    y_centres: list[float] = []
    y = top
    for h in row_heights:
        y_centres.append(y + h / 2)
        y += h
    sub = sub.copy()
    sub["wrapped_label"] = labels
    sub["row_height"] = row_heights
    sub["y"] = y_centres
    height = y + 62.0
    return sub, height


def x_map(value: float, x0: float, x1: float, xlim: tuple[float, float]) -> float:
    lo, hi = xlim
    return x0 + (value - lo) / (hi - lo) * (x1 - x0)


def ticks(xlim: tuple[float, float], step: int) -> list[int]:
    lo, hi = xlim
    start = int(math.ceil(lo / step) * step)
    end = int(math.floor(hi / step) * step)
    return list(range(start, end + 1, step))


def draw_pdf(spec: dict[str, object], sub: pd.DataFrame, path: Path) -> None:
    page_w = 520.0
    text_right = 322.0
    plot_left = 333.0
    plot_right = 506.0
    label_width = text_right - 12
    sub, page_h = prepare_layout(sub, label_width)
    plot_top = 52.0
    plot_bottom = float(sub["y"].max() + sub["row_height"].iloc[-1] / 2)
    xlim = tuple(spec["xlim"])  # type: ignore[arg-type]

    c = canvas.Canvas(str(path), pagesize=(page_w, page_h))
    c.setTitle(str(spec["title"]))

    c.setFillColor(hex_color(TEXT))
    c.setFont(font_name(True), 9.2)
    c.drawString(12, page_h - 17, str(spec["title"]))
    c.setFillColor(hex_color(MUTED))
    c.setFont(font_name(False), 6.7)
    c.drawString(12, page_h - 29, str(spec["subtitle"]))
    c.drawRightString(page_w - 12, page_h - 18, "Full fixed-concept audit: 20 concepts")

    def cy(y: float) -> float:
        return page_h - y

    # Row guides and plot background grid.
    y_bounds = [plot_top]
    for _, row in sub.iterrows():
        y_bounds.append(float(row["y"] + row["row_height"] / 2))
    c.setStrokeColor(hex_color(GRID))
    c.setLineWidth(0.35)
    for yb in y_bounds:
        c.line(12, cy(yb), plot_right, cy(yb))

    for tick in ticks(xlim, int(spec["tick_step"])):
        x = x_map(tick, plot_left, plot_right, xlim)
        c.setStrokeColor(hex_color(ZERO if tick == 0 else GRID))
        c.setLineWidth(0.8 if tick == 0 else 0.45)
        c.line(x, cy(plot_top), x, cy(plot_bottom))
        c.setFillColor(hex_color(TEXT))
        c.setFont(font_name(False), 6.2)
        c.drawCentredString(x, cy(plot_bottom + 10), f"{tick:g}")

    c.setStrokeColor(hex_color(AXIS))
    c.setLineWidth(0.6)
    c.line(plot_left, cy(plot_bottom), plot_right, cy(plot_bottom))

    # Labels and estimates.
    for _, row in sub.iterrows():
        y = float(row["y"])
        label_color = TEXT if bool(row["is_significant"]) else MUTED_LIGHT
        draw_right_multiline_pdf(
            c,
            text_right,
            cy(y),
            row["wrapped_label"],
            size=6.6,
            color=label_color,
            line_height=6.9,
            bold=False,
        )
        cat = str(row["category_display"])
        color = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["Unclassified"])
        marker = CATEGORY_MARKERS.get(cat, "circle")
        significant = bool(row["is_significant"])
        line_color = color if significant else blend(color, 0.42)
        c.setStrokeColor(hex_color(line_color))
        c.setLineWidth(0.8 if significant else 0.65)
        xlo = x_map(float(row["ci_low_pp"]), plot_left, plot_right, xlim)
        xhi = x_map(float(row["ci_high_pp"]), plot_left, plot_right, xlim)
        x = x_map(float(row["effect_pp"]), plot_left, plot_right, xlim)
        c.line(xlo, cy(y), xhi, cy(y))
        draw_marker_pdf(c, x, cy(y), marker, color, significant, size=3.7 if significant else 3.4)

    c.setFillColor(hex_color(TEXT))
    c.setFont(font_name(False), 6.6)
    c.drawCentredString((plot_left + plot_right) / 2, cy(plot_bottom + 24), str(spec["xlabel"]))

    # Legend.
    cats = [cat for cat in CATEGORY_COLORS if cat in set(sub["category_display"])]
    legend_items = cats + ["Bonferroni-significant", "Not significant"]
    # ReportLab uses a bottom-origin coordinate system; keep the legend in the
    # bottom margin so it does not collide with the title and subtitle.
    y_leg = 27.0
    x = 12
    c.setFont(font_name(False), 6.0)
    for item in legend_items:
        if item in CATEGORY_COLORS:
            color = CATEGORY_COLORS[item]
            marker = CATEGORY_MARKERS.get(item, "circle")
            draw_marker_pdf(c, x + 4, y_leg, marker, color, True, size=3.0)
            c.setFillColor(hex_color(TEXT))
            c.drawString(x + 10, y_leg - 2.0, item)
            x += pdfmetrics.stringWidth(item, font_name(False), 6.0) + 22
        elif item == "Bonferroni-significant":
            draw_marker_pdf(c, x + 4, y_leg, "circle", "#6D7B8A", True, size=3.0)
            c.setFillColor(hex_color(TEXT))
            c.drawString(x + 10, y_leg - 2.0, item)
            x += 95
        else:
            draw_marker_pdf(c, x + 4, y_leg, "circle", "#6D7B8A", False, size=3.0)
            c.setFillColor(hex_color(TEXT))
            c.drawString(x + 10, y_leg - 2.0, item)

    c.save()


def draw_png(spec: dict[str, object], sub: pd.DataFrame, path: Path) -> None:
    page_w = 520.0
    text_right = 322.0
    plot_left = 333.0
    plot_right = 506.0
    label_width = text_right - 12
    sub, page_h = prepare_layout(sub, label_width)
    plot_top = 52.0
    plot_bottom = float(sub["y"].max() + sub["row_height"].iloc[-1] / 2)
    xlim = tuple(spec["xlim"])  # type: ignore[arg-type]
    scale = 3

    img = Image.new("RGB", (int(page_w * scale), int(page_h * scale)), "white")
    draw = ImageDraw.Draw(img)

    def sx(x: float) -> float:
        return x * scale

    def sy(y: float) -> float:
        return y * scale

    def line(x1: float, y1: float, x2: float, y2: float, color: str, width: float = 0.6) -> None:
        draw.line([sx(x1), sy(y1), sx(x2), sy(y2)], fill=rgb(color), width=max(1, int(width * scale)))

    def txt(x: float, y: float, text: str, size: float, color: str, bold: bool = False, anchor: str = "la") -> None:
        font = pil_font(size, bold=bold, scale=scale)
        draw.text((sx(x), sy(y)), text, fill=rgb(color), font=font, anchor=anchor)

    txt(12, 10, str(spec["title"]), 9.2, TEXT, bold=True)
    txt(12, 23, str(spec["subtitle"]), 6.7, MUTED)
    # Right-aligned small audit label.
    font = pil_font(6.7, scale=scale)
    audit = "Full fixed-concept audit: 20 concepts"
    bbox = draw.textbbox((0, 0), audit, font=font)
    draw.text((sx(page_w - 12) - (bbox[2] - bbox[0]), sy(10)), audit, fill=rgb(MUTED), font=font)

    y_bounds = [plot_top]
    for _, row in sub.iterrows():
        y_bounds.append(float(row["y"] + row["row_height"] / 2))
    for yb in y_bounds:
        line(12, yb, plot_right, yb, GRID, 0.35)
    for tick in ticks(xlim, int(spec["tick_step"])):
        x = x_map(tick, plot_left, plot_right, xlim)
        line(x, plot_top, x, plot_bottom, ZERO if tick == 0 else GRID, 0.8 if tick == 0 else 0.45)
        txt(x, plot_bottom + 7.2, f"{tick:g}", 6.2, TEXT, anchor="ma")
    line(plot_left, plot_bottom, plot_right, plot_bottom, AXIS, 0.6)

    for _, row in sub.iterrows():
        y = float(row["y"])
        label_color = TEXT if bool(row["is_significant"]) else MUTED_LIGHT
        draw_right_multiline_png(
            draw,
            text_right,
            y,
            row["wrapped_label"],
            size=6.6,
            color=label_color,
            line_height=6.9,
            bold=False,
            scale=scale,
        )
        cat = str(row["category_display"])
        color = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["Unclassified"])
        marker = CATEGORY_MARKERS.get(cat, "circle")
        significant = bool(row["is_significant"])
        line_color = color if significant else blend(color, 0.42)
        xlo = x_map(float(row["ci_low_pp"]), plot_left, plot_right, xlim)
        xhi = x_map(float(row["ci_high_pp"]), plot_left, plot_right, xlim)
        x = x_map(float(row["effect_pp"]), plot_left, plot_right, xlim)
        line(xlo, y, xhi, y, line_color, 0.8 if significant else 0.65)
        draw_marker_png(draw, x, y, marker, color, significant, size=3.7 if significant else 3.4, scale=scale)

    txt((plot_left + plot_right) / 2, plot_bottom + 20, str(spec["xlabel"]), 6.6, TEXT, anchor="ma")

    cats = [cat for cat in CATEGORY_COLORS if cat in set(sub["category_display"])]
    y_leg = page_h - 27
    x = 12
    for item in cats:
        color = CATEGORY_COLORS[item]
        marker = CATEGORY_MARKERS.get(item, "circle")
        draw_marker_png(draw, x + 4, y_leg, marker, color, True, size=3.0, scale=scale)
        txt(x + 10, y_leg - 5, item, 6.0, TEXT)
        x += (len(item) * 3.1 + 25)
    draw_marker_png(draw, x + 4, y_leg, "circle", "#6D7B8A", True, size=3.0, scale=scale)
    txt(x + 10, y_leg - 5, "Bonferroni-significant", 6.0, TEXT)
    x += 94
    draw_marker_png(draw, x + 4, y_leg, "circle", "#6D7B8A", False, size=3.0, scale=scale)
    txt(x + 10, y_leg - 5, "Not significant", 6.0, TEXT)

    img.save(path)


def write_source_summary(df: pd.DataFrame) -> None:
    CHECKDIR.mkdir(parents=True, exist_ok=True)
    summary = (
        df.groupby("target_name")
        .agg(
            n_concepts=("hypothesis_id", "count"),
            n_bonferroni_significant=("is_significant", "sum"),
            n_generic=("category_display", lambda s: int((s == "Generic margin wording").sum())),
        )
        .reset_index()
    )
    summary.to_csv(CHECKDIR / "hypothesaes_figure_input_summary.csv", index=False)


def combine_pdfs(paths: Iterable[Path], out: Path) -> None:
    from pypdf import PdfWriter, PdfReader

    writer = PdfWriter()
    for path in paths:
        reader = PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)
    with out.open("wb") as f:
        writer.write(f)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    CHECKDIR.mkdir(parents=True, exist_ok=True)
    setup_fonts()
    df = load_data()
    write_source_summary(df)

    pdf_paths: list[Path] = []
    for spec in TARGETS:
        sub = df[df["target_name"] == spec["target_name"]].copy()
        if len(sub) != 20:
            raise RuntimeError(f"{spec['target_name']} has {len(sub)} concepts, expected 20")
        if spec["slug"] == "exposure" and (
            sub["ci_low_pp"].min() < spec["xlim"][0]
            or sub["ci_high_pp"].max() > spec["xlim"][1]
        ):
            raise RuntimeError("Exposure child CI falls outside the configured x-axis limits")
        stem = OUTDIR / f"fig_appendix_hypothesaes_{spec['slug']}_20_concepts"
        pdf_path = stem.with_suffix(".pdf")
        png_path = stem.with_suffix(".png")
        draw_pdf(spec, sub, pdf_path)
        draw_png(spec, sub, png_path)
        pdf_paths.append(pdf_path)

    try:
        combine_pdfs(pdf_paths, OUTDIR / "full_fixed_concept_appendix_figures.pdf")
    except Exception:
        manifest = OUTDIR / "full_fixed_concept_appendix_figures_manifest.csv"
        with manifest.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["figure_pdf"])
            for path in pdf_paths:
                writer.writerow([path.name])


if __name__ == "__main__":
    main()
