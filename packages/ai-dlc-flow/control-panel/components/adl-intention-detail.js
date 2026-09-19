class AdlIntentionDetail extends HTMLElement {
  set item(value) {
    this._item = value;
    this.render();
  }

  set intentions(value) {
    this._intentions = value || [];
    this.render();
  }

  render() {
    const item = this._item;
    if (!item) return;
    const history = Array.isArray(item.history) ? item.history : [];
    const workUnits = Array.isArray(item.work_units) ? item.work_units : [];
    const otherIntentions = (this._intentions || []).filter((entry) => entry.id !== item.id);
    this.innerHTML = `
      <section class="journey-columns">
        <article class="journey-lane journey-past">
          <div class="lane-heading"><span class="lane-marker">✓</span><div><p class="eyebrow">o que já passou</p><h2>Histórico da intenção</h2></div></div>
          ${history.length ? `<ol class="mini-timeline">${history.map((entry) => `<li><strong>${this.escape(entry.title || entry.label || "Marco registrado")}</strong><span>${this.escape(entry.detail || entry.date || "Evidência registrada no repo.")}</span></li>`).join("")}</ol>` : '<p class="empty-inline">Nenhum marco anterior foi registrado para esta intenção.</p>'}
        </article>
        <article class="journey-lane journey-now">
          <div class="lane-heading"><span class="lane-marker">↗</span><div><p class="eyebrow">o que está em construção</p><h2>Work units vinculadas</h2></div></div>
          ${workUnits.length ? `<div class="work-list">${workUnits.map((unit) => `<button type="button" class="work-item" data-work-unit-id="${this.escape(unit.id || "WU")}" aria-label="Abrir contexto da ${this.escape(unit.id || "work unit")}"><span>${this.escape(unit.id || "WU")}</span><strong>${this.escape(unit.title || unit.objective || "Work unit")}</strong><small>${this.escape(unit.state_label || unit.state || "estado não registrado")}</small><em>Abrir contexto →</em></button>`).join("")}</div>` : '<p class="empty-inline">Nenhuma work unit em construção foi registrada para esta intenção.</p>'}
        </article>
        <article class="journey-lane journey-next">
          <div class="lane-heading"><span class="lane-marker">01</span><div><p class="eyebrow">próximo movimento</p><h2>O que desbloqueia avanço</h2></div></div>
          <p class="next-copy">${this.escape(item.next_action || "Próximo movimento ainda não registrado.")}</p>
          <div class="detail-meta"><span>Fase<strong>${this.escape(item.phase)}</strong></span><span>Gate<strong>${this.escape(item.gate)}</strong></span><span>Responsável<strong>${this.escape(item.owner)}</strong></span></div>
        </article>
      </section>
      <section class="panel intention-navigation">
        <div class="panel-heading"><div><p class="eyebrow">continuar navegando</p><h2>Outras intenções</h2></div><a class="text-link" href="#/overview">Ver todas →</a></div>
        <div class="other-intentions">${otherIntentions.length ? otherIntentions.map((entry) => `<a href="#/intentions/${encodeURIComponent(entry.id)}" class="other-intention"><span>${this.escape(entry.id)}</span><strong>${this.escape(entry.title)}</strong><small>${this.escape(entry.state)}</small></a>`).join("") : '<span class="empty-inline">Esta é a única intenção registrada.</span>'}</div>
      </section>
    `;
    this.querySelectorAll("[data-work-unit-id]").forEach((workItem) => {
      workItem.addEventListener("click", () => {
        const unit = workUnits.find((entry) => entry.id === workItem.dataset.workUnitId);
        if (unit) this.openWorkUnit(unit);
      });
    });
  }

  openWorkUnit(unit) {
    const modal = document.createElement("div");
    modal.className = "modal-backdrop work-unit-modal";
    const context = this.contextText(unit);
    const list = (items, empty = "nenhum registrado") =>
      Array.isArray(items) && items.length
        ? `<ul>${items.map((item) => `<li>${this.escape(item)}</li>`).join("")}</ul>`
        : `<p class="context-empty">${empty}</p>`;
    modal.innerHTML = `
      <section class="modal-dialog" role="dialog" aria-modal="true" aria-labelledby="work-unit-modal-title">
        <div class="modal-header">
          <div>
            <p class="eyebrow">work unit selecionada</p>
            <h2 id="work-unit-modal-title">${this.escape(unit.id)} · ${this.escape(unit.state_label || unit.state)}</h2>
            <p class="modal-subtitle">${this.escape(unit.title || "Work unit")}</p>
          </div>
          <button type="button" class="modal-close" data-close-work-unit aria-label="Fechar">×</button>
        </div>
        <div class="work-unit-context">
          <div class="modal-meta">
            <span>Ciclo: ${this.escape(unit.lifecycle || "não definido")}</span>
            <span>Responsável: ${this.escape(unit.owner || "não definido")}</span>
            <span>Saída: ${this.escape(unit.exit_gate || "não definido")}</span>
          </div>
          <article class="context-highlight">
            <p class="eyebrow">próximo movimento</p>
            <p>${this.escape(unit.next_action || "Não registrado")}</p>
          </article>
          <div class="context-grid">
            <section class="context-section"><h3>Entradas e contexto</h3>${list(unit.inputs, "nenhuma entrada vinculada")}</section>
            <section class="context-section"><h3>Dependências</h3>${list(unit.dependencies)}</section>
            <section class="context-section"><h3>Bloqueios</h3>${list(unit.blockers)}</section>
            <section class="context-section"><h3>Critérios de aceite</h3>${list(unit.acceptance_criteria, "nenhum critério registrado")}</section>
            <section class="context-section"><h3>Evidências exigidas</h3>${list(unit.evidence_required, "nenhuma evidência registrada")}</section>
          </div>
        </div>
        <div class="modal-actions context-actions">
          <button type="button" class="button button-primary" data-copy-work-unit>Copiar contexto da work unit</button>
          <span class="copy-feedback" aria-live="polite"></span>
        </div>
      </section>
    `;
    document.body.append(modal);

    const close = () => {
      document.removeEventListener("keydown", onKeyDown);
      modal.remove();
    };
    const onKeyDown = (event) => {
      if (event.key === "Escape") close();
    };
    modal.querySelector("[data-close-work-unit]").addEventListener("click", close);
    modal.addEventListener("click", (event) => {
      if (event.target === modal) close();
    });
    modal.querySelector("[data-copy-work-unit]").addEventListener("click", () => {
      this.copy(context, modal.querySelector(".copy-feedback"));
    });
    document.addEventListener("keydown", onKeyDown);
    modal.querySelector("[data-close-work-unit]").focus();
  }

  contextText(unit) {
    return [
      `Work unit: ${unit.id} — ${unit.title}`,
      `Estado: ${unit.state_label || unit.state}`,
      `Ciclo: ${unit.lifecycle || "não definido"}`,
      `Responsável: ${unit.owner || "não definido"}`,
      `Saída: ${unit.exit_gate || "não definido"}`,
      `Próximo movimento: ${unit.next_action || "não registrado"}`,
      `Entradas: ${(unit.inputs || []).join(", ") || "nenhuma"}`,
      `Dependências: ${(unit.dependencies || []).join(", ") || "nenhuma"}`,
      `Bloqueios: ${(unit.blockers || []).join(", ") || "nenhum"}`,
      `Critérios de aceite: ${(unit.acceptance_criteria || []).join("; ") || "não registrados"}`,
      `Evidências exigidas: ${(unit.evidence_required || []).join(", ") || "nenhuma"}`,
    ].join("\n");
  }

  async copy(value, feedback) {
    try {
      await navigator.clipboard.writeText(value);
      feedback.textContent = "Copiado para a área de transferência.";
    } catch (error) {
      feedback.textContent = "Não foi possível copiar automaticamente.";
    }
  }

  escape(value) {
    return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
  }
}

customElements.define("adl-intention-detail", AdlIntentionDetail);
