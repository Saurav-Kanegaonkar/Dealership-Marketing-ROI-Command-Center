const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const number = new Intl.NumberFormat("en-US");
const percent = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 1,
});

let payload;
let activeView = "executive";

const view = document.querySelector("#view");
const headerRoas = document.querySelector("#headerRoas");
const tabs = Array.from(document.querySelectorAll(".tab"));

function metric(label, value, note) {
  return `
    <article class="metric">
      <span>${label}</span>
      <strong>${value}</strong>
      <em>${note}</em>
    </article>
  `;
}

function table(headers, rows) {
  return `
    <div class="table-wrap">
      <table>
        <thead>
          <tr>${headers.map((header) => `<th>${header}</th>`).join("")}</tr>
        </thead>
        <tbody>${rows.join("")}</tbody>
      </table>
    </div>
  `;
}

function barRows(items, valueKey, labelKey, formatValue) {
  const maxValue = Math.max(...items.map((item) => Number(item[valueKey])));
  return items
    .map((item) => {
      const width = Math.max(4, (Number(item[valueKey]) / maxValue) * 100);
      return `
        <div class="bar-row">
          <div>
            <span>${item[labelKey]}</span>
            <strong>${formatValue(item[valueKey])}</strong>
          </div>
          <div class="bar-track"><i style="width:${width}%"></i></div>
        </div>
      `;
    })
    .join("");
}

function renderExecutive() {
  const { summary, channels } = payload;
  const rows = channels.map(
    (channel) => `
      <tr>
        <td>${channel.channel}</td>
        <td>${currency.format(channel.spend)}</td>
        <td>${currency.format(channel.attributed_gross)}</td>
        <td>${channel.roas.toFixed(2)}x</td>
        <td><span class="pill ${channel.recommendation === "Scale" ? "good" : channel.recommendation === "Fix measurement" ? "risk" : "watch"}">${channel.recommendation}</span></td>
      </tr>
    `
  );

  view.innerHTML = `
    <section class="metric-grid">
      ${metric("Marketing spend", currency.format(summary.total_spend), "16 week synthetic plan")}
      ${metric("Attributed gross", currency.format(summary.total_gross), "service + sales")}
      ${metric("Average ROAS", `${summary.avg_roas.toFixed(2)}x`, "blended channel view")}
      ${metric("Vendor waste flagged", currency.format(summary.budget_waste), "needs proof or cutback")}
    </section>
    <section class="layout two">
      <article class="panel">
        <div class="panel-head">
          <p class="eyebrow">Budget control</p>
          <h2>Channel ROI and next move</h2>
        </div>
        ${table(["Channel", "Spend", "Gross", "ROAS", "Call"], rows)}
      </article>
      <article class="panel">
        <div class="panel-head">
          <p class="eyebrow">Operating mix</p>
          <h2>Spend by channel</h2>
        </div>
        <div class="bars">
          ${barRows(channels, "spend", "channel", (value) => currency.format(value))}
        </div>
      </article>
    </section>
  `;
}

function renderRetention() {
  const { summary, opportunities } = payload;
  const rows = opportunities.map(
    (item) => `
      <tr>
        <td>${item.customer_id}</td>
        <td>${item.rooftop}</td>
        <td>${item.opportunity_type}</td>
        <td>${item.best_channel}</td>
        <td>${percent.format(item.predicted_book_rate)}</td>
        <td>${currency.format(item.estimated_gross)}</td>
        <td><strong>${item.priority_score.toFixed(1)}</strong></td>
      </tr>
    `
  );

  const grouped = opportunities.reduce((acc, item) => {
    acc[item.opportunity_type] = (acc[item.opportunity_type] || 0) + 1;
    return acc;
  }, {});
  const mix = Object.entries(grouped)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);

  view.innerHTML = `
    <section class="metric-grid">
      ${metric("Priority customers", number.format(summary.retention_queue_customers), "weekly call list")}
      ${metric("Expected gross", currency.format(summary.retention_queue_expected_gross), "modeled from top queue")}
      ${metric("Show rate", percent.format(summary.show_rate), "campaign-attributed")}
      ${metric("Top trigger", summary.top_opportunity_type, "highest scored segment")}
    </section>
    <section class="layout two">
      <article class="panel wide">
        <div class="panel-head">
          <p class="eyebrow">Fixed operations retention</p>
          <h2>Service opportunity queue</h2>
        </div>
        ${table(["Customer", "Rooftop", "Trigger", "Channel", "Book rate", "Gross", "Score"], rows)}
      </article>
      <article class="panel">
        <div class="panel-head">
          <p class="eyebrow">Campaign planning</p>
          <h2>Trigger mix</h2>
        </div>
        <div class="bars">
          ${barRows(mix, "count", "name", (value) => `${value} customers`)}
        </div>
        <div class="callout">
          <b>Recommended cadence</b>
          <p>Run recall, inspection, declined-work, and alignment lists every Monday, then hand phone-heavy segments to advisors before the weekend.</p>
        </div>
      </article>
    </section>
  `;
}

function renderTrust() {
  const { summary, quality, ai } = payload;
  const qualityRows = quality.map(
    (item) => `
      <tr>
        <td>${item.source}</td>
        <td>${number.format(item.rows)}</td>
        <td>${item.freshness_score}</td>
        <td>${percent.format(item.match_rate)}</td>
        <td>${item.join_key}</td>
        <td><span class="pill ${item.quality_risk > 30 ? "risk" : item.quality_risk > 20 ? "watch" : "good"}">${item.quality_risk}</span></td>
      </tr>
    `
  );
  const aiRows = ai.map(
    (item) => `
      <article class="use-case">
        <span>${item.owner}</span>
        <h3>${item.use_case}</h3>
        <p>${item.workflow}</p>
        <dl>
          <div><dt>Effort</dt><dd>${item.effort_hours} hrs</dd></div>
          <div><dt>Gross</dt><dd>${currency.format(item.expected_monthly_gross)}</dd></div>
          <div><dt>Control</dt><dd>${item.control}</dd></div>
        </dl>
      </article>
    `
  ).join("");

  view.innerHTML = `
    <section class="metric-grid">
      ${metric("Sources checked", `${summary.high_quality_sources}/${summary.source_count}`, "low quality risk")}
      ${metric("Vendor waste", currency.format(summary.budget_waste), "measurement issue")}
      ${metric("AI experiments", number.format(ai.length), "with controls")}
      ${metric("Queue rows", number.format(payload.opportunities.length), "visible sample")}
    </section>
    <section class="layout stacked">
      <article class="panel">
        <div class="panel-head">
          <p class="eyebrow">Data trust</p>
          <h2>Source quality controls</h2>
        </div>
        ${table(["Source", "Rows", "Freshness", "Match", "Join key", "Risk"], qualityRows)}
      </article>
      <section class="use-case-grid" aria-label="AI use cases">
        ${aiRows}
      </section>
    </section>
  `;
}

function render() {
  if (activeView === "retention") {
    renderRetention();
  } else if (activeView === "trust") {
    renderTrust();
  } else {
    renderExecutive();
  }
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    activeView = tab.dataset.view;
    tabs.forEach((item) => item.classList.toggle("active", item === tab));
    render();
  });
});

fetch("analysis/outputs/dashboard_payload.json")
  .then((response) => response.json())
  .then((data) => {
    payload = data;
    headerRoas.textContent = `${payload.summary.avg_roas.toFixed(2)}x ROAS`;
    render();
  })
  .catch(() => {
    view.innerHTML = `<article class="panel"><h2>Data could not load</h2></article>`;
  });
