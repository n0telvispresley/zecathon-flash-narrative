import io
import textwrap
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.colors import navy, black, gray, HexColor
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter

# Import your new demo loader
try:
    from .. import demo_loader
except ImportError:
    import demo_loader # Fallback for local run

# --- Helper to create sentiment pie chart ---
def _create_sentiment_pie(sentiment_ratio):
    """Creates a doughnut chart for sentiment and returns as image bytes."""
    labels, sizes, colors = [], [], []
    color_map = {
        'positive': '#28a745', 'appreciation': '#007bff', 'neutral': '#6c757d',
        'mixed': '#ffc107', 'negative': '#dc3545', 'anger': '#8b0000'
    }
    sentiment_order = ['positive', 'appreciation', 'neutral', 'mixed', 'negative', 'anger']
    
    for tone in sentiment_order:
        val = float(sentiment_ratio.get(tone, 0))
        if val > 0.1: # Threshold to avoid tiny slices
            labels.append(f"{tone.capitalize()} ({val:.1f}%)")
            sizes.append(val)
            colors.append(color_map.get(tone, 'grey'))
            
    if not sizes:
        labels = ['Neutral (100.0%)']; sizes = [100.0]; colors = ['grey']

    # --- Use Matplotlib to create the chart ---
    plt.style.use('dark_background') # Use dark theme for the chart
    fig, ax = plt.subplots(figsize=(4, 4))
    
    # Create the doughnut chart
    wedges, texts, autotexts = ax.pie(
        sizes, 
        colors=colors, 
        autopct='%1.1f%%', 
        startangle=90, 
        pctdistance=0.85, 
        wedgeprops=dict(width=0.4, edgecolor='#1E1E1E') # Match bg
    )
    
    plt.setp(autotexts, size=8, weight="bold", color="white")
    ax.axis('equal')
    
    # --- Save chart to a bytes buffer ---
    buf = io.BytesIO()
    fig.patch.set_facecolor('#1E1E1E') # Match dashboard dark background
    plt.tight_layout()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', transparent=True)
    plt.close(fig)
    plt.style.use('default') # Reset style
    buf.seek(0)
    return buf

# --- Helper to create SOV bar chart ---
def _create_sov_bar_chart(all_brands, sov_values):
    """Creates a horizontal bar chart for SOV and returns as image bytes."""
    if not all_brands or not sov_values: return None
    try:
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(6, max(3, len(all_brands) * 0.5))) # Dynamic height
        df = pd.DataFrame({'Brand': all_brands, 'SOV': sov_values}).sort_values(by='SOV', ascending=True)
        bars = ax.barh(df['Brand'], df['SOV'], color='#FFD700') # Gold bars
        ax.set_title("Share of Voice (SOV)", color='white', fontsize=12, fontweight='bold')
        ax.set_xlabel('SOV (%)', color='#F5F5DC')
        ax.tick_params(axis='y', colors='#F5F5DC'); ax.tick_params(axis='x', colors='#F5F5DC')
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#F5F5DC'); ax.spines['bottom'].set_color('#F5F5DC')
        for bar in bars:
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{bar.get_width():.1f}%', va='center', ha='left', color='white', fontsize=9)
        fig.patch.set_facecolor('#1E1E1E'); ax.set_facecolor('#1E1E1E')
        buf = io.BytesIO()
        plt.tight_layout(); fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', transparent=True); plt.close(fig)
        plt.style.use('default')
        return buf
    except Exception as e:
        print(f"Error creating SOV bar chart: {e}"); plt.style.use('default'); return None

