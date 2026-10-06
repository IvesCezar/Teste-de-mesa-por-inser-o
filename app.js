const form = document.querySelector("#sort-form");
const input = document.querySelector("#numbers");
const rowsElement = document.querySelector("#trace-rows");
const previousButton = document.querySelector("#previous-button");
const nextButton = document.querySelector("#next-button");
const errorElement = document.querySelector("#input-error");

let trace = [];
let currentStep = 0;
let sortedValues = [];
let comparisonCount = 0;
let shiftCount = 0;

function parseNumbers(rawValue) {
  const parts = rawValue.trim().replaceAll(",", " ").split(/\s+/).filter(Boolean);
  if (parts.length === 0) throw new Error("Digite pelo menos um número inteiro.");
  if (parts.length > 40) throw new Error("Use no máximo 40 números para manter a tabela legível.");

  const values = parts.map((part) => {
    if (!/^[+-]?\d+$/.test(part)) throw new Error("Use apenas números inteiros, separados por espaço ou vírgula.");
    const value = Number(part);
    if (!Number.isSafeInteger(value)) throw new Error("Um dos valores é grande demais. Use números inteiros seguros.");
    return value;
  });
  return values;
}

function createTrace(values) {
  const working = [...values];
  const steps = [{
    type: "initial",
    round: 0,
    key: null,
    comparison: null,
    action: "Lista original",
    values: [...working],
    explanation: "Esta é a lista antes da ordenação. O primeiro valor já forma, sozinho, uma parte ordenada. A cada rodada, vamos inserir o próximo número no lugar certo dessa parte.",
  }];
  let comparisons = 0;
  let shifts = 0;

  for (let index = 1; index < working.length; index += 1) {
    const key = working[index];
    let cursor = index - 1;
    let stoppedByComparison = false;

    while (cursor >= 0) {
      const compared = working[cursor];
      comparisons += 1;

      if (compared > key) {
        working[cursor + 1] = compared;
        shifts += 1;
        const displayValues = [...working];
        displayValues[cursor] = null;
        steps.push({
          type: "shift",
          round: index,
          key,
          comparison: `${compared} > ${key}`,
          action: `Mover ${compared} para a direita`,
          values: displayValues,
          explanation: `A chave ${key} é menor que ${compared}. Para abrir espaço na parte ordenada, movemos ${compared} uma posição para a direita. Agora verificamos o valor imediatamente anterior.`,
        });
        cursor -= 1;
      } else {
        stoppedByComparison = true;
        const displayValues = [...working];
        if (cursor + 1 < index) displayValues[cursor + 1] = null;
        steps.push({
          type: "compare",
          round: index,
          key,
          comparison: `${compared} ≤ ${key}`,
          action: "Encontrou o lugar da chave",
          values: displayValues,
          explanation: `${compared} é menor ou igual à chave ${key}, então já está no lado correto. Paramos aqui: a chave entra logo depois dele.`,
        });
        break;
      }
    }

    working[cursor + 1] = key;
    const position = cursor + 2;
    const insertionExplanation = stoppedByComparison
      ? `Inserimos ${key} na posição ${position}, logo depois de ${working[cursor]}. A parte à esquerda continua em ordem.`
      : `Chegamos ao início: todos os valores anteriores eram maiores que ${key}. Inserimos a chave na primeira posição.`;
    steps.push({
      type: "insert",
      round: index,
      key,
      comparison: null,
      action: `Inserir na posição ${position}`,
      values: [...working],
      explanation: `${insertionExplanation} A lista agora é ${working.join(", ")}.`,
    });
  }

  return { steps, sorted: working, comparisons, shifts };
}

function makeCell(value, className = "") {
  const cell = document.createElement("span");
  cell.className = className;
  cell.textContent = value === null ? "···" : String(value);
  return cell;
}

function makeMiniVector(step) {
  const vector = document.createElement("span");
  vector.className = "mini-vector";
  const visibleValues = step.values.slice(0, 8);
  visibleValues.forEach((value) => {
    const isKey = step.key !== null && value === step.key && step.type !== "shift";
    const className = `mini-cell${value === null ? " is-gap" : isKey ? " is-key" : ""}`;
    vector.append(makeCell(value, className));
  });
  if (step.values.length > 8) {
    const more = document.createElement("span");
    more.className = "mini-more";
    more.textContent = `+${step.values.length - 8}`;
    vector.append(more);
  }
  return vector;
}

function renderTable() {
  rowsElement.replaceChildren();
  trace.forEach((step, index) => {
    const row = document.createElement("tr");
    row.dataset.step = String(index);
    row.setAttribute("aria-current", index === currentStep ? "step" : "false");
    row.setAttribute("tabindex", "0");

    const cells = [
      String(index).padStart(2, "0"),
      step.key === null ? "—" : String(step.key),
      step.comparison ?? "—",
      step.action,
    ];
    cells.forEach((value, cellIndex) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      if (cellIndex === 1 && step.key !== null) cell.className = "row-key";
      if (cellIndex === 3) cell.className = "row-action";
      row.append(cell);
    });

    const vectorCell = document.createElement("td");
    vectorCell.append(makeMiniVector(step));
    row.append(vectorCell);
    row.addEventListener("click", () => showStep(index));
    row.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        showStep(index);
      }
    });
    rowsElement.append(row);
  });

  document.querySelector("#step-count").textContent = `${trace.length} ETAPAS`;
  document.querySelector("#empty-state").hidden = trace.length > 0;
}

