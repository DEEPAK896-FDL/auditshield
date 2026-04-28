/* ============================================================
   AUDITSHIELD CHATBOT -- Smart Hybrid Assistant v2.0
   Intent-based matching + fuzzy scoring + synonym expansion
   Pure JavaScript -- no external APIs -- lightweight
   ============================================================ */
(function () {
  'use strict';

  /* ── State ── */
  var isOpen      = false;
  var isTyping    = false;
  var msgCount    = 0;
  var lastIntent  = null;
  var turnCount   = 0;
  var fallbackIdx = 0;

  /* ── DOM refs ── */
  var panel    = document.getElementById('cbPanel');
  var trigger  = document.getElementById('cbTrigger');
  var messages = document.getElementById('cbMessages');
  var inp      = document.getElementById('cbInput');
  var sendBtn  = document.getElementById('cbSendBtn');
  var typingEl = document.getElementById('cbTyping');
  var unread   = document.getElementById('cbUnread');
  var backdrop = document.getElementById('cbBackdrop');

  /* ── Synonym dictionary ── */
  var SYN = {
    "auditing"    : "audit",     "audited"      : "audit",     "audits"       : "audit",
    "inspection"  : "audit",     "review"       : "audit",     "examination"  : "audit",
    "assessment"  : "audit",     "evaluation"   : "audit",
    "findings"    : "finding",   "issue"        : "finding",   "issues"       : "finding",
    "problem"     : "finding",   "problems"     : "finding",   "observation"  : "finding",
    "gap"         : "finding",   "vulnerability": "finding",   "deficiency"   : "finding",
    "reports"     : "report",    "pdf"          : "report",    "document"     : "report",
    "download"    : "report",    "export"       : "report",
    "fix"         : "resolve",   "fixed"        : "resolve",   "fixing"       : "resolve",
    "close"       : "resolve",   "closed"       : "resolve",   "closing"      : "resolve",
    "remediate"   : "resolve",   "correct"      : "resolve",   "corrective"   : "resolve",
    "risk"        : "severity",  "priority"     : "severity",  "critical"     : "severity",
    "urgent"      : "severity",  "serious"      : "severity",
    "late"        : "overdue",   "delayed"      : "overdue",   "missed"       : "overdue",
    "deadline"    : "overdue",   "expired"      : "overdue",
    "roles"       : "role",      "permission"   : "role",      "permissions"  : "role",
    "access"      : "role",      "users"        : "role",      "account"      : "role",
    "create"      : "create",    "creating"     : "create",    "make"         : "create",
    "start"       : "create",    "begin"        : "create",    "initiate"     : "create",
    "new"         : "create",    "plan"         : "create",
    "overview"    : "dashboard", "analytics"    : "dashboard", "statistics"   : "dashboard",
    "charts"      : "dashboard", "graph"        : "dashboard", "kpi"          : "dashboard",
    "compliance"  : "compliance","regulation"   : "compliance","standard"     : "compliance",
    "iso"         : "compliance","gdpr"         : "compliance","sox"          : "compliance",
    "login"       : "login",     "signin"       : "login",
    "logout"      : "logout",    "signout"      : "logout",    "exit"         : "logout",
    "workflow"    : "workflow",  "process"      : "workflow",
    "steps"       : "workflow",  "procedure"    : "workflow"
  };

  /* ── Intent knowledge base ── */
  var KB = [
    {
      id: "greeting",
      combos: ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "howdy"],
      signals: ["hello", "hi", "hey", "greet", "morning", "afternoon", "evening"],
      reply: "Hello! I am the <strong>AuditShield Assistant</strong>. I can help you with audit processes, compliance tracking, platform features, and more. What would you like to know?"
    },
    {
      id: "platform",
      combos: [
        "what is auditshield", "about auditshield", "tell me about auditshield",
        "what does auditshield do", "purpose of auditshield", "explain auditshield",
        "what is this system", "what is this platform"
      ],
      signals: ["auditshield", "platform", "system", "application", "software", "product", "tool"],
      reply: "<strong>AuditShield</strong> is an Internal IT Audit Management System that replaces scattered spreadsheets with a single intelligent platform.<br><br>It covers the full audit lifecycle:<br>Plan and schedule audits across departments<br>Track findings with severity classification<br>Monitor corrective actions in real time<br>Live compliance dashboards<br>Professional PDF audit reports"
    },
    {
      id: "audit_concept",
      combos: [
        "what is internal audit", "what is an audit", "define audit",
        "audit definition", "what is auditing", "explain audit", "audit meaning"
      ],
      signals: ["internal", "concept", "definition", "meaning", "define"],
      reply: "An <strong>Internal IT Audit</strong> is a structured examination of an organization's IT systems, processes, and controls.<br><br>Key objectives:<br>Identify security vulnerabilities and control gaps<br>Verify compliance with policies and regulations<br>Confirm IT processes meet required standards<br>Recommend improvements and corrective actions<br><br>AuditShield digitizes this entire process end-to-end."
    },
    {
      id: "workflow",
      combos: [
        "how it works", "how does it work", "workflow of auditshield", "audit process",
        "audit steps", "how to use auditshield", "platform workflow", "explain the process",
        "tell me the steps", "audit lifecycle"
      ],
      signals: ["workflow", "process", "steps", "procedure", "lifecycle", "flow"],
      reply: "AuditShield follows a clean <strong>4-step audit lifecycle</strong>:<br><br><strong>Step 1 -- Create Audit</strong><br>Define the audit title, department, auditor, scope, and timeline.<br><br><strong>Step 2 -- Record Findings</strong><br>Log issues with severity levels and recommendations.<br><br><strong>Step 3 -- Track Corrective Actions</strong><br>Auditee teams respond, update progress, and close resolved issues.<br><br><strong>Step 4 -- Generate Final Report</strong><br>Close the audit and download a comprehensive PDF report."
    },
    {
      id: "create_audit",
      combos: [
        "how to create audit", "how do i create an audit", "create an audit",
        "create new audit", "make an audit", "start an audit", "how to start audit",
        "new audit", "plan an audit", "schedule an audit", "steps to create audit",
        "add audit", "how to make audit"
      ],
      signals: ["create", "audit"],
      reply: "Creating an audit (Audit Manager role required):<br><br><strong>1.</strong> Click <em>Create Audit</em> in the sidebar.<br><strong>2.</strong> Fill in: Title, Department, Assigned Auditor, Start and End Dates, Scope.<br><strong>3.</strong> Set status to <em>Planned</em> and save.<br><strong>4.</strong> Change to <em>Ongoing</em> when the audit begins.<br><br>You can then add findings directly from the audit detail page."
    },
    {
      id: "findings",
      combos: [
        "what are findings", "what is a finding", "audit findings", "how to add findings",
        "record findings", "log a finding", "finding detail", "findings management",
        "explain findings", "what does finding mean"
      ],
      signals: ["finding"],
      reply: "<strong>Findings</strong> are issues or deficiencies discovered during an audit.<br><br>Each finding captures:<br><strong>Title</strong> -- short name<br><strong>Description</strong> -- detailed explanation<br><strong>Severity</strong> -- Critical / High / Medium / Low<br><strong>Recommendation</strong> -- how to fix it<br><strong>Target Closure Date</strong> -- resolution deadline<br><strong>Status</strong> -- Open / In Progress / Closed"
    },
    {
      id: "severity",
      combos: [
        "what is severity", "severity levels", "risk levels", "severity classification",
        "what is risk level", "explain severity", "audit risk", "finding severity"
      ],
      signals: ["severity", "risk", "priority", "critical", "urgent"],
      reply: "AuditShield uses four severity levels:<br><br><span style=\"color:#dc2626;font-weight:700;\">Critical</span> -- Immediate action required<br><span style=\"color:#ea580c;font-weight:700;\">High</span> -- Resolve urgently<br><span style=\"color:#ca8a04;font-weight:700;\">Medium</span> -- Resolve in next cycle<br><span style=\"color:#16a34a;font-weight:700;\">Low</span> -- Monitor and document<br><br>The dashboard shows a severity distribution chart for quick prioritization."
    },
    {
      id: "overdue",
      combos: [
        "what is overdue", "overdue findings", "overdue items", "overdue detection",
        "how does overdue work", "late findings", "missed deadline",
        "overdue alerts", "how to see overdue"
      ],
      signals: ["overdue", "late", "missed", "deadline", "expired"],
      reply: "<strong>Overdue detection</strong> is fully automatic in AuditShield.<br><br>A finding is overdue when its Target Closure Date has passed AND its status is still Open or In Progress.<br><br>How overdue is surfaced:<br>Bell icon badge shows the overdue count<br>Overdue Items page lists all overdue findings and audits<br>Dashboard KPI card shows the total<br>Red row highlighting in all tables"
    },
    {
      id: "corrective_actions",
      combos: [
        "corrective action", "how to resolve finding", "how to close finding",
        "fixing findings", "remediation", "auditee response", "respond to finding",
        "update finding status", "resolve a finding", "action plan", "how to handle findings"
      ],
      signals: ["resolve", "correct", "respond", "action"],
      reply: "<strong>Corrective actions</strong> are steps taken by the Auditee Head to address findings:<br><br><strong>1.</strong> Open the finding detail page.<br><strong>2.</strong> Add <em>Response Notes</em> describing the action taken.<br><strong>3.</strong> Update status to <em>In Progress</em> or <em>Closed</em>.<br><br>Once all findings are handled, the Audit Manager closes the audit and generates the final PDF report."
    },
    {
      id: "reports",
      combos: [
        "how to generate report", "pdf report", "download report", "audit report",
        "generate report", "final report", "how to download pdf", "export report",
        "report generation", "what is in the report", "get report"
      ],
      signals: ["report", "pdf", "download", "export", "document"],
      reply: "PDF reports are generated when an audit is <strong>Closed</strong>.<br><br><strong>How to generate:</strong><br><strong>1.</strong> Open the audit detail page.<br><strong>2.</strong> Change status to <em>Closed</em>.<br><strong>3.</strong> Click <em>Download Report</em>.<br><br>The PDF includes audit details, all findings with severity and status, recommendations, and a closure summary.<br><br><em>Only Audit Managers can download reports.</em>"
    },
    {
      id: "roles",
      combos: [
        "what are the roles", "user roles", "who can do what", "permissions",
        "audit manager role", "auditee head role", "observer role",
        "role based access", "explain roles", "user access", "difference between roles"
      ],
      signals: ["role", "permission", "access", "user"],
      reply: "AuditShield has <strong>three user roles</strong>:<br><br><strong>Audit Manager</strong><br>Full control -- create and edit audits, manage findings, download PDFs, view all departments.<br><br><strong>Auditee Head</strong><br>Department access -- view assigned audits, respond to findings, update status, download own department reports.<br><br><strong>Observer</strong><br>Read-only -- view all data but cannot create, edit, or download anything."
    },
    {
      id: "dashboard",
      combos: [
        "what does dashboard show", "dashboard features", "dashboard overview",
        "how does dashboard work", "explain dashboard", "dashboard analytics",
        "dashboard charts", "what are kpi cards"
      ],
      signals: ["dashboard", "analytics", "chart", "kpi", "statistic", "metric"],
      reply: "The <strong>Dashboard</strong> is the real-time command center:<br><br><strong>KPI Cards:</strong><br>Total Audits -- all audits in the system<br>Open Findings -- unresolved issues<br>Critical Issues -- high-risk items<br>Overdue Items -- past-deadline findings<br><br>All cards are clickable and navigate to detailed views.<br><br><strong>Live Charts:</strong><br>Audit Status Overview (bar chart)<br>Findings by Severity (doughnut chart)<br>Audits per Department (horizontal bar)"
    },
    {
      id: "departments",
      combos: [
        "what is departments", "department analytics", "department view", "departments page",
        "how to view department", "department details", "what does departments show"
      ],
      signals: ["department", "dept"],
      reply: "The <strong>Departments</strong> section gives Audit Managers a full analytical view of each department:<br><br>Total audits per department<br>Open findings count<br>Overdue findings count<br>Closed audits count<br>Severity distribution chart<br>Audit status breakdown chart"
    },
    {
      id: "login",
      combos: [
        "how to login", "how do i login", "how to sign in", "how to get started",
        "getting started", "how to access", "first time login", "sign in process"
      ],
      signals: ["login", "signin", "started", "access"],
      reply: "Getting started:<br><br><strong>1.</strong> Click <em>Get Started</em> on the landing page.<br><strong>2.</strong> Enter your username and password.<br><strong>3.</strong> You will be directed to your role-specific dashboard:<br>Audit Manager -- full dashboard with all features<br>Auditee Head -- department-filtered view<br>Observer -- read-only view of all data"
    },
    {
      id: "logout",
      combos: [
        "how to logout", "how to log out", "how to sign out",
        "logout process", "where is logout"
      ],
      signals: ["logout", "signout", "exit"],
      reply: "To log out:<br><br><strong>Option 1</strong> -- Click <em>Sign Out</em> at the bottom of the sidebar.<br><strong>Option 2</strong> -- Click the user button (top-right) and select <em>Sign Out</em>.<br><br>After logout you are returned to the landing page. Your session is cleared and the back button will not show authenticated pages."
    },
    {
      id: "profile",
      combos: [
        "how to change password", "change my password", "my profile", "edit profile",
        "update profile", "profile settings", "change email", "update name",
        "personal information", "account settings"
      ],
      signals: ["password", "profile", "personal"],
      reply: "To manage your profile:<br><br><strong>1.</strong> Click the user button (top-right) in the dashboard.<br><strong>2.</strong> Select <em>My Profile</em> to edit your name and email.<br><strong>3.</strong> Select <em>Change Password</em> to set a new password.<br><br>After changing your password you remain logged in. Your username cannot be changed."
    },
    {
      id: "compliance",
      combos: [
        "how does auditshield help compliance", "compliance tracking", "regulatory compliance",
        "compliance management", "iso compliance", "gdpr compliance",
        "what standards does it support"
      ],
      signals: ["compliance", "regulation", "standard", "iso", "gdpr", "sox", "regulatory"],
      reply: "AuditShield supports internal <strong>IT compliance management</strong>:<br><br><strong>Audit Trail</strong> -- every action is timestamped and traceable<br><strong>Accountability</strong> -- role-based access controls who can make changes<br><strong>Evidence Collection</strong> -- PDF reports serve as formal compliance documentation<br><strong>Overdue Monitoring</strong> -- automatic alerts prevent missed compliance deadlines<br><br>Useful for ISO 27001, SOX, GDPR, and NIST frameworks."
    },
    {
      id: "features",
      combos: [
        "what are the features", "list of features", "what can auditshield do", "all features",
        "feature list", "platform capabilities", "key features", "main features", "core features"
      ],
      signals: ["feature", "capabilit", "offer", "function"],
      reply: "<strong>AuditShield core features:</strong><br><br>Audit Lifecycle Management<br>Risk-Based Findings Tracking<br>Automatic Overdue Detection<br>Corrective Action Monitoring<br>Department Analytics and Charts<br>PDF Report Generation<br>Role-Based Access Control (3 roles)<br>Real-Time Dashboard with KPI cards"
    },
    {
      id: "thanks",
      combos: ["thank you", "thanks a lot", "thanks so much", "appreciate it", "that was helpful", "very helpful"],
      signals: ["thank", "thanks", "appreciate", "helpful"],
      reply: "You are very welcome! Feel free to ask anything else about AuditShield or internal audits anytime."
    },
    {
      id: "help",
      combos: [
        "help me", "what can you help with", "what can you answer", "what do you know",
        "what topics", "what questions can i ask", "i need help", "what can i ask", "guide me"
      ],
      signals: ["help", "assist", "guide", "topic"],
      reply: "I can help with:<br><br>What is AuditShield and how it works<br>Creating and managing audits<br>Findings and severity levels<br>Corrective actions and closing findings<br>Overdue tracking and compliance monitoring<br>PDF report generation<br>User roles and permissions<br>Dashboard and analytics features<br>Profile and password management<br><br>Just type your question!"
    }
  ];

  /* ── Fallback responses ── */
  var FALLBACKS = [
    "I may not have specific details on that, but I can help with <strong>audit processes, compliance tracking, findings management, and how AuditShield works</strong>. Try asking: How do I create an audit? What are findings? How does the dashboard work?",
    "That is a bit outside my specialized knowledge, but I am an expert in AuditShield platform features, internal audit concepts, findings, severity levels, corrective actions, and compliance tracking. What audit-related topic can I help you with?",
    "I am designed for <strong>audit and compliance topics</strong>. If your question relates to audits, findings, reports, user roles, or the AuditShield platform, I can give you a detailed answer. What would you like to know?",
    "Good question -- though slightly outside my area. I specialize in internal IT audit management. Try asking about audit planning, findings, corrective actions, PDF reports, user roles, or compliance."
  ];

  /* ── Levenshtein distance (i and j declared once -- no duplicate var) ── */
  function lev(a, b) {
    var i, j, m;
    if (a === b) { return 0; }
    if (!a.length) { return b.length; }
    if (!b.length) { return a.length; }
    m = [];
    for (i = 0; i <= b.length; i++) { m[i] = [i]; }
    for (j = 0; j <= a.length; j++) { m[0][j] = j; }
    for (i = 1; i <= b.length; i++) {
      for (j = 1; j <= a.length; j++) {
        m[i][j] = (b[i - 1] === a[j - 1])
          ? m[i - 1][j - 1]
          : 1 + Math.min(m[i - 1][j - 1], m[i][j - 1], m[i - 1][j]);
      }
    }
    return m[b.length][a.length];
  }

  /* ── Token similarity ── */
  function sim(wordA, wordB) {
    var mx;
    if (wordA === wordB) { return 1; }
    if (wordA.indexOf(wordB) !== -1) { return 0.9; }
    if (wordB.indexOf(wordA) !== -1) { return 0.85; }
    mx = Math.max(wordA.length, wordB.length);
    return mx ? Math.max(0, 1 - lev(wordA, wordB) / mx) : 1;
  }

  /* ── Normalize query and expand synonyms (x, y used in sort -- no shadow) ── */
  function normalize(text) {
    var i, k, keys, t;
    t = text.toLowerCase()
            .replace(/[?!.,;:'"()\[\]{}]/g, " ")
            .replace(/\s+/g, " ")
            .trim();
    keys = Object.keys(SYN).sort(function (x, y) { return y.length - x.length; });
    for (i = 0; i < keys.length; i++) {
      k = keys[i];
      if (t.indexOf(k) !== -1) { t = t.split(k).join(SYN[k]); }
    }
    return t.replace(/\s+/g, " ").trim();
  }

  /* ── Score one intent against the query
        c, ci, w, si declared once -- no duplicate var declarations
        single combo loop handles both exact and fuzzy matching ── */
  function scoreIntent(intent, q) {
    var c, ci, w, si;
    var s, hits, best, sv, cw, matched, words, sg;
    s     = 0;
    hits  = 0;
    words = q.split(" ").filter(function (wd) { return wd.length > 1; });

    for (c = 0; c < intent.combos.length; c++) {
      /* Exact combo match */
      if (q.indexOf(intent.combos[c]) !== -1) {
        s = Math.max(s, 0.95);
      }
      /* Fuzzy combo match */
      cw      = intent.combos[c].split(" ");
      matched = 0;
      for (ci = 0; ci < cw.length; ci++) {
        if (cw[ci].length < 3) { matched++; continue; }
        best = 0;
        for (w = 0; w < words.length; w++) {
          sv = sim(words[w], cw[ci]);
          if (sv > best) { best = sv; }
        }
        if (best > 0.8) { matched++; }
      }
      if (cw.length > 0 && (matched / cw.length) >= 0.75) {
        s = Math.max(s, 0.72);
      }
    }

    /* Signal token match */
    for (si = 0; si < intent.signals.length; si++) {
      sg = intent.signals[si];
      if (q.indexOf(sg) !== -1) { hits += 1; continue; }
      for (w = 0; w < words.length; w++) {
        if (sim(words[w], sg) >= 0.8) { hits += 0.7; break; }
      }
    }
    if (intent.signals.length > 0) {
      s = Math.max(s, (hits / intent.signals.length) * 0.6);
    }
    return s;
  }

  /* ── Find best matching intent ── */
  function matchIntent(raw) {
    var i, sc, q, best, found;
    if (!raw || !raw.trim()) { return null; }
    q     = normalize(raw);
    best  = 0;
    found = null;
    for (i = 0; i < KB.length; i++) {
      sc = scoreIntent(KB[i], q);
      if (sc > best) { best = sc; found = KB[i]; }
    }
    return (best >= 0.38) ? found : null;
  }

  /* ── Build reply text ── */
  function buildReply(intent) {
    var r = (typeof intent.reply === "function") ? intent.reply() : intent.reply;
    lastIntent = intent.id;
    return r;
  }

  /* ── Scroll messages pane to bottom ── */
  function scrollBot() {
    setTimeout(function () { messages.scrollTop = messages.scrollHeight; }, 50);
  }

  /* ── Create a message bubble DOM element ── */
  function mkMsg(html, type) {
    var wrap, av, ic, bub;
    wrap = document.createElement("div");
    wrap.className = "cb-msg cb-msg-" + type;
    av = document.createElement("div");
    av.className = "cb-msg-avatar";
    ic = document.createElement("i");
    if (type === "bot") {
      ic.className = "bi bi-shield-check";
    } else {
      ic.className         = "bi bi-person-fill";
      av.style.background  = "rgba(0,229,200,0.15)";
      av.style.borderColor = "rgba(0,229,200,0.3)";
      ic.style.color       = "#00e5c8";
      ic.style.fontSize    = "13px";
    }
    av.appendChild(ic);
    bub = document.createElement("div");
    bub.className = "cb-msg-bubble";
    bub.innerHTML = html;
    wrap.appendChild(av);
    wrap.appendChild(bub);
    return wrap;
  }

  /* ── Append a user message ── */
  function addUser(text) {
    var safe = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    messages.appendChild(mkMsg(safe, "user"));
    scrollBot();
    msgCount++;
  }

  /* ── Append a bot message after `delay` ms ── */
  function addBot(html, delay) {
    delay = delay || 0;
    setTimeout(function () {
      typingEl.classList.remove("visible");
      messages.appendChild(mkMsg(html, "bot"));
      scrollBot();
    }, delay);
  }

  /* ── Show typing indicator for `dur` ms ── */
  function showTyping(dur) {
    isTyping = true;
    typingEl.classList.add("visible");
    scrollBot();
    setTimeout(function () { isTyping = false; }, dur);
  }

  /* ══════════ PUBLIC API ══════════════════════════════════════ */

  window.cbSend = function () {
    var text, intent, reply, delay;
    text = (inp.value || "").trim();
    if (!text || isTyping) { return; }
    inp.value = "";
    inp.focus();
    sendBtn.disabled = true;
    turnCount++;
    addUser(text);
    intent = matchIntent(text);
    reply  = intent
      ? buildReply(intent)
      : FALLBACKS[fallbackIdx++ % FALLBACKS.length];
    delay = 700 + Math.min(reply.length / 8, 800) + Math.random() * 300;
    showTyping(delay);
    addBot(reply, delay + 80);
    setTimeout(function () { sendBtn.disabled = false; }, delay + 200);
  };

  window.cbQuick = function (text) {
    inp.value = text;
    window.cbSend();
  };

  window.cbToggle = function () {
    isOpen = !isOpen;
    if (isOpen) {
      panel.classList.add("cb-open");
      trigger.classList.add("cb-hidden");
      backdrop.classList.add("visible");
      unread.classList.remove("visible");
      setTimeout(function () { inp.focus(); }, 300);
    } else {
      panel.classList.remove("cb-open");
      trigger.classList.remove("cb-hidden");
      backdrop.classList.remove("visible");
    }
  };

  /* ── Keyboard shortcuts ── */
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && isOpen) { window.cbToggle(); }
  });

  if (trigger) {
    trigger.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        window.cbToggle();
      }
    });
  }

  /* ── Show unread indicator after 4 s if panel not yet opened ── */
  setTimeout(function () {
    if (!isOpen && unread) { unread.classList.add("visible"); }
  }, 4000);

}());
