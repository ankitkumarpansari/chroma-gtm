"""
Generate Chroma SEO Strategy Diagrams - Clean, Minimal Style
Black & White, no emojis, organic layouts without excessive boxing
"""

import html
from datetime import datetime

# =============================================================================
# MINIMAL SVG HELPERS
# =============================================================================

def svg_start(width: int, height: int, title: str = "Diagram") -> str:
    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <title>{html.escape(title)}</title>
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;display=swap');
      text {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
    </style>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1a1a1a" />
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="#ffffff" />
'''

def svg_end() -> str:
    return "</svg>"

def text(x, y, content, size=14, weight="400", color="#1a1a1a", anchor="start"):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{html.escape(content)}</text>'

def line(x1, y1, x2, y2, color="#1a1a1a", width=1, dashed=False):
    dash = 'stroke-dasharray="4,4"' if dashed else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" {dash}/>'

def arrow(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#1a1a1a" stroke-width="1.5" marker-end="url(#arrow)"/>'

def rect(x, y, w, h, fill="#ffffff", stroke="#1a1a1a", radius=4, stroke_width=1.5):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'

def circle(cx, cy, r, fill="#1a1a1a"):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'

def bullet_point(x, y, content, size=13):
    """Simple bullet point with dot"""
    return circle(x, y - 4, 3) + "\n" + text(x + 12, y, content, size)

def numbered_item(x, y, num, content, size=13):
    """Numbered list item"""
    return text(x, y, f"{num}.", size, "600") + "\n" + text(x + 20, y, content, size)

def save(svg_content: str, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Saved: {filename}")


# =============================================================================
# DIAGRAM 1: Executive Overview (Clean Layout)
# =============================================================================

def create_overview():
    width, height = 900, 700
    parts = [svg_start(width, height, "Chroma SEO Strategy Overview")]
    
    # Title
    parts.append(text(width//2, 45, "Chroma SEO Strategy", 24, "700", anchor="middle"))
    parts.append(text(width//2, 72, "Organic Growth & Category Dominance Plan", 14, "400", "#666666", "middle"))
    parts.append(line(60, 95, width-60, 95, "#e0e0e0", 1))
    
    # Six Goals - Simple numbered list with descriptions
    y = 140
    goals = [
        ("Own 40 high-priority non-branded keywords", "vector database, RAG, retrieval augmented generation, technical terms"),
        ("Achieve category dominance in organic search", "5x organic traffic, top positions, beat Pinecone benchmark"),
        ("Become default citation in AI search experiences", "ChatGPT, Perplexity, LLM-optimized content, retrieval-first"),
        ("Scale through programmatic SEO", "Airtable/Canva model, comparison pages, long-tail templates"),
        ("Capture early attention from technical decision-makers", "Backend engineers, ML practitioners, AI startup founders"),
        ("Drive product signups through organic discovery", "~30% visitor-to-signup, PLG motion, 2026 targets"),
    ]
    
    for i, (title, desc) in enumerate(goals, 1):
        parts.append(text(60, y, f"{i}.", 16, "700"))
        parts.append(text(90, y, title, 16, "600"))
        parts.append(text(90, y + 22, desc, 12, "400", "#666666"))
        y += 70
    
    # Divider
    parts.append(line(60, y + 10, width-60, y + 10, "#e0e0e0", 1))
    
    # Key Metrics - Simple inline
    y += 50
    parts.append(text(60, y, "Key Metrics", 14, "600"))
    y += 30
    metrics = ["40 target keywords", "5x traffic growth", "30% signup rate", "2026 conversion goals"]
    x = 60
    for m in metrics:
        parts.append(circle(x, y - 4, 3))
        parts.append(text(x + 12, y, m, 13))
        x += 200
    
    # North Star callout - simple underlined text
    y += 60
    parts.append(text(60, y, "North Star:", 14, "700"))
    parts.append(text(145, y, "Product signups through organic discovery", 14, "400"))
    parts.append(line(145, y + 4, 480, y + 4, "#1a1a1a", 1))
    
    parts.append(svg_end())
    return "\n".join(parts)


# =============================================================================
# DIAGRAM 2: Keyword Strategy (Mind Map Style)
# =============================================================================

def create_keywords():
    width, height = 900, 550
    parts = [svg_start(width, height, "Keyword Ownership Strategy")]
    
    # Title
    parts.append(text(width//2, 45, "Goal 1: Own 40 High-Priority Keywords", 20, "700", anchor="middle"))
    parts.append(line(60, 75, width-60, 75, "#e0e0e0", 1))
    
    # Central concept
    cx, cy = width//2, 180
    parts.append(rect(cx-100, cy-25, 200, 50, "#f5f5f5"))
    parts.append(text(cx, cy+6, "Keyword Leadership", 14, "600", anchor="middle"))
    
    # Three branches with simple lines and text lists
    branches = [
        (150, 320, "Vector Database Terms", [
            '"vector database"',
            '"what is vector database"',
            '"best vector database"',
            '"vector db comparison"'
        ]),
        (450, 320, "RAG & Retrieval Terms", [
            '"retrieval augmented generation"',
            '"RAG tutorial"',
            '"RAG implementation"',
            '"RAG vs fine-tuning"'
        ]),
        (750, 320, "Technical Terms", [
            '"embedding database"',
            '"semantic search"',
            '"vector similarity"',
            '"AI memory"'
        ]),
    ]
    
    for bx, by, title, items in branches:
        # Connection line
        parts.append(line(cx, cy + 25, bx, by - 50, "#1a1a1a", 1))
        
        # Branch title (underlined)
        parts.append(text(bx, by, title, 14, "600", anchor="middle"))
        parts.append(line(bx - 80, by + 6, bx + 80, by + 6, "#1a1a1a", 1))
        
        # Items as simple list
        iy = by + 35
        for item in items:
            parts.append(text(bx, iy, item, 12, "400", "#333333", "middle"))
            iy += 24
    
    parts.append(svg_end())
    return "\n".join(parts)


# =============================================================================
# DIAGRAM 3: Traffic & Dominance Goals
# =============================================================================

def create_traffic():
    width, height = 900, 500
    parts = [svg_start(width, height, "Category Dominance")]
    
    # Title
    parts.append(text(width//2, 45, "Goal 2: Achieve Category Dominance", 20, "700", anchor="middle"))
    parts.append(text(width//2, 72, "5x Organic Traffic & Top Search Positions", 13, "400", "#666666", "middle"))
    parts.append(line(60, 95, width-60, 95, "#e0e0e0", 1))
    
    # Two columns layout
    col1_x, col2_x = 80, 500
    y = 140
    
    # Left: Current State
    parts.append(text(col1_x, y, "Current Benchmark", 16, "700"))
    parts.append(line(col1_x, y + 6, col1_x + 160, y + 6, "#1a1a1a", 1))
    items = [
        'Pinecone leads "what is vector database"',
        "Competitors have more documentation",
        "Gap in topical authority",
        "Opportunity in technical depth"
    ]
    y += 35
    for item in items:
        parts.append(bullet_point(col1_x, y, item, 13))
        y += 28
    
    # Right: Target
    y = 140
    parts.append(text(col2_x, y, "Target Outcomes", 16, "700"))
    parts.append(line(col2_x, y + 6, col2_x + 145, y + 6, "#1a1a1a", 1))
    items = [
        "5x organic traffic increase",
        "Top 3 positions on key terms",
        "Clear topical authority",
        "Category-wide dominance"
    ]
    y += 35
    for item in items:
        parts.append(bullet_point(col2_x, y, item, 13))
        y += 28
    
    # Arrow between columns
    parts.append(arrow(380, 200, 470, 200))
    
    # Bottom: Success metrics inline
    y = 350
    parts.append(line(60, y - 20, width-60, y - 20, "#e0e0e0", 1))
    parts.append(text(80, y, "Success Metrics:", 14, "600"))
    metrics = ["Organic traffic volume", "Keyword rankings", "SERP features", "Domain authority"]
    x = 230
    for m in metrics:
        parts.append(text(x, y, m, 13, "400", "#333333"))
        x += 170
    
    # Key insight at bottom
    y = 420
    parts.append(text(80, y, "Key Insight:", 13, "600"))
    parts.append(text(175, y, "Pinecone sets the benchmark. Must surpass on core terms to win category.", 13, "400", "#333333"))
    
    parts.append(svg_end())
    return "\n".join(parts)


# =============================================================================
# DIAGRAM 4: AI Search Visibility
# =============================================================================

def create_ai_search():
    width, height = 900, 480
    parts = [svg_start(width, height, "AI Search Citations")]
    
    # Title
    parts.append(text(width//2, 45, "Goal 3: Default Citation in AI Search", 20, "700", anchor="middle"))
    parts.append(text(width//2, 72, "Surface as preferred answer in ChatGPT, Perplexity & LLM platforms", 13, "400", "#666666", "middle"))
    parts.append(line(60, 95, width-60, 95, "#e0e0e0", 1))
    
    # Flow: Content Structure -> Index -> Retrieve -> Cite
    flow_y = 160
    steps = ["Structure Content", "Get Indexed", "LLM Retrieves", "Get Cited"]
    step_x = 120
    for i, step in enumerate(steps):
        parts.append(rect(step_x - 70, flow_y - 20, 140, 40, "#f5f5f5"))
        parts.append(text(step_x, flow_y + 5, step, 13, "500", anchor="middle"))
        if i < len(steps) - 1:
            parts.append(arrow(step_x + 70, flow_y, step_x + 130, flow_y))
        step_x += 200
    
    # Three columns below
    y = 250
    cols = [
        (100, "Target Platforms", ["ChatGPT / OpenAI", "Perplexity AI", "Google AI Overviews", "Claude / Anthropic"]),
        (380, "Query Types", ["Vector database questions", "RAG implementation", "Developer workflows", "Technical comparisons"]),
        (660, "Content Strategy", ["Retrieval-first structure", "Clear factual answers", "Structured data markup", "Authoritative citations"]),
    ]
    
    for cx, title, items in cols:
        parts.append(text(cx, y, title, 14, "600"))
        parts.append(line(cx, y + 6, cx + len(title) * 8, y + 6, "#1a1a1a", 1))
        iy = y + 35
        for item in items:
            parts.append(bullet_point(cx, iy, item, 12))
            iy += 26
    
    parts.append(svg_end())
    return "\n".join(parts)


# =============================================================================
# DIAGRAM 5: Programmatic SEO
# =============================================================================

def create_programmatic():
    width, height = 900, 520
    parts = [svg_start(width, height, "Programmatic SEO")]
    
    # Title
    parts.append(text(width//2, 45, "Goal 4: Scale Through Programmatic SEO", 20, "700", anchor="middle"))
    parts.append(text(width//2, 72, "Modeled on Airtable & Canva success", 13, "400", "#666666", "middle"))
    parts.append(line(60, 95, width-60, 95, "#e0e0e0", 1))
    
    # Central box
    parts.append(rect(width//2 - 120, 120, 240, 45, "#f5f5f5"))
    parts.append(text(width//2, 148, "Programmatic SEO Engine", 14, "600", anchor="middle"))
    
    # Four branches below - simpler layout
    y = 220
    branches = [
        ("Long-tail Templates", ["Template-based pages", "Scalable system", "Automated generation"]),
        ("Comparison Pages", ['"pinecone alternative"', '"qdrant vs chroma"', "Feature comparisons"]),
        ("Use Case Pages", ["RAG applications", "LLM app tutorials", "Semantic search"]),
        ("Integration Pages", ["LangChain + Chroma", "LlamaIndex + Chroma", "OpenAI + Chroma"]),
    ]
    
    spacing = width // (len(branches) + 1)
    for i, (title, items) in enumerate(branches):
        bx = spacing * (i + 1)
        
        # Line from center
        parts.append(line(width//2, 165, bx, y - 30, "#1a1a1a", 1))
        
        # Title
        parts.append(text(bx, y, title, 13, "600", anchor="middle"))
        parts.append(line(bx - 70, y + 6, bx + 70, y + 6, "#1a1a1a", 1))
        
        # Items
        iy = y + 35
        for item in items:
            parts.append(text(bx, iy, item, 11, "400", "#333333", "middle"))
            iy += 22
    
    # Bottom note
    y = 440
    parts.append(line(60, y - 20, width-60, y - 20, "#e0e0e0", 1))
    parts.append(text(80, y, "Execution:", 13, "600"))
    parts.append(text(160, y, "Build templates -> Generate at scale -> Optimize based on performance -> Iterate", 13, "400", "#333333"))
    
    parts.append(svg_end())
    return "\n".join(parts)


# =============================================================================
# DIAGRAM 6: Target Audience
# =============================================================================

def create_audience():
    width, height = 900, 480
    parts = [svg_start(width, height, "Target Audience")]
    
    # Title
    parts.append(text(width//2, 45, "Goal 5: Capture Technical Decision-Makers", 20, "700", anchor="middle"))
    parts.append(text(width//2, 72, "Reach recently funded AI startups with no-fluff content", 13, "400", "#666666", "middle"))
    parts.append(line(60, 95, width-60, 95, "#e0e0e0", 1))
    
    # Two main sections side by side
    y = 140
    
    # Left: Who
    parts.append(text(80, y, "Who", 18, "700"))
    y += 40
    
    parts.append(text(80, y, "Primary Roles", 14, "600"))
    parts.append(line(80, y + 6, 175, y + 6, "#1a1a1a", 1))
    roles = ["Backend engineers", "ML practitioners", "Technical founders", "AI/ML team leads"]
    y += 30
    for role in roles:
        parts.append(bullet_point(80, y, role, 13))
        y += 26
    
    y += 20
    parts.append(text(80, y, "Target Companies", 14, "600"))
    parts.append(line(80, y + 6, 200, y + 6, "#1a1a1a", 1))
    companies = ["Recently funded AI startups", "Series A-C companies", "AI-native organizations"]
    y += 30
    for c in companies:
        parts.append(bullet_point(80, y, c, 13))
        y += 26
    
    # Right: What content
    y = 140
    parts.append(text(500, y, "What Content", 18, "700"))
    y += 40
    
    parts.append(text(500, y, "Topics", 14, "600"))
    parts.append(line(500, y + 6, 555, y + 6, "#1a1a1a", 1))
    topics = ["RAG implementation", "LLM application building", "Semantic search setup", "Production deployment"]
    y += 30
    for t in topics:
        parts.append(bullet_point(500, y, t, 13))
        y += 26
    
    y += 20
    parts.append(text(500, y, "Style", 14, "600"))
    parts.append(line(500, y + 6, 540, y + 6, "#1a1a1a", 1))
    style = ["Deeply technical", "No marketing fluff", "Code-first examples", "Real-world use cases"]
    y += 30
    for s in style:
        parts.append(bullet_point(500, y, s, 13))
        y += 26
    
    # Bottom insight
    parts.append(line(60, 420, width-60, 420, "#e0e0e0", 1))
    parts.append(text(80, 450, "Strategic insight:", 13, "600"))
    parts.append(text(200, 450, "Long vendor lock-in cycles mean early attention is critical for adoption.", 13, "400", "#333333"))
    
    parts.append(svg_end())
    return "\n".join(parts)


# =============================================================================
# DIAGRAM 7: Conversion & PLG
# =============================================================================

def create_conversion():
    width, height = 900, 450
    parts = [svg_start(width, height, "Conversion Strategy")]
    
    # Title
    parts.append(text(width//2, 45, "Goal 6: Drive Signups Through Organic", 20, "700", anchor="middle"))
    parts.append(text(width//2, 72, "Optimize for conversion with PLG motion", 13, "400", "#666666", "middle"))
    parts.append(line(60, 95, width-60, 95, "#e0e0e0", 1))
    
    # Funnel visualization - simple horizontal flow
    y = 160
    parts.append(text(80, y, "Organic Funnel", 14, "600"))
    parts.append(line(80, y + 6, 175, y + 6, "#1a1a1a", 1))
    
    y += 50
    funnel = ["Discover", "Read Content", "Try Product", "Sign Up", "Convert"]
    x = 100
    for i, step in enumerate(funnel):
        parts.append(text(x, y, step, 13, "500"))
        if i < len(funnel) - 1:
            parts.append(arrow(x + len(step) * 7 + 10, y - 5, x + len(step) * 7 + 50, y - 5))
        x += 150
    
    # Key numbers
    y += 60
    parts.append(line(60, y - 15, width-60, y - 15, "#e0e0e0", 1))
    
    parts.append(text(100, y + 20, "30%", 36, "700"))
    parts.append(text(100, y + 45, "visitor-to-signup", 12, "400", "#666666"))
    
    parts.append(text(300, y + 20, "PLG", 36, "700"))
    parts.append(text(300, y + 45, "motion type", 12, "400", "#666666"))
    
    parts.append(text(480, y + 20, "2026", 36, "700"))
    parts.append(text(480, y + 45, "target year", 12, "400", "#666666"))
    
    # Optimization focus
    y += 100
    parts.append(text(80, y, "Optimization Focus", 14, "600"))
    items = ["Traffic quality over quantity", "High-intent keywords", "Conversion path optimization", "Signup friction reduction"]
    x = 250
    for item in items:
        parts.append(bullet_point(x, y, item, 12))
        x += 180
    
    # North star
    y += 50
    parts.append(line(60, y - 10, width-60, y - 10, "#e0e0e0", 1))
    parts.append(text(80, y + 20, "True North Star:", 14, "700"))
    parts.append(text(210, y + 20, "Rankings are the KPI, but CONVERSION is what matters.", 14, "400"))
    
    parts.append(svg_end())
    return "\n".join(parts)


# =============================================================================
# DIAGRAM 8: Competitive Landscape
# =============================================================================

def create_competitive():
    width, height = 900, 480
    parts = [svg_start(width, height, "Competitive Landscape")]
    
    # Title
    parts.append(text(width//2, 45, "Competitive SEO Landscape", 20, "700", anchor="middle"))
    parts.append(line(60, 75, width-60, 75, "#e0e0e0", 1))
    
    # Two columns with VS in middle
    y = 120
    
    # Left: Chroma
    parts.append(text(180, y, "Chroma Opportunities", 16, "700", anchor="middle"))
    parts.append(line(80, y + 6, 280, y + 6, "#1a1a1a", 1))
    items = [
        "Open-source credibility",
        "Developer community (25k stars)",
        "AI-native positioning",
        "Technical content depth",
        "Programmatic SEO potential"
    ]
    iy = y + 40
    for item in items:
        parts.append(bullet_point(80, iy, item, 13))
        iy += 30
    
    # VS
    parts.append(text(width//2, 220, "vs", 20, "700", "#999999", "middle"))
    
    # Right: Competitors
    parts.append(text(720, y, "Competitor Advantages", 16, "700", anchor="middle"))
    parts.append(line(600, y + 6, 840, y + 6, "#1a1a1a", 1))
    items = [
        'Pinecone: "vector database" leader',
        "More documentation coverage",
        "Larger content teams",
        "Enterprise SEO investment",
        "Established domain authority"
    ]
    iy = y + 40
    for item in items:
        parts.append(bullet_point(600, iy, item, 13))
        iy += 30
    
    # Common ground at bottom
    y = 360
    parts.append(line(60, y - 20, width-60, y - 20, "#e0e0e0", 1))
    parts.append(text(width//2, y, "Common Ground", 14, "600", anchor="middle"))
    common = ["Vector search category", "Developer audience", "Technical content", "AI/LLM focus"]
    x = 150
    for c in common:
        parts.append(text(x, y + 35, c, 12, "400", "#666666"))
        x += 180
    
    parts.append(svg_end())
    return "\n".join(parts)


# =============================================================================
# DIAGRAM 9: Implementation Roadmap
# =============================================================================

def create_roadmap():
    width, height = 1000, 300
    parts = [svg_start(width, height, "Implementation Roadmap")]
    
    # Title
    parts.append(text(width//2, 45, "SEO Strategy Roadmap", 20, "700", anchor="middle"))
    
    # Timeline
    line_y = 150
    parts.append(line(80, line_y, width - 80, line_y, "#1a1a1a", 2))
    
    # Milestones
    milestones = [
        ("Q1 2025", "Keyword Research\n& Content Audit"),
        ("Q2 2025", "Programmatic\nSEO Setup"),
        ("Q3 2025", "Scale Content\nProduction"),
        ("Q4 2025", "AI Search\nOptimization"),
        ("2026", "Conversion\nGoals"),
    ]
    
    spacing = (width - 160) // (len(milestones) - 1)
    for i, (date, label) in enumerate(milestones):
        x = 80 + i * spacing
        
        # Dot
        parts.append(circle(x, line_y, 8, "#1a1a1a"))
        parts.append(circle(x, line_y, 5, "#ffffff"))
        
        # Date below
        parts.append(text(x, line_y + 30, date, 12, "600", anchor="middle"))
        
        # Label above (handle newlines)
        lines = label.split("\n")
        ly = line_y - 25 - (len(lines) - 1) * 16
        for l in lines:
            parts.append(text(x, ly, l, 11, "400", "#333333", "middle"))
            ly += 16
    
    parts.append(svg_end())
    return "\n".join(parts)


# =============================================================================
# DIAGRAM 10: Summary
# =============================================================================

def create_summary():
    width, height = 900, 550
    parts = [svg_start(width, height, "Strategy Summary")]
    
    # Title
    parts.append(text(width//2, 45, "Chroma SEO Strategy Summary", 22, "700", anchor="middle"))
    parts.append(line(60, 75, width-60, 75, "#e0e0e0", 1))
    
    # Four phase flow
    y = 120
    parts.append(text(80, y, "Strategy Flow", 14, "600"))
    
    phases = [
        ("Foundation", ["40 priority keywords", "Category authority", "Technical credibility"]),
        ("Execution", ["Programmatic SEO", "Comparison pages", "Use case content"]),
        ("Distribution", ["Organic search", "AI search citations", "Developer discovery"]),
        ("Outcomes", ["5x traffic growth", "30% signup rate", "Category dominance"]),
    ]
    
    y += 40
    px = 100
    for i, (phase, items) in enumerate(phases):
        # Phase title
        parts.append(text(px, y, phase, 14, "700"))
        parts.append(line(px, y + 6, px + len(phase) * 9, y + 6, "#1a1a1a", 1))
        
        # Items
        iy = y + 30
        for item in items:
            parts.append(text(px, iy, item, 12, "400", "#333333"))
            iy += 22
        
        # Arrow to next
        if i < len(phases) - 1:
            parts.append(arrow(px + 140, y + 50, px + 170, y + 50))
        
        px += 200
    
    # Key takeaways
    y = 320
    parts.append(line(60, y - 20, width-60, y - 20, "#e0e0e0", 1))
    parts.append(text(80, y, "Key Takeaways", 16, "700"))
    
    takeaways = [
        "Strategy designed for dev-tools product with PLG motion",
        "Focus on technical decision-makers at AI startups",
        "Modeled on Airtable/Canva programmatic SEO success",
        "Rankings are KPI, but conversion is the true north star",
        "Early attention critical due to long vendor lock-in cycles"
    ]
    
    y += 35
    for t in takeaways:
        parts.append(numbered_item(80, y, takeaways.index(t) + 1, t, 13))
        y += 30
    
    parts.append(svg_end())
    return "\n".join(parts)


# =============================================================================
# GENERATE ALL DIAGRAMS
# =============================================================================

if __name__ == "__main__":
    diagrams = [
        (create_overview, "chroma_seo_1_overview.svg"),
        (create_keywords, "chroma_seo_2_keywords.svg"),
        (create_traffic, "chroma_seo_3_traffic.svg"),
        (create_ai_search, "chroma_seo_4_ai_search.svg"),
        (create_programmatic, "chroma_seo_5_programmatic.svg"),
        (create_audience, "chroma_seo_6_audience.svg"),
        (create_conversion, "chroma_seo_7_conversion.svg"),
        (create_competitive, "chroma_seo_8_competitive.svg"),
        (create_roadmap, "chroma_seo_9_roadmap.svg"),
        (create_summary, "chroma_seo_10_summary.svg"),
    ]
    
    print("\n" + "=" * 60)
    print("Generating Chroma SEO Strategy Diagrams (Clean Style)")
    print("=" * 60 + "\n")
    
    for func, filename in diagrams:
        svg = func()
        save(svg, filename)
    
    print("\n" + "=" * 60)
    print("10 SVG files created with minimal, clean layouts")
    print("=" * 60 + "\n")