function showStep(index) {
  if (!trace.length) return;
  currentStep = Math.max(0, Math.min(index, trace.length - 1));
  const step = trace[currentStep];
  const isInitial = step.type === "initial" && trace.length > 1;
  const isResult = currentStep === trace.length - 1;

  document.querySelectorAll("#trace-rows tr").forEach((row, rowIndex) => {
    row.setAttribute("aria-current", rowIndex === currentStep ? "step" : "false");
  });
  const activeRow = rowsElement.querySelector(`[data-step="${currentStep}"]`);
  activeRow?.scrollIntoView({ block: "nearest" });

  document.querySelector("#stage-pill").textContent = `ETAPA ${currentStep}`;
  document.querySelector("#detail-index").textContent = String(currentStep + 1).padStart(2, "0");
  document.querySelector("#detail-overline").textContent = isInitial ? "ANTES DE COMEÇAR" : isResult ? "LISTA COMPLETA" : `RODADA ${step.round}`;
  document.querySelector("#detail-title").textContent = isInitial ? "Sua lista original" : isResult ? "Tudo em ordem" : step.action;
  document.querySelector("#vector-caption").textContent = isInitial ? "estado inicial" : isResult ? "resultado desta rodada" : "após esta ação";
  const keyLabel = document.querySelector("#vector-key");
  keyLabel.hidden = step.key === null;
  keyLabel.textContent = step.key === null ? "" : `CHAVE ${step.key}`;
  document.querySelector("#explanation").textContent = isResult
    ? `${step.explanation} A lista está ordenada do menor para o maior.`
    : step.explanation;
  document.querySelector("#progress-fill").style.width = `${trace.length === 1 ? 100 : (currentStep / (trace.length - 1)) * 100}%`;

  const vector = document.querySelector("#current-vector");
  vector.replaceChildren();
  step.values.forEach((value) => {
    const isKey = step.key !== null && value === step.key && step.type !== "shift";
    vector.append(makeCell(value, `vector-cell${value === null ? " is-gap" : isKey ? " is-key" : ""}`));
  });
  vector.setAttribute("aria-label", `Lista: ${step.values.map((value) => value === null ? "espaço temporário" : value).join(", ")}`);

  const comparisonBox = document.querySelector("#comparison-box");
  comparisonBox.hidden = !step.comparison;
  if (step.comparison) {
    document.querySelector("#comparison-text").textContent = `${step.comparison}: ${step.type === "shift" ? "a chave é menor; deslocamos o valor." : "a chave encontrou seu lugar."}`;
  }

  previousButton.disabled = currentStep === 0;
  nextButton.disabled = isResult;
  document.querySelector("#result-button").textContent = isResult ? "Resultado exibido" : "Ver resultado final ↗";
  document.querySelector("#summary-items").textContent = String(sortedValues.length);
  document.querySelector("#summary-comparisons").textContent = String(comparisonCount);
  document.querySelector("#summary-shifts").textContent = String(shiftCount);
  document.querySelector("#summary-result").textContent = isResult
    ? `Resultado: ${sortedValues.join("  ·  ")}`
    : "Resultado ao concluir a trilha.";
}

function startSimulation(event) {
  event?.preventDefault();
  try {
    const values = parseNumbers(input.value);
    const result = createTrace(values);
    trace = result.steps;
    sortedValues = result.sorted;
    comparisonCount = result.comparisons;
    shiftCount = result.shifts;
    currentStep = 0;
    errorElement.hidden = true;
    input.removeAttribute("aria-invalid");
    renderTable();
    showStep(0);
  } catch (error) {
    errorElement.textContent = error.message;
    errorElement.hidden = false;
    input.setAttribute("aria-invalid", "true");
    input.focus();
  }
}

form.addEventListener("submit", startSimulation);
previousButton.addEventListener("click", () => showStep(currentStep - 1));
nextButton.addEventListener("click", () => showStep(currentStep + 1));
document.querySelector("#result-button").addEventListener("click", () => showStep(trace.length - 1));
document.querySelector("#sample-button").addEventListener("click", () => {
  input.value = "8, 3, 5, 1, 9, 2";
  startSimulation();
  input.focus();
});
document.addEventListener("keydown", (event) => {
  if (event.target === input || event.altKey || event.ctrlKey || event.metaKey) return;
  if (event.key === "ArrowLeft") showStep(currentStep - 1);
  if (event.key === "ArrowRight") showStep(currentStep + 1);
});

startSimulation();