# --- Helper function to draw a section of mentions ---
def _draw_mention_section(c, y, title, mentions, width, margin_x, height):
    """Draws a titled section with mentions (headline, source, link)."""
    if y < 80: c.showPage(); y = height - 60
    c.setFont("Helvetica-Bold", 14); c.setFillColor(navy)
    c.drawString(margin_x, y, title); y -= 20; c.setFillColor(black)
    mention_count = 0; max_mentions = 10
    for item in mentions:
        if mention_count >= max_mentions: break
        headline = item.get('text', 'No Headline')[:200]
        source = item.get('source', 'Unknown Source')
        link = item.get('link', None)
        
        # --- THIS IS THE FIX ---
        headline_lines = textwrap.wrap(headline, width=80) # Define headline_lines
        # --- END OF FIX ---
        
        estimated_height = len(headline_lines) * 14 + 14 + 10
        if y < estimated_height + 60:
            c.showPage(); y = height - 60
            c.setFont("Helvetica-Bold", 14); c.setFillColor(navy)
            c.drawString(margin_x, y, title + " (cont.)"); y -= 20; c.setFillColor(black)
        
        c.setFont("Helvetica-Bold", 10)
        # --- THIS IS THE FIX ---
        for line in headline_lines: # Loop over headline_lines, not 'lines'
            if y < 60: c.showPage(); y = height - 60; c.setFont("Helvetica-Bold", 10)
            c.drawString(margin_x, y, line); y -= 12
        # --- END OF FIX ---
            
        c.setFont("Helvetica", 9); c.setFillColor(gray)
        source_text = f"Source: {source}"
        if y < 60: c.showPage(); y = height - 60; c.setFont("Helvetica", 9); c.setFillColor(gray)
        c.drawString(margin_x, y, source_text)
        if link and str(link).startswith('http'):
             link_text = " (Link)"; text_width = c.stringWidth(source_text, "Helvetica", 9)
             link_x = margin_x + text_width; c.setFillColor(navy)
             try:
                 c.linkURL(link, (link_x, y - 2, link_x + c.stringWidth(link_text, "Helvetica", 9), y + 10), relative=1)
                 c.drawString(link_x, y, link_text)
                 c.line(link_x, y - 1, link_x + c.stringWidth(link_text, "Helvetica", 9), y-1)
             except Exception as link_e: print(f"Warning: Could not create PDF link for {link}: {link_e}")
        y -= 14; c.setFillColor(black); y -= 10; mention_count += 1
    if mention_count == 0:
         if y < 60: c.showPage(); y = height - 60
         c.setFont("Helvetica-Oblique", 10); c.drawString(margin_x, y, "No specific mentions found."); y -= 20
    return y

