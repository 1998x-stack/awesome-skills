#!/usr/bin/env python3
"""Generate an infographic-style pricing comparison image from a pasted pricing table.

Expected columns, in order, when headers are ambiguous:
model, tier, list_input, list_output, discount, discounted_input, discounted_output, notes

The parser accepts tab-separated text, simple Markdown pipe tables, and section header rows.
"""

from __future__ import annotations

import argparse
import math
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as exc:  # pragma: no cover
    raise SystemExit("Pillow is required. Install with: pip install -r scripts/requirements.txt") from exc

NOT_CHARGED = {"", "-", "na", "n/a", "none", "null", "free", "not charged", "no charge", "\u4e0d\u8ba1\u8d39"}
THIRD_PARTY = "\u7b2c\u4e09\u65b9"
SPEECH = "\u8bed\u97f3"
VIDEO = "\u89c6\u9891"
CHARACTER = "\u5b57\u7b26"
TOKEN = "token"

LABELS = {
    "title": "\u6a21\u578b\u4ef7\u683c\u5bf9\u6bd4\u5206\u6790",
    "subtitle": "\u6309\u8868\u5185\u6298\u540e\u4ef7\u6bd4\u8f83\uff1b\u4e0d\u540c\u8ba1\u8d39\u5355\u4f4d\u4e0d\u76f4\u63a5\u6a2a\u5411\u6bd4\u8f83",
    "lowest_text_input": "\u6700\u4f4e\u6587\u672c\u8f93\u5165",
    "lowest_text_output": "\u6700\u4f4e\u6587\u672c\u8f93\u51fa",
    "lowest_third_output": "\u7b2c\u4e09\u65b9\u6700\u4f4e\u8f93\u51fa",
    "highest_text_output": "\u6700\u9ad8\u6587\u672c\u8f93\u51fa",
    "speech": "\u8bed\u97f3\u5408\u6210",
    "video": "\u89c6\u9891\u6700\u4f4e",
    "section_text": "\u4e00\u3001\u6587\u672c\u6a21\u578b\uff1a\u6309\u6298\u540e\u8f93\u51fa\u4ef7\u4ece\u4f4e\u5230\u9ad8\u6392\u5e8f",
    "section_text_desc": "\u8f93\u51fa\u4ef7\u901a\u5e38\u66f4\u80fd\u51b3\u5b9a\u751f\u6210\u578b\u5e94\u7528\u6210\u672c\uff1b\u540c\u65f6\u5217\u51fa\u8f93\u5165\u4ef7\u4e0e\u8f93\u51fa/\u8f93\u5165\u500d\u6570\u3002",
    "model_tier": "\u6a21\u578b / \u9636\u68af",
    "category": "\u5206\u7c7b",
    "input": "\u8f93\u5165",
    "output": "\u8f93\u51fa",
    "ratio": "\u51fa/\u5165",
    "bar": "\u8f93\u51fa\u4ef7\u76f8\u5bf9\u6761",
    "insights": "\u4e8c\u3001\u5173\u952e\u7ed3\u8bba",
    "premium": "\u4e09\u3001\u957f\u4e0a\u4e0b\u6587\u9636\u68af\u6ea2\u4ef7",
    "premium_desc": "\u540c\u4e00\u6a21\u578b\u4e0d\u540c\u4e0a\u4e0b\u6587\u9636\u68af\u7684\u6700\u9ad8\u6863 / \u6700\u4f4e\u6863\u6298\u540e\u4ef7\u683c\u500d\u6570\u3002",
    "non_text": "\u56db\u3001\u975e\u6587\u672c\u6a21\u578b",
    "unit_note": "\u5355\u4f4d\u4e0d\u540c\uff0c\u4e0d\u5efa\u8bae\u4e0e\u6587\u672c Token \u5355\u4ef7\u76f4\u63a5\u76f8\u9664\u6bd4\u8f83\u3002",
    "footer": "\u6ce8\uff1a\u672c\u56fe\u53ea\u57fa\u4e8e\u8f93\u5165\u8868\u683c\u8ba1\u7b97\uff1b\u975e\u8ba1\u8d39\u9879\u672a\u53c2\u4e0e\u8f93\u5165/\u8f93\u51fa\u6bd4\u8ba1\u7b97\u3002",
}


