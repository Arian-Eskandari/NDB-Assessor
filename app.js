/* ==========================================================
   NDB Breach Assessor — app.js
   Privacy Act 1988 (Cth), Part IIIC — NDB Scheme
   ========================================================== */

const answers = {};
let currentStep = 0;

const HARM_KEYS = [
  'g2_sensitive',
  'g2_volume',
  'g2_malicious',
  'g2_identity_risk',
  'g2_financial_risk',
  'g2_physical_risk',
];

const HARM_LABELS = {
  g2_sensitive:     'Sensitive data',
  g2_volume:        '>50 individuals',
  g2_malicious:     'Malicious/criminal act',
  g2_identity_risk: 'Identity fraud risk',
  g2_financial_risk:'Financial harm risk',
  g2_physical_risk: 'Physical harm risk',
};

const RISK       = ['Low','Low','Medium','Medium','High','Critical','Critical'];
const RISK_COLOR = ['#1a6644','#1a6644','#a85c0a','#a85c0a','#c0321e','#8b1a0a','#8b1a0a'];

/* ----------------------------------------------------------
   Navigation
---------------------------------------------------------- */
function goTo(step) {
  document.getElementById(`step-${currentStep}`).classList.remove('active');
  document.getElementById(`step-${step}`).classList.add('active');

  document.querySelectorAll('.step-item').forEach((item, i) => {
    item.classList.remove('active', 'done');
    const dot = item.querySelector('.step-dot');
    if (i < step) {
      item.classList.add('done');
      dot.textContent = '';
    } else if (i === step) {
      item.classList.add('active');
      dot.textContent = i === 0 ? '→' : i;
    } else {
      dot.textContent = i === 0 ? '→' : i;
    }
  });

  currentStep = step;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* ----------------------------------------------------------
   Answer handling
---------------------------------------------------------- */
function setAnswer(key, val, btn) {
  answers[key] = val;
  btn.closest('.yn-group')
     .querySelectorAll('.yn-btn')
     .forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}

/* ----------------------------------------------------------
   Validation helpers
---------------------------------------------------------- */
function getVal(id) {
  return document.getElementById(id).value.trim();
}

function showError(errId, inputId) {
  document.getElementById(errId).classList.add('visible');
  if (inputId) document.getElementById(inputId).classList.add('invalid');
}

function clearError(errId, inputId) {
  document.getElementById(errId).classList.remove('visible');
  if (inputId) document.getElementById(inputId).classList.remove('invalid');
}

function allAnswered(...keys) {
  return keys.every(k => answers[k] !== undefined);
}

/* ----------------------------------------------------------
   Step 1 — Incident details
---------------------------------------------------------- */
function validateStep1() {
  const fields = [
    ['f-org',       'err-org'],
    ['f-date',      'err-date'],
    ['f-desc',      'err-desc'],
    ['f-datatypes', 'err-datatypes'],
    ['f-count',     'err-count'],
    ['f-assessor',  'err-assessor'],
  ];
  let ok = true;
  fields.forEach(([fid, eid]) => {
    if (!getVal(fid)) { showError(eid, fid); ok = false; }
    else               { clearError(eid, fid); }
  });
  if (ok) goTo(2);
}

/* ----------------------------------------------------------
   Gate 1 — Eligible data breach
---------------------------------------------------------- */
function validateGate1() {
  if (!allAnswered('g1_personal_info', 'g1_unauthorised')) {
    alert('Please answer all questions before continuing.');
    return;
  }
  if (!answers.g1_personal_info || !answers.g1_unauthorised) {
    buildResult();
    goTo(5);
    return;
  }
  goTo(3);
}

/* ----------------------------------------------------------
   Gate 2 — Likely serious harm
---------------------------------------------------------- */
function validateGate2() {
  if (!allAnswered(...HARM_KEYS)) {
    alert('Please answer all questions before continuing.');
    return;
  }
  const score = HARM_KEYS.reduce((s, k) => s + (answers[k] ? 1 : 0), 0);
  if (score < 2) {
    buildResult();
    goTo(5);
    return;
  }
  goTo(4);
}

/* ----------------------------------------------------------
   Gate 3 — Exemptions
---------------------------------------------------------- */
function validateGate3() {
  if (!allAnswered('g3_remedied', 'g3_law_enforcement', 'g3_other_law')) {
    alert('Please answer all questions before continuing.');
    return;
  }
  buildResult();
  goTo(5);
}

/* ----------------------------------------------------------
   Assessment logic
   Mirrors the three-gate test from Part IIIC, Privacy Act 1988
---------------------------------------------------------- */
function assess() {
  // Gate 1
  if (!answers.g1_personal_info) {
    return {
      notifiable: false,
      gate1: { passed: false, reason: 'No personal information was involved. Not an eligible data breach under the NDB scheme.' },
      gate2: null, gate3: null, harmScore: 0,
    };
  }
  if (!answers.g1_unauthorised) {
    return {
      notifiable: false,
      gate1: { passed: false, reason: 'There was no unauthorised access, disclosure, or loss. Gate 1 not satisfied.' },
      gate2: null, gate3: null, harmScore: 0,
    };
  }
  const gate1 = { passed: true, reason: 'Unauthorised access/disclosure/loss of personal information confirmed.' };

  // Gate 2
  const harmScore = HARM_KEYS.reduce((s, k) => s + (answers[k] ? 1 : 0), 0);
  if (harmScore < 2) {
    return {
      notifiable: false,
      gate1,
      gate2: { passed: false, reason: `Only ${harmScore} of 6 harm factor(s) identified. A reasonable person would not likely expect serious harm. Gate 2 not satisfied.` },
      gate3: null, harmScore,
    };
  }
  const gate2 = { passed: true, reason: `${harmScore} of 6 harm factors present. A reasonable person would likely expect serious harm.` };

  // Gate 3
  if (answers.g3_remedied) {
    return { notifiable: false, gate1, gate2, gate3: { passed: false, reason: 'Remedial action taken that removes the likelihood of serious harm. Exemption under s26WF applies.' }, harmScore };
  }
  if (answers.g3_law_enforcement) {
    return { notifiable: false, gate1, gate2, gate3: { passed: false, reason: 'Law enforcement body has requested delay or non-notification. Exemption under s26WN applies.' }, harmScore };
  }
  if (answers.g3_other_law) {
    return { notifiable: false, gate1, gate2, gate3: { passed: false, reason: 'Another Australian law prohibits notification. Exemption applies.' }, harmScore };
  }

  return {
    notifiable: true,
    gate1, gate2,
    gate3: { passed: true, reason: 'No exemptions identified. All three gates are satisfied.' },
    harmScore,
  };
}

/* ----------------------------------------------------------
   Result builder — renders the Step 5 panel
---------------------------------------------------------- */
function buildResult() {
  const result    = assess();
  const org       = getVal('f-org');
  const dateDisc  = getVal('f-date');
  const desc      = getVal('f-desc');
  const datatypes = getVal('f-datatypes');
  const count     = getVal('f-count');
  const assessor  = getVal('f-assessor');
  const today     = new Date().toLocaleDateString('en-AU');

  /* Banner */
  document.getElementById('result-banner-container').innerHTML = result.notifiable
    ? `<div class="result-banner notifiable">
         <div class="result-verdict">⚑ Notifiable data breach</div>
         <div class="result-title">Notification required</div>
         <div class="result-desc">All three eligibility gates are satisfied. You must notify the OAIC and affected individuals within <strong>30 days</strong> of becoming aware of this breach (s26WK, Privacy Act 1988).</div>
       </div>`
    : `<div class="result-banner not-notifiable">
         <div class="result-verdict">✓ Not notifiable</div>
         <div class="result-title">Notification not required</div>
         <div class="result-desc">Based on your responses, this incident does not meet the NDB eligibility threshold. Document this assessment and retain it in your incident register.</div>
       </div>`;

  /* Gate summary cards */
  const gateRows = [
    { num: 1, label: 'Gate 1 — Eligible data breach',   result: result.gate1 },
    { num: 2, label: 'Gate 2 — Likely serious harm',    result: result.gate2 },
    { num: 3, label: 'Gate 3 — No exemption applies',   result: result.gate3 },
  ];

  document.getElementById('gate-summary-container').innerHTML = gateRows.map(g => {
    if (!g.result) {
      return `<div class="gate-summary">
        <div class="gate-summary-header">
          <span class="gate-summary-title">${g.label}</span>
          <span class="gate-status-pill pill-skip">Skipped</span>
        </div>
        <div class="gate-summary-body">Assessment ended before this gate was reached.</div>
      </div>`;
    }
    const pill = g.result.passed
      ? `<span class="gate-status-pill pill-pass">Passed</span>`
      : `<span class="gate-status-pill pill-notmet">Not satisfied</span>`;
    return `<div class="gate-summary">
      <div class="gate-summary-header">
        <span class="gate-summary-title">${g.label}</span>${pill}
      </div>
      <div class="gate-summary-body">${g.result.reason}</div>
    </div>`;
  }).join('');

  /* Harm severity */
  if (result.gate2) {
    const score      = result.harmScore;
    const pct        = (score / 6) * 100;
    const riskLabel  = RISK[score];
    const riskColor  = RISK_COLOR[score];
    const factorTags = HARM_KEYS.map(k =>
      `<span class="harm-factor-tag ${answers[k] ? 'present' : ''}">${HARM_LABELS[k]}</span>`
    ).join('');

    document.getElementById('harm-section-container').innerHTML = `
      <p class="result-section-title">Harm severity rating</p>
      <div class="harm-section">
        <div class="harm-label">
          <span class="harm-label-text">Severity: <span style="color:${riskColor}">${riskLabel}</span></span>
          <span class="harm-score-val">${score} / 6 factors</span>
        </div>
        <div class="harm-bar"><div class="harm-fill" style="width:${pct}%;background:${riskColor}"></div></div>
        <div class="harm-factors-list">${factorTags}</div>
      </div>`;
  } else {
    document.getElementById('harm-section-container').innerHTML = '';
  }

  /* Required actions */
  const actionsContainer = document.getElementById('actions-container');
  if (result.notifiable) {
    actionsContainer.innerHTML = `
      <p class="result-section-title">Required actions</p>
      <ul class="action-list">
        <li class="action-item"><span class="action-num">1</span><span>Submit an NDB notification to the OAIC via the online form at <a href="https://www.oaic.gov.au/privacy/notifiable-data-breaches/report-a-data-breach" target="_blank" style="color:var(--accent)">oaic.gov.au</a>.</span></li>
        <li class="action-item"><span class="action-num">2</span><span>Notify all affected individuals as soon as practicable, or publish a public notice if individual notification is not reasonably practicable.</span></li>
        <li class="action-item"><span class="action-num">3</span><span>Complete notification within <strong>30 days</strong> of becoming aware of the eligible data breach (s26WK).</span></li>
        <li class="action-item"><span class="action-num">4</span><span>Retain this assessment document in your incident register and preserve evidence of your investigation and response.</span></li>
        <li class="action-item"><span class="action-num">5</span><span>Engage a qualified privacy lawyer to review the notification before submission if the breach is complex or high-severity.</span></li>
      </ul>`;
  } else {
    actionsContainer.innerHTML = `
      <p class="result-section-title">Recommended actions</p>
      <ul class="action-list">
        <li class="action-item"><span class="action-num" style="background:var(--green)">1</span><span>Retain this assessment document in your incident register with the date and assessor name.</span></li>
        <li class="action-item"><span class="action-num" style="background:var(--green)">2</span><span>Document the reasoning for the non-notification decision in case the OAIC makes a future inquiry.</span></li>
        <li class="action-item"><span class="action-num" style="background:var(--green)">3</span><span>Continue monitoring — if new information emerges that changes the harm assessment, re-run this assessment.</span></li>
      </ul>`;
  }

  /* Draft OAIC notification */
  const draftContainer = document.getElementById('draft-container');
  if (result.notifiable) {
    const draftText =
`TO: Office of the Australian Information Commissioner (OAIC)
SUBJECT: Notifiable Data Breach — ${org}

Organisation: ${org}
Date breach discovered: ${dateDisc}
Date of this notification: ${today}
Prepared by: ${assessor}

DESCRIPTION OF THE BREACH
${desc}

TYPES OF PERSONAL INFORMATION INVOLVED
${datatypes}

NUMBER OF INDIVIDUALS AFFECTED
Approximately ${count} individuals.

STEPS THE ORGANISATION HAS TAKEN IN RESPONSE
[TO BE COMPLETED — describe containment actions, investigation steps, and remediation measures taken.]

RECOMMENDED STEPS FOR AFFECTED INDIVIDUALS
[TO BE COMPLETED — e.g. change passwords, monitor financial accounts, place fraud alerts with credit reporting agencies, contact Services Australia if Medicare information was involved.]

This notification is submitted in accordance with Part IIIC of the Privacy Act 1988 (Cth).`;

    draftContainer.innerHTML = `
      <p class="result-section-title">Draft OAIC notification statement</p>
      <p style="font-size:13px;color:var(--ink-3);margin-bottom:0.75rem">Review and complete the bracketed sections with your legal or privacy team before submission.</p>
      <div class="draft-box" id="draft-text">${escapeHTML(draftText)}</div>
      <button class="copy-btn" onclick="copyDraft()">⎘ Copy to clipboard</button>`;
  } else {
    draftContainer.innerHTML = '';
  }
}

/* ----------------------------------------------------------
   Utilities
---------------------------------------------------------- */
function escapeHTML(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function copyDraft() {
  const text = document.getElementById('draft-text').innerText;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.querySelector('.copy-btn');
    btn.textContent = '✓ Copied';
    setTimeout(() => { btn.textContent = '⎘ Copy to clipboard'; }, 2000);
  });
}

function resetAll() {
  Object.keys(answers).forEach(k => delete answers[k]);
  document.querySelectorAll('.yn-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('input, textarea').forEach(el => el.value = '');
  document.querySelectorAll('.field-error').forEach(el => el.classList.remove('visible'));
  document.querySelectorAll('input.invalid, textarea.invalid').forEach(el => el.classList.remove('invalid'));
  goTo(0);
}
