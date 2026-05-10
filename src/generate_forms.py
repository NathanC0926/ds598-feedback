#!/usr/bin/env python3
"""
DS598 Feedback Form Generator
Generates 12 static HTML pages (one per team) for GitHub Pages + Web3Forms.
"""

import csv
import io
import os
from collections import defaultdict
from pathlib import Path

# ── Load .env (no external dependencies required) ────────────────────────────
def _load_env(path=".env"):
    env_path = Path(path)
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

_load_env()

# ── Configuration ─────────────────────────────────────────────────────────────
WEB3FORMS_ACCESS_KEY = os.environ.get("WEB3FORMS_ACCESS_KEY")
RESPONSE_EMAIL       = os.environ.get("RESPONSE_EMAIL")
GITHUB_PAGES_BASE    = "https://nathanc0926.github.io/ds598-feedback"

if WEB3FORMS_ACCESS_KEY == "YOUR_WEB3FORMS_ACCESS_KEY":
    print("⚠️  Warning: WEB3FORMS_ACCESS_KEY not set in .env — forms will not submit!")
# ──────────────────────────────────────────────────────────────────────────────

RATING_OPTIONS = ["Poor", "Not Great", "Ok", "Good", "Excellent"]

SELF_RATINGS = [
    ("self_attend",    "I attend team meetings regularly and on time. I arrive prepared to contribute."),
    ("self_positive",  "I help build a positive team environment by being cooperative, treating my team with respect, and providing assistance and/or encouragement."),
    ("self_tasks",     "I complete all assigned tasks by the deadline. My work is thorough, comprehensive, and advances the project."),
    ("team_engaged",   "Overall, the team is engaged during meetings. The team arrives prepared to contribute."),
    ("team_comms",     "Overall, the team responds to communications in a timely manner and all communications are polite and constructive."),
    ("team_quality",   "Overall, the team completes tasks on time and produces high quality work."),
    ("team_climate",   "Overall, the team has built a positive team climate. Teammates cooperate and treat everyone with respect."),
    ("self_exp",       "How would you rate your experience this semester with the project?"),
    ("recommend",      "Although a required course, how likely are you to recommend DS598 to a classmate or peer?"),
]

TEAMMATE_RATINGS = [
    ("attend",    "Attends team meetings regularly and on time. They arrive prepared to contribute."),
    ("comms",     "Responds to communications in a timely manner and their communications are polite and constructive."),
    ("positive",  "Helps build a positive team environment by being cooperative, treating their team with respect, and providing assistance and/or encouragement."),
    ("tasks",     "Completes all assigned tasks by the deadline. Their work is thorough, comprehensive, and advances the project."),
]

TAs = ["Nathan Chang",
       "Zihao Guo"]


def normalize_name(raw: str) -> str:
    """Convert 'Last, First' → 'First Last'. Pass-through if no comma."""
    raw = raw.strip()
    if "," in raw:
        parts = raw.split(",", 1)
        return f"{parts[1].strip()} {parts[0].strip()}"
    return raw


