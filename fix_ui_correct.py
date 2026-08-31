import re

with open("index.html", "r") as f:
    html = f.read()

# Replace CSS
css_old = ".news-link:hover { text-decoration: underline; }" # wait, what is the hover class currently?
# let's just insert the new CSS before Patches
css_new = """
        /* News Full Content Modal/Expand */
        .news-content-full {
            display: none;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px dashed var(--border-color);
            font-size: 14px;
            line-height: 1.6;
            color: #333;
            white-space: pre-wrap;
        }
        .news-card.expanded .news-content-full {
            display: block;
        }
        .news-card.expanded {
            grid-column: 1 / -1;
            border-color: var(--link-color);
        }
        .btn-expand {
            background: none;
            border: none;
            color: var(--link-color);
            cursor: pointer;
            font-weight: bold;
            font-size: 13px;
            padding: 5px 0;
            text-align: left;
        }
        .btn-expand:hover { text-decoration: underline; }
"""
if ".news-content-full" not in html:
    html = html.replace("/* Patches */", css_new + "\n        /* Patches */")

# Replace JS
js_old_pattern = r'card\.innerHTML = `.*?grid\.appendChild\(card\);'

js_new = """                    const contentSnippet = item.summary_pt || (item.content_pt ? item.content_pt.substring(0, 200) + '...' : '');
                    const fullContent = item.content_pt || item.summary_pt || 'Conteúdo não disponível.';
                    
                    card.innerHTML = `
                        <div>
                            <span class="news-source ${sourceClass}">${escapeHtml(item.source)}</span>
                            <div class="news-title">${escapeHtml(item.title_pt)}</div>
                            <div class="news-date">Date: ${escapeHtml(dateStr)}</div>
                            <div class="news-summary">${escapeHtml(contentSnippet)}</div>
                            <div class="news-content-full">${escapeHtml(fullContent)}</div>
                        </div>
                        <div style="display:flex; justify-content: space-between; align-items: center; margin-top:15px; gap: 10px;">
                            <button class="btn-expand" onclick="this.closest('.news-card').classList.toggle('expanded'); this.textContent = this.closest('.news-card').classList.contains('expanded') ? 'Menos detalhes' : 'Ler notícia completa'">Ler notícia completa</button>
                            <a href="${item.link}" target="_blank" class="news-link" style="margin:0;">Ver no LWN ↗</a>
                        </div>
                    `;
                    grid.appendChild(card);"""

html = re.sub(js_old_pattern, js_new, html, flags=re.DOTALL)

with open("index.html", "w") as f:
    f.write(html)
print("UI fixed")
