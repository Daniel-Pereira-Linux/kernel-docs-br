#!/usr/bin/env python3
"""Gera a página revisoes.html com botão de análise por patch."""

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
.btn-analisar {{ background: #ff55ff; color: #000; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 13px; margin-top: 10px; }}
.btn-analisar:hover {{ background: #ff88ff; }}
.btn-analisar:disabled {{ background: #555; color: #999; cursor: not-allowed; }}
.badge-pendente {{ background: #555; color: #ccc; }}
.badge-analisado {{ background: #55ff55; color: #000; }}
.config-bar {{ background: #1a1a1a; padding: 10px 15px; border-radius: 4px; margin-bottom: 15px; font-size: 12px; }}
.config-bar input {{ background: #2a2a2a; color: #fff; border: 1px solid #444; padding: 5px 10px; border-radius: 3px; font-family: monospace; width: 300px; }}
.config-bar button {{ background: #55ff55; color: #000; border: none; padding: 5px 12px; border-radius: 3px; font-weight: bold; cursor: pointer; margin-left: 5px; }}
.stats {{ font-size: 12px; color: #888; margin-bottom: 10px; }}
</style>
</head><body>
{header}
<div id="content" style="padding: 20px;">
    <h2>🤖 Miguel - Revisões de Patches pt_BR</h2>

    <div class="config-bar">
        <label>🔑 Token GitHub (salvo apenas no seu navegador):
        <input type="password" id="gh-token" placeholder="ghp_xxxx..." />
        <button onclick="salvarToken()">Salvar</button>
        <button onclick="limparToken()" style="background:#ff5555;">Limpar</button>
        </label>
        <span id="token-status" style="margin-left:10px;"></span>
    </div>

    <div class="stats" id="stats"></div>
    <div id="reviews-container">Carregando patches do Lore...</div>
</div>
<script>
function salvarToken() {{
    var t = document.getElementById('gh-token').value.trim();
    if (t) {{ localStorage.setItem('gh_pat', t); atualizarTokenStatus(); }}
}}
function limparToken() {{
    localStorage.removeItem('gh_pat');
    document.getElementById('gh-token').value = '';
    atualizarTokenStatus();
}}
function atualizarTokenStatus() {{
    var el = document.getElementById('token-status');
    if (localStorage.getItem('gh_pat')) {{
        el.innerHTML = '<span style="color:#55ff55">\\u2705 Token salvo (apenas neste navegador)</span>';
    }} else {{
        el.innerHTML = '<span style="color:#ff5555">\\u274c Sem token. Cole o seu GitHub PAT para usar o botão Analisar.</span>';
    }}
}}

function analisar(msgId, btn) {{
    var token = localStorage.getItem('gh_pat');
    if (!token) {{ alert('Configure seu token do GitHub primeiro!'); return; }}

    btn.disabled = true;
    btn.textContent = '\\u23f3 Disparando análise...';

    fetch('https://api.github.com/repos/Daniel-Pereira-Linux/kernel-docs-br/actions/workflows/revisor.yml/dispatches', {{
        method: 'POST',
        headers: {{
            'Accept': 'application/vnd.github+json',
            'Authorization': 'Bearer ' + token,
            'X-GitHub-Api-Version': '2022-11-28'
        }},
        body: JSON.stringify({{ ref: 'docs-next', inputs: {{ message_id: msgId }} }})
    }}).then(function(r) {{
        if (r.status === 204) {{
            btn.textContent = '\\u2705 Análise disparada! Aguarde ~2min e recarregue.';
            btn.style.background = '#55ff55';
        }} else {{
            btn.textContent = '\\u274c Erro ' + r.status + '. Verifique o token.';
            btn.style.background = '#ff5555';
            btn.disabled = false;
        }}
    }}).catch(function(e) {{
        btn.textContent = '\\u274c Erro de rede';
        btn.disabled = false;
    }});
}}

function esc(s) {{ return (s || '').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }}

fetch('data_reviews.json')
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
        }}

        var botao = isAnalised
            ? ''
            : '<button class="btn-analisar" onclick="analisar(\\'' + esc(p.message_id).replace(/'/g, "\\\\'") + '\\', this)">\\ud83d\\udd0d Analisar com IA</button>';

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

atualizarTokenStatus();
</script></body></html>
"""

with open('public/revisoes.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("revisoes.html gerado com sucesso!")
