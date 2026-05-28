# formatters.py
# HTML parsing and visual rendering formatters for causes, fixes, and tips cards.

import re


def format_causes_html(text: str) -> str:
    """Parse numbered causes into individual styled cards."""
    parts = re.split(r'\n\s*(\d+)\.\s+', text.strip())
    html = ""
    if len(parts) < 3:
        return f'<div class="result-body">{text.replace(chr(10), "<br>")}</div>'
    i = 1
    while i < len(parts) - 1:
        num = parts[i]
        body = parts[i + 1].strip()
        title_match = re.match(r'^([^:]+?):\s*(.*)', body, re.DOTALL)
        if title_match:
            title = title_match.group(1).replace('**', '').strip()
            desc = title_match.group(2).replace('**', '').strip().replace('\n', ' ')
        else:
            title = body.split('.')[0].replace('**', '').strip()
            desc = '.'.join(body.split('.')[1:]).replace('**', '').strip().replace('\n', ' ')
        html += f'''<div class="cause-card">
          <div class="cause-num">{num}</div>
          <div><div class="cause-title">{title}</div><div class="cause-desc">{desc}</div></div>
        </div>'''
        i += 2
    return html

def format_fixes_html(text: str, is_user_fix: bool = False, device_type: str = "Device") -> str:
    """Parse fix groups into professional, interactive UI cards."""
    # Split text into fix blocks
    blocks = re.split(r'(?m)^###\s*Fix', text)
    
    html = ""

    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        # Parse Title and Difficulty from the first line
        lines = block.split('\n')
        first_line = lines[0].strip()
        
        # Extract difficulty
        difficulty = "EASY"
        diff_match = re.search(r'\[(EASY|MEDIUM|HARD)\]', first_line, re.IGNORECASE)
        if diff_match:
            difficulty = diff_match.group(1).upper()
            first_line = first_line.replace(diff_match.group(0), "").strip()
        
        title = first_line.lstrip(':').strip().replace('**', '')
        if not title:
            title = "Repair Instructions"
            
        clean_title = re.sub(r'^\d+[\:\.\-]?\s*', '', title).strip()
            
        # Parse Tools and Steps
        tools_html = ""
        steps_html = ""

        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('**Tools Required:**') or line.startswith('Tools Required:'):
                tools_text = line.replace('**Tools Required:**', '').replace('Tools Required:', '').strip()
                if tools_text.lower() != 'none':
                    tools_html = f'<div style="background:rgba(245,158,11,0.06); border:1px solid rgba(245,158,11,0.2); padding:1rem 1.2rem; border-radius:14px; margin-bottom:1.5rem; display:flex; gap:1rem; align-items:center;"><div style="font-size:1.4rem;">🧰</div><div><div style="color:#fbbf24; font-size:0.75rem; font-weight:800; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.2rem;">Tools Required</div><div style="color:#fde68a; font-size:0.95rem;">{tools_text}</div></div></div>'
                continue
                          # Match numbered steps
            step_match = re.match(r'^(\d+)[\.\)]\s+(.*)', line)
            if step_match:
                num = step_match.group(1)
                step_text = step_match.group(2).replace('**', '')
                steps_html += f'<div style="display:flex; flex-direction:column; gap:6px; margin-bottom:1.5rem; background:rgba(255,255,255,0.015); padding:1rem; border-radius:10px; border:1px solid rgba(255,255,255,0.04);"><div style="display:flex; flex-direction:column; gap:4px;"><div style="color:#10b981; font-weight:800; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.05em;">Step {num}</div><div style="color:#f1f5f9; font-size:0.98rem; line-height:1.6; font-weight:400;">{step_text}</div></div></div>'

                
            # Match bullets
            elif line.startswith(('-', '*')):
                bullet_text = line.lstrip('-* ').replace('**', '')
                steps_html += f'<div style="display:flex; gap:0.8rem; align-items:flex-start; margin-left:3.2rem; margin-bottom:0.8rem;"><div style="color:#10b981; margin-top:2px;">•</div><div style="color:#cbd5e1; font-size:0.95rem; line-height:1.6;">{bullet_text}</div></div>'
                
            else:
                steps_html += f'<div style="margin-left:3.2rem; margin-bottom:0.8rem; color:#cbd5e1; font-size:0.95rem;">{line.replace("**","")}</div>'
                
        # Badge
        css = {"EASY": "diff-easy", "MEDIUM": "diff-medium", "HARD": "diff-hard"}.get(difficulty, "diff-easy")
        diff_html = f'<span class="diff-badge {css}">{difficulty}</span>'
        
        # Wrap group
        html += f'<div class="fix-group"><div class="fix-group-title"><span>🔧 {title}</span> {diff_html}</div>{tools_html}{steps_html}</div>'
        
    if not html:
        return f'<div class="result-body">{text.replace(chr(10), "<br>")}</div>'
        
    return html

