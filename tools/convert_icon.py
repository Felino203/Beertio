#!/usr/bin/env python3
"""
Convert SVG icons to Monkey C polygon data files.

Supports both <polygon> and <path> elements. Path elements are parsed
into polygon points (curves are approximated with line segments).

Usage:
    python convert_icon.py <input.svg> <ModuleName> <output.mc>

Example:
    python convert_icon.py icons/beer.svg BeerIconData ../Beertio/source/icons/BeerIconData.mc
"""

import sys
import re
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"

CURVE_SEGMENTS = 8  # Number of line segments to approximate a cubic bezier


def parse_polygon_points(points_str: str) -> list[tuple[float, float]]:
    """Parse SVG polygon points attribute into list of (x, y) tuples."""
    points = []
    pairs = re.split(r"[\s,]+", points_str.strip())
    for i in range(0, len(pairs) - 1, 2):
        points.append((float(pairs[i]), float(pairs[i + 1])))
    return points


def cubic_bezier(p0, p1, p2, p3, segments: int) -> list[tuple[float, float]]:
    """Approximate a cubic bezier curve with line segments."""
    points = []
    for i in range(1, segments + 1):
        t = i / segments
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        points.append((x, y))
    return points


def quadratic_bezier(p0, p1, p2, segments: int) -> list[tuple[float, float]]:
    """Approximate a quadratic bezier curve with line segments."""
    points = []
    for i in range(1, segments + 1):
        t = i / segments
        u = 1 - t
        x = u**2 * p0[0] + 2 * u * t * p1[0] + t**2 * p2[0]
        y = u**2 * p0[1] + 2 * u * t * p1[1] + t**2 * p2[1]
        points.append((x, y))
    return points


def tokenize_path(d: str) -> list[str]:
    """Tokenize an SVG path d attribute into commands and numbers."""
    return re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", d)


