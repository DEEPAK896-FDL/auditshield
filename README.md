# 🛡️ AuditShield — Intelligent Audit Management System

> *Streamline your internal audits. Track findings. Generate reports. All in one secure platform.*

---

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-4.x-FF6384?logo=chartdotjs&logoColor=white)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF-red?logo=adobeacrobatreader&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?logo=opensourceinitiative&logoColor=white)

---

## 📖 Overview

**AuditShield** is a full-stack Django web application designed for managing internal audits end-to-end. It enables organisations to create and assign audits across departments, track observations and findings with severity classifications, and generate professional PDF reports — all within a secure, role-based environment.

The platform supports three distinct user roles — **Audit Manager**, **Auditee Head**, and **Observer** — each with precisely scoped permissions enforced at the view and decorator level. A dynamic Chart.js-powered dashboard gives real-time visibility into audit health, finding distributions, and overdue items, making AuditShield the single pane of glass for your internal compliance operations.

---

## ✨ Key Features

- 🔐 **Role-Based Access Control** — Audit Manager, Auditee Head, and Observer roles using Django's built-in auth system with custom `UserProfile` model and decorator-level enforcement
- 📋 **Audit Lifecycle Management** — Create, assign, and manage audits through Planned → Ongoing → Closed states with full audit trail
- 🏢 **Department Management** — Department creation, assignment, per-department analytics, and head-user mapping
- 🔍 **Finding & Observation Tracking** — Log findings with severity levels (Low / Medium / High / Critical), recommendations, target closure dates, and response notes
- 📊 **Interactive Dashboards** — Chart.js 4.x powered bar, pie, and line charts for audit status overview, findings by severity, and monthly trends
- 📄 **PDF Report Generation** — Downloadable professional audit reports built with ReportLab, including findings summary, status, and recommendations
- 🗂️ **Audit Trail & Activity Logs** — Track report generation, finding closure events, and key lifecycle timestamps
- ⚠️ **Critical Issues & Overdue Tracker** — Dedicated views surfacing critical-severity findings and past-deadline audits/findings
- 🔎 **Search, Filter & Sort** — Across audits and findings by status, severity, department, and date
- 🤖 **AI Chatbot Assistant** — Intent-based v3.0 chatbot on the landing page with fuzzy matching, synonym expansion, contextual suggestions, and voice assistant integration
- 📱 **Fully Responsive UI** — Bootstrap 5.3 with a premium dark-themed glowing design system, micro-animations, and glassmorphism components
- 🌐 **CSRF-Protected Views** — All state-changing endpoints protected; REST-friendly Django views throughout
- 🧩 **Modular Django App Architecture** — Clean separation via the `audits` app with its own models, views, forms, decorators, context processors, and management commands

---

## 🛠️ Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Backend | Python | 3.11+ | Core language |
| Backend | Django | 4.2 | Web framework, ORM, Auth |
| Frontend | HTML5 | — | Templating via Django templates |
| Frontend | CSS3 | — | Custom dark-theme design system |
| Frontend | Vanilla JavaScript | ES6+ | Client-side interactivity & chatbot engine |
| UI Framework | Bootstrap | 5.3 | Responsive design system |
| Charts | Chart.js | 4.x | Data visualization (CDN) |
| PDF | ReportLab | 4.1.0 | PDF report generation |
| Image | Pillow | 10.3.0 | Image processing support |
| Database | SQLite | Django default | Development database |
| Auth | Django Auth | Built-in | Custom role-based access via UserProfile |

---

## 📁 Project Structure

