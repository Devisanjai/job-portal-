# Deploynix — Job Portal

A full-featured job portal built with Django. Employers can post jobs and manage
candidates; job seekers can browse, apply, save jobs, and chat with a built-in
job assistant.

## Key Features

- **Job Assistant Chatbot** — a floating chat widget that answers questions about
  current openings. When nothing matches a query, it collects the user's name and
  email so the team can reach out once a suitable role is posted (see *Job Alerts*
  in the admin control panel).
- **Job posting with auto-expiry** — every post has a configurable lifetime
  (2 / 3 / 6 / 12 months, minimum 2). Posts are automatically hidden when their
  time is up, and employers can "Mark as Filled" or "Reactivate" any post.
- Employer dashboard, candidate management, resume unlock (paid), Razorpay
  subscriptions, ATS resume checker, background verification, saved jobs, and more.

## Tech Stack

- Python 3.11+, Django 5.2
- PostgreSQL (production) or SQLite (local dev)
- Razorpay for payments, Gmail SMTP for email

## Local Setup

1. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** in the project root (required — `SECRET_KEY` has no default):

   ```env
   SECRET_KEY=change-this-to-a-long-random-string
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # SQLite (easiest for local dev)
   DATABASE_URL=sqlite:///db.sqlite3

   # OR PostgreSQL
   # DATABASE_URL=postgres://postgres:postgres@localhost:5432/job_portal

   # Optional — needed only for sending real emails (job alerts, notifications)
   # Use a Gmail "App Password", not your normal password
   # EMAIL_HOST_USER=you@gmail.com
   # EMAIL_HOST_PASSWORD=your-gmail-app-password
   ```

4. **Run migrations**

   ```bash
   python manage.py migrate
   ```

5. **(Optional) Load sample data**

   ```bash
   python manage.py loaddata datadump.json
   ```

6. **Create a superuser** (for Django admin and the Control Panel)

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**

   ```bash
   python manage.py runserver
   ```

   Visit `http://127.0.0.1:8000`.
   - Control panel: `/control-panel/`
   - Django admin: `/admin/`

## Auto-Expiry of Job Posts

Job posts are soft-hidden (records are kept) when filled or expired:

- **Mark as Filled** — the employer hides a post from job seekers from *My Posted Jobs*.
- **Expiry** — each post auto-hides after its chosen duration (default 2 months).
- **Reactivate** — restores a hidden post and resets its expiry date.

Run the expiry job on a schedule:

```bash
python manage.py expire_job_posts           # hide expired posts (notifies employers)
python manage.py expire_job_posts --dry-run # preview without changes
```

Scheduling examples:

- **Linux/macOS (cron, daily at 3am):**
  ```
  0 3 * * * cd /path/to/job-portal- && .venv/bin/python manage.py expire_job_posts
  ```
- **Windows (Task Scheduler):** run `C:\path\to\.venv\Scripts\python.exe manage.py expire_job_posts` daily.
- **Render:** add a Cron Job with the command `python manage.py expire_job_posts`.

## Running Tests

```bash
python manage.py test
```

> Note: two existing tests fail on the base commit
> (`test_new_username_creates_account_and_logs_in`,
> `test_new_email_creates_employer_account`) — unrelated to the chatbot and
> auto-expiry features.

## Project Structure

```
core/                  # Django app (models, views, templates, migrations)
  management/commands/ # expire_job_posts scheduler command
  static/core/         # css/js assets (incl. chatbot.css)
  templates/core/      # HTML templates (incl. chatbot_widget.html)
deploynix/             # project settings/urls
manage.py
```
