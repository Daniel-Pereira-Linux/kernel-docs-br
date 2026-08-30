#!/usr/bin/env python3
"""Gera a página revisoes.html com botão de análise pública via GitHub Issues."""

header = open('/tmp/global_header.html').read()

html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Revisões IA (Miguel)</title>
<link rel="stylesheet" type="text/css" href="style.css" />
<style>
body {{ background: #111; color: #eee; font-family: sans-serif; }}
.card {{ background: #1e1e1e; color: #fff; margin: 15px 0; padding: 15px; border-radius: 8px; border-left: 4px solid #b16286; font-family: monospace; }}
.card h3 {{ margin-top: 0; color: #ffaa00; font-size: 14px; word-break: break-word; }}
.error {{ color: #ff5555; }}
.success {{ color: #55ff55; }}
.ai-text {{ background: #2a2a2a; padding: 10px; border-radius: 4px; margin-top: 5px; white-space: pre-wrap; font-size: 12px; border: 1px solid #444; max-height: 300px; overflow-y: auto; }}
.badge {{ display: inline-block; padding: 4px 8px; border-radius: 3px; font-weight: bold; font-size: 11px; margin: 5px 2px; }}
.disclaimer {{ font-size: 10px; color: #999; margin-top: 15px; border-top: 1px dashed #555; padding-top: 10px; text-align: center; }}
.btn-analisar {{ background: #ff55ff; color: #000; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 13px; margin-top: 10px; text-decoration: none; display: inline-block; }}
.btn-analisar:hover {{ background: #ff88ff; }}
.badge-pendente {{ background: #555; color: #ccc; }}
.badge-analisado {{ background: #55ff55; color: #000; }}
.stats {{ font-size: 12px; color: #888; margin-bottom: 10px; }}
</style>
</head><body>
{header}
<div id="content" style="padding: 20px;">
    <h2>🤖 Miguel - Revisões de Patches pt_BR</h2>
    <p style="font-size:13px; color:#aaa;">Clique em "Analisar com IA" e você será redirecionado para o GitHub. Apenas clique em <b>Submit new issue</b> e o bot fará o resto!</p>
    <div class="stats" id="stats"></div>
    <div id="reviews-container">Carregando patches do Lore...</div>
</div>
<script>
function esc(s) {{ return (s || '').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }}

fetch('data_reviews.json?t=' + new Date().getTime())
.then(function(r) {{ if (!r.ok) throw new Error('Sem dados'); return r.json(); }})
.then(function(data) {{
    var c = document.getElementById('reviews-container');
    c.innerHTML = '';

    if (data.length === 0) {{ c.innerHTML = '<p>Nenhum patch pt_BR encontrado ainda. O bot roda a cada 30 minutos.</p>'; return; }}

    var analisados = data.filter(function(p) {{ return p.analisado; }}).length;
    document.getElementById('stats').innerHTML = '📊 ' + data.length + ' patches encontrados | ' + analisados + ' analisados | ' + (data.length - analisados) + ' pendentes';

    data.forEach(function(p) {{
        var isAnalised = p.analisado;
        var statusBadge = isAnalised
            ? '<span class="badge badge-analisado">\\u2705 Analisado</span>'
            : '<span class="badge badge-pendente">\\u23f3 Pendente</span>';

        var detalhes = '';
        var botao = '';

        if (isAnalised) {{
            var estrutErros = (p.erros_estrutura && p.erros_estrutura.length > 0)
                ? p.erros_estrutura.map(function(e) {{ return '<li class="error">\\u274c ' + e + '</li>'; }}).join('')
                : '<li class="success">\\u2705 Estrutura DCO perfeita.</li>';

            detalhes = '<hr style="border:1px solid #444">' +
                '<h4>Estrutura:</h4><ul>' + estrutErros + '</ul>' +
                '<h4>1. Gramática (Gemini):</h4><div class="ai-text">' + esc(p.revisao_ia) + '</div>' +
                '<h4>2. Checkpatch:</h4><div class="ai-text">' + esc(p.checkpatch) + '</div>' +
                '<h4>3. Sphinx:</h4><div class="ai-text">' + esc(p.sphinx) + '</div>' +
                '<div class="disclaimer">\\u26a0\\ufe0f O Miguel é uma IA e pode cometer erros. Verifique sempre.</div>';
        }} else {{
            var urlBase = "https://github.com/Daniel-Pereira-Linux/kernel-docs-br/issues/new";
            var titulo = encodeURIComponent("Miguel Analisar Patch " + p.message_id);
            var corpo = encodeURIComponent("Solicitação automática para analisar o patch: " + p.message_id + "\\n\\nNão edite o título. Apenas clique em Submit new issue.");
            botao = '<br><a class="btn-analisar" target="_blank" href="' + urlBase + '?title=' + titulo + '&body=' + corpo + '">\\ud83d\\udd0d Analisar com IA (Automático)</a>';
        }}

        c.innerHTML += '<div class="card">' +
            '<h3>' + esc(p.assunto) + '</h3>' +
            '<p style="font-size:11px"><b>Autor:</b> ' + esc(p.autor) + ' | <b>Data:</b> ' + esc(p.data) + '</p>' +
            statusBadge +
            (isAnalised ? '<span class="badge" style="background:#333;color:#ccc">' + esc(p.status_git) + '</span>' : '') +
            botao +
            detalhes +
            '</div>';
    }});
}}).catch(function(e) {{ document.getElementById('reviews-container').innerHTML = '<p>' + e.message + '</p>'; }});
</script></body></html>
"""

with open('public/revisoes.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("revisoes.html gerado com sucesso!")
