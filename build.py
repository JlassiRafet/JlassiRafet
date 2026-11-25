"""Builds profile.svg: animated terminal-style GitHub card. Needs `gh` (GH_TOKEN) and python3 only."""
import math, base64, re, subprocess, json, datetime, pathlib

D = pathlib.Path(__file__).parent
A = D / "assets"
U = "JlassiRafet"


def gh(*args):
    return json.loads(subprocess.check_output(["gh", "api", *args]))


gq = '''{user(login:"%s"){createdAt followers{totalCount}
 contributionsCollection{totalCommitContributions restrictedContributionsCount
  contributionCalendar{totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}
 repositories(first:100,ownerAffiliations:OWNER,isFork:false){totalCount nodes{stargazerCount languages(first:20){edges{size node{name color}}}}}}}''' % U
u = gh("graphql", "-f", "query=" + gq)["data"]["user"]
repo = gh("repos/%s/IGRIS" % U)

repos = u["repositories"]["nodes"]
stars = sum(r["stargazerCount"] for r in repos)
cc = u["contributionsCollection"]
commits = cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
followers = u["followers"]["totalCount"]
nrepos = u["repositories"]["totalCount"]

# uptime since account creation
a = datetime.datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00")).date()
b = datetime.date.today()
y, m, d = b.year - a.year, b.month - a.month, b.day - a.day
if d < 0:
    m -= 1
    d += (b.replace(day=1) - datetime.timedelta(days=1)).day
if m < 0:
    y -= 1
    m += 12
pl = lambda n, w: f"{n} {w}" + ("" if n == 1 else "s")
uptime = ", ".join(pl(n, w) for n, w in ((y, "year"), (m, "month"), (d, "day")) if n)

# languages by bytes (private repos included; only percentages are shown)
tot, col = {}, {}
for r in repos:
    for e in r["languages"]["edges"]:
        n = e["node"]["name"]
        tot[n] = tot.get(n, 0) + e["size"]
        col[n] = e["node"]["color"]
S = sum(tot.values())
LANGC = ["#9890F3", "#C2B45A", "#7F5DBC", "#B8B2FA", "#5a4d9a"]  # fruit palette by rank, not GitHub colours
pct = [(n, round(100 * v / S), LANGC[i]) for i, (n, v) in enumerate(sorted(tot.items(), key=lambda x: -x[1])[:5])]

# activity
cal = cc["contributionCalendar"]
weeks = cal["weeks"]
days = [x for w in weeks for x in w["contributionDays"]]
LVL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
run = longest = 0
for x in days:
    run = run + 1 if x["contributionCount"] else 0
    longest = max(longest, run)
cur = 0
for x in reversed(days[:-1] if not days[-1]["contributionCount"] else days):
    if not x["contributionCount"]:
        break
    cur += 1
best = max(days, key=lambda x: x["contributionCount"])
best_s = f'{best["contributionCount"]} · {datetime.date.fromisoformat(best["date"]):%b} {datetime.date.fromisoformat(best["date"]).day}'

img = base64.b64encode((A / "wanted.jpg").read_bytes()).decode()
icon = lambda s: re.search(r' d="([^"]+)"', (A / f"{s}.svg").read_text()).group(1)

W, H = 904, 1125
# Gum-Gum fruit palette: body #9890F3, mid #7F6BCA, shadow #7F5DBC, outline #2A2760, stem olive-gold
RED, YEL, ORG, DIM, TXT = "#9890F3", "#C2B45A", "#B8B2FA", "#8c88b8", "#e6e3f8"
HEAT = ["#242040", "#4a3f8f", "#6b58b8", "#9890F3", "#cfc9ff"]
o = []
a_ = o.append

