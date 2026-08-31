import re

with open("index.html", "r") as f:
    html = f.read()

# Replace CSS
css_old = re.search(r'<style>.*?</style>', html, re.DOTALL)
if css_old:
    css_new = """<style>
        /* Utilitarian / Kernel.org inspired theme */
        :root {
            --bg-color: #ffffff;
            --text-color: #333333;
            --link-color: #0056b3;
            --header-bg: #f8f9fa;
            --header-border: #e9ecef;
            --nav-bg: #343a40;
            --nav-text: #ffffff;
            --nav-active: #ffcc00;
            --code-bg: #f4f4f4;
            --border-color: #cccccc;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: "Liberation Sans", Arial, sans-serif;
            line-height: 1.5;
            background: var(--bg-color);
            color: var(--text-color);
            font-size: 14px;
        }

        header {
            background: var(--header-bg);
            border-bottom: 1px solid var(--header-border);
            padding: 20px 40px;
        }
        
        header h1 {
            font-size: 24px;
            font-weight: normal;
            color: #000;
        }
        
        header p {
            font-size: 13px;
            color: #666;
            margin-top: 5px;
        }

        nav {
            background: var(--nav-bg);
            padding: 0 40px;
            display: flex;
        }

        nav a {
            color: var(--nav-text);
            text-decoration: none;
            padding: 10px 20px;
            font-size: 14px;
            cursor: pointer;
            border-top: 3px solid transparent;
        }

        nav a:hover {
            background: #495057;
        }

        nav a.active-tab {
            border-top-color: var(--nav-active);
            background: #212529;
            font-weight: bold;
        }

        .container {
            max-width: 1000px;
            margin: 20px auto;
            padding: 0 20px;
        }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* Banner */
        .kernel-banner {
            margin: 20px 40px;
            padding: 15px;
            border: 1px solid var(--border-color);
            background: #fff;
            display: none;
        }
        .kernel-banner.open { border-left: 5px solid #28a745; }
        .kernel-banner.closed { border-left: 5px solid #ffc107; }
        
        .banner-title { font-weight: bold; font-size: 15px; margin-bottom: 5px; }
        .banner-desc { font-size: 13px; color: #444; margin-bottom: 15px; }

        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid var(--border-color);
            padding: 6px 10px;
            text-align: left;
        }
        th { background: #f0f0f0; font-weight: bold; }
        
        /* Typography */
        h1, h2, h3 { margin: 20px 0 10px 0; font-weight: normal; }
        h1 { font-size: 22px; border-bottom: 1px solid var(--border-color); padding-bottom: 5px; }
        h2 { font-size: 18px; }
        p { margin-bottom: 15px; }
        
        a { color: var(--link-color); text-decoration: none; }
        a:hover { text-decoration: underline; }

        /* Code & Pre */
        pre, code {
            font-family: "Courier New", Courier, monospace;
            background: var(--code-bg);
            font-size: 13px;
        }
        pre {
            padding: 10px;
            border: 1px solid var(--border-color);
            overflow-x: auto;
            margin-bottom: 15px;
        }
        code { padding: 2px 4px; }
        pre code { padding: 0; background: none; }

        /* News Grid */
        .news-grid {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .news-card {
            border: 1px solid var(--border-color);
            padding: 15px;
            background: #fff;
        }
        .news-source {
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 5px;
            display: block;
        }
        .news-title {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .news-date {
            font-size: 11px;
            color: #888;
            margin-bottom: 10px;
        }
        .news-summary {
            font-size: 13px;
            color: #333;
        }
        .news-link {
            font-size: 12px;
            font-weight: bold;
            margin-top: 10px;
            display: inline-block;
        }

        /* Patches */
        .search-box {
            width: 100%;
            padding: 8px;
            border: 1px solid var(--border-color);
            margin-bottom: 15px;
            font-family: inherit;
        }
        .patch-list {
            list-style: none;
            border-top: 1px solid var(--border-color);
        }
        .patch-list li {
            padding: 10px 0;
            border-bottom: 1px solid var(--border-color);
            cursor: pointer;
        }
        .patch-list li:hover { background: #f9f9f9; }
        .patch-title { font-size: 14px; font-weight: bold; color: var(--link-color); }
        .patch-meta { font-size: 12px; color: #666; margin-top: 4px; }
        
        .patch-viewer {
            display: none;
            border: 1px solid var(--border-color);
            padding: 20px;
            background: #fff;
        }
        .patch-content {
            white-space: pre-wrap;
            background: #fff;
            color: #000;
            padding: 10px;
            border: 1px solid var(--border-color);
            margin-top: 15px;
            font-size: 12px;
            max-height: 600px;
            overflow-y: auto;
        }
        
        /* Basic Diff Colors */
        .diff-add { color: #008000; }
        .diff-del { color: #cc0000; }
        .diff-hunk { color: #0000cc; }
        .diff-file { font-weight: bold; }
        
        .btn {
            padding: 4px 10px;
            border: 1px solid var(--border-color);
            background: #f0f0f0;
            cursor: pointer;
            font-size: 12px;
            text-decoration: none;
            color: #000;
        }
        .btn:hover { background: #e0e0e0; }
        
        footer {
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: #666;
            border-top: 1px solid var(--border-color);
            margin-top: 40px;
        }
    </style>"""
    html = html[:css_old.start()] + css_new + html[css_old.end():]

# Remove emojis
html = html.replace("🐧 Kernel Docs BR", "Kernel Docs BR")
html = html.replace("📖 Documentação", "Documentação")
html = html.replace("📬 PATCHS", "Patches")
html = html.replace("📰 Notícias", "Notícias")
html = html.replace("📰 Últimas Notícias do Kernel", "Últimas Notícias do Kernel")
html = html.replace("👤 ", "Author: ")
html = html.replace("📅 ", "Date: ")
html = html.replace("🟢 ", "")
html = html.replace("🔒 ", "")
html = html.replace("⚠️ ", "")

with open("index.html", "w") as f:
    f.write(html)
print("Reformulated layout!")
