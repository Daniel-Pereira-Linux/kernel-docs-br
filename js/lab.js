/* KernelBase :: Laboratório LPI-101 — terminal Linux real no navegador via v86 (WebAssembly) */
(() => {
	'use strict';

	const LAB_CDN = "https://cdn.jsdelivr.net/gh/Daniel-Pereira-Linux/kernel-docs-br@lab-assets";

	// Estrutura seguindo os tópicos do exame LPIC-1 101 (LPI-101-500).
	// "flagSha256" evita deixar a resposta em texto puro no código-fonte.
	const TOPICS = [
		{
			name: "101 — Arquitetura do sistema",
			challenges: [
				{
					id: "101-1-hardware",
					objective: "101.1 Determinar e configurar hardware",
					title: "Mapeando o hardware",
					desc: "Descubra quantos núcleos de CPU e quanta RAM esta máquina tem, usando arquivos do <code>/proc</code>. A flag está em <code>/challenges/101-1-hardware/flag.txt</code>.",
					flagSha256: "6dac06ea6de876f6de7e321f8027732685c905daccf234f13721eef208404116",
					available: true,
				},
			],
		},
		{
			name: "101 — Boot e runlevels",
			challenges: [
				{ id: "101-2", objective: "101.2 Bootar o sistema", title: "Em breve", available: false },
				{ id: "101-3", objective: "101.3 Runlevels / boot targets", title: "Em breve", available: false },
			],
		},
		{
			name: "102 — Instalação e pacotes",
			challenges: [
				{ id: "102-1", objective: "102.1 Layout de disco", title: "Em breve", available: false },
				{ id: "102-2", objective: "102.2 Boot manager", title: "Em breve", available: false },
				{ id: "102-3", objective: "102.3 Bibliotecas compartilhadas", title: "Em breve", available: false },
				{ id: "102-4", objective: "102.4 dpkg / apt (Debian)", title: "Em breve", available: false },
				{ id: "102-5", objective: "102.5 rpm / yum", title: "Em breve", available: false },
				{ id: "102-6", objective: "102.6 Linux como guest de virtualização", title: "Em breve", available: false },
			],
		},
		{
			name: "103 — Comandos GNU/Unix",
			challenges: [
				{ id: "103-1", objective: "103.1 Linha de comando", title: "Em breve", available: false },
				{ id: "103-2", objective: "103.2 Filtros de texto", title: "Em breve", available: false },
				{ id: "103-3", objective: "103.3 Gerenciamento de arquivos", title: "Em breve", available: false },
				{ id: "103-4", objective: "103.4 Streams, pipes, redirects", title: "Em breve", available: false },
				{ id: "103-5", objective: "103.5 Processos", title: "Em breve", available: false },
				{ id: "103-6", objective: "103.6 Prioridade de execução", title: "Em breve", available: false },
				{ id: "103-7", objective: "103.7 Regex", title: "Em breve", available: false },
				{ id: "103-8", objective: "103.8 Edição com vi", title: "Em breve", available: false },
			],
		},
		{
			name: "104 — Dispositivos e filesystems",
			challenges: [
				{ id: "104-1", objective: "104.1 Partições e filesystems", title: "Em breve", available: false },
				{ id: "104-2", objective: "104.2 Integridade de filesystems", title: "Em breve", available: false },
				{ id: "104-3", objective: "104.3 Mount / umount", title: "Em breve", available: false },
				{ id: "104-5", objective: "104.5 Permissões e ownership", title: "Em breve", available: false },
				{ id: "104-6", objective: "104.6 Hard e symbolic links", title: "Em breve", available: false },
				{ id: "104-7", objective: "104.7 Localização de arquivos (FHS)", title: "Em breve", available: false },
			],
		},
	];

	let current = null;
	let emulator = null;
	let booted = false;

	function solvedSet() {
		try { return new Set(JSON.parse(localStorage.getItem("kb-lab-solved") || "[]")); }
		catch (e) { return new Set(); }
	}
	function saveSolved(set) {
		try { localStorage.setItem("kb-lab-solved", JSON.stringify([...set])); } catch (e) {}
	}

	async function sha256(text) {
		const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
		return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("");
	}

	function allChallenges() {
		return TOPICS.flatMap(t => t.challenges);
	}

	function renderSidebar() {
		const solved = solvedSet();
		const nav = document.getElementById("lab-nav");
		nav.innerHTML = "";
		TOPICS.forEach(topic => {
			const wrap = document.createElement("div");
			wrap.className = "lab-topic";
			const h4 = document.createElement("h4");
			h4.textContent = topic.name;
			wrap.appendChild(h4);
			topic.challenges.forEach(c => {
				const el = document.createElement("div");
				el.className = "lab-challenge" + (c.available ? "" : " locked") + (solved.has(c.id) ? " solved" : "") + (current === c.id ? " active" : "");
				el.innerHTML = `<span class="dot"></span>${c.title}`;
				if (c.available) el.onclick = () => selectChallenge(c.id);
				wrap.appendChild(el);
			});
			nav.appendChild(wrap);
		});

		const total = allChallenges().filter(c => c.available).length;
		const done = allChallenges().filter(c => c.available && solved.has(c.id)).length;
		document.getElementById("lab-progress").textContent =
			`${done}/${total} desafio(s) disponível(is) resolvido(s) — ${allChallenges().length - total} em construção`;
	}

	function selectChallenge(id) {
		current = id;
		const c = allChallenges().find(x => x.id === id);
		renderSidebar();
		const card = document.getElementById("lab-challenge-card");
		const solved = solvedSet().has(id);
		card.innerHTML = `
			<h3>${c.title}</h3>
			<div class="lab-objective">${c.objective}</div>
			<div class="lab-desc">${c.desc}</div>
			<div class="lab-flag-row">
				<input type="text" id="lab-flag-input" placeholder="kernelbase{...}" autocomplete="off" spellcheck="false">
				<button class="btn primary" id="lab-flag-submit">Enviar flag</button>
			</div>
			<div class="lab-flag-msg" id="lab-flag-msg">${solved ? "✓ já resolvido" : ""}</div>
		`;
		if (solved) card.querySelector(".lab-flag-msg").className = "lab-flag-msg ok";
		document.getElementById("lab-flag-submit").onclick = submitFlag;
		document.getElementById("lab-flag-input").addEventListener("keydown", e => {
			if (e.key === "Enter") submitFlag();
		});
	}

	async function submitFlag() {
		const c = allChallenges().find(x => x.id === current);
		const input = document.getElementById("lab-flag-input");
		const msg = document.getElementById("lab-flag-msg");
		const val = input.value.trim();
		if (!val) return;
		const hash = await sha256(val);
		if (hash === c.flagSha256) {
			const solved = solvedSet();
			solved.add(c.id);
			saveSolved(solved);
			msg.textContent = "✓ Flag correta!";
			msg.className = "lab-flag-msg ok";
			renderSidebar();
		} else {
			msg.textContent = "✗ Flag incorreta, tente de novo.";
			msg.className = "lab-flag-msg err";
		}
	}

	function loadScript(src) {
		return new Promise((resolve, reject) => {
			const s = document.createElement("script");
			s.src = src;
			s.onload = resolve;
			s.onerror = reject;
			document.head.appendChild(s);
		});
	}

	async function bootVM() {
		if (booted) return;
		booted = true;

		const startBtn = document.getElementById("lab-start-btn");
		const note = document.getElementById("lab-boot-note");
		startBtn.disabled = true;
		startBtn.textContent = "Carregando emulador...";
		note.textContent = "Baixando o motor do emulador (v86)...";

		try {
			await loadScript(`${LAB_CDN}/v86/libv86.js`);
		} catch (e) {
			note.textContent = "Erro ao carregar o emulador. Tente recarregar a página.";
			return;
		}

		startBtn.remove();
		note.textContent = "Bootando Alpine Linux... isso pode levar de 20s a 2min, dependendo do seu dispositivo. Acompanhe o log abaixo.";

		emulator = new V86({
			wasm_path: `${LAB_CDN}/v86/v86.wasm`,
			memory_size: 256 * 1024 * 1024,
			vga_memory_size: 8 * 1024 * 1024,
			screen_container: document.getElementById("screen_container"),
			bios: { url: `${LAB_CDN}/v86/seabios.bin` },
			vga_bios: { url: `${LAB_CDN}/v86/vgabios.bin` },
			filesystem: {
				baseurl: `${LAB_CDN}/images/alpine-rootfs-flat`,
				basefs: `${LAB_CDN}/images/alpine-fs.json`,
			},
			autostart: true,
			bzimage_initrd_from_filesystem: true,
			cmdline: "rw root=host9p rootfstype=9p rootflags=trans=virtio,version=9p2000.L,cache=loose modules=virtio_pci,9pnet,9pnet_virtio,9p",
		});

		emulator.add_listener("emulator-ready", () => {
			note.textContent = "Máquina virtual pronta. Clique na tela preta pra focar o teclado.";
		});
	}

	function resetVM() {
		if (emulator) {
			emulator.destroy();
			emulator = null;
		}
		booted = false;
		document.getElementById("screen_container").innerHTML = "";
		const note = document.getElementById("lab-boot-note");
		note.textContent = "Terminal reiniciado — sua sessão anterior foi destruída (nada fica salvo entre boots).";
		const btn = document.createElement("button");
		btn.className = "btn primary";
		btn.id = "lab-start-btn";
		btn.textContent = "Iniciar laboratório";
		btn.onclick = bootVM;
		document.getElementById("screen_container").appendChild(btn);
	}

	document.addEventListener("DOMContentLoaded", () => {
		renderSidebar();
		selectChallenge("101-1-hardware");
		document.getElementById("lab-start-btn").onclick = bootVM;
		document.getElementById("lab-reset-btn").onclick = resetVM;
	});
})();
