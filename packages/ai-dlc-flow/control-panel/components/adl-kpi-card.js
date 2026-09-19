class AdlKpiCard extends HTMLElement {
  connectedCallback() {
    const tone = this.getAttribute("tone") || "default";
    this.innerHTML = `
      <article class="kpi-card kpi-${tone}">
        <span class="kpi-label">${this.escape(this.getAttribute("label"))}</span>
        <strong class="kpi-value">${this.escape(this.getAttribute("value"))}</strong>
        <span class="kpi-detail">${this.escape(this.getAttribute("detail"))}</span>
      </article>
    `;
  }

  escape(value) {
    return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
  }
}

customElements.define("adl-kpi-card", AdlKpiCard);
