class AdlDecisionTimeline extends HTMLElement {
  set items(value) {
    this._items = value || [];
    this.render();
  }

  render() {
    if (!this._items.length) {
      this.innerHTML = '<div class="empty-card"><strong>Nenhuma decisão encontrada</strong><p>O painel só apresenta decisões registradas no repo.</p></div>';
      return;
    }
    this.innerHTML = `
      <ol class="decision-timeline">
        ${this._items.map((item) => `
          <li class="decision-item">
            <span class="timeline-dot"></span>
            <div class="decision-date">
              <strong>${this.escape(this.formatDate(item.date))}</strong>
              <small>${this.escape(this.sourceLabel(item))}</small>
            </div>
            <div class="decision-content">
              <div class="card-topline"><span class="intention-id">${this.escape(item.id)}</span><span class="decision-status">${this.escape(item.status)}</span></div>
              <h3>${this.escape(item.title)}</h3>
              <p>${this.escape(item.summary)}</p>
              <code>${this.escape(item.path)}</code>
            </div>
          </li>
        `).join("")}
      </ol>
    `;
  }

  formatDate(value) {
    if (!value) return "data não registrada";
    const dateOnly = /^\d{4}-\d{2}-\d{2}$/.test(value);
    const date = dateOnly
      ? (() => {
          const [year, month, day] = value.split("-").map(Number);
          return new Date(year, month - 1, day);
        })()
      : new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium" }).format(date);
  }

  sourceLabel(item) {
    if (item.date_source === "documento") return "registrada no documento";
    if (item.date_source === "commit") return `inferida do commit ${item.commit || "Git"}`;
    return "data não encontrada";
  }

  escape(value) {
    return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
  }
}

customElements.define("adl-decision-timeline", AdlDecisionTimeline);
