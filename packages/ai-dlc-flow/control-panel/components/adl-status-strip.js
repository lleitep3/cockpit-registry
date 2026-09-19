class AdlStatusStrip extends HTMLElement {
  set metrics(value) {
    this._metrics = value || {};
    this.render();
  }

  render() {
    const items = [
      ["Intenções", this._metrics.intentions, "trilhas registradas", ""],
      ["Bloqueios", this._metrics.blockers, "pedem atenção", "warning"],
      ["Decisões", this._metrics.decisions, "registros encontrados", ""],
      ["Documentos", this._metrics.documents, "fontes versionadas", ""],
    ];
    this.innerHTML = `
      <section class="status-strip" aria-label="Resumo do projeto">
        ${items.map(([label, value, detail, tone]) => `
          <div class="status-strip-item ${tone ? `status-strip-${tone}` : ""}">
            <span>${this.escape(label)}</span>
            <strong>${this.escape(value ?? "—")}</strong>
            <small>${this.escape(detail)}</small>
          </div>
        `).join("")}
      </section>
    `;
  }

  escape(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }
}

customElements.define("adl-status-strip", AdlStatusStrip);
