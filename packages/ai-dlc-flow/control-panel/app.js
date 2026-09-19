import "./components/adl-shell.js";
import "./components/adl-status-strip.js";
import "./components/adl-intention-card.js";
import "./components/adl-intention-detail.js";
import "./components/adl-roadmap.js";
import "./components/adl-decision-timeline.js";
import "./components/adl-scope-page.js";
import "./components/adl-gate-board.js";

const app = document.querySelector("#app");
let state = null;

function route() {
  return window.location.hash.replace(/^#\/?/, "") || "overview";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDate(value) {
  if (!value) return "não registrada";
  const dateOnly = /^\d{4}-\d{2}-\d{2}$/.test(value);
  const date = dateOnly
    ? (() => {
        const [year, month, day] = value.split("-").map(Number);
        return new Date(year, month - 1, day);
      })()
    : new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "medium",
  }).format(date);
}

function renderOverview() {
  const { project, intentions } = state;
  const focus = intentions.find(
    (item) => item.id === project.focus_intention_id,
  );
  return `
    <section class="page-enter page-heading">
      <div>
        <p class="eyebrow">controle do fluxo</p>
        <h1>${escapeHtml(project.name)}</h1>
        <p>${escapeHtml(project.summary)}</p>
      </div>
      <div class="project-start">
        <span>Projeto iniciado em</span>
        <strong>${escapeHtml(formatDate(project.started_at))}</strong>
      </div>
    </section>
    <adl-status-strip></adl-status-strip>
    <section class="section-heading" id="portfolio">
      <div>
        <p class="eyebrow">portfólio</p>
        <h2>Intenções caminhando em paralelo</h2>
      </div>
      <span class="section-note">${intentions.length ? "Cada trilha tem seu próprio próximo movimento" : "Registre as primeiras intenções no repo"}</span>
    </section>
    <section class="intention-grid">
      ${intentions.length ? intentions.map((item) => `<adl-intention-card></adl-intention-card>`).join("") : `
        <div class="empty-card">
          <strong>Nenhuma intenção registrada ainda</strong>
          <p>O painel não inventa trabalho. Adicione intenções ao contrato do AI-DLC para abrir as trilhas do projeto.</p>
        </div>
      `}
    </section>
    <section class="panel gate-panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">controle dos gates</p>
          <h2>Onde está concentrado o trabalho</h2>
        </div>
        <span class="section-note">Volume de work units por etapa</span>
      </div>
      <adl-gate-board></adl-gate-board>
    </section>
    <section class="overview-grid">
      <article class="panel panel-dark">
        <div class="panel-heading">
          <div>
            <p class="eyebrow">foco operacional</p>
            <h2>${focus ? escapeHtml(focus.title) : "Nenhuma intenção em foco"}</h2>
          </div>
          <span class="focus-mark">${focus ? "FOCO" : "—"}</span>
        </div>
        <p>${focus ? escapeHtml(focus.next_action) : "Selecione uma intenção quando houver trabalho pronto para avançar."}</p>
        ${focus ? `<div class="focus-meta"><span>${escapeHtml(focus.gate)}</span><span>${escapeHtml(focus.owner)}</span></div>` : ""}
      </article>
      <article class="panel">
        <div class="panel-heading">
          <div>
            <p class="eyebrow">jornada selecionada</p>
            <h2>Lifecycle do foco</h2>
          </div>
          <a class="text-link" href="#/scope-b">Ver escopo B →</a>
        </div>
        <adl-roadmap></adl-roadmap>
      </article>
    </section>
  `;
}

function renderDecisions() {
  return `
    <section class="page-enter page-heading">
      <div>
        <p class="eyebrow">memória do projeto</p>
        <h1>Histórico de decisões</h1>
        <p>O painel apresenta decisões registradas no repositório, sem transformar atividade de agente em aprovação humana.</p>
      </div>
    </section>
    <section class="panel decision-panel">
      <adl-decision-timeline></adl-decision-timeline>
    </section>
  `;
}

function renderScope() {
  return `
    <section class="page-enter page-heading">
      <div>
        <p class="eyebrow">intenção em detalhe</p>
        <h1>Escopo B</h1>
        <p>Uma leitura operacional do objetivo, da fonte e das pendências do recorte.</p>
      </div>
    </section>
    <adl-scope-page></adl-scope-page>
  `;
}

function renderIntentionDetail(item) {
  return `
    <section class="page-enter page-heading">
      <div>
        <a class="back-link" href="#/overview">← Voltar ao portfólio</a>
        <p class="eyebrow">intenção selecionada</p>
        <h1>${escapeHtml(item.title)}</h1>
        <p>${escapeHtml(item.objective || "Objetivo ainda não registrado.")}</p>
      </div>
      <span class="state-badge state-${escapeHtml(item.state)}">${escapeHtml(item.state)}</span>
    </section>
    <adl-intention-detail></adl-intention-detail>
  `;
}

function renderPage() {
  const currentRoute = route();
  const intentionMatch = currentRoute.match(/^intentions\/(.+)$/);
  const selectedIntention = intentionMatch
    ? state.intentions.find((item) => item.id === decodeURIComponent(intentionMatch[1]))
    : null;
  const view = currentRoute === "decisions"
    ? renderDecisions()
    : currentRoute === "scope-b"
      ? renderScope()
      : selectedIntention
        ? renderIntentionDetail(selectedIntention)
        : renderOverview();
  app.innerHTML = `<adl-shell route="${escapeHtml(currentRoute)}">${view}</adl-shell>`;
  const shell = app.querySelector("adl-shell");
  shell.project = state.project;
  shell.refresh();
  const statusStrip = app.querySelector("adl-status-strip");
  if (statusStrip) {
    statusStrip.metrics = {
      intentions: intentionsCount(state.intentions),
      blockers: state.intentions.reduce(
        (total, item) => total + (Array.isArray(item.blockers) ? item.blockers.length : 0),
        0,
      ),
      decisions: state.signals.decisions,
      documents: state.signals.documents,
    };
  }
  const roadmap = app.querySelector("adl-roadmap");
  if (roadmap) roadmap.steps = state.roadmap;
  const gateBoard = app.querySelector("adl-gate-board");
  if (gateBoard) {
    gateBoard.project = state.project;
    gateBoard.gates = state.gates;
  }
  const decisionTimeline = app.querySelector("adl-decision-timeline");
  if (decisionTimeline) decisionTimeline.items = state.decisions;
  const scopePage = app.querySelector("adl-scope-page");
  if (scopePage) scopePage.scope = state.scope_b;
  const intentionDetail = app.querySelector("adl-intention-detail");
  if (intentionDetail) {
    intentionDetail.item = selectedIntention;
    intentionDetail.intentions = state.intentions;
  }
  const intentionCards = app.querySelectorAll("adl-intention-card");
  intentionCards.forEach((card, index) => {
    card.item = state.intentions[index];
    card.focused = state.intentions[index]?.id === state.project.focus_intention_id;
  });
}

function intentionsCount(items) {
  return Array.isArray(items) ? items.length : 0;
}

async function load() {
  try {
    const response = await fetch("./api/project", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state = await response.json();
    renderPage();
  } catch (error) {
    app.innerHTML = `<div class="error-state"><strong>Não foi possível ler o projeto.</strong><span>${escapeHtml(error.message)}</span></div>`;
  }
}

window.addEventListener("hashchange", () => state && renderPage());
load();