a_(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="JetBrains Mono, DejaVu Sans Mono, Menlo, Consolas, monospace">')
a_('''<style>
.p{opacity:0;animation:up .8s cubic-bezier(.2,.8,.2,1) forwards}
@keyframes up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.fl{animation:fl 3.6s ease-in-out infinite}
@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}
.kb{transform-box:fill-box;transform-origin:center;animation:kb 12s ease-in-out infinite}
.sp{transform-box:fill-box;transform-origin:center;animation:spin 40s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes kb{0%,100%{transform:scale(1)}50%{transform:scale(1.035)}}
.cv{transform-box:fill-box;transform-origin:right;animation:wipe 1.4s cubic-bezier(.65,0,.25,1) both}
@keyframes wipe{to{transform:scaleX(0)}}
.ty{animation:wipe 1s steps(12,end) .4s both}
.cu{animation:type 1s steps(12,end) .4s both,blink 1.1s steps(1) 1.4s infinite}
@keyframes type{to{transform:translateX(108px)}}
@keyframes blink{50%{opacity:0}}
.c{transform-box:fill-box;transform-origin:center;opacity:0;animation:pop .5s cubic-bezier(.2,.8,.2,1) forwards}
@keyframes pop{from{opacity:0;transform:scale(.3)}to{opacity:1;transform:scale(1)}}
.td{animation:pulse 2s ease-in-out 2.6s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
.gl{animation:glint 3.8s linear infinite}
@keyframes glint{from{transform:translateX(-140px)}to{transform:translateX(840px)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.p,.c{opacity:1!important}.cv,.glw{display:none}}
</style>''')
a_('<defs><linearGradient id="py" x1="0" y1="0" x2="1" y2="1"><stop offset=".45" stop-color="#4B8BBE"/><stop offset=".55" stop-color="#FFD43B"/></linearGradient>'
   '<linearGradient id="gl"><stop offset="0" stop-color="#b8b2fa" stop-opacity="0"/><stop offset=".5" stop-color="#e2dfff"/><stop offset="1" stop-color="#b8b2fa" stop-opacity="0"/></linearGradient>'
   '<clipPath id="pc"><rect x="38" y="133" width="269" height="402"/></clipPath>'
   '<clipPath id="rl"><rect x="38" y="1109" width="838" height="4"/></clipPath></defs>')
a_(f'<rect width="{W}" height="{H}" fill="#0e0c1c"/><rect x=".5" y=".5" width="{W-1}" height="{H-1}" fill="none" stroke="#2A2760"/>')


def sec(delay, cls="p"):
    a_(f'<g class="{cls}" style="animation-delay:{delay}s">')


end = lambda: a_("</g>")


def panel(x, y, w, h, fill="#181630"):
    a_(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>')


def lead(x1, x2, y, label, val, vcol=TXT, lcol=YEL):
    a_(f'<text x="{x1}" y="{y}" font-size="15" fill="{lcol}">. {label}:</text>')
    a_(f'<text x="{x2}" y="{y}" font-size="15" fill="{vcol}" text-anchor="end">{val}</text>')
    a_(f'<line x1="{x1+(len(label)+4)*9.1}" x2="{x2-len(val)*9.1-8}" y1="{y-4}" y2="{y-4}" stroke="#3b3770" stroke-dasharray="1 5" stroke-linecap="round"/>')


def head(x1, x2, y, t):
    a_(f'<text x="{x1}" y="{y}" font-size="15" fill="{RED}">— {t} </text>')
    a_(f'<line x1="{x1+(len(t)+3)*9.1}" x2="{x2}" y1="{y-5}" y2="{y-5}" stroke="#4a4585"/>')


label = lambda x, y, t: a_(f'<text x="{x}" y="{y}" font-size="12" fill="{DIM}" letter-spacing="3">{t}</text>')

# header
sec(0)
panel(38, 28, 838, 96)
a_('<text x="64" y="76" font-size="32" fill="#fff" letter-spacing="1">JoyBoy</text>')
a_(f'<text x="64" y="106" font-size="15" fill="{RED}">@{U}</text>')
a_('<rect class="ty" x="62" y="92" width="130" height="18" fill="#181630"/>')
a_(f'<rect class="cu" x="64" y="93" width="9" height="16" fill="{RED}"/>')
sw = "M" + " L".join(f"{800 + r*math.cos(t):.1f} {76 + r*math.sin(t):.1f}" for t in [i * .2 for i in range(0, 90)] for r in [2 + t * 2.1])
a_(f'<path class="sp" d="{sw}" fill="none" stroke="{RED}" stroke-width="3" stroke-linecap="round" opacity=".45"/>')
end()

# poster
sec(.15)
a_('<g clip-path="url(#pc)"><image class="kb" href="data:image/jpeg;base64,%s" x="38" y="133" width="269" height="402" preserveAspectRatio="xMidYMid slice"/></g>' % img)
end()

# info
sec(.3)
panel(316, 133, 560, 291)
X1, X2, mid = 330, 860, 590
head(X1, X2, 154, f"{U}@github")
lead(X1, X2, 177, "Uptime", uptime)
lead(X1, X2, 200, "Languages", ", ".join(n for n, _, _ in pct[:4]))
head(X1, X2, 236, "Contact")
lead(X1, X2, 259, "GitHub", f"github.com/{U}")
head(X1, X2, 295, "GitHub Stats")
lead(X1, mid, 318, "Repos", f"{nrepos}", ORG)
lead(mid + 18, X2, 318, "Stars", f"{stars}", ORG)
lead(X1, mid, 342, "Commits", f"{commits:,}", ORG)
lead(mid + 18, X2, 342, "Followers", f"{followers}", ORG)
for yy in (318, 342):
    a_(f'<text x="{mid+9}" y="{yy}" font-size="15" fill="{DIM}" text-anchor="middle">|</text>')
end()

# tech
sec(.45)
panel(316, 433, 560, 102)
label(342, 467, "[ TECHNOLOGIES &amp; SKILLS ]")
tiles = [("github", "#241f45", "#ffffff"), ("linux", "#241f45", "#FCC624"), ("gnubash", "#241f45", "#e6e6e6"),
         ("postgresql", "#241f45", "#5B9BD5"), ("rust", "#E43716", "#ffffff"), ("python", "#241f45", "url(#py)"), ("c", "#3D4DA5", "#ffffff")]
for i, (s, bg, fg) in enumerate(tiles):
    x = 342 + i * 50
    a_(f'<g class="fl" style="animation-delay:-{i*.5}s"><rect x="{x}" y="481" width="42" height="42" rx="10" fill="{bg}"/>'
       f'<g transform="translate({x+7} 488) scale(1.1667)"><path fill="{fg}" d="{icon(s)}"/></g></g>')
end()

# languages
sec(.6)
panel(38, 544, 838, 170)
label(64, 579, "[ TOP LANGUAGES ]")
bx, bw, tp, x = 64, 787, sum(p for _, p, _ in pct), 64
for i, (n, p, c) in enumerate(pct):
    w = bw * p / tp
    a_(f'<rect x="{x:.1f}" y="598" width="{w:.1f}" height="8" fill="{c}" rx="{4 if i in (0, len(pct)-1) else 0}"/>')
    x += w
a_('<rect class="cv" style="animation-delay:.9s" x="62" y="596" width="791" height="12" fill="#181630"/>')
for i, (n, p, c) in enumerate(pct):
    cx, cy = 64 + (i % 2) * 394, 630 + (i // 2) * 26
    a_(f'<circle cx="{cx+5}" cy="{cy-4}" r="4.5" fill="{c}"/><text x="{cx+17}" y="{cy}" font-size="13" fill="{TXT}">{n} <tspan fill="{DIM}">{p}%</tspan></text>')
end()

# featured
sec(.75)
panel(38, 723, 838, 124)
label(64, 753, "[ FEATURED REPOSITORIES ]")
a_(f'<rect x="64" y="770" width="787" height="62" fill="#201d3d"/><rect x="64" y="770" width="3" height="62" fill="{RED}"/>')
desc = repo["description"] or ""
desc = (desc if len(desc) <= 92 else desc[:91].rstrip() + "…").replace("&", "&amp;")
a_(f'<text x="78" y="792" font-size="13" fill="{RED}">{repo["name"]}</text>')
a_(f'<text x="78" y="811" font-size="11" fill="#9a96c4">{desc}</text>')
a_(f'<text x="78" y="826" font-size="11" fill="{RED}">{repo["language"]} • {repo["stargazers_count"]}</text>')
end()

# activity tracker
sec(.9)
AY = 856
panel(38, AY, 838, 244)
label(64, AY + 35, "[ ACTIVITY ]")
a_(f'<text x="851" y="{AY+35}" font-size="12" fill="{DIM}" text-anchor="end">{cal["totalContributions"]:,} contributions in the last year</text>')
GX, GY, ST, SZ = 92, AY + 74, 14.3, 11.5
prev, marks = None, []
for i, w in enumerate(weeks):
    mo = datetime.date.fromisoformat(w["contributionDays"][0]["date"]).month
    if mo != prev:
        marks.append((i, mo))
    prev = mo
if len(marks) > 1 and marks[1][0] - marks[0][0] < 3:
    marks.pop(0)
for i, mo in marks:
    a_(f'<text x="{GX+i*ST:.1f}" y="{GY-8}" font-size="10" fill="{DIM}">{datetime.date(2000, mo, 1):%b}</text>')
for r, t in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    a_(f'<text x="64" y="{GY+r*ST+9:.1f}" font-size="10" fill="{DIM}">{t}</text>')
last = days[-1]["date"]
for i, w in enumerate(weeks):
    for x in w["contributionDays"]:
        dt = datetime.date.fromisoformat(x["date"])
        r = (dt.weekday() + 1) % 7
        cls = "c td" if x["date"] == last else "c"
        # pop wave runs left to right across weeks, 1.1s lead-in after the panel fades in
        a_(f'<rect class="{cls}" style="animation-delay:{1.1 + i*.025:.3f}s" x="{GX+i*ST:.1f}" y="{GY+r*ST:.1f}" width="{SZ}" height="{SZ}" rx="2.5" fill="{HEAT[LVL[x["contributionLevel"]]]}"/>')
# legend
lx = 851 - 4 * 6.6 - 6 - 5 * ST + 2.8
a_(f'<text x="{lx-6:.1f}" y="{GY+7*ST+13:.1f}" font-size="10" fill="{DIM}" text-anchor="end">Less</text>')
for i, c in enumerate(HEAT):
    a_(f'<rect x="{lx+i*ST:.1f}" y="{GY+7*ST+4:.1f}" width="{SZ}" height="{SZ}" rx="2.5" fill="{c}"/>')
a_(f'<text x="851" y="{GY+7*ST+13:.1f}" font-size="10" fill="{DIM}" text-anchor="end">More</text>')
sy = GY + 7 * ST + 48
for i, (k, v) in enumerate((("CONTRIBUTIONS", f'{cal["totalContributions"]:,}'), ("CURRENT STREAK", pl(cur, "day")),
                            ("LONGEST STREAK", pl(longest, "day")), ("BEST DAY", best_s))):
    a_(f'<text x="{64+i*200}" y="{sy-17}" font-size="10" fill="{DIM}" letter-spacing="2">{k}</text>')
    a_(f'<text x="{64+i*200}" y="{sy+4}" font-size="19" fill="{ORG}">{v}</text>')
end()

# footer line with sweeping glint
a_(f'<rect x="38" y="1109" width="838" height="4" fill="{RED}"/>')
a_('<g class="glw" clip-path="url(#rl)"><rect class="gl" x="38" y="1109" width="140" height="4" fill="url(#gl)"/></g>')
a_("</svg>")

(D / "profile.svg").write_text("\n".join(o))
print(json.dumps({"uptime": uptime, "repos": nrepos, "stars": stars, "commits": commits, "langs": pct,
                  "total": cal["totalContributions"], "cur": cur, "longest": longest, "best": best_s}))
