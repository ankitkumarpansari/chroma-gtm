"""
SVG Diagram Generator - Karpathy/Excalidraw Style
=================================================
Generate beautiful, shareable SVG diagrams from any information.

Usage: Just paste your content in the chat and describe what you want!
"""

import html
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from datetime import datetime
import textwrap

# ============================================================================
# EXCALIDRAW COLOR PALETTE
# ============================================================================

COLORS = {
    # Main section colors (pastel fills)
    "yellow": "#fff9db",      # Inputs, data sources, starting points
    "purple": "#d0bfff",      # Active/push processes
    "green": "#b2f2bb",       # Passive/pull processes
    "blue": "#a5d8ff",        # Features, capabilities, attributes
    "pink": "#fcc2d7",        # People, roles, personas
    "orange": "#ffd8a8",      # Outputs, results
    "gray": "#f8f9fa",        # Supporting info, tools
    "white": "#ffffff",       # Background, nested boxes
    "light_gray": "#e9ecef",  # Subtle backgrounds
    
    # Text and lines
    "text": "#1a1a1a",
    "text_secondary": "#555555",
    "text_muted": "#777777",
    "stroke": "#1a1a1a",
    
    # Special
    "insight_border": "#ff922b",  # Orange dashed for key insights
    "tag_bg": "#343a40",          # Dark pills for tags
    "tag_text": "#ffffff",
    "accent": "#228be6",          # Blue accent
}

# ============================================================================
# SVG PRIMITIVES
# ============================================================================