@dataclass
class PricingRow:
    category: str
    unit_type: str
    model: str
    tier: str
    list_input: Optional[float]
    list_output: Optional[float]
    discount: Optional[float]
    discounted_input: Optional[float]
    discounted_output: Optional[float]
    note: str

    @property
    def output_input_ratio(self) -> Optional[float]:
        if self.discounted_input and self.discounted_output:
            return self.discounted_output / self.discounted_input
        return None


def split_row(line: str) -> list[str]:
    line = line.strip()
    if not line or line.startswith("```"):
        return []
    if "|" in line:
        parts = [p.strip() for p in line.strip("|").split("|")]
        if all(set(p) <= {"-", ":", " "} for p in parts):
            return []
        return parts
    return [p.strip() for p in line.split("\t")]


def parse_num(value: str | None) -> Optional[float]:
    if value is None:
        return None
    s = str(value).strip().replace(",", "")
    if s.lower() in NOT_CHARGED:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return None
    return float(m.group(0))


def classify_unit(section: str) -> str:
    s = section.lower()
    if TOKEN in s:
        return "text"
    if SPEECH in section or CHARACTER in section or "character" in s:
        return "speech"
    if VIDEO in section or "video" in s or "second" in s:
        return "video"
    return "other"


def infer_header(parts: list[str]) -> bool:
    joined = " ".join(parts).lower()
    return ("model" in joined or "\u6a21\u578b" in joined) and ("discount" in joined or "\u6298\u6263" in joined)


def parse_table(text: str) -> list[PricingRow]:
    rows: list[PricingRow] = []
    current_section = "uncategorized"
    current_unit = "other"
    for raw in text.splitlines():
        parts = split_row(raw)
        if not parts:
            continue
        while len(parts) < 8:
            parts.append("")
        nonempty = [p for p in parts if p.strip()]
        if infer_header(parts):
            continue
        if len(nonempty) == 1 and not parse_num(nonempty[0]):
            current_section = nonempty[0]
            current_unit = classify_unit(current_section)
            continue
        model = parts[0].strip()
        if not model:
            continue
        list_input = parse_num(parts[2])
        list_output = parse_num(parts[3])
        discount = parse_num(parts[4])
        discounted_input = parse_num(parts[5])
        discounted_output = parse_num(parts[6])
        if discounted_input is None and list_input is not None and discount is not None:
            discounted_input = list_input * discount
        if discounted_output is None and list_output is not None and discount is not None:
            discounted_output = list_output * discount
        rows.append(PricingRow(
            category=current_section,
            unit_type=current_unit,
            model=model,
            tier=parts[1].strip() or "-",
            list_input=list_input,
            list_output=list_output,
            discount=discount,
            discounted_input=discounted_input,
            discounted_output=discounted_output,
            note=parts[7].strip(),
        ))
    return rows


def find_font(candidates: Iterable[str]) -> str | None:
    roots = ["/usr/share/fonts", "/usr/local/share/fonts", "/System/Library/Fonts", "/Library/Fonts"]
    paths: list[str] = []
    for root in roots:
        if os.path.exists(root):
            for parent, _, files in os.walk(root):
                for name in files:
                    if name.lower().endswith((".ttf", ".ttc", ".otf")):
                        paths.append(os.path.join(parent, name))
    for key in candidates:
        key_l = key.lower()
        for path in paths:
            if key_l in path.lower():
                return path
    return paths[0] if paths else None


