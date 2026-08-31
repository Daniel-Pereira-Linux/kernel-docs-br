import markdown
import os

with open('../how-to.md', 'r') as f:
    md_content = f.read()

# basic parsing of markdown
html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])

template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Como contribuir com o Kernel</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            color: #333;
        }}
        header {{
            background: #333;
            color: #fff;
            padding: 1rem 0;
            text-align: center;
        }}
        .container {{
            max-width: 900px;
            margin: auto;
            padding: 20px;
            background: #fff;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        nav {{
            display: flex;
            justify-content: center;
            background: #444;
        }}
        nav a {{
            color: white;
            padding: 15px 20px;
            text-decoration: none;
            cursor: pointer;
        }}
        nav a:hover {{
            background: #555;
        }}
        pre {{
            background: #eee;
            padding: 10px;
            overflow-x: auto;
        }}
        .tab-content {{
            display: none;
        }}
        .active {{
            display: block;
        }}
        .patch-list {{
            list-style: none;
            padding: 0;
        }}
        .patch-item {{
            padding: 15px;
            border-bottom: 1px solid #ddd;
        }}
        .patch-title {{
            font-weight: bold;
            color: #0066cc;
            text-decoration: none;
        }}
        .patch-title:hover {{
            text-decoration: underline;
        }}
        .patch-meta {{
            font-size: 0.9em;
            color: #666;
        }}
        #patch-viewer {{
            display: none;
            margin-top: 20px;
            border: 1px solid #ddd;
            background: #fff;
            padding: 15px;
        }}
        #patch-content {{
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 0.9em;
            background: #f9f9f9;
            padding: 10px;
            border: 1px solid #ccc;
            max-height: 600px;
            overflow-y: auto;
        }}
        .close-btn {{
            background: #d9534f;
            color: white;
            border: none;
            padding: 5px 10px;
            cursor: pointer;
            float: right;
        }}
        footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <header>
        <h1>Como contribuir com o Kernel</h1>
    </header>
    <nav>
        <a onclick="showTab('docs')">Documentação</a>
        <a onclick="showTab('patches')">PATCHS (Tempo Real)</a>
    </nav>

    <div class="container">
        <div id="docs" class="tab-content active">
            {html_content}
        </div>

        <div id="patches" class="tab-content">
            <h2>Patches Recentes (linux-doc) - pt_BR</h2>
            <p>Buscando atualizações em tempo real do lore.kernel.org...</p>
            <div id="loading" style="display: none;">Carregando...</div>
            <ul id="patch-list" class="patch-list"></ul>
            
            <div id="patch-viewer">
                <button class="close-btn" onclick="closePatch()">X Fechar</button>
                <h3 id="patch-viewer-title"></h3>
                <div id="patch-content"></div>
            </div>
        </div>
    </div>

    <footer>
        Mantido por Daniel Pereira
    </footer>

    <script>
        function showTab(tabName) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            if(tabName === 'patches') {{
                loadPatches();
            }}
        }}

        function closePatch() {{
            document.getElementById('patch-viewer').style.display = 'none';
            document.getElementById('patch-list').style.display = 'block';
        }}

        async function loadPatches() {{
            const list = document.getElementById('patch-list');
            if (list.children.length > 0) return; // Ja carregou
            
            document.getElementById('loading').style.display = 'block';
            try {{
                // Usando codetabs proxy como fallback para evitar CORS
                const url = "https://api.codetabs.com/v1/proxy?quest=" + encodeURIComponent("https://lore.kernel.org/linux-doc/?q=pt_BR&x=a");
                const res = await fetch(url);
                const text = await res.text();
                
                const parser = new DOMParser();
                const xmlDoc = parser.parseFromString(text, "text/xml");
                const entries = xmlDoc.getElementsByTagName("entry");
                
                document.getElementById('loading').style.display = 'none';
                list.innerHTML = '';
                
                for (let i = 0; i < entries.length; i++) {{
                    const title = entries[i].getElementsByTagName("title")[0].textContent;
                    const author = entries[i].getElementsByTagName("author")[0].getElementsByTagName("name")[0].textContent;
                    const updated = entries[i].getElementsByTagName("updated")[0].textContent;
                    let link = "";
                    const links = entries[i].getElementsByTagName("link");
                    for (let j = 0; j < links.length; j++) {{
                        if (links[j].getAttribute("rel") === "alternate") {{
                            link = links[j].getAttribute("href");
                        }}
                    }}
                    
                    const li = document.createElement('li');
                    li.className = 'patch-item';
                    li.innerHTML = `
                        <a href="javascript:void(0)" class="patch-title" onclick="openPatch('${{link}}', '${{title.replace(/'/g, "\\'")}}')">${{title}}</a>
                        <div class="patch-meta">Por: ${{author}} | Em: ${{new Date(updated).toLocaleString()}}</div>
                    `;
                    list.appendChild(li);
                }}
            }} catch (e) {{
                document.getElementById('loading').innerText = "Erro ao carregar patches: " + e.message;
            }}
        }}

        async function openPatch(link, title) {{
            document.getElementById('patch-list').style.display = 'none';
            document.getElementById('patch-viewer').style.display = 'block';
            document.getElementById('patch-viewer-title').innerText = title;
            document.getElementById('patch-content').innerText = "Carregando conteúdo do patch...";
            
            try {{
                const url = "https://api.codetabs.com/v1/proxy?quest=" + encodeURIComponent(link + "raw");
                const res = await fetch(url);
                const text = await res.text();
                document.getElementById('patch-content').innerText = text;
            }} catch (e) {{
                document.getElementById('patch-content').innerText = "Erro ao carregar patch: " + e.message;
            }}
        }}
    </script>
</body>
</html>
"""

with open('index.html', 'w') as f:
    f.write(template)

