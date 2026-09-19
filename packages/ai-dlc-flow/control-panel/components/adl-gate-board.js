class AdlGateBoard extends HTMLElement {
  set gates(value) {
    this._gates = Array.isArray(value) ? value : [];
    this.render();
  }

  set project(value) {
    this._project = value || {};
  }

  render() {
    const gates = this._gates || [];
    if (!gates.length) {
      this.innerHTML = '<div class="empty-inline">Gates ainda não registrados.</div>';
      return;
    }
    const workUnitTotal = gates.reduce(
      (total, gate) => total + (Array.isArray(gate.work_units) ? gate.work_units.length : 0),
      0,
    );
    this.innerHTML = `
      <div class="gate-board-summary">
        <span><strong>${gates.length}</strong> gates registrados</span>
        <span><strong>${workUnitTotal}</strong> vínculos de work unit</span>
      </div>
      <div class="gate-grid">
        ${gates.map((gate) => `
          <button type="button" class="gate-card gate-${this.escape(gate.state)}" data-gate-id="${this.escape(gate.id)}" aria-label="Abrir detalhes do ${this.escape(gate.id)}">
            <div class="gate-card-topline">
              <span class="gate-id">${this.escape(gate.id)}</span>
              <span class="state-badge state-${this.escape(gate.state)}">${this.escape(gate.state_label)}</span>
            </div>
            <h3>${this.escape(gate.work_units?.length || 0)} work units</h3>
            <p>${this.escape(gate.authority)}</p>
            <div class="gate-work-units">
              ${(gate.work_units || []).map((unit) => `<span>${this.escape(unit)}</span>`).join("") || "<span>sem work unit vinculada</span>"}
            </div>
            <span class="gate-card-hint">Abrir detalhes →</span>
          </button>
        `).join("")}
      </div>
    `;
    this.querySelectorAll("[data-gate-id]").forEach((card) => {
      card.addEventListener("click", () => {
        const gate = gates.find((item) => item.id === card.dataset.gateId);
        if (gate) this.openModal(gate);
      });
    });
  }

  openModal(gate) {
    const workUnits = gate.work_unit_details || [];
    const context = this.contextText(gate, workUnits);
    const prompt = this.agentPrompt(gate, workUnits);
    const modal = document.createElement("div");
    modal.className = "modal-backdrop";
    modal.innerHTML = `
      <section class="modal-dialog" role="dialog" aria-modal="true" aria-labelledby="gate-modal-title">
        <div class="modal-header">
          <div>
            <p class="eyebrow">gate selecionado</p>
            <h2 id="gate-modal-title">${this.escape(gate.id)} · ${this.escape(gate.state_label)}</h2>
            <p class="modal-subtitle">${this.escape(gate.authority)} · ${(gate.work_units || []).length} work unit(s) vinculada(s)</p>
          </div>
          <button type="button" class="modal-close" data-close-modal aria-label="Fechar">×</button>
        </div>
        <div class="modal-work-list">
          ${workUnits.length ? workUnits.map((unit) => `
            <article class="modal-work-unit">
              <div class="modal-work-topline">
                <span class="gate-id">${this.escape(unit.id)}</span>
                <span class="state-badge state-${this.escape(unit.state)}">${this.escape(unit.state_label)}</span>
              </div>
              <h3>${this.escape(unit.title)}</h3>
              <p><strong>Próximo movimento:</strong> ${this.escape(unit.next_action)}</p>
              <div class="modal-meta">
                <span>Saída: ${this.escape(unit.exit_gate)}</span>
                <span>Blockers: ${unit.blockers.length}</span>
                <span>Dependências: ${unit.dependencies.length}</span>
              </div>
              ${unit.acceptance_criteria.length ? `<details><summary>Critérios de aceite</summary><ul>${unit.acceptance_criteria.map((item) => `<li>${this.escape(item)}</li>`).join("")}</ul></details>` : ""}
            </article>
          `).join("") : `<p class="empty-inline">Os detalhes das work units ainda não foram registrados.</p>`}
        </div>
        <div class="agent-action">
          <div>
            <p class="eyebrow">próxima atuação</p>
            <h3>Converse com a IA sobre este gate</h3>
            <p class="modal-help">Edite o pedido se quiser e copie o contexto para qualquer agente compatível com o seu fluxo.</p>
          </div>
          <textarea class="agent-prompt" aria-label="Pedido para a IA">${this.escape(prompt)}</textarea>
          <div class="modal-actions">
            <button type="button" class="button button-primary" data-copy-prompt>Copiar pedido para a IA</button>
            <button type="button" class="button button-secondary" data-copy-context>Copiar contexto</button>
          </div>
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
    modal.querySelector("[data-close-modal]").addEventListener("click", close);
    modal.addEventListener("click", (event) => {
      if (event.target === modal) close();
    });
      modal.querySelector("[data-copy-prompt]").addEventListener("click", () => {
        this.copy(modal.querySelector(".agent-prompt").value, modal.querySelector(".copy-feedback"));
      });
    modal.querySelector("[data-copy-context]").addEventListener("click", () => {
      this.copy(context, modal.querySelector(".copy-feedback"));
    });
    document.addEventListener("keydown", onKeyDown);
    modal.querySelector(".agent-prompt").focus();
  }

  contextText(gate, workUnits) {
    return [
      `Gate: ${gate.id} (${gate.state_label})`,
      `Autoridade: ${gate.authority}`,
      "",
      "Work units:",
      ...workUnits.map((unit) => [
        `${unit.id} — ${unit.title}`,
        `Estado: ${unit.state_label}`,
        `Próximo movimento: ${unit.next_action}`,
        `Blockers: ${unit.blockers.join(", ") || "nenhum registrado"}`,
        `Critérios: ${unit.acceptance_criteria.join("; ") || "não registrados"}`,
      ].join("\n")),
    ].join("\n");
  }

  agentPrompt(gate, workUnits) {
    const projectName = this._project.name || "o projeto";
    return [
      `Atue no ${projectName} respeitando o processo AI-DLC e o gate ${gate.id}.`,
      "Leia primeiro AGENTS.md, o estado canônico, as work units e os artefatos referenciados.",
      "Não invente decisões clínicas; se faltar autoridade humana, registre a pergunta e pare nesse limite.",
      "",
      `Gate: ${gate.id} (${gate.state_label})`,
      `Work units: ${workUnits.map((unit) => `${unit.id} — ${unit.title}`).join("; ") || "não detalhadas"}`,
      `Próximos movimentos: ${workUnits.map((unit) => `${unit.id}: ${unit.next_action}`).join(" | ") || "não registrados"}`,
      "",
      "Meu pedido adicional:",
      "",
    ].join("\n");
  }

  async copy(value, feedback) {
    try {
      await navigator.clipboard.writeText(value);
      feedback.textContent = "Copiado para a área de transferência.";
    } catch (error) {
      feedback.textContent = "Não foi possível copiar automaticamente; selecione o texto acima.";
    }
  }

  escape(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }
}

customElements.define("adl-gate-board", AdlGateBoard);
