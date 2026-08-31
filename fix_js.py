with open("index.html", "r") as f:
    html = f.read()

js_old = """        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('nav a').forEach(el => el.classList.remove('active-tab'));
            document.getElementById(tabName).classList.add('active');
            document.getElementById('nav-' + tabName).classList.add('active-tab');
            if (tabName === 'patches' && allPatches.length === 0) {"""

js_new = """        let newsLoaded = false;
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
        }

        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('nav a').forEach(el => el.classList.remove('active-tab'));
            document.getElementById(tabName).classList.add('active');
            document.getElementById('nav-' + tabName).classList.add('active-tab');
            
            if (tabName === 'news' && !newsLoaded) {
                loadNews();
            }
            if (tabName === 'patches' && allPatches.length === 0) {"""

html = html.replace(js_old, js_new)

with open("index.html", "w") as f:
    f.write(html)
print("Updated showTab JS")
