import re

with open("index.html", "r") as f:
    html = f.read()

# Remove the full-content CSS
css_pattern = r'/\* News Full Content Modal/Expand \*/.*?\.btn-expand:hover \{ text-decoration: underline; \}'
html = re.sub(css_pattern, '', html, flags=re.DOTALL)

# Revert JS to simple gateway cards
js_old_pattern = r'const contentSnippet = item.summary_pt.*?;.*?grid\.appendChild\(card\);'

js_new = """                    card.innerHTML = `
                        <div>
                            <span class="news-source ${sourceClass}">${escapeHtml(item.source)}</span>
                            <div class="news-title">${escapeHtml(item.title_pt)}</div>
                            <div class="news-date">Date: ${escapeHtml(dateStr)}</div>
                            <div class="news-summary">${escapeHtml(item.summary_pt)}</div>
                        </div>
                        <a href="${item.link}" target="_blank" class="news-link">Ler notícia na fonte ↗</a>
                    `;
                    grid.appendChild(card);"""

html = re.sub(js_old_pattern, js_new, html, flags=re.DOTALL)

# Add CSS for new sources
css_source_old = ".news-source.planet { background: #1976d2; }"
css_source_new = """.news-source.planet { background: #1976d2; }
        .news-source.kernel-org { background: #ffcc00; color: #000; }
        .news-source.9to5linux { background: #e65100; }
        .news-source.linux-com { background: #000000; }"""

if ".news-source.kernel-org" not in html:
    html = html.replace(css_source_old, css_source_new)

# Update source classes in JS
js_source_old = "if (item.source.toLowerCase().includes('lwn')) sourceClass = 'lwn';"
js_source_new = """if (item.source.toLowerCase().includes('lwn')) sourceClass = 'lwn';
                    if (item.source.toLowerCase().includes('kernel.org')) sourceClass = 'kernel-org';
                    if (item.source.toLowerCase().includes('9to5linux')) sourceClass = '9to5linux';
                    if (item.source.toLowerCase().includes('linux.com')) sourceClass = 'linux-com';"""
if "kernel-org" not in html:
    html = html.replace(js_source_old, js_source_new)
    
with open("index.html", "w") as f:
    f.write(html)
print("UI reverted to gateway style")