def svg_header(width: int, height: int, title: str = "Diagram") -> str:
    """Generate SVG header."""
    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <title>{html.escape(title)}</title>
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;display=swap');
      text {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="{COLORS['stroke']}" />
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="{COLORS['white']}" />
'''

def svg_footer() -> str:
    return "</svg>"

def text_element(x: int, y: int, content: str, size: int = 12, 
                 weight: str = "400", color: str = None, anchor: str = "start") -> str:
    """Create a text element."""
    fill = color or COLORS["text"]
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{html.escape(content)}</text>'

def rect_element(x: int, y: int, w: int, h: int, fill: str = "white",
                 stroke: str = None, stroke_width: float = 1.5, 
                 radius: int = 4, dashed: bool = False) -> str:
    """Create a rectangle element."""
    stroke_attr = f'stroke="{stroke}" stroke-width="{stroke_width}"' if stroke else ""
    dash_attr = 'stroke-dasharray="6,3"' if dashed else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" {stroke_attr} {dash_attr}/>'

def line_element(x1: int, y1: int, x2: int, y2: int, 
                 stroke: str = None, width: float = 1) -> str:
    """Create a line element."""
    stroke_color = stroke or COLORS["stroke"]
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke_color}" stroke-width="{width}"/>'

def arrow_line(x1: int, y1: int, x2: int, y2: int) -> str:
    """Create a line with arrow."""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{COLORS["stroke"]}" stroke-width="1.5" marker-end="url(#arrowhead)"/>'

def path_element(d: str, stroke: str = None, fill: str = "none", 
                 width: float = 1.5, arrow: bool = False) -> str:
    """Create a path element."""
    stroke_color = stroke or COLORS["stroke"]
    marker = 'marker-end="url(#arrowhead)"' if arrow else ""
    return f'<path d="{d}" stroke="{stroke_color}" stroke-width="{width}" fill="{fill}" {marker}/>'

# ============================================================================
# COMPONENT BUILDERS
# ============================================================================

def build_section_box(x: int, y: int, w: int, title: str, 
                      items: List[str], color: str = "gray") -> Tuple[str, int]:
    """Build a colored section box with nested items. Returns SVG and height."""
    fill = COLORS.get(color, color)
    parts = []
    
    # Calculate height
    item_height = 32
    padding = 12
    title_height = 30
    h = title_height + len(items) * item_height + padding * 2
    
    # Outer box
    parts.append(rect_element(x, y, w, h, fill, COLORS["stroke"], 1.5, 6))
    
    # Title
    parts.append(text_element(x + padding, y + 22, title, 14, "600"))
    
    # Items as nested white boxes
    item_y = y + title_height + 8
    for item in items:
        parts.append(rect_element(x + 8, item_y, w - 16, item_height - 4, COLORS["white"], COLORS["stroke"], 1, 4))
        parts.append(text_element(x + 18, item_y + 20, item, 12, "400"))
        item_y += item_height
    
    return "\n".join(parts), h

def build_flow_step(x: int, y: int, w: int, h: int, 
                    label: str, color: str = "gray") -> str:
    """Build a single flow step box."""
    fill = COLORS.get(color, color)
    parts = []
    parts.append(rect_element(x, y, w, h, fill, COLORS["stroke"], 1.5, 6))
    parts.append(text_element(x + w//2, y + h//2 + 5, label, 13, "500", anchor="middle"))
    return "\n".join(parts)

def build_metric_box(x: int, y: int, value: str, label: str, 
                     w: int = 100, h: int = 70) -> str:
    """Build a metric display."""
    parts = []
    parts.append(rect_element(x, y, w, h, COLORS["white"], COLORS["stroke"], 1.5, 6))
    parts.append(text_element(x + w//2, y + 32, value, 22, "700", anchor="middle"))
    parts.append(text_element(x + w//2, y + 52, label, 10, "500", COLORS["text_secondary"], "middle"))
    return "\n".join(parts)

def build_insight_box(x: int, y: int, w: int, title: str, 
                      content: List[str]) -> Tuple[str, int]:
    """Build an insight box with orange dashed border."""
    parts = []
    h = 35 + len(content) * 18 + 15
    
    parts.append(rect_element(x, y, w, h, COLORS["white"], COLORS["insight_border"], 2, 6, True))
    parts.append(text_element(x + 12, y + 24, title, 13, "600"))
    
    content_y = y + 48
    for line in content:
        parts.append(text_element(x + 12, content_y, line, 11, "400", COLORS["text_secondary"]))
        content_y += 18
    
    return "\n".join(parts), h

def build_tag(x: int, y: int, label: str, bg_color: str = None) -> str:
    """Build a small pill/tag."""
    bg = bg_color or COLORS["tag_bg"]
    w = len(label) * 7 + 16
    h = 20
    parts = []
    parts.append(rect_element(x, y, w, h, bg, radius=10))
    parts.append(text_element(x + w//2, y + 14, label, 10, "600", COLORS["tag_text"], "middle"))
    return "\n".join(parts)

# ============================================================================
# DIAGRAM GENERATORS
# ============================================================================

def generate_info_diagram(
    title: str,
    subtitle: str = None,
    sections: List[Dict] = None,  # [{"title": str, "color": str, "items": [str]}]
    flow: List[Dict] = None,      # [{"label": str, "color": str}]
    metrics: List[Dict] = None,   # [{"value": str, "label": str}]
    insight: Dict = None,         # {"title": str, "content": [str]}
    notes: List[str] = None,
    tags: List[str] = None,
) -> str:
    """
    Generate a comprehensive information diagram.
    
    This is the main function - it intelligently lays out all the components.
    """
    # Calculate dimensions
    sections = sections or []
    flow = flow or []
    metrics = metrics or []
    
    # Layout calculations
    margin = 40
    section_gap = 20
    
    # Estimate width based on content
    num_sections = len(sections)
    section_width = 240
    min_width = max(900, num_sections * (section_width + section_gap) + margin * 2)
    width = min_width
    
    # Start building SVG
    parts = []
    current_y = margin
    
    # Title
    parts.append(text_element(width // 2, current_y + 5, title, 18, "700", anchor="middle"))
    current_y += 25
    
    if subtitle:
        parts.append(text_element(width // 2, current_y + 5, subtitle, 12, "400", COLORS["text_secondary"], "middle"))
        current_y += 25
    
    # Horizontal line under title
    parts.append(line_element(margin, current_y, width - margin, current_y, COLORS["light_gray"], 1))
    current_y += 25
    
    # Sections row
    if sections:
        section_x = margin
        available_width = width - margin * 2
        actual_section_width = (available_width - (len(sections) - 1) * section_gap) // len(sections)
        
        max_section_height = 0
        for section in sections:
            svg, h = build_section_box(
                section_x, current_y, actual_section_width,
                section["title"], section.get("items", []), section.get("color", "gray")
            )
            parts.append(svg)
            max_section_height = max(max_section_height, h)
            section_x += actual_section_width + section_gap
        
        current_y += max_section_height + 30
    
    # Flow diagram
    if flow:
        step_width = 130
        step_height = 45
        step_gap = 45
        total_flow_width = len(flow) * step_width + (len(flow) - 1) * step_gap
        flow_x = (width - total_flow_width) // 2
        
        for i, step in enumerate(flow):
            parts.append(build_flow_step(
                flow_x, current_y, step_width, step_height,
                step["label"], step.get("color", "gray")
            ))
            
            # Arrow to next
            if i < len(flow) - 1:
                parts.append(arrow_line(
                    flow_x + step_width, current_y + step_height // 2,
                    flow_x + step_width + step_gap, current_y + step_height // 2
                ))
            
            flow_x += step_width + step_gap
        
        current_y += step_height + 35
    
    # Bottom row: metrics + insight
    if metrics or insight:
        # Metrics on left
        if metrics:
            metric_x = margin
            for metric in metrics:
                parts.append(build_metric_box(metric_x, current_y, metric["value"], metric["label"]))
                metric_x += 115
        
        # Insight on right
        if insight:
            insight_width = 340
            svg, h = build_insight_box(
                width - margin - insight_width, current_y, insight_width,
                insight["title"], insight.get("content", [])
            )
            parts.append(svg)
        
        current_y += 85
    
    # Notes
    if notes:
        current_y += 10
        parts.append(line_element(margin, current_y - 5, width - margin, current_y - 5, COLORS["light_gray"], 1))
        for note in notes:
            parts.append(text_element(margin, current_y + 15, note, 10, "400", COLORS["text_muted"]))
            current_y += 16
        current_y += 10
    
    # Tags
    if tags:
        tag_x = margin
        for tag in tags:
            parts.append(build_tag(tag_x, current_y, tag))
            tag_x += len(tag) * 7 + 26
    
    # Final height
    height = current_y + margin
    
    # Assemble SVG
    return svg_header(width, height, title) + "\n".join(parts) + "\n" + svg_footer()


def generate_comparison_diagram(
    title: str,
    left: Dict,   # {"title": str, "color": str, "items": [str]}
    right: Dict,  # {"title": str, "color": str, "items": [str]}
    shared: List[str] = None,
) -> str:
    """Generate a comparison/versus diagram."""
    width = 900
    margin = 40
    col_width = 340
    
    parts = []
    current_y = margin
    
    # Title
    parts.append(text_element(width // 2, current_y + 5, title, 18, "700", anchor="middle"))
    current_y += 40
    
    # VS indicator
    parts.append(text_element(width // 2, current_y + 100, "VS", 16, "700", COLORS["text_muted"], "middle"))
    
    # Left column
    left_svg, left_h = build_section_box(
        margin, current_y, col_width,
        left["title"], left.get("items", []), left.get("color", "blue")
    )
    parts.append(left_svg)
    
    # Right column
    right_svg, right_h = build_section_box(
        width - margin - col_width, current_y, col_width,
        right["title"], right.get("items", []), right.get("color", "orange")
    )
    parts.append(right_svg)
    
    current_y += max(left_h, right_h) + 30
    
    # Shared items
    if shared:
        shared_svg, shared_h = build_section_box(
            (width - 300) // 2, current_y, 300,
            "Shared / Common", shared, "gray"
        )
        parts.append(shared_svg)
        current_y += shared_h + 20
    
    height = current_y + margin
    return svg_header(width, height, title) + "\n".join(parts) + "\n" + svg_footer()


def generate_timeline_diagram(
    title: str,
    events: List[Dict],  # [{"date": str, "title": str, "color": str}]
) -> str:
    """Generate a timeline diagram."""
    width = 1000
    margin = 60
    
    parts = []
    current_y = margin
    
    # Title
    parts.append(text_element(width // 2, current_y + 5, title, 18, "700", anchor="middle"))
    current_y += 60
    
    # Timeline line
    line_y = current_y + 60
    parts.append(line_element(margin, line_y, width - margin, line_y, COLORS["stroke"], 2))
    
    # Events
    if events:
        spacing = (width - margin * 2) // (len(events) + 1)
        
        for i, event in enumerate(events):
            event_x = margin + (i + 1) * spacing
            color = COLORS.get(event.get("color", "blue"), COLORS["blue"])
            
            # Dot
            parts.append(f'<circle cx="{event_x}" cy="{line_y}" r="8" fill="{color}" stroke="{COLORS["stroke"]}" stroke-width="2"/>')
            
            # Alternating above/below
            if i % 2 == 0:
                parts.append(line_element(event_x, line_y - 8, event_x, line_y - 25))
                parts.append(text_element(event_x, line_y - 45, event["title"], 12, "500", anchor="middle"))
                parts.append(text_element(event_x, line_y - 30, event.get("date", ""), 10, "400", COLORS["text_muted"], "middle"))
            else:
                parts.append(line_element(event_x, line_y + 8, event_x, line_y + 25))
                parts.append(text_element(event_x, line_y + 45, event["title"], 12, "500", anchor="middle"))
                parts.append(text_element(event_x, line_y + 60, event.get("date", ""), 10, "400", COLORS["text_muted"], "middle"))
    
    height = current_y + 150
    return svg_header(width, height, title) + "\n".join(parts) + "\n" + svg_footer()


def generate_hierarchy_diagram(
    title: str,
    root: str,
    children: List[Dict],  # [{"label": str, "color": str, "items": [str]}]
) -> str:
    """Generate a hierarchy/tree diagram."""
    margin = 40
    child_width = 200
    child_gap = 25
    
    num_children = len(children)
    width = max(800, num_children * (child_width + child_gap) + margin * 2)
    
    parts = []
    current_y = margin
    
    # Title
    parts.append(text_element(width // 2, current_y + 5, title, 18, "700", anchor="middle"))
    current_y += 50
    
    # Root node
    root_w, root_h = 220, 50
    root_x = (width - root_w) // 2
    parts.append(build_flow_step(root_x, current_y, root_w, root_h, root, "purple"))
    
    root_bottom = current_y + root_h
    current_y += root_h + 60
    
    # Children
    if children:
        child_start_x = (width - (num_children * child_width + (num_children - 1) * child_gap)) // 2
        
        max_child_h = 0
        for i, child in enumerate(children):
            child_x = child_start_x + i * (child_width + child_gap)
            child_center = child_x + child_width // 2
            
            # Connection line
            parts.append(path_element(
                f"M {width // 2} {root_bottom} L {width // 2} {root_bottom + 25} L {child_center} {root_bottom + 25} L {child_center} {current_y}",
                arrow=True
            ))
            
            # Child box
            svg, h = build_section_box(
                child_x, current_y, child_width,
                child["label"], child.get("items", []), child.get("color", "blue")
            )
            parts.append(svg)
            max_child_h = max(max_child_h, h)
        
        current_y += max_child_h + 20
    
    height = current_y + margin
    return svg_header(width, height, title) + "\n".join(parts) + "\n" + svg_footer()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def save_svg(svg_content: str, filename: str = None) -> str:
    """Save SVG to file."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"diagram_{timestamp}.svg"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"✅ Saved: {filename}")
    return filename


def demo():
    """Generate demo diagrams."""
    
    # Demo 1: Process Flow
    svg1 = generate_info_diagram(
        title="Chroma GTM Strategy Overview",
        subtitle="Data Layer & Customer Acquisition Pipeline",
        sections=[
            {
                "title": "📥 Data Sources",
                "color": "yellow",
                "items": ["Chroma Database", "PostHog Events", "Signal List"]
            },
            {
                "title": "⚡ Enrichment",
                "color": "purple", 
                "items": ["Sumble", "Clay", "Claude AI"]
            },
            {
                "title": "🎯 Outreach",
                "color": "green",
                "items": ["LinkedIn ABM", "Email Sequences", "Content"]
            },
            {
                "title": "📊 Outcomes",
                "color": "orange",
                "items": ["SQLs", "Cloud Signups", "Deals"]
            }
        ],
        flow=[
            {"label": "Discover", "color": "yellow"},
            {"label": "Enrich", "color": "purple"},
            {"label": "Qualify", "color": "blue"},
            {"label": "Engage", "color": "green"},
            {"label": "Convert", "color": "orange"}
        ],
        metrics=[
            {"value": "2,000", "label": "Target Companies"},
            {"value": "$5-10k", "label": "Monthly Budget"},
            {"value": "25k", "label": "GitHub Stars"}
        ],
        insight={
            "title": "Key Insight",
            "content": [
                "Using Chroma Database for prospect list",
                "Product events tracked in PostHog",
                "Sumble, Clay & Claude for expansion"
            ]
        },
        tags=["#data-layer", "#gtm", "#abm"]
    )
    save_svg(svg1, "demo_process_flow.svg")
    
    # Demo 2: Comparison
    svg2 = generate_comparison_diagram(
        title="Chroma vs Competitors",
        left={
            "title": "✅ Chroma Strengths",
            "color": "green",
            "items": ["Open-source first", "25k GitHub stars", "Easy integration", "AI-native"]
        },
        right={
            "title": "⚠️ Competitor Features",
            "color": "orange",
            "items": ["Enterprise support", "Managed hosting", "More docs", "Larger teams"]
        },
        shared=["Vector search", "Python SDK", "Cloud offering"]
    )
    save_svg(svg2, "demo_comparison.svg")
    
    print("\n🎨 Demo diagrams generated!")
    print("   - demo_process_flow.svg")
    print("   - demo_comparison.svg\n")


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════╗
║         SVG Diagram Generator - Karpathy/Excalidraw Style     ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Just paste your content in the chat and I'll generate        ║
║  a beautiful SVG diagram for you!                             ║
║                                                               ║
║  Diagram Types:                                               ║
║    • Process Flow  - For pipelines, workflows, GTM            ║
║    • Comparison    - For vs analysis, before/after            ║
║    • Timeline      - For roadmaps, milestones                 ║
║    • Hierarchy     - For org charts, feature trees            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    demo()
