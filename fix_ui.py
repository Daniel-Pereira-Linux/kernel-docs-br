with open("index.html", "r") as f:
    html = f.read()

# Add CSS for modal / full content expansion
css_old = """        .news-link:hover {
            background: #e0e0e0;
        }
    </style>"""
css_new = """        .news-link:hover {
            background: #e0e0e0;
        }

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
    </style>"""

if css_old in html:
    html = html.replace(css_old, css_new)

# Update Javascript in loadNews
js_old = """                    card.innerHTML = `
                        <div>
                            <span class="news-source ${sourceClass}">${escapeHtml(item.source)}</span>
                            <div class="news-title">${escapeHtml(item.title_pt)}</div>
                            <div class="news-date">📅 ${escapeHtml(dateStr)}</div>
                            <div class="news-summary">${escapeHtml(item.summary_pt)}</div>
                        </div>
                        <a href="${item.link}" target="_blank" class="news-link">Ler original ↗</a>
                    `;
                    grid.appendChild(card);"""

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
                        <div style="display:flex; justify-content: space-between; align-items: center; margin-top:15px;">
                            <button class="btn-expand" onclick="this.closest('.news-card').classList.toggle('expanded'); this.textContent = this.closest('.news-card').classList.contains('expanded') ? 'Menos detalhes' : 'Ler notícia completa'">Ler notícia completa</button>
                            <a href="${item.link}" target="_blank" class="news-link" style="margin:0;">Ver no LWN ↗</a>
                        </div>
                    `;
                    grid.appendChild(card);"""

if js_old in html:
    html = html.replace(js_old, js_new)

with open("index.html", "w") as f:
    f.write(html)
print("Updated UI for full news")
