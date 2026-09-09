# Work Report — Deploynix Job Portal

**Date:** 2026-09-08
**Repository:** `Devisanjai/job-portal-`
**Working branch:** `arena/01a07f36-job-portal`
**Base commit:** `1ee55a4` — *"Added Database and worked with Ai chatbot"*

---

## 1. Summary

Two features were designed, implemented, tested, and pushed to GitHub today:

| # | Feature | Commit |
|---|---------|--------|
| 1 | Job-assistant chatbot for job seekers (with job-alert capture) | `2fc6cd9` |
| 2 | Auto-expiry + "position filled" handling for job posts | `553d899` |

Plus two sets of VS Code instructions (local setup + how to pull the changes).

---

## 2. Feature 1 — Job Assistant Chatbot

**Requirement:** Add a chatbot on the job-seeker page that answers queries about job openings. If no relevant posting is found for a query, it should ask for the user's **full name** and **email**, so the team can email them when a suitable posting appears.

### What was built

- **Floating chat widget** (red 💬 button, bottom-right) on all job-seeker-facing pages.
  - Visible to **guests and job seekers**; hidden for **employers and admins**.
- **Conversation flow:**
  - Greets and handles `hi`, `hello`, `show latest jobs`, etc. (with quick-reply chips).
  - Searches **approved** postings by title, skills, company, location, and description; replies with ranked job cards linking to the job detail page.
  - When **no match is found**, asks for full name → then email → saves a **JobAlert** and confirms.
  - **Logged-in job seekers skip the questions** — their name/email is taken from their profile automatically.
- **Admin management ("Job Alerts" page)** in the custom Control Panel:
  - Lists every alert request, shows how many openings currently match, and has a one-click **"✉ Email matches"** button that emails the seeker with links to the matching jobs and marks it `Notified`.
- **Django admin** registration for the `JobAlert` model.

### Backend

- **Endpoint:** `POST /chatbot/message/` (`@csrf_exempt`, JSON) with a session-based state machine (greeting → search → collect name → collect email → confirm).
- **Model:** `JobAlert` (`full_name`, `email`, `job_query`, `status`, `created_at`) + migration `0031_jobalert`.
- **Search helper:** `search_jobs_for_query()` — tokenizes the query, drops stopwords, and scores jobs by field matches.

### Files touched

| File | Change |
|------|--------|
| `core/models.py` | Added `JobAlert` model |
| `core/migrations/0031_jobalert.py` | New migration |
| `core/views.py` | `chatbot_message` view + chatbot helpers |
| `core/urls.py` | `/chatbot/message/` route |
| `core/templates/core/chatbot_widget.html` | Widget markup + client JS |
| `core/static/core/css/chatbot.css` | Widget styles |
| `core/templates/core/base.html` | Include widget (guest/job-seeker only) |
| `core/admin.py` | Register `JobAlert` |
| `core/admin_panel_views.py` | Alert list / status / notify views |
| `core/templates/core/admin_panel/admin_base.html` | "Job Alerts" sidebar link |
| `core/templates/core/admin_panel/job_alerts_list.html` | New admin page |

---

## 3. Feature 2 — Auto-Expiry & "Position Filled" Handling

**Requirement:** Automatically remove a job post when the position is filled, or when it has been posted too long. Minimum posting lifetime is 2 months; after that the posting should be removed.

### Design decisions (confirmed with user)

1. **Soft-hide / archive** — posts are hidden, not deleted, so applications and records are kept.
2. **Manual "Mark as Filled"** button for the employer (not auto-detection by hired count).
3. **Configurable expiry duration per job** — 2 / 3 / 6 / 12 months, minimum 2, default 2.

### What was built

- **New `Job` fields:**
  - `expiry_months` (choices 2/3/6/12, min 2, default 2)
  - `expires_at` (auto-computed as `posted_at + expiry_months × 30 days`)
  - `is_active` (default `True`)
  - `inactive_reason` (`filled` / `expired` / `closed` / blank)
  - `ActiveJobManager.active()` — queryset helper returning currently-visible posts.
- **Employer controls** (in *My Posted Jobs*):
  - **"Mark as Filled"** — instantly hides the post from job seekers, keeps records.
  - **"Reactivate"** — restores a hidden/filled/expired post and resets its expiry date.
  - Status badges (Active / Position Filled / Expired) and the expiry date shown per job.
