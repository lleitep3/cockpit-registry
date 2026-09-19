class AdlIntentionCard extends HTMLElement {
  set item(value) {
    this._item = value;
    this.render();
  }

  set focused(value) {
    this._focused = value;
    this.render();
  }

  render() {
    if (!this._item) return;
    const item = this._item;
    const blockerCount = Array.isArray(item.blockers) ? item.blockers.length : 0;
    const sharedBlockerCount = Array.isArray(item.blockers)
      ? item.blockers.filter((blocker) => blocker.scope === "shared" || blocker.scope === "project").length
      : 0;
    const dependencyCount = Array.isArray(item.dependencies) ? item.dependencies.length : 0;
    this.innerHTML = `
      <a class="intention-card-link" href="#/intentions/${encodeURIComponent(item.id)}">
      <article class="intention-card ${this._focused ? "is-focused" : ""}">
        <div class="card-topline">
          <span class="intention-id">${this.escape(item.id)}</span>
          <span class="state-badge state-${this.escape(item.state)}">${this.label(item.state)}</span>
        </div>
        <h3>${this.escape(item.title)}</h3>
        <p>${this.escape(item.objective)}</p>
        <div class="intention-progress">
          <span>Fase</span><strong>${this.escape(item.phase)}</strong>
          <span>Gate</span><strong>${this.escape(item.gate)}</strong>
        </div>
        <div class="card-footer">
          <span>${blockerCount ? `${blockerCount} blocker(s)` : "sem blocker local"}</span>
          ${sharedBlockerCount ? `<span class="shared-blocker">${sharedBlockerCount} compartilhado</span>` : ""}
          <span>${dependencyCount} dependência(s)</span>
        </div>
        <div class="next-action"><small>Próximo movimento</small><strong>${this.escape(item.next_action)}</strong></div>
      </article>
      </a>
    `;
  }

  label(value) {
    return { active: "ativa", blocked: "bloqueada", waiting: "aguardando", completed: "concluída", parked: "pausada", proposed: "proposta", superseded: "substituída", current: "atual", in_review: "em revisão" }[value] || value;
  }

  escape(value) {
    return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
  }
}

customElements.define("adl-intention-card", AdlIntentionCard);
