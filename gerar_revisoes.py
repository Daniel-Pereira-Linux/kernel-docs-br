#!/usr/bin/env python3
"""Gera a página revisoes.html para o site do Miguel."""

header = open('/tmp/global_header.html').read()

JS = """
<script>
fetch("data_reviews.json")
.then(function(r) { if (!r.ok) throw new Error("Sem dados"); return r.json(); })
.then(function(data) {
    var c = document.getElementById("reviews-container");
    c.innerHTML = "";
    if (data.length === 0) { c.innerHTML = "<p>Nenhum patch pt_BR recente encontrado no lore.</p>"; return; }
    data.forEach(function(p) {
        var cg = (p.status_git || "").indexOf("\\u274c") >= 0 ? "background:#ff5555;color:#fff;" : ((p.status_git || "").indexOf("\\u26a0") >= 0 ? "background:#ffaa00;color:#000;" : "background:#55ff55;color:#000;");
        var ee = p.erros_estrutura.length > 0 ? p.erros_estrutura.map(function(e) { return "<li class='error'>\\u274c " + e + "</li>"; }).join("") : "<li class='success'>\\u2705 Estrutura DCO perfeita.</li>";
        function esc(s) { return (s || "Sem dados.").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
        c.innerHTML += "<div class='card'>" +
            "<h3>" + esc(p.assunto) + "</h3>" +
            "<p style='font-size:11px'><b>Autor:</b> " + esc(p.autor) + " | <b>Data:</b> " + esc(p.data) + "</p>" +
            "<div class='badge' style='" + cg + "'>" + esc(p.status_git) + "</div>" +
            "<hr style='border:1px solid #444'>" +
            "<h4>Estrutura:</h4><ul>" + ee + "</ul>" +
            "<h4>1. Gramática (Gemini 2.5 Pro):</h4><div class='ai-text'>" + esc(p.revisao_ia) + "</div>" +
            "<h4>2. Checkpatch (.pl):</h4><div class='ai-text'>" + esc(p.checkpatch) + "</div>" +
            "<h4>3. Make htmldocs (Sphinx):</h4><div class='ai-text'>" + esc(p.sphinx) + "</div>" +
            "<div class='disclaimer'>\\u26a0\\ufe0f <b>Aviso:</b> O Miguel é uma ferramenta automatizada baseada em Inteligência Artificial. Ele pode cometer erros ou gerar falsos positivos. Verifique sempre o contexto.</div>" +
            "</div>";
    });
}).catch(function(e) { document.getElementById("reviews-container").innerHTML = "<p>" + e.message + "</p>"; });
</script>
"""

html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Revisões IA (Miguel)</title>
<link rel="stylesheet" type="text/css" href="style.css" />
<style>
body {{ background: #111; color: #eee; font-family: sans-serif; }}
.card {{ background: #1e1e1e; color: #fff; margin: 15px 0; padding: 15px; border-radius: 8px; border-left: 4px solid #b16286; font-family: monospace; }}
.card h3 {{ margin-top: 0; color: #ffaa00; font-size: 14px; }}
.error {{ color: #ff5555; }}
.success {{ color: #55ff55; }}
.ai-text {{ background: #2a2a2a; padding: 10px; border-radius: 4px; margin-top: 5px; white-space: pre-wrap; font-size: 12px; border: 1px solid #444; }}
.badge {{ display: inline-block; padding: 3px 6px; border-radius: 3px; font-weight: bold; font-size: 11px; margin-bottom: 10px; }}
.disclaimer {{ font-size: 10px; color: #999; margin-top: 15px; border-top: 1px dashed #555; padding-top: 10px; text-align: center; font-family: sans-serif; }}
</style>
</head><body>
{header}
<div id="content" style="padding: 20px;">
    <h2>Análises Automáticas da Lista (Gramática + Sphinx + Checkpatch)</h2>
    <div id="reviews-container">Carregando relatórios avançados da IA...</div>
</div>
{JS}
</body></html>
"""

with open('public/revisoes.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("revisoes.html gerado com sucesso!")
