"""Intersection-over-union helpers (stdlib only)."""

from __future__ import annotations

from cetodex.models import BBox


def iou(a: BBox, b: BBox) -> float:
    ax1, ay1, ax2, ay2 = a.to_xyxy()
    bx1, by1, bx2, by2 = b.to_xyxy()
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    inter_w = max(0.0, ix2 - ix1)
    inter_h = max(0.0, iy2 - iy1)
    inter = inter_w * inter_h
    union = a.area() + b.area() - inter
    if union <= 0.0:
        return 0.0
    return inter / union