def format_tips_html(text: str) -> str:
    """Parse numbered tips into individual styled items."""
    tips = re.findall(r'\d+\.\s+(.+?)(?=\n\d+\.|\Z)', text.strip(), re.DOTALL)
    if not tips:
        return f'<div class="result-body">{text.replace(chr(10), "<br>")}</div>'
    html = ""
    for tip in tips:
        clean = tip.replace('**', '').replace('\n', ' ').strip()
        tip_match = re.match(r'^([^:]+?):\s*(.*)', clean)
        if tip_match:
            tip_title = tip_match.group(1).strip()
            tip_desc = tip_match.group(2).strip()
            # CRITICAL: No extra indentation
            html += f'<div class="tip-item"><div class="tip-icon">💡</div><div class="tip-text"><strong style="color:#a78bfa;">{tip_title}:</strong> {tip_desc}</div></div>'
        else:
            html += f'<div class="tip-item"><div class="tip-icon">💡</div><div class="tip-text">{clean}</div></div>'
    return html

def format_verdict_html(text: str) -> str:
    """Clean verdict text into a styled detail box."""
    clean = text.replace('**', '').strip()
    clean = re.sub(r'✅\s*USER CAN FIX THIS\s*—?\s*', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'🏥\s*GO TO SERVICE CENTER\s*—?\s*', '', clean, flags=re.IGNORECASE)
    clean = clean.replace('✅', '').replace('🏥', '').strip()
    paragraphs = [p.strip() for p in clean.split('\n') if p.strip()]
    return '<div class="verdict-detail">' + '<br>'.join(paragraphs) + '</div>'

def format_vision_analysis_html(text: str) -> str:
    """Format the raw Markdown vision analysis into a styled, industry-ready HTML layout."""
    # Convert bold **text** to styled <strong> tags
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#bae6fd; font-weight:700;">\1</strong>', text)
    
    # Split by lines to handle lists
    lines = formatted.split('\n')
    html = '<div class="vision-content" style="display:flex; flex-direction:column; gap:0.5rem; margin-top:0.5rem;">'
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Headers (e.g., **Overall Assessment:**)
        if (line.startswith('<strong') and line.endswith('</strong>')) or line.startswith('#'):
            clean_line = line.replace('#', '').strip()
            html += f'<div style="font-size:1.05rem; margin-top:1.2rem; border-bottom:1px solid rgba(147,197,253,0.15); padding-bottom:0.4rem; margin-bottom:0.4rem;">{clean_line}</div>'
            continue
            
        # Numbered lists (e.g., 1. **Battery Pack:**)
        num_match = re.match(r'^(\d+)\.\s+(.*)', line)
        if num_match:
            num = num_match.group(1)
            content = num_match.group(2)
            html += f'<div style="display:flex; gap:0.8rem; align-items:flex-start; margin-top:1rem; background:rgba(59,130,246,0.06); padding:1.2rem; border-radius:12px; border:1px solid rgba(59,130,246,0.2); box-shadow:0 4px 15px rgba(0,0,0,0.2);"><div style="background:linear-gradient(135deg, #3b82f6, #60a5fa); color:#0a0e1a; font-weight:800; font-size:0.8rem; min-width:24px; height:24px; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:2px; box-shadow:0 2px 8px rgba(59,130,246,0.4);">{num}</div><div style="color:#e0f2fe; line-height:1.6;">{content}</div></div>'
            continue
            
        # Bullet points
        bullet_match = re.match(r'^[\*\-]\s+(.*)', line)
        if bullet_match:
            content = bullet_match.group(1)
            html += f'<div style="display:flex; gap:0.6rem; align-items:flex-start; padding-left:1.5rem; margin-top:0.5rem;"><div style="color:#3b82f6; margin-top:2px; font-weight:bold;">•</div><div style="color:#bae6fd; font-size:0.95rem; line-height:1.6;">{content}</div></div>'
            continue
            
        # Regular text
        html += f'<div style="color:#e0f2fe; line-height:1.7; padding-left:0.2rem;">{line}</div>'
        
    html += '</div>'
    return html