def parse_teams() -> dict[int, list[str]]:
    teams: dict[int, list[str]] = defaultdict(list)

    with open("src/teams.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            group = int(row["groups"])
            display_name = normalize_name(row["name"])
            teams[group].append(display_name)

    return dict(sorted(teams.items()))


def radio_matrix(field_prefix: str, questions: list[tuple[str, str]], options: list[str]) -> str:
    """Build a rating matrix table."""
    header_cells = "".join(f'<th class="opt-label">{o}</th>' for o in options)
    rows = ""
    for key, label in questions:
        name = f"{field_prefix}_{key}"
        radio_cells = "".join(
            f'<td class="radio-cell">'
            f'<input type="radio" name="{name}" value="{opt}" required>'
            f'</td>'
            for opt in options
        )
        rows += f"""
        <tr>
          <td class="q-label">{label}</td>
          {radio_cells}
        </tr>"""
    return f"""
    <div class="matrix-wrap">
      <table class="matrix">
        <thead>
          <tr>
            <th class="q-col"></th>
            {header_cells}
          </tr>
        </thead>
        <tbody>{rows}
        </tbody>
      </table>
    </div>"""


def teammate_section(member: str, idx: int) -> str:
    safe_id = f"tm{idx}"
    questions = [(f"{safe_id}_{key}", label) for key, label in TEAMMATE_RATINGS]
    matrix = radio_matrix(safe_id, questions, RATING_OPTIONS)
    comments_name = f"{safe_id}_comments"
    return f"""
    <div class="teammate-block">
      <h3 class="teammate-name">{member}</h3>
      {matrix}
      <div class="field-group">
        <label for="{comments_name}">Any additional comments about {member}?</label>
        <textarea id="{comments_name}" name="{comments_name}" rows="3"
                  placeholder="Optional — share anything else about {member}'s contribution…"></textarea>
      </div>
    </div>"""


def generate_html(team_num: int, members: list[str]) -> str:
    # ── Respondent dropdown ───────────────────────────────────────────────────
    options_html = '<option value="" disabled selected>— Select your name —</option>\n'
    for m in members:
        options_html += f'        <option value="{m}">{m}</option>\n'

    # ── Section 1 self-rating matrix ──────────────────────────────────────────
    section1_matrix = radio_matrix("s1", SELF_RATINGS, RATING_OPTIONS)

    # ── Section 2 teammate blocks ─────────────────────────────────────────────
    teammate_blocks = ""
    for i, member in enumerate(members):
        teammate_blocks += teammate_section(member, i + 1)

    # ── Full HTML ─────────────────────────────────────────────────────────────
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>DS598 Team {team_num} — End-of-Semester Feedback</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet" />
  <style>
    /* ── Reset & Variables ───────────────────────────────────────────── */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg:        #f7f5f0;
      --surface:   #ffffff;
      --border:    #e2ddd6;
      --accent:    #c0392b;
      --accent-dk: #962d22;
      --text:      #1a1714;
      --muted:     #6b6560;
      --radius:    10px;
      --shadow:    0 2px 12px rgba(0,0,0,.07);
    }}

    body {{
      font-family: 'DM Sans', sans-serif;
      font-size: 15px;
      line-height: 1.6;
      background: var(--bg);
      color: var(--text);
      padding: 40px 16px 80px;
    }}

    /* ── Layout ──────────────────────────────────────────────────────── */
    .page-wrap {{
      max-width: 860px;
      margin: 0 auto;
    }}

    /* ── Header ──────────────────────────────────────────────────────── */
    .page-header {{
      text-align: center;
      margin-bottom: 48px;
    }}
    .course-tag {{
      display: inline-block;
      background: var(--accent);
      color: #fff;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: .12em;
      text-transform: uppercase;
      padding: 4px 14px;
      border-radius: 40px;
      margin-bottom: 18px;
    }}
    .page-header h1 {{
      font-family: 'DM Serif Display', serif;
      font-size: clamp(28px, 5vw, 42px);
      line-height: 1.15;
      color: var(--text);
    }}
    .page-header p {{
      margin-top: 10px;
      color: var(--muted);
      font-size: 14px;
    }}

    /* ── Card / Section ──────────────────────────────────────────────── */
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding: 32px 36px;
      margin-bottom: 28px;
    }}
    @media(max-width:600px) {{
      .card {{ padding: 20px 16px; }}
    }}

    .section-header {{
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 2px solid var(--border);
    }}
    .section-num {{
      width: 34px; height: 34px;
      border-radius: 50%;
      background: var(--accent);
      color: #fff;
      font-weight: 700;
      font-size: 14px;
      display: grid;
      place-items: center;
      flex-shrink: 0;
    }}
    .section-header h2 {{
      font-family: 'DM Serif Display', serif;
      font-size: 22px;
      line-height: 1.2;
    }}

    /* ── Respondent dropdown ─────────────────────────────────────────── */
    .field-group {{
      margin-bottom: 20px;
    }}
    .field-group label {{
      display: block;
      font-weight: 500;
      margin-bottom: 6px;
      font-size: 14px;
    }}
    select, textarea {{
      width: 100%;
      font-family: inherit;
      font-size: 14px;
      border: 1.5px solid var(--border);
      border-radius: 6px;
      padding: 9px 12px;
      background: #faf9f7;
      color: var(--text);
      transition: border-color .15s;
    }}
    select:focus, textarea:focus {{
      outline: none;
      border-color: var(--accent);
    }}
    textarea {{ resize: vertical; }}

    /* ── Rating Matrix ───────────────────────────────────────────────── */
    .matrix-wrap {{
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      margin-bottom: 24px;
    }}
    .matrix {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13.5px;
    }}
    .matrix thead th {{
      background: #f3ede6;
      font-weight: 600;
      font-size: 12px;
      letter-spacing: .05em;
      text-transform: uppercase;
      padding: 8px 14px;
      text-align: center;
      color: var(--muted);
    }}
    .matrix th.q-col {{ width: 52%; text-align: left; }}
    .matrix td, .matrix th {{
      border: 1px solid var(--border);
      padding: 10px 12px;
    }}
    .matrix tbody tr:nth-child(odd) {{ background: #faf9f7; }}
    .matrix tbody tr:hover {{ background: #f3ede6; transition: background .1s; }}
    .q-label {{ text-align: left; line-height: 1.45; }}
    .radio-cell {{ text-align: center; }}
    .radio-cell input[type=radio] {{
      width: 17px; height: 17px;
      accent-color: var(--accent);
      cursor: pointer;
    }}
    .opt-label {{ text-align: center; min-width: 72px; }}

    /* ── Teammate blocks ─────────────────────────────────────────────── */
    .teammate-block {{
      margin-bottom: 36px;
      padding-bottom: 36px;
      border-bottom: 1px dashed var(--border);
    }}
    .teammate-block:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
    .teammate-name {{
      font-family: 'DM Serif Display', serif;
      font-size: 18px;
      margin-bottom: 14px;
      color: var(--accent-dk);
    }}

    /* ── Submit button ───────────────────────────────────────────────── */
    .submit-area {{
      text-align: center;
      margin-top: 10px;
    }}
    .btn-submit {{
      display: inline-block;
      background: var(--accent);
      color: #fff;
      border: none;
      border-radius: 8px;
      padding: 14px 52px;
      font-family: 'DM Sans', sans-serif;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      letter-spacing: .02em;
      transition: background .15s, transform .1s;
    }}
    .btn-submit:hover  {{ background: var(--accent-dk); transform: translateY(-1px); }}
    .btn-submit:active {{ transform: translateY(0); }}
    .submit-note {{
      margin-top: 10px;
      font-size: 13px;
      color: var(--muted);
    }}

    /* ── Thank-you page ──────────────────────────────────────────────── */
    .thankyou {{
      display: none;
      text-align: center;
      padding: 60px 20px;
    }}
    .thankyou h2 {{
      font-family: 'DM Serif Display', serif;
      font-size: 36px;
      margin-bottom: 14px;
      color: var(--accent);
    }}
    .thankyou p {{ color: var(--muted); font-size: 15px; }}
  </style>
</head>
<body>
<div class="page-wrap">

  <!-- Header -->
  <header class="page-header">
    <div class="course-tag">DS598 · Team {team_num}</div>
    <h1>End-of-Semester Feedback</h1>
    <p>Your responses are confidential and help us improve the course experience.</p>
  </header>

  <!-- Form -->
  <div id="form-container">
    <form id="feedback-form"
          action="https://api.web3forms.com/submit"
          method="POST">

      <!-- Web3Forms hidden fields -->
      <input type="hidden" name="access_key" value="{WEB3FORMS_ACCESS_KEY}" />
      <input type="hidden" name="subject"    value="DS598 Team {team_num} Feedback Submission" />
      <input type="hidden" name="from_name"  value="DS598 Feedback Form" />
      <input type="hidden" name="redirect"   value="" />
      <input type="hidden" name="team_number" value="{team_num}" />
      <input type="hidden" name="botcheck"   value="" style="display:none" />

      <!-- ── Section 1: Self & Team Ratings ──────────────────────────── -->
      <div class="card">
        <div class="section-header">
          <div class="section-num">1</div>
          <h2>Self &amp; Team Ratings</h2>
        </div>

        <div class="field-group">
          <label for="respondent">Who are you? <span style="color:var(--accent)">*</span></label>
          <select id="respondent" name="respondent" required>
            {options_html}
          </select>
        </div>

        {section1_matrix}
      </div>

      <!-- ── Section 2: Teammate Evaluations ─────────────────────────── -->
      <div class="card">
        <div class="section-header">
          <div class="section-num">2</div>
          <h2>Teammate Evaluations</h2>
        </div>
        <p style="color:var(--muted);font-size:13.5px;margin-bottom:24px;">
          Rate each of your teammates below. Skip anyone who is you (you rated yourself above).
        </p>
        {teammate_blocks}
      </div>

      <!-- ── Section 3: Project Experience ───────────────────────────── -->
      <div class="card">
        <div class="section-header">
          <div class="section-num">3</div>
          <h2>Project Experience</h2>
        </div>

        <div class="field-group">
          <label for="successes">What successes has your team had? What went well? <span style="color:var(--accent)">*</span></label>
          <textarea id="successes" name="successes" rows="4" required
                    placeholder="Describe your team's wins and high points…"></textarea>
        </div>

        <div class="field-group">
          <label for="challenges">What has been the biggest challenge for your team or with the project? <span style="color:var(--accent)">*</span></label>
          <textarea id="challenges" name="challenges" rows="4" required
                    placeholder="Be honest — this helps us improve the course…"></textarea>
        </div>

        {radio_matrix("s3", [("exp", "How would you rate your experience this semester?")], RATING_OPTIONS)}

        <!-- Prof / TA feedback -->
        {"".join([
            f'<div class="field-group"><label for="{fid}">{label} <span style="color:var(--accent)">*</span></label>'
            f'<textarea id="{fid}" name="{fid}" rows="3" required placeholder="{placeholder}"></textarea></div>'
            for fid, label, placeholder in [
                ("prof_well",   "What's one thing Professor Seferlis did really well?", "Something specific that helped you…"),
                ("prof_better", "What's one thing Professor Seferlis could do better?",  "Constructive suggestion…"),
                ("ta1_well",   f"What's one thing {TAs[0]} did really well?",    "Something specific that helped you…"),
                ("ta1_better", f"What's one thing {TAs[0]} could do better?",    "Constructive suggestion…"),
                ("ta2_well",   f"What's one thing {TAs[1]} did really well?",              "Something specific that helped you…"),
                ("ta2_better", f"What's one thing {TAs[1]} could do better?",              "Constructive suggestion…"),
            ]
        ])}
      </div>

      <!-- Submit -->
      <div class="submit-area">
        <button type="submit" class="btn-submit" id="submit-btn">Submit Feedback</button>
        <p class="submit-note">All fields marked <span style="color:var(--accent)">*</span> are required.</p>
      </div>

    </form>
  </div><!-- /#form-container -->

  <!-- Thank-you message (shown after submission) -->
  <div class="thankyou" id="thankyou">
    <h2>Thank you!</h2>
    <p>Your feedback has been submitted successfully.<br>
       We appreciate you taking the time to share your thoughts.</p>
  </div>

</div><!-- /.page-wrap -->

<script>
  document.getElementById('feedback-form').addEventListener('submit', async function(e) {{
    e.preventDefault();
    const btn  = document.getElementById('submit-btn');
    const form = this;

    btn.textContent = 'Submitting…';
    btn.disabled    = true;

    try {{
      const resp = await fetch(form.action, {{
        method:  'POST',
        body:    new FormData(form),
        headers: {{ 'Accept': 'application/json' }},
      }});
      const data = await resp.json();

      if (data.success) {{
        document.getElementById('form-container').style.display = 'none';
        document.getElementById('thankyou').style.display       = 'block';
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }} else {{
        alert('Submission failed. Please check your connection and try again.');
        btn.textContent = 'Submit Feedback';
        btn.disabled    = false;
      }}
    }} catch(err) {{
      alert('Network error. Please try again.');
      btn.textContent = 'Submit Feedback';
      btn.disabled    = false;
    }}
  }});
</script>
</body>
</html>
"""


def main():
    import os
    teams = parse_teams()
    out_dir = ".."
    os.makedirs(out_dir, exist_ok=True)

    print("Generating HTML files…\n")
    for team_num, members in teams.items():
        html = generate_html(team_num, members)
        path = os.path.join(out_dir, f"team-{team_num}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✓ team-{team_num}.html  ({len(members)} members: {', '.join(members)})")

    # Also write a minimal index.html redirect to team-1 so the root doesn't 404
    index = """<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0;url=team-1.html"></head>
<body><p>Redirecting…</p></body></html>\n"""
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(index)

    print(f"\nDone — {len(teams)} files written to ./{out_dir}/")
    print("\n── Final URLs ──────────────────────────────────────────")
    base = "https://nathanc0926.github.io/ds598-feedback"
    for t in teams:
        print(f"  Team {t:>2}: {base}/team-{t}.html")
    print()


if __name__ == "__main__":
    main()