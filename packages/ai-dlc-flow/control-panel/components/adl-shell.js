class AdlShell extends HTMLElement {
  constructor() {
    super();
    this.project = { name: "AI-DLC Flow" };
    this.view = "";
  }

  connectedCallback() {
    this.view = this.innerHTML;
    this.refresh();
  }

  refresh() {
    const route = this.getAttribute("route") || "overview";
    const navigationRoute = route.startsWith("intentions/") ? "overview" : route;
    const projectName = this.escape(this.project.name || "AI-DLC Flow");
    this.innerHTML = `
      <div class="app-shell">
        <header class="topbar">
          <a class="brand" href="#/overview" aria-label="Ir para a visão geral">
            <span class="brand-mark">AI</span>
            <span><strong>AI-DLC</strong><small>CONTROL PANEL</small></span>
          </a>
          <div class="topbar-project">
            <span>Projeto conectado</span>
            <strong>${projectName}</strong>
          </div>
          <span class="live-pill"><i></i> leitura local</span>
        </header>
        <div class="workspace">
          <aside class="sidebar" aria-label="Navegação do painel">
            <p class="sidebar-label">Navegar</p>
            ${this.link("overview", "Visão geral", "⌂", navigationRoute)}
            ${this.link("decisions", "Decisões", "◈", navigationRoute)}
            ${this.link("scope-b", "Escopo B", "B", navigationRoute)}
            <div class="sidebar-rule"></div>
            <p class="sidebar-label">Princípio</p>
            <p class="sidebar-help">O painel mostra estado observável. A intenção humana continua sendo a autoridade do fluxo.</p>
          </aside>
          <main class="main-content">${this.view}</main>
        </div>
      </div>
    `;
  }

  link(id, label, icon, route) {
    const active = id === route ? "active" : "";
    return `<a class="nav-link ${active}" href="#/${id}"><span class="nav-icon">${icon}</span>${label}</a>`;
  }

  escape(value) {
    return String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
  }
}

customElements.define("adl-shell", AdlShell);