- **Auto-expiry scheduler:** management command `expire_job_posts` (with `--dry-run`) that hides expired posts and notifies the employer. Designed to be run by cron / Task Scheduler (e.g., daily).
- **Hidden everywhere for job seekers:** search (home), job vacancies, internships, walk-in jobs, chatbot search, job detail (404), apply, and save all exclude hidden/expired posts.
- **Post form** shows an "Auto-remove after" selector.
- **Job detail** shows the auto-removal date; owners see a warning banner with a Reactivate button.
- **Django admin** updated with the new fields and filters.

### Files touched

| File | Change |
|------|--------|
| `core/models.py` | Expiry fields + `ActiveJobManager` + `save()`/properties |
| `core/migrations/0032_job_auto_expiry.py` | Schema migration + backfill of existing posts |
| `core/forms.py` | `expiry_months` field on `JobPostForm` |
| `core/views.py` | `mark_job_filled`, `reactivate_job` views + visibility filters |
| `core/urls.py` | `/mark-filled/`, `/reactivate/` routes |
| `core/management/commands/expire_job_posts.py` | Scheduler command |
| `core/templates/core/post_job.html` | "Auto-remove after" selector |
| `core/templates/core/jobs_list.html` | Status badges + Mark as Filled / Reactivate |
| `core/templates/core/job_detail.html` | Expiry date + hidden-status banner |
| `core/admin.py` | Admin list display/filters for new fields |

---

## 4. Testing & Validation

### Feature 1 (chatbot)
- ✅ Greeting → search → match (job cards with links) → no-match → name → email → `JobAlert` saved.
- ✅ Pending/rejected jobs excluded from results.
- ✅ Admin "notify" email contains correct job links and marks the alert `Notified`.
- ✅ Widget correctly hidden for employer accounts.
- ✅ `manage.py check` passes; migration chain applies cleanly.

### Feature 2 (auto-expiry)
- ✅ Expiry date auto-set (~60 days for 2 months); `expiry_months = 1` rejected (min 2 enforced).
- ✅ Mark-as-Filled hides from seekers (404) while keeping owner access; Reactivate restores + resets expiry.
- ✅ `expire_job_posts` hides only expired posts and notifies the employer.
- ✅ Seeker listings (vacancies, internships) exclude hidden/expired posts.
- ✅ Guest hitting a hidden job gets a 404; active job returns 200.
- ✅ `manage.py check` passes; `0032_job_auto_expiry` applies cleanly.

### Existing test suite
- 9 tests run; **2 failures are pre-existing** on the base commit (`test_new_username_creates_account_and_logs_in`, `test_new_email_creates_employer_account`) and are unrelated to today's work. No new failures introduced.

---

## 5. VS Code Instructions Provided

1. **Local setup** — virtual environment, `pip install -r requirements.txt`, required `.env` file (with `SECRET_KEY`, `DATABASE_URL`, optional SMTP), `migrate`, `createsuperuser`, `runserver`. Optional `launch.json` debug config.
2. **How to pull today's changes** — `git fetch`, `checkout arena/01a07f36-job-portal`, `pull`, `migrate`, restart server; plus where to find each changed file.

---

## 6. Git / Branch Status

| Branch | HEAD | Contains |
|--------|------|----------|
| `arena/01a07f36-job-portal` | `553d899` | Chatbot + auto-expiry (all today's work) |
| `main` | `2fc6cd9` | Chatbot only (auto-expiry **not** yet merged) |

**Commits pushed today:**
- `2fc6cd9` — *Add job-assistant chatbot for job seekers*
- `553d899` — *Add auto-expiry and filled-status handling for job posts*

---

## 7. Pending / Recommended Next Steps

- [ ] **Merge into `main`** — the auto-expiry feature still needs to reach `main` (open a PR from `arena/01a07f36-job-portal`).
- [ ] **Schedule the expiry command** — e.g. daily cron / Render cron job:
  ```bash
  python manage.py expire_job_posts
  ```
- [ ] **Configure real SMTP** — notification emails (job alerts + expiry notices) need a valid `EMAIL_HOST_PASSWORD` (Gmail App Password).
- [ ] *(Optional)* Document the setup + scheduler in `README.md`.

---

## 8. Quick Reference — Useful Commands

```bash
# Local run
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Chatbot endpoint (for manual testing)
curl -X POST http://127.0.0.1:8000/chatbot/message/ \
  -H "Content-Type: application/json" \
  -d '{"message": "python developer"}'

# Auto-expiry (dry run first)
python manage.py expire_job_posts --dry-run
python manage.py expire_job_posts
```
