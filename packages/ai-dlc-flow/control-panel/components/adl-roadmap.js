class AdlRoadmap extends HTMLElement {
  set steps(value) {
    this._steps = value || [];
    this.render();
  }

  render() {
    if (!this._steps?.length) {
      this.innerHTML = '<div class="empty-inline">Lifecycle ainda não registrado.</div>';
      return;
    }
    this.innerHTML = `
      <ol class="roadmap">
        ${this._steps.map((step, index) => `
          <li class="roadmap-step roadmap-${step.status}">
            <span class="step-marker">${index + 1}</span>
            <span><strong>${this.escape(step.label)}</strong><small>${this.label(step.status)}</small></span>
          </li>
        `).join("")}
      </ol>
    `;
  }

  label(value) {
    return { done: "concluída", current: "agora", upcoming: "a seguir" }[value] || value;
  }

  escape(value) {
    return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
  }
}

customElements.define("adl-roadmap", AdlRoadmap);
