class AdlScopePage extends HTMLElement {
  set scope(value) {
    this._scope = value || {};
    this.render();
  }

  render() {
    const scope = this._scope;
    this.innerHTML = `
      <article class="panel scope-panel page-enter">
        <div class="scope-hero">
          <span class="scope-letter">MVP</span>
          <div><p class="eyebrow">objetivo em validação</p><h2>${this.escape(scope.title || "Escopo atual")}</h2><p>${this.escape(scope.summary || "Resumo ainda não registrado.")}</p></div>
        </div>
        <div class="scope-source"><span>Fonte</span><code>${this.escape(scope.source || "não encontrada")}</code></div>
        <div class="markdown-content">${this.markdown(scope.content || "")}</div>
      </article>
    `;
  }

  markdown(value) {
    if (!value) return '<p class="empty-inline">O documento do escopo atual ainda não foi encontrado.</p>';
    const lines = value.split("\n");
    const output = [];
    let listOpen = false;
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) {
        if (listOpen) { output.push("</ul>"); listOpen = false; }
        continue;
      }
      if (trimmed.startsWith("#")) {
        if (listOpen) { output.push("</ul>"); listOpen = false; }
        const level = Math.min(trimmed.match(/^#+/)[0].length + 1, 4);
        output.push(`<h${level}>${this.inline(trimmed.replace(/^#+\s*/, ""))}</h${level}>`);
      } else if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        if (!listOpen) { output.push("<ul>"); listOpen = true; }
        output.push(`<li>${this.inline(trimmed.slice(2))}</li>`);
      } else if (!trimmed.startsWith("|")) {
        if (listOpen) { output.push("</ul>"); listOpen = false; }
        output.push(`<p>${this.inline(trimmed)}</p>`);
      }
    }
    if (listOpen) output.push("</ul>");
    return output.join("");
  }

  inline(value) {
    return this.escape(value).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/`(.+?)`/g, "<code>$1</code>");
  }

  escape(value) {
    return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
  }
}

customElements.define("adl-scope-page", AdlScopePage);