def make_font(path: str | None, size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if bold:
        bold_path = find_font(["notosanscjk-bold", "sourcehansanscn-bold", "wenquanyi", "arial unicode"])
        if bold_path:
            return ImageFont.truetype(bold_path, size)
    if path:
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def fmt(x: Optional[float], digits: int = 2) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "\u4e0d\u8ba1\u8d39"
    if abs(x) < 1:
        return f"{x:.3f}".rstrip("0").rstrip(".")
    return f"{x:.{digits}f}".rstrip("0").rstrip(".")


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), str(text), font=font)
    return box[2] - box[0], box[3] - box[1]


def wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.ImageFont, max_width: int, fill: str, spacing: int = 6) -> int:
    x, y = xy
    lines: list[str] = []
    cur = ""
    for ch in text:
        candidate = cur + ch
        if text_size(draw, candidate, font)[0] <= max_width or not cur:
            cur = candidate
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    yy = y
    for line in lines:
        draw.text((x, yy), line, font=font, fill=fill)
        yy += text_size(draw, line, font)[1] + spacing
    return yy


def card(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], title: str, value: str, desc: str, fonts: dict[str, ImageFont.ImageFont]) -> None:
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=24, fill="#FFFFFF", outline="#E0E0DF", width=1)
    draw.text((x1 + 22, y1 + 22), title, font=fonts["h3"], fill="#333333")
    draw.text((x1 + 22, y1 + 62), value, font=fonts["value"], fill="#111111")
    wrapped(draw, (x1 + 22, y1 + 115), desc, fonts["small"], x2 - x1 - 44, "#666666", 3)


def row_label(row: PricingRow) -> str:
    return f"{row.model} | {row.tier}"


def summarize(rows: list[PricingRow]) -> dict[str, PricingRow | None]:
    text_rows = [r for r in rows if r.unit_type == "text"]
    bill_input = [r for r in text_rows if r.discounted_input is not None]
    bill_output = [r for r in text_rows if r.discounted_output is not None]
    third = [r for r in text_rows if THIRD_PARTY in r.category or "third" in r.category.lower()]
    speech = [r for r in rows if r.unit_type == "speech" and r.discounted_input is not None]
    video = [r for r in rows if r.unit_type == "video" and r.discounted_input is not None]
    return {
        "min_text_input": min(bill_input, key=lambda r: r.discounted_input) if bill_input else None,
        "min_text_output": min(bill_output, key=lambda r: r.discounted_output) if bill_output else None,
        "min_third_output": min([r for r in third if r.discounted_output is not None], key=lambda r: r.discounted_output) if third else None,
        "max_text_output": max(bill_output, key=lambda r: r.discounted_output) if bill_output else None,
        "speech": min(speech, key=lambda r: r.discounted_input) if speech else None,
        "video": min(video, key=lambda r: r.discounted_input) if video else None,
    }


def premiums(rows: list[PricingRow]) -> list[tuple[str, float, float]]:
    grouped: dict[str, list[PricingRow]] = {}
    for row in rows:
        if row.unit_type == "text":
            grouped.setdefault(row.model, []).append(row)
    result = []
    for model, group in grouped.items():
        usable = [r for r in group if r.discounted_input and r.discounted_output]
        if len(usable) < 2:
            continue
        low_in = min(r.discounted_input for r in usable if r.discounted_input)
        high_in = max(r.discounted_input for r in usable if r.discounted_input)
        low_out = min(r.discounted_output for r in usable if r.discounted_output)
        high_out = max(r.discounted_output for r in usable if r.discounted_output)
        result.append((model, high_in / low_in, high_out / low_out))
    return sorted(result, key=lambda x: x[2], reverse=True)