def parse_path_d(d: str) -> list[list[tuple[float, float]]]:
    """Parse SVG path d attribute into list of subpaths (list of points)."""
    tokens = tokenize_path(d)
    subpaths = []
    current_points: list[tuple[float, float]] = []
    cx, cy = 0.0, 0.0  # current position
    start_x, start_y = 0.0, 0.0  # subpath start
    last_control = None  # for S/T smooth commands
    last_cmd = ""

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token.replace('.', '').replace('-', '').replace('+', '').replace('e', '').replace('E', '').isdigit():
            # Implicit repeat of last command
            token = last_cmd
        else:
            i += 1

        def consume_float() -> float:
            nonlocal i
            val = float(tokens[i])
            i += 1
            return val

        if token == 'M':
            if current_points:
                subpaths.append(current_points)
                current_points = []
            cx, cy = consume_float(), consume_float()
            start_x, start_y = cx, cy
            current_points.append((cx, cy))
            last_cmd = 'L'  # subsequent coords are implicit LineTo
            last_control = None

        elif token == 'm':
            if current_points:
                subpaths.append(current_points)
                current_points = []
            cx += consume_float()
            cy += consume_float()
            start_x, start_y = cx, cy
            current_points.append((cx, cy))
            last_cmd = 'l'
            last_control = None

        elif token == 'L':
            cx, cy = consume_float(), consume_float()
            current_points.append((cx, cy))
            last_cmd = 'L'
            last_control = None

        elif token == 'l':
            dx, dy = consume_float(), consume_float()
            cx += dx
            cy += dy
            current_points.append((cx, cy))
            last_cmd = 'l'
            last_control = None

        elif token == 'H':
            cx = consume_float()
            current_points.append((cx, cy))
            last_cmd = 'H'
            last_control = None

        elif token == 'h':
            cx += consume_float()
            current_points.append((cx, cy))
            last_cmd = 'h'
            last_control = None

        elif token == 'V':
            cy = consume_float()
            current_points.append((cx, cy))
            last_cmd = 'V'
            last_control = None

        elif token == 'v':
            cy += consume_float()
            current_points.append((cx, cy))
            last_cmd = 'v'
            last_control = None

        elif token == 'C':
            x1, y1 = consume_float(), consume_float()
            x2, y2 = consume_float(), consume_float()
            x3, y3 = consume_float(), consume_float()
            pts = cubic_bezier((cx, cy), (x1, y1), (x2, y2), (x3, y3), CURVE_SEGMENTS)
            current_points.extend(pts)
            last_control = (x2, y2)
            cx, cy = x3, y3
            last_cmd = 'C'

        elif token == 'c':
            x1, y1 = cx + consume_float(), cy + consume_float()
            x2, y2 = cx + consume_float(), cy + consume_float()
            x3, y3 = cx + consume_float(), cy + consume_float()
            pts = cubic_bezier((cx, cy), (x1, y1), (x2, y2), (x3, y3), CURVE_SEGMENTS)
            current_points.extend(pts)
            last_control = (x2, y2)
            cx, cy = x3, y3
            last_cmd = 'c'

        elif token == 'S':
            if last_control and last_cmd in ('C', 'c', 'S', 's'):
                x1 = 2 * cx - last_control[0]
                y1 = 2 * cy - last_control[1]
            else:
                x1, y1 = cx, cy
            x2, y2 = consume_float(), consume_float()
            x3, y3 = consume_float(), consume_float()
            pts = cubic_bezier((cx, cy), (x1, y1), (x2, y2), (x3, y3), CURVE_SEGMENTS)
            current_points.extend(pts)
            last_control = (x2, y2)
            cx, cy = x3, y3
            last_cmd = 'S'

        elif token == 's':
            if last_control and last_cmd in ('C', 'c', 'S', 's'):
                x1 = 2 * cx - last_control[0]
                y1 = 2 * cy - last_control[1]
            else:
                x1, y1 = cx, cy
            dx2, dy2 = consume_float(), consume_float()
            dx3, dy3 = consume_float(), consume_float()
            x2, y2 = cx + dx2, cy + dy2
            x3, y3 = cx + dx3, cy + dy3
            pts = cubic_bezier((cx, cy), (x1, y1), (x2, y2), (x3, y3), CURVE_SEGMENTS)
            current_points.extend(pts)
            last_control = (x2, y2)
            cx, cy = x3, y3
            last_cmd = 's'

        elif token == 'Q':
            x1, y1 = consume_float(), consume_float()
            x2, y2 = consume_float(), consume_float()
            pts = quadratic_bezier((cx, cy), (x1, y1), (x2, y2), CURVE_SEGMENTS)
            current_points.extend(pts)
            last_control = (x1, y1)
            cx, cy = x2, y2
            last_cmd = 'Q'

        elif token == 'q':
            x1, y1 = cx + consume_float(), cy + consume_float()
            x2, y2 = cx + consume_float(), cy + consume_float()
            pts = quadratic_bezier((cx, cy), (x1, y1), (x2, y2), CURVE_SEGMENTS)
            current_points.extend(pts)
            last_control = (x1, y1)
            cx, cy = x2, y2
            last_cmd = 'q'

        elif token == 'T':
            if last_control and last_cmd in ('Q', 'q', 'T', 't'):
                x1 = 2 * cx - last_control[0]
                y1 = 2 * cy - last_control[1]
            else:
                x1, y1 = cx, cy
            x2, y2 = consume_float(), consume_float()
            pts = quadratic_bezier((cx, cy), (x1, y1), (x2, y2), CURVE_SEGMENTS)
            current_points.extend(pts)
            last_control = (x1, y1)
            cx, cy = x2, y2
            last_cmd = 'T'

        elif token == 't':
            if last_control and last_cmd in ('Q', 'q', 'T', 't'):
                x1 = 2 * cx - last_control[0]
                y1 = 2 * cy - last_control[1]
            else:
                x1, y1 = cx, cy
            dx, dy = consume_float(), consume_float()
            x2, y2 = cx + dx, cy + dy
            pts = quadratic_bezier((cx, cy), (x1, y1), (x2, y2), CURVE_SEGMENTS)
            current_points.extend(pts)
            last_control = (x1, y1)
            cx, cy = x2, y2
            last_cmd = 't'

        elif token in ('A', 'a'):
            # Arc: approximate by skipping to endpoint (simple fallback)
            is_rel = (token == 'a')
            _rx = consume_float()
            _ry = consume_float()
            _x_rot = consume_float()
            _large_arc = consume_float()
            _sweep = consume_float()
            ex, ey = consume_float(), consume_float()
            if is_rel:
                cx += ex
                cy += ey
            else:
                cx, cy = ex, ey
            current_points.append((cx, cy))
            last_cmd = token
            last_control = None

        elif token in ('Z', 'z'):
            cx, cy = start_x, start_y
            if current_points:
                subpaths.append(current_points)
                current_points = []
            last_control = None
            last_cmd = token

        else:
            # Unknown command, skip
            i += 1
            last_control = None

    if current_points:
        subpaths.append(current_points)

    return subpaths