```
auditshield/                          ← Django project root
├── manage.py                         ← Django management entry point
├── requirements.txt                  ← Python dependencies
├── .gitignore                        ← Git ignore rules
│
├── auditshield/                      ← Project configuration package
│   ├── __init__.py
│   ├── settings.py                   ← Django settings (DB, apps, static, media)
│   ├── urls.py                       ← Root URL configuration
│   └── wsgi.py                       ← WSGI entry point
│
└── audits/                           ← Main Django application
    ├── __init__.py
    ├── admin.py                      ← Django admin registrations
    ├── apps.py                       ← App configuration
    ├── models.py                     ← Data models (UserProfile, Audit, Finding, etc.)
    ├── views.py                      ← All view functions (dashboard, audits, findings, reports)
    ├── urls.py                       ← App-level URL patterns
    ├── forms.py                      ← Django ModelForms
    ├── decorators.py                 ← Role-based access decorators
    ├── context_processors.py         ← Global template context (user role, notifications)
    ├── utils.py                      ← PDF generation (ReportLab) & utility helpers
    │
    ├── migrations/                   ← Database migrations
    │   ├── 0001_initial.py
    │   └── 0002_alter_userprofile_role.py
    │
    ├── management/
    │   └── commands/
    │       ├── setup_demo_data.py    ← Management command: populate demo data
    │       └── fix_user_roles.py     ← Management command: repair user role assignments
    │
    ├── static/audits/
    │   ├── css/
    │   │   └── main.css              ← Global dark-theme design system
    │   └── js/
    │       └── main.js               ← Client-side utilities & animations
    │
    └── templates/audits/
        ├── base.html                 ← Master layout template (sidebar, navbar, glowing UI)
        ├── landing.html              ← Public landing page with AI chatbot
        ├── login.html                ← Authentication page
        ├── dashboard.html            ← Main dashboard with Chart.js charts
        ├── audit_list.html           ← Paginated audit list with filters
        ├── audit_create.html         ← Audit creation form
        ├── audit_detail.html         ← Audit detail + findings list
        ├── audit_edit.html           ← Audit editing form
        ├── finding_list.html         ← Findings list with severity filter
        ├── finding_create.html       ← Finding creation form
        ├── finding_detail.html       ← Finding detail view
        ├── finding_edit.html         ← Finding editing form
        ├── department_analytics.html ← Department overview with charts
        ├── department_detail.html    ← Per-department audit & findings breakdown
        ├── report_preview.html       ← Audit report preview before PDF download
        ├── critical_issues.html      ← Critical-severity findings tracker
        ├── overdue_items.html        ← Overdue audits & findings tracker
        ├── user_profile.html         ← User profile & role display
        ├── change_password.html      ← Password change form
        └── access_denied.html        ← 403-style access denied page
```

---

## ⚙️ Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/DEEPAK896-FDL/auditshield.git
cd auditshield

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Create a superuser (Admin)
python manage.py createsuperuser

# 6. (Optional) Load demo data
python manage.py setup_demo_data

# 7. Run the development server
python manage.py runserver
```

Then open **http://127.0.0.1:8000** in your browser.

> **Note:** The landing page is publicly accessible at `/`. After logging in, you will be redirected based on your assigned role.

---

## 👥 User Roles & Permissions

| Permission | Audit Manager | Auditee Head | Observer |
|---|:---:|:---:|:---:|
| View landing page | ✅ | ✅ | ✅ |
| Login / Logout | ✅ | ✅ | ✅ |
| View Dashboard | ✅ | ✅ | ✅ |
| Create / Edit Audits | ✅ | ❌ | ❌ |
| Assign Audits to Departments | ✅ | ❌ | ❌ |
| View Audit List & Details | ✅ | ✅ (own dept) | ✅ (read-only) |
| Create / Edit Findings | ✅ | ✅ | ❌ |
| Close Findings | ✅ | ✅ | ❌ |
| View Finding Details | ✅ | ✅ | ✅ |
| Generate & Download PDF Reports | ✅ | ❌ | ❌ |
| View Department Analytics | ✅ | ✅ (own dept) | ✅ |
| View Critical Issues & Overdue | ✅ | ✅ | ✅ |
| Manage Users (Django Admin) | Superuser only | ❌ | ❌ |

> Role assignment is done via Django Admin → User Profiles. Each role is enforced via custom `@role_required` decorators on every view.

---

## 📊 Dashboard & Reports

### Chart.js Dashboard
The main dashboard at `/dashboard/` renders three live Chart.js 4.x visualisations:

- **Audit Status Bar Chart** — Count of Planned, Ongoing, and Closed audits side-by-side
- **Findings by Severity Pie Chart** — Distribution of Low / Medium / High / Critical findings
- **Monthly Audit Trend Line Chart** — Audit creation volume over the past 6 months

All chart data is injected directly from Django views as inline template variables for reliability and performance.

### PDF Report Generation (ReportLab)
Navigate to any audit detail page → **Generate Report** → **Download PDF**.

The exported PDF includes:
- Audit metadata (title, department, dates, status, assigned auditor)
- Executive summary / objectives
- Complete findings table with severity, status, and recommendations
- Report generation timestamp and generated-by attribution

Reports are built using **ReportLab 4.1.0** via `audits/utils.py` and streamed directly as HTTP responses — no files are stored on disk.

---

## 📸 Screenshots

> Screenshots will be added here.

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. **Fork** the repository
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Commit your changes**
   ```bash
   git commit -m "feat: describe your change"
   ```
4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open a Pull Request** against the `main` branch

Please ensure your code follows Django best practices, includes relevant comments, and does not break existing functionality.

---

## 📜 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 Deepak

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 👨‍💻 Author

**Deepak**
GitHub: [@DEEPAK896-FDL](https://github.com/DEEPAK896-FDL)

---

<div align="center">
  <sub>Built with ❤️ using Django 4.2 · Bootstrap 5.3 · Chart.js 4.x · ReportLab</sub>
</div>