def generate_image(rows: list[PricingRow], output_path: Path, title: str | None = None) -> None:
    W, H = 1800, 2600
    img = Image.new("RGB", (W, H), "#F7F7F5")
    draw = ImageDraw.Draw(img)
    font_path = find_font(["notosanscjk", "sourcehansans", "wenquanyi", "pingfang", "simhei", "arial unicode", "dejavusans"])
    fonts = {
        "title": make_font(font_path, 48, True),
        "subtitle": make_font(font_path, 24),
        "h2": make_font(font_path, 30, True),
        "h3": make_font(font_path, 24, True),
        "body": make_font(font_path, 22),
        "small": make_font(font_path, 17),
        "tiny": make_font(font_path, 15),
        "value": make_font(font_path, 40, True),
    }

    draw.text((70, 55), title or LABELS["title"], font=fonts["title"], fill="#111111")
    draw.text((72, 120), LABELS["subtitle"], font=fonts["subtitle"], fill="#555555")
    draw.line((70, 165, W - 70, 165), fill="#CCCCCC", width=2)

    summary = summarize(rows)
    def card_data(key: str, label: str, price_field: str) -> tuple[str, str, str]:
        row = summary.get(key)
        if row is None:
            return (label, "--", "no matching row")
        price = getattr(row, price_field)
        return (label, f"¥{fmt(price)}", f"{row.model}\n{row.tier}")

    cards = [
        card_data("min_text_input", LABELS["lowest_text_input"], "discounted_input"),
        card_data("min_text_output", LABELS["lowest_text_output"], "discounted_output"),
        card_data("min_third_output", LABELS["lowest_third_output"], "discounted_output"),
        card_data("max_text_output", LABELS["highest_text_output"], "discounted_output"),
        card_data("speech", LABELS["speech"], "discounted_input"),
        card_data("video", LABELS["video"], "discounted_input"),
    ]
    x0, y0, card_w, card_h, gap = 70, 200, 265, 175, 22
    for i, item in enumerate(cards):
        x = x0 + i * (card_w + gap)
        card(draw, (x, y0, x + card_w, y0 + card_h), item[0], item[1], item[2], fonts)

    section_y = 430
    draw.text((70, section_y), LABELS["section_text"], font=fonts["h2"], fill="#111111")
    draw.text((70, section_y + 42), LABELS["section_text_desc"], font=fonts["body"], fill="#555555")

    text_rows = [r for r in rows if r.unit_type == "text" and r.discounted_output is not None]
    ranked = sorted(text_rows, key=lambda r: (r.discounted_output or 999999, r.discounted_input or 999999, r.model))
    table_x, table_y = 70, section_y + 90
    table_w, row_h, header_h = W - 140, 48, 54
    table_h = header_h + row_h * max(len(ranked), 1) + 18
    draw.rounded_rectangle((table_x, table_y, table_x + table_w, table_y + table_h), radius=22, fill="#FFFFFF", outline="#E0E0DF")
    col_model = table_x + 24
    col_cat = table_x + 520
    col_in = table_x + 720
    col_out = table_x + 850
    col_ratio = table_x + 990
    bar_x = table_x + 1100
    bar_w = table_x + table_w - bar_x - 24
    for h, x in [(LABELS["model_tier"], col_model), (LABELS["category"], col_cat), (LABELS["input"], col_in), (LABELS["output"], col_out), (LABELS["ratio"], col_ratio), (LABELS["bar"], bar_x)]:
        draw.text((x, table_y + 16), h, font=fonts["small"], fill="#555555")
    draw.line((table_x + 20, table_y + header_h, table_x + table_w - 20, table_y + header_h), fill="#DDDDDD", width=1)
    max_out = max((r.discounted_output or 0 for r in ranked), default=1)
    for idx, row in enumerate(ranked):
        y = table_y + header_h + idx * row_h
        if idx % 2:
            draw.rectangle((table_x + 12, y, table_x + table_w - 12, y + row_h), fill="#FAFAF9")
        label = row_label(row)
        if len(label) > 48:
            label = label[:47] + "..."
        draw.text((col_model, y + 12), label, font=fonts["small"], fill="#222222")
        cat = row.category[:12]
        draw.text((col_cat, y + 12), cat, font=fonts["small"], fill="#666666")
        draw.text((col_in, y + 12), fmt(row.discounted_input), font=fonts["small"], fill="#333333")
        draw.text((col_out, y + 12), fmt(row.discounted_output), font=fonts["small"], fill="#111111")
        ratio = row.output_input_ratio
        draw.text((col_ratio, y + 12), f"{ratio:.1f}x" if ratio else "--", font=fonts["small"], fill="#333333")
        bw = int(((row.discounted_output or 0) / max_out) * bar_w) if max_out else 0
        draw.rounded_rectangle((bar_x, y + 15, bar_x + bw, y + 32), radius=8, fill="#AFAFAF")
        draw.text((bar_x + bw + 8, y + 9), fmt(row.discounted_output), font=fonts["tiny"], fill="#555555")

    insight_y = table_y + table_h + 47
    draw.text((70, insight_y), LABELS["insights"], font=fonts["h2"], fill="#111111")
    min_out = summary.get("min_text_output")
    min_in = summary.get("min_text_input")
    max_out_row = summary.get("max_text_output")
    note_rows = [r for r in rows if r.note]
    insight_cards = [
        ("\u6210\u672c\u68af\u961f", f"{min_out.model if min_out else '--'} \u662f\u8f93\u51fa\u4ef7\u6700\u4f4e\u7684\u6587\u672c\u884c\uff1b{min_in.model if min_in else '--'} \u662f\u8f93\u5165\u4ef7\u6700\u4f4e\u7684\u6587\u672c\u884c\u3002"),
        ("\u957f\u4e0a\u4e0b\u6587\u6ea2\u4ef7", "\u6709\u591a\u4e2a\u8ba1\u8d39\u9636\u68af\u7684\u6a21\u578b\u9700\u8981\u5355\u72ec\u770b\u9ad8\u6863/\u4f4e\u6863\u500d\u6570\uff0c\u907f\u514d\u4e0d\u5fc5\u8981\u8de8\u6863\u3002"),
        ("\u8f93\u51fa\u66f4\u8d35", "\u751f\u6210\u578b\u573a\u666f\u5e94\u4f18\u5148\u770b\u6298\u540e\u8f93\u51fa\u4ef7\u548c\u8f93\u51fa/\u8f93\u5165\u500d\u6570\uff0c\u800c\u4e0d\u53ea\u770b\u8f93\u5165\u4ef7\u3002"),
        ("\u5907\u6ce8\u98ce\u9669", f"\u5171\u6709 {len(note_rows)} \u6761\u5e26\u5907\u6ce8\u7684\u4ef7\u683c\u884c\uff0c\u9884\u7b97\u6216\u91c7\u8d2d\u65f6\u5e94\u5355\u72ec\u6807\u8bb0\u3002"),
    ]
    box_w = (W - 140 - 30) // 2
    box_h = 150
    for i, (t, body) in enumerate(insight_cards):
        x = 70 + (i % 2) * (box_w + 30)
        y = insight_y + 55 + (i // 2) * (box_h + 28)
        draw.rounded_rectangle((x, y, x + box_w, y + box_h), radius=22, fill="#FFFFFF", outline="#E0E0DF")
        draw.text((x + 24, y + 20), t, font=fonts["h3"], fill="#111111")
        wrapped(draw, (x + 24, y + 62), body, fonts["body"], box_w - 48, "#555555", 4)

    prem_y = insight_y + 55 + 2 * (box_h + 28) + 30
    draw.text((70, prem_y), LABELS["premium"], font=fonts["h2"], fill="#111111")
    draw.text((70, prem_y + 42), LABELS["premium_desc"], font=fonts["body"], fill="#555555")
    prem_rows = premiums(rows)
    prem_x, prem_table_y, prem_table_w = 70, prem_y + 88, 800
    draw.rounded_rectangle((prem_x, prem_table_y, prem_x + prem_table_w, prem_table_y + 65 + 56 * max(len(prem_rows), 1)), radius=22, fill="#FFFFFF", outline="#E0E0DF")
    for h, x in [("\u6a21\u578b", prem_x + 24), ("\u8f93\u5165\u500d\u6570", prem_x + 450), ("\u8f93\u51fa\u500d\u6570", prem_x + 600)]:
        draw.text((x, prem_table_y + 20), h, font=fonts["small"], fill="#555555")
    draw.line((prem_x + 20, prem_table_y + 58, prem_x + prem_table_w - 20, prem_table_y + 58), fill="#DDDDDD", width=1)
    for i, (model, input_x, output_x) in enumerate(prem_rows):
        y = prem_table_y + 64 + i * 56
        draw.text((prem_x + 24, y + 14), model[:36], font=fonts["small"], fill="#222222")
        draw.text((prem_x + 450, y + 14), f"{input_x:.1f}x", font=fonts["small"], fill="#333333")
        draw.text((prem_x + 600, y + 14), f"{output_x:.1f}x", font=fonts["small"], fill="#111111")

    sv_x = 930
    draw.text((sv_x, prem_y), LABELS["non_text"], font=fonts["h2"], fill="#111111")
    draw.text((sv_x, prem_y + 42), LABELS["unit_note"], font=fonts["body"], fill="#555555")
    sv_y = prem_y + 88
    draw.rounded_rectangle((sv_x, sv_y, W - 70, sv_y + 400), radius=22, fill="#FFFFFF", outline="#E0E0DF")
    speech_rows = [r for r in rows if r.unit_type == "speech" and r.discounted_input is not None]
    video_rows = [r for r in rows if r.unit_type == "video" and r.discounted_input is not None]
    draw.text((sv_x + 24, sv_y + 20), LABELS["speech"], font=fonts["h3"], fill="#111111")
    if speech_rows:
        row = min(speech_rows, key=lambda r: r.discounted_input or 999999)
        draw.text((sv_x + 24, sv_y + 62), f"{row.model}: ¥{fmt(row.discounted_input)}", font=fonts["body"], fill="#555555")
    draw.text((sv_x + 24, sv_y + 122), "\u89c6\u9891\u751f\u6210\uff08\u6298\u540e ¥/\u79d2\uff09", font=fonts["h3"], fill="#111111")
    max_vid = max((r.discounted_input or 0 for r in video_rows), default=1)
    vy = sv_y + 175
    for row in video_rows[:5]:
        label = f"{row.model} / {row.tier}"
        draw.text((sv_x + 24, vy), label[:34], font=fonts["small"], fill="#222222")
        vx = sv_x + 385
        bw = int(((row.discounted_input or 0) / max_vid) * 360) if max_vid else 0
        draw.rounded_rectangle((vx, vy + 5, vx + bw, vy + 24), radius=8, fill="#AFAFAF")
        draw.text((vx + bw + 10, vy - 1), fmt(row.discounted_input, 6), font=fonts["small"], fill="#333333")
        vy += 50

    footer_y = H - 85
    draw.line((70, footer_y - 25, W - 70, footer_y - 25), fill="#CCCCCC", width=1)
    draw.text((70, footer_y), LABELS["footer"], font=fonts["small"], fill="#666666")
    img.save(output_path, quality=95)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="UTF-8 text file containing the pricing table")
    parser.add_argument("--output", required=True, help="Output PNG path")
    parser.add_argument("--title", default=None, help="Optional chart title")
    args = parser.parse_args()
    text = Path(args.input).read_text(encoding="utf-8")
    rows = parse_table(text)
    if not rows:
        raise SystemExit("No pricing rows parsed. Check table formatting.")
    generate_image(rows, Path(args.output), title=args.title)
    print(f"wrote {args.output} with {len(rows)} parsed rows")


if __name__ == "__main__":
    main()
