with open("index.html", "r") as f:
    html = f.read()

# Add the News tab to nav
nav_old = """    <nav>
        <a onclick="showTab('docs')" class="active-tab" id="nav-docs">📖 Documentação</a>
        <a onclick="showTab('patches')" id="nav-patches">📬 PATCHS</a>
    </nav>"""
nav_new = """    <nav>
        <a onclick="showTab('docs')" class="active-tab" id="nav-docs">📖 Documentação</a>
        <a onclick="showTab('patches')" id="nav-patches">📬 PATCHS</a>
        <a onclick="showTab('news')" id="nav-news">📰 Notícias</a>
    </nav>"""

if nav_old in html:
    html = html.replace(nav_old, nav_new)
else:
    print("Nav old not found")

# Add the News container CSS
css_old = """        .eol-badge {
            background: #ffcdd2;
            color: #c62828;
            padding: 1px 6px;
            border-radius: 3px;
            font-size: 0.75rem;
            font-weight: 600;
        }
    </style>"""
css_new = """        .eol-badge {
            background: #ffcdd2;
            color: #c62828;
            padding: 1px 6px;
            border-radius: 3px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        /* News styles */
        .news-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .news-card {
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .news-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .news-source {
            font-size: 0.75rem;
            font-weight: 600;
            color: #fff;
            background: #0f3460;
            padding: 2px 8px;
            border-radius: 4px;
            display: inline-block;
            margin-bottom: 8px;
            align-self: flex-start;
        }
        .news-source.phoronix { background: #d32f2f; }
        .news-source.lwn { background: #388e3c; }
        .news-source.planet { background: #1976d2; }
        
        .news-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 8px;
            line-height: 1.3;
        }
        .news-summary {
            font-size: 0.9rem;
            color: #555;
            margin-bottom: 12px;
            flex-grow: 1;
        }
        .news-date {
            font-size: 0.8rem;
            color: #999;
            margin-bottom: 12px;
        }
        .news-link {
            text-align: center;
            display: block;
            background: #eee;
            color: #333;
            text-decoration: none;
            padding: 8px;
            border-radius: 4px;
            font-weight: 500;
            font-size: 0.9rem;
        }
        .news-link:hover {
            background: #e0e0e0;
        }
    </style>"""

if css_old in html:
    html = html.replace(css_old, css_new)
else:
    print("CSS old not found")

# Add the News HTML container
container_old = """    <div class="container">
        <div id="docs" class="tab-content active docs">"""
container_new = """    <div class="container">
        <div id="news" class="tab-content">
            <h2 style="margin-bottom: 10px;">📰 Últimas Notícias do Kernel</h2>
            <p style="color: #666; margin-bottom: 20px; font-size: 0.9rem;">
                Notícias traduzidas automaticamente do Phoronix, LWN e Planet Kernel. Atualizado a cada 30 minutos.
            </p>
            <div id="news-grid" class="news-grid">
                <div class="loading">Carregando notícias... <div class="spinner"></div></div>
            </div>
        </div>

        <div id="docs" class="tab-content active docs">"""

if container_old in html:
    html = html.replace(container_old, container_new)
else:
    print("Container old not found")

# Add JS logic for news tab
js_old = """        function showTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('nav a').forEach(el => el.classList.remove('active-tab'));
            
            document.getElementById(tabId).classList.add('active');
            document.getElementById('nav-' + tabId).classList.add('active-tab');
        }"""
js_new = """        function showTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('nav a').forEach(el => el.classList.remove('active-tab'));
            
            document.getElementById(tabId).classList.add('active');
            document.getElementById('nav-' + tabId).classList.add('active-tab');
            
            if (tabId === 'news' && !newsLoaded) {
                loadNews();
            }
        }
        
        let newsLoaded = false;
        async function loadNews() {
            try {
                const res = await fetch('news.json?' + Date.now());
                const data = await res.json();
                
                const grid = document.getElementById('news-grid');
                grid.innerHTML = '';
                
                if (data.length === 0) {
                    grid.innerHTML = '<p>Nenhuma notícia encontrada.</p>';
                    return;
                }
                
                data.forEach(item => {
                    const card = document.createElement('div');
                    card.className = 'news-card';
                    
                    let sourceClass = 'planet';
                    if (item.source.toLowerCase().includes('phoronix')) sourceClass = 'phoronix';
                    if (item.source.toLowerCase().includes('lwn')) sourceClass = 'lwn';
                    
                    // Simple date parsing
                    let dateStr = item.date;
                    try {
                        if (dateStr) {
                            const d = new Date(dateStr);
                            dateStr = d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
                        }
                    } catch(e) {}
                    
                    card.innerHTML = `
                        <div>
                            <span class="news-source ${sourceClass}">${escapeHtml(item.source)}</span>
                            <div class="news-title">${escapeHtml(item.title_pt)}</div>
                            <div class="news-date">📅 ${escapeHtml(dateStr)}</div>
                            <div class="news-summary">${escapeHtml(item.summary_pt)}</div>
                        </div>
                        <a href="${item.link}" target="_blank" class="news-link">Ler original ↗</a>
                    `;
                    grid.appendChild(card);
                });
                newsLoaded = true;
            } catch (e) {
                console.error("Erro ao carregar noticias:", e);
                document.getElementById('news-grid').innerHTML = '<p style="color:red">Erro ao carregar as notícias. Tente novamente mais tarde.</p>';
            }
        }"""

if js_old in html:
    html = html.replace(js_old, js_new)
else:
    print("JS old not found")

with open("index.html", "w") as f:
    f.write(html)
print("Updated index.html with News tab!")
