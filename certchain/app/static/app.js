/* CertChain UI — i18n + tabs + forms + explorer.
   LANGS index.html se inject hota hai (langs.json — single source of truth).
   Naya language add karna = langs.json me ek naya block, baaki kuch nahi! */

const RTL_LANGS = ["ar"];

function currentLang() {
  return localStorage.getItem("certchain-lang") || "en";
}

function dict() {
  return LANGS[currentLang()] || LANGS.en;
}

function applyLang(lang) {
  const d = LANGS[lang] || LANGS.en;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (d[key]) el.textContent = d[key];
  });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => {
    const key = el.getAttribute("data-i18n-ph");
    if (d[key]) el.setAttribute("placeholder", d[key]);
  });
  document.documentElement.dir = RTL_LANGS.includes(lang) ? "rtl" : "ltr";
  document.documentElement.lang = lang;
  localStorage.setItem("certchain-lang", lang);
}

const langSelect = document.getElementById("lang");
langSelect.value = currentLang();
langSelect.addEventListener("change", (e) => applyLang(e.target.value));
applyLang(currentLang());

/* ---- tabs ---- */
document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("page-" + btn.id.replace("tab-", "")).classList.add("active");
    if (btn.id === "tab-explorer") loadExplorer();
  });
});

function show(box, cls, html) {
  box.classList.remove("hidden", "ok", "err");
  box.classList.add(cls);
  box.innerHTML = html;
}

/* ---- issue ---- */
document.getElementById("issue-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const box = document.getElementById("issue-result");
  const d = dict();
  const payload = {
    account_id: document.getElementById("issue-account").value.trim(),
    university: document.getElementById("issue-university").value.trim(),
    cert_id: document.getElementById("issue-certid").value.trim(),
    holder: document.getElementById("issue-holder").value.trim(),
    course: document.getElementById("issue-course").value.trim(),
  };
  try {
    const res = await fetch("/issue", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await res.json();
    if (res.status === 201) {
      show(box, "ok",
        `✅ ${d.issueSuccess}: <b>${body.cert_id}</b><br>` +
        `UPI: ${body.upi_txn_id} · ₹${body.fee_rupees}<br>` +
        `${d.lblBlock} #${body.block_index} · <code>${body.block_hash.slice(0, 18)}…</code>`);
    } else {
      show(box, "err", `❌ ${body.reason || body.error}`);
    }
  } catch (err) {
    show(box, "err", "❌ " + err.message);
  }
});

/* ---- verify ---- */
document.getElementById("verify-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const box = document.getElementById("verify-result");
  const d = dict();
  const certId = document.getElementById("verify-input").value.trim();
  if (!certId) return;
  try {
    const res = await fetch("/verify/" + encodeURIComponent(certId));
    const body = await res.json();
    if (body.verified) {
      show(box, "ok",
        `<span class="badge ok-badge">✅ ${d.verified}</span><br><br>` +
        `<b>${d.lblHolder}:</b> ${body.holder}<br>` +
        `<b>${d.lblCourse}:</b> ${body.course}<br>` +
        `<b>${d.lblUniversity}:</b> ${body.university}<br>` +
        `<b>${d.lblIssuedBy}:</b> <code>${body.issued_by}</code><br>` +
        `<b>${d.lblBlock}:</b> #${body.block_index} · <code>${body.block_hash.slice(0, 18)}…</code><br>` +
        `<b>${d.lblFee}:</b> ${body.fee}`);
    } else {
      show(box, "err", `<span class="badge err-badge">❌ ${d.notVerified}</span><br>${body.reason}`);
    }
  } catch (err) {
    show(box, "err", "❌ " + err.message);
  }
});

/* ---- explorer ---- */
async function loadExplorer() {
  const container = document.getElementById("blocks");
  const d = dict();
  try {
    const res = await fetch("/api/blocks");
    const body = await res.json();
    const blocks = body.blocks || [];
    if (!blocks.length) {
      container.innerHTML = `<p class="hint">${d.noBlocks}</p>`;
      return;
    }
    container.innerHTML = blocks.map((b) => {
      const records = b.records.map((rec) => {
        if (typeof rec === "string") return `<div class="record">${rec}</div>`;
        return `<div class="record">📜 <b>${rec.record_type}</b> · ${rec.cert_id} ·
          <code>${rec.signature.slice(0, 14)}…</code></div>`;
      }).join("");
      return `<div class="block-card">
        <div class="block-head">#${b.index} · <code>${b.hash.slice(0, 20)}…</code></div>
        <div class="block-meta">${d.nonce}: <b>${b.nonce}</b></div>
        ${records}
      </div>`;
    }).join("");
  } catch (err) {
    container.innerHTML = `<p class="hint">❌ ${err.message}</p>`;
  }
}

document.getElementById("explorer-refresh").addEventListener("click", loadExplorer);

/* ---- hero stats ---- */
async function loadStats() {
  try {
    const body = await (await fetch("/api/blocks")).json();
    const el = document.getElementById("stat-blocks");
    if (el && typeof body.length === "number") el.textContent = body.length;
  } catch (_) { /* node offline — stat stays "—" */ }
}
loadStats();
