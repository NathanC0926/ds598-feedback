# DS598 Feedback Forms — Deployment Guide

Static HTML feedback forms for all 12 DS598 teams, hosted on GitHub Pages and
submitted via Web3Forms.

---

## Step 1 — Get your Web3Forms access key (free, 2 min)

1. Go to **https://web3forms.com** and enter `your_email`
2. Click **Create Access Key** — Web3Forms will email you a key instantly
3. Open `generate_forms.py` and replace the placeholder at the top:

   ```python
   WEB3FORMS_ACCESS_KEY = "YOUR_WEB3FORMS_ACCESS_KEY"   # ← paste here
   ```

4. Re-run the generator (see Step 3) to bake the key into all HTML files.

---

## Step 2 — Generate the HTML files

Make sure Python 3 is installed, then from the project root:

```bash
python3 generate_forms.py
```

This writes `ds598-feedback/team-1.html` … `team-12.html` plus `index.html`.

---

## Step 4 — Deploy to GitHub Pages


Enable Pages:

1. Go to your repo → **Settings** → **Pages** (left sidebar)
2. Under **Build and deployment → Source**, choose **Deploy from a branch**
3. Branch: `main`, folder: `/ (root)`
4. Click **Save**

GitHub will build and publish in ~60 seconds.

---

## Step 5 — Verify

Visit `https://nathanc0926.github.io/ds598-feedback/team-1.html` — you should
see the Team 1 form. Test a submission; it should arrive at `nc0926@bu.edu`
within a minute.

---

## Final URLs to distribute

| Team | URL |
|------|-----|
| 1  | https://nathanc0926.github.io/ds598-feedback/team-1.html  |
| 2  | https://nathanc0926.github.io/ds598-feedback/team-2.html  |
| 3  | https://nathanc0926.github.io/ds598-feedback/team-3.html  |
| 4  | https://nathanc0926.github.io/ds598-feedback/team-4.html  |
| 5  | https://nathanc0926.github.io/ds598-feedback/team-5.html  |
| 6  | https://nathanc0926.github.io/ds598-feedback/team-6.html  |
| 7  | https://nathanc0926.github.io/ds598-feedback/team-7.html  |
| 8  | https://nathanc0926.github.io/ds598-feedback/team-8.html  |
| 9  | https://nathanc0926.github.io/ds598-feedback/team-9.html  |
| 10 | https://nathanc0926.github.io/ds598-feedback/team-10.html |
| 11 | https://nathanc0926.github.io/ds598-feedback/team-11.html |
| 12 | https://nathanc0926.github.io/ds598-feedback/team-12.html |

---

## Notes

- **Duplicate submissions** are not blocked — acceptable per spec.
- **Team number** is sent as a hidden field (`team_number`) in every submission,
  so you can filter emails by subject line ("DS598 Team N Feedback Submission").
- Re-running `generate_forms.py` overwrites all files; safe to do at any time.
- Web3Forms free tier allows 250 submissions/month — more than enough for 50 students.