# --- Main Report Generation Function ---
def generate_report(kpis, top_keywords, full_articles_data, brand="Brand", competitors=None, timeframe_hours=24, include_json=False):
    if competitors is None: competitors = []

    # --- Categorize Mentions ---
    main_brand_mentions = []; competitor_mentions = []; related_mentions = []
    lower_brand = brand.lower(); lower_competitors = {c.lower() for c in competitors}
    for item in full_articles_data:
        mentioned_brands_lower = set()
        mentioned_str = item.get('mentioned_brands', '')
        if isinstance(mentioned_str, str): mentioned_brands_lower = {b.strip().lower() for b in mentioned_str.split(',') if b.strip()}
        elif isinstance(mentioned_str, list): mentioned_brands_lower = {b.strip().lower() for b in mentioned_str}
        mentions_main = lower_brand in mentioned_brands_lower
        mentions_comp = any(comp in mentioned_brands_lower for comp in lower_competitors)
        if mentions_main and not mentions_comp: main_brand_mentions.append(item)
        elif not mentions_main and mentions_comp: competitor_mentions.append(item)
        else: related_mentions.append(item)

    # --- Get KPI data ---
    sentiment_ratio = kpis.get('sentiment_ratio', {}); sov = kpis.get('sov', [])
    all_brands = kpis.get('all_brands', [brand] + competitors)
    mis = kpis.get('mis', 0); mpi = kpis.get('mpi', 0)
    engagement = kpis.get('engagement_rate', 0); reach = kpis.get('reach', 0)
    generated_on = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    if isinstance(timeframe_hours, int): time_text = f"the last {timeframe_hours} hours"
    else: time_text = timeframe_hours

    # --- Load Pre-Written AI Summary ---
    ai_summary = demo_loader.load_ai_summary()

    # ---- 1. Markdown Generation (for email body) ----
    md_lines = [f"# Flash Narrative Report: {brand}",
                f"**Period:** {time_text}", f"**Generated:** {generated_on}", ai_summary,
                "\n## Key Performance Indicators",
                f"- **Media Impact Score (MIS):** {mis:.0f}", f"- **Message Penetration (MPI):** {mpi:.1f}%",
                f"- **Avg. Social Engagement:** {engagement:.1f}", f"- **Total Reach:** {reach:,}",
                f"- **Sentiment Ratio:** " + ", ".join([f"{k.capitalize()}: {v:.1f}%" for k, v in sentiment_ratio.items()]),
                "\n### Share of Voice (SOV)", "| Brand | SOV (%) |", "|---|---|"]
    if len(sov) < len(all_brands): sov += [0] * (len(all_brands) - len(sov))
    for b, s in zip(all_brands, sov): md_lines.append(f"| {b} | {s:.1f} |")
    md = "\n".join(md_lines)

    # ---- 2. PDF Generation ----
    pdf_buffer = io.BytesIO(); c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter; margin_x = 50; margin_y = 60; content_width = width - 2 * margin_x
    y = height - margin_y
    c.setFont("Helvetica-Bold", 18); c.drawString(margin_x, y, f"Flash Narrative Report: {brand}"); y -= 20
    c.setFont("Helvetica", 10); c.drawString(margin_x, y, f"Period: {time_text} | Generated: {generated_on}"); y -= 25
    c.setFont("Helvetica-Bold", 12); c.drawString(margin_x, y, "Key Performance Indicators"); y -= 16
    c.setFont("Helvetica", 10)
    kpi_text = f"MIS: {mis:.0f} | MPI: {mpi:.1f}% | Avg. Engagement: {engagement:.1f} | Reach: {reach:,}"
    for line in textwrap.wrap(kpi_text, width=70): c.drawString(margin_x, y, line); y -= 14
    
    # Draw Sentiment Pie Chart (Top-Right)
    pie_buf = _create_sentiment_pie(sentiment_ratio)
    try:
        img = ImageReader(pie_buf)
        img_width = 200; img_height = 200; img_x = width - margin_x - img_width
        img_y = height - margin_y - 20 - img_height
        c.drawImage(img, img_x, img_y, width=img_width, height=img_height, preserveAspectRatio=True, mask='auto')
        y = min(y, img_y - 20)
    except Exception as pie_e:
        print(f"Error drawing pie chart: {pie_e}"); y -= 20

    # Draw SOV Bar Chart (Below KPIs)
    sov_buf = _create_sov_bar_chart(all_brands, sov)
    if sov_buf:
        try:
            img_sov = ImageReader(sov_buf)
            img_width = 400; img_height = 150
            if y < img_height + 20: c.showPage(); y = height - margin_y
            y -= (img_height + 20)
            c.drawImage(img_sov, margin_x, y, width=img_width, height=img_height, preserveAspectRatio=True, mask='auto')
            y -= 20
        except Exception as sov_e: print(f"Error drawing SOV chart: {sov_e}")
            
    
    # --- IMPROVED AI SUMMARY MARKDOWN PARSER ---
    if y < 200: c.showPage(); y = height - margin_y
    c.setFont("Helvetica-Bold", 12); c.drawString(margin_x, y, "AI Summary & Recommendations"); y -= 16

    # Pre-process: Replace <br> with \n for line breaks in text (e.g., in tables)
    ai_summary = ai_summary.replace('<br>', '\n')

    ai_lines = ai_summary.split('\n')
    i = 0
    while i < len(ai_lines):
        r = ai_lines[i].rstrip()  # Use rstrip to handle trailing spaces
        
        if not r:  # Skip empty lines but add small space
            y -= 6
            if y < margin_y + 10: c.showPage(); y = height - margin_y
            i += 1
            continue

        # Horizontal rule
        if r in ['---', '***', '___']:
            c.setLineWidth(0.5)
            c.setStrokeColor(gray)
            c.line(margin_x, y - 5, width - margin_x, y - 5)
            y -= 10
            if y < margin_y + 10: c.showPage(); y = height - margin_y
            i += 1
            continue

        # Table detection
        if r.startswith('|'):
            # Collect table lines (header, separator, data)
            table_lines = []
            while i < len(ai_lines) and ai_lines[i].strip().startswith('|'):
                table_lines.append(ai_lines[i].strip())
                i += 1
            i -= 1  # Loop will increment i at end

            # Parse rows (skip separator line if it's all ---)
            rows = []
            for line in table_lines:
                if '---' in line and all('-' in cell or '|' in cell for cell in line.split('|')):
                    continue  # Skip separator
                cells = [cell.strip() for cell in line.strip('|').split('|')]
                rows.append(cells)

            if not rows:
                i += 1
                continue

            # Draw table (simple: fixed cell width, no borders for minimalism)
            num_cols = max(len(row) for row in rows)
            cell_width = content_width / num_cols
            cell_height = 12  # Fixed row height; adjust if needed

            # Estimate table height and page break if needed
            table_height = len(rows) * cell_height + 20
            if y < table_height + margin_y:
                c.showPage(); y = height - margin_y

            # Header row (bold)
            header = rows[0]
            c.setFont("Helvetica-Bold", 10)
            for j, cell in enumerate(header):
                # Handle bold in cells (e.g., **Driver**)
                cell = cell.replace('**', '')
                wrapped = textwrap.wrap(cell, width=int(cell_width / 5))  # Rough char width
                for k, wline in enumerate(wrapped):
                    c.drawString(margin_x + j * cell_width, y - k * 12, wline)
            y -= cell_height

            # Data rows
            c.setFont("Helvetica", 9)
            for row in rows[1:]:
                for j, cell in enumerate(row):
                    # Handle multi-line (from <br> -> \n)
                    cell_lines = cell.split('\n')
                    for k, cline in enumerate(cell_lines):
                        cline = cline.strip().replace('**', '')  # Remove any leftover bold
                        wrapped = textwrap.wrap(cline, width=int(cell_width / 5))
                        for m, wline in enumerate(wrapped):
                            c.drawString(margin_x + j * cell_width + (5 if m > 0 else 0), y - (k + m) * 12, wline)
                y -= cell_height * max(1, max(len(cell.split('\n')) for cell in row))
            y -= 10  # Space after table
            i += 1
            continue

        # Header detection (#, ##, ###)
        is_header = False
        if r.startswith('# '):
            font = "Helvetica-Bold"
            font_size = 14
            r = r[2:].strip()
            is_header = True
        elif r.startswith('## '):
            font = "Helvetica-Bold"
            font_size = 12
            r = r[3:].strip()
            is_header = True
        elif r.startswith('### '):
            font = "Helvetica-Bold"
            font_size = 11
            r = r[4:].strip()
            is_header = True
        else:
            font_size = 10
            font = "Helvetica"

        # Bold (**text**)
        is_bold = r.startswith('**') and r.endswith('**')
        if is_bold:
            r = r[2:-2].strip()
            font = "Helvetica-Bold"

        # Bullets (* or -)
        is_bullet = r.startswith('* ') or r.startswith('- ')
        if is_bullet:
            r = r[2:].strip()
            # Check for sub-bold in bullet (e.g., **Strengths**)
            if r.startswith('**') and r.endswith('**'):
                r = r[2:-2].strip()
                font = "Helvetica-Bold"

        # Set font
        c.setFont(font, font_size)

        # Wrap and draw lines
        wrap_width = 80 if is_bullet else 85
        lines = textwrap.wrap(r, width=wrap_width)
        for j, line in enumerate(lines):
            if y < margin_y + 10:  # Page break
                c.showPage(); y = height - margin_y
                c.setFont(font, font_size)  # Reset font after page break

            draw_x = margin_x + (15 if is_bullet else 0)  # Indent bullets
            draw_string = line
            if is_bullet and j == 0:
                draw_string = f"• {line}"  # Add bullet symbol
            c.drawString(draw_x, y, draw_string)
            y -= 12 + (2 if is_header else 0)  # Extra space for headers

        if is_header:
            y -= 5  # Extra space after headers

        i += 1

    y -= 15  # Space after AI summary
    # --- END OF IMPROVED PARSER ---


    # --- Mention Sections ---
    if y < height / 2: c.showPage(); y = height - margin_y
    y = _draw_mention_section(c, y, f"{brand} News Mentions", main_brand_mentions, content_width, margin_x, height)
    y = _draw_mention_section(c, y, "Competition News Mentions", competitor_mentions, content_width, margin_x, height)
    y = _draw_mention_section(c, y, "Related News / Passive Mentions", related_mentions, content_width, margin_x, height)

    # --- Keywords Section ---
    if y < 150: c.showPage(); y = height - margin_y
    c.setFont("Helvetica-Bold", 12); c.drawString(margin_x, y, "Top Keywords & Phrases"); y -= 16
    c.setFont("Helvetica", 10)
    kw_count = 0
    for w, f in top_keywords:
        text = f"- {w}: {f}"
        if y < margin_y + 10:
             c.showPage(); y = height - margin_y
             c.setFont("Helvetica-Bold", 12); c.drawString(margin_x, y, "Top Keywords & Phrases (cont.)"); y -= 16
             c.setFont("Helvetica", 10)
        c.drawString(margin_x, y, text); y -= 12
        kw_count += 1
    if kw_count == 0:
        c.setFont("Helvetica-Oblique", 10); c.drawString(margin_x, y, "No keywords identified."); y -= 20

    # --- Finalize PDF ---
    c.save()
    pdf_bytes = pdf_buffer.getvalue()
    pdf_buffer.close()

    # ---- 3. Return Values ----
    json_summary = {"brand": brand, "competitors": competitors, "kpis": kpis, "top_keywords": top_keywords, "generated_on": generated_on, "ai_summary": ai_summary}
    if include_json:
        return md, pdf_bytes, json_summary
    return md, pdf_bytes