def get_fill_color(elem) -> str | None:
    """Extract fill color from element (checks both fill attr and style attr)."""
    # Check style attribute first
    style = elem.get("style", "")
    if style:
        match = re.search(r"fill\s*:\s*(#[0-9a-fA-F]{3,8}|none)", style)
        if match:
            color = match.group(1)
            if color == "none":
                return None
            return color

    # Fall back to fill attribute
    fill = elem.get("fill")
    if fill == "none":
        return None
    return fill


def hex_color_to_int(color_str: str) -> str:
    """Convert #RRGGBB to 0xRRGGBB."""
    color_str = color_str.strip().lstrip("#")
    # Handle shorthand #RGB -> RRGGBB
    if len(color_str) == 3:
        color_str = "".join(c * 2 for c in color_str)
    return f"0x{color_str.upper()}"


def normalize_points(
    points: list[tuple[float, float]], viewbox_width: float, viewbox_height: float
) -> list[tuple[float, float]]:
    """Normalize points from SVG coordinates to 0.0-1.0 range."""
    return [(x / viewbox_width, y / viewbox_height) for x, y in points]


def find_elements(root, tag: str):
    """Find elements with or without SVG namespace."""
    results = list(root.iter(f"{{{SVG_NS}}}{tag}"))
    if not results:
        results = list(root.iter(tag))
    return results


def parse_svg(svg_path: str) -> tuple[list[dict], float, float]:
    """Parse SVG file and extract polygons with colors."""
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # Parse viewBox
    viewbox = root.get("viewBox", "0 0 100 100")
    parts = viewbox.split()
    vb_width = float(parts[2])
    vb_height = float(parts[3])

    polygons = []

    # Process <polygon> elements
    for elem in find_elements(root, "polygon"):
        points_str = elem.get("points", "")
        color = get_fill_color(elem)
        if color is None:
            continue

        points = parse_polygon_points(points_str)
        if points:
            polygons.append({"color": color, "points": points})

    # Process <path> elements
    for elem in find_elements(root, "path"):
        color = get_fill_color(elem)
        if color is None:
            continue

        d = elem.get("d", "")
        if not d:
            continue

        subpaths = parse_path_d(d)
        for points in subpaths:
            if len(points) >= 3:
                polygons.append({"color": color, "points": points})

    # Process <rect> elements
    for elem in find_elements(root, "rect"):
        color = get_fill_color(elem)
        if color is None:
            continue

        x = float(elem.get("x", "0"))
        y = float(elem.get("y", "0"))
        w = float(elem.get("width", "0"))
        h = float(elem.get("height", "0"))
        if w > 0 and h > 0:
            points = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
            polygons.append({"color": color, "points": points})

    return polygons, vb_width, vb_height


def generate_monkey_c(
    module_name: str, polygons: list[dict], vb_width: float, vb_height: float
) -> str:
    """Generate Monkey C source code for the polygon data."""
    lines = [
        "import Toybox.Lang;",
        "import Toybox.Graphics;",
        "",
        f"// Generated by tools/convert_icon.py — do not edit manually",
        f"// Coordinates are normalized 0.0 to 1.0",
        f"module {module_name} {{",
        "    function getPolygons() as Array {",
        "        return [",
    ]

    for i, poly in enumerate(polygons):
        color = hex_color_to_int(poly["color"])
        normalized = normalize_points(poly["points"], vb_width, vb_height)

        lines.append("            {")
        lines.append(f"                :color => {color},")
        lines.append("                :points => [")

        for j, (x, y) in enumerate(normalized):
            comma = "," if j < len(normalized) - 1 else ""
            lines.append(f"                    [{x:.2f}, {y:.2f}]{comma}")

        lines.append("                ]")
        comma = "," if i < len(polygons) - 1 else ""
        lines.append(f"            }}{comma}")

    lines.append("        ];")
    lines.append("    }")
    lines.append("}")
    lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <input.svg> <ModuleName> <output.mc>")
        sys.exit(1)

    svg_path = sys.argv[1]
    module_name = sys.argv[2]
    output_path = sys.argv[3]

    polygons, vb_width, vb_height = parse_svg(svg_path)

    if not polygons:
        print(f"Error: No polygons found in {svg_path}")
        sys.exit(1)

    mc_code = generate_monkey_c(module_name, polygons, vb_width, vb_height)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(mc_code)

    print(f"Generated {output_path} with {len(polygons)} polygons from {svg_path}")


if __name__ == "__main__":
    main()
