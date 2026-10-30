#!/usr/bin/env python3
"""src/ 의 데이터와 글을 읽어 docs/ 에 정적 사이트를 만든다.

사용법: python3 build.py
GitHub Pages 설정에서 main 브랜치의 /docs 폴더를 배포 대상으로 지정한다.
"""
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

# ── 사이트 설정 (도메인·애드센스가 정해지면 여기만 바꾸고 다시 빌드) ──────────
SITE_URL = "https://myolong.github.io/airfryer-guide"  # 개인 도메인 연결 후 "https://도메인" 으로 변경
CUSTOM_DOMAIN = ""  # 예: "airfryerguide.kr" → docs/CNAME 생성
SITE_NAME = "에어프라이어 시간표"
CONTACT_EMAIL = ""  # 문의용 이메일 (본업과 분리된 주소)
ADSENSE_CLIENT = ""  # 예: "ca-pub-1234567890123456" → 광고 스크립트·ads.txt 생성
GOOGLE_VERIFICATION = ""  # 구글 서치 콘솔 HTML 태그의 content 값
NAVER_VERIFICATION = ""  # 네이버 서치어드바이저 HTML 태그의 content 값
UPDATED = date.today().isoformat()
# ───────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "docs"
BASE_PATH = re.sub(r"^https?://[^/]+", "", SITE_URL).rstrip("/")

CATEGORIES = ["냉동식품", "데우기", "고기", "생선·해산물", "채소·곡물", "계란·빵"]


def url(path):
    """사이트 내부 경로 (GitHub Pages 하위 경로 대응)."""
    return BASE_PATH + path


def esc(text):
    return html.escape(text, quote=True)


def read_guides():
    guides = []
    for f in sorted((SRC / "guides").glob("*.html")):
        raw = f.read_text(encoding="utf-8")
        _, front, body = raw.split("---", 2)
        meta = dict(
            line.split(":", 1) for line in front.strip().splitlines() if ":" in line
        )
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        guides.append({
            "slug": f.stem,
            "title": meta["title"],
            "description": meta["description"],
            "order": int(meta.get("order", 99)),
            "body": body.strip().replace('href="/', f'href="{BASE_PATH}/'),
        })
    return sorted(guides, key=lambda g: g["order"])


def layout(*, title, description, path, body, json_ld=None, page_title=None):
    canonical = SITE_URL + path
    full_title = page_title or f"{title} | {SITE_NAME}"
    head_extra = []
    if GOOGLE_VERIFICATION:
        head_extra.append(f'<meta name="google-site-verification" content="{esc(GOOGLE_VERIFICATION)}">')
    if NAVER_VERIFICATION:
        head_extra.append(f'<meta name="naver-site-verification" content="{esc(NAVER_VERIFICATION)}">')
    if ADSENSE_CLIENT:
        head_extra.append(
            f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={esc(ADSENSE_CLIENT)}" crossorigin="anonymous"></script>'
        )
    if json_ld:
        head_extra.append(
            '<script type="application/ld+json">' + json.dumps(json_ld, ensure_ascii=False) + "</script>"
        )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(SITE_NAME)}">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#e8590c">
<link rel="icon" href="{url('/assets/favicon.svg')}" type="image/svg+xml">
<link rel="stylesheet" href="{url('/assets/style.css')}">
{chr(10).join(head_extra)}
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="{url('/')}"><span class="logo-mark" aria-hidden="true">⏲</span>{esc(SITE_NAME)}</a>
    <nav>
      <a href="{url('/')}">시간표</a>
      <a href="{url('/guides/')}">조리 가이드</a>
      <a href="{url('/about/')}">소개</a>
    </nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p>표의 온도·시간은 일반적인 바스켓형 에어프라이어 기준의 참고값입니다. 기종·용량·음식 양에 따라 달라질 수 있으니 처음에는 중간에 확인하며 조리하세요.</p>
    <p class="footer-links">
      <a href="{url('/about/')}">사이트 소개</a> ·
      <a href="{url('/privacy/')}">개인정보처리방침</a> ·
      <a href="{url('/contact/')}">문의</a>
    </p>
    <p>© {date.today().year} {esc(SITE_NAME)}</p>
  </div>
</footer>
</body>
</html>
"""


def write(path, content):
    target = OUT / path.lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def food_rows(foods, guides_by_slug):
    rows = []
    for f in foods:
        name = esc(f["name"])
        if f.get("guide") in guides_by_slug:
            name = f'<a href="{url("/guides/" + f["guide"] + "/")}">{name}</a>'
        rows.append(
            f'<tr data-cat="{esc(f["cat"])}" data-name="{esc(f["name"])}">'
            f'<td class="food">{name}<span class="cat-tag">{esc(f["cat"])}</span></td>'
            f'<td class="num">{esc(f["temp"])}</td>'
            f'<td class="num">{esc(f["time"])}</td>'
            f'<td class="tip">{esc(f["tip"])}</td></tr>'
        )
    return "\n".join(rows)


def guide_cards(guides):
    return "\n".join(
        f'<li><a href="{url("/guides/" + g["slug"] + "/")}"><strong>{esc(g["title"])}</strong>'
        f'<span>{esc(g["description"])}</span></a></li>'
        for g in guides
    )


def build_index(foods, guides):
    by_slug = {g["slug"]: g for g in guides}
    chips = "".join(
        f'<button type="button" class="chip" data-cat="{esc(c)}">{esc(c)}</button>' for c in CATEGORIES
    )
    body = f"""
<section class="hero">
  <h1>에어프라이어 온도·시간표</h1>
  <p>감자튀김, 삼겹살, 고구마, 냉동만두… 매번 검색하지 말고 여기서 한 번에 찾으세요. 음식 이름을 입력하면 온도와 시간이 바로 나옵니다.</p>
  <label class="search">
    <span class="sr-only">음식 검색</span>
    <input id="q" type="search" placeholder="예: 고구마, 만두, 치킨" autocomplete="off">
  </label>
  <div class="chips" role="group" aria-label="분류">
    <button type="button" class="chip is-on" data-cat="">전체</button>{chips}
  </div>
</section>

<section aria-label="음식별 온도·시간">
  <div class="table-wrap">
    <table class="food-table" id="food-table">
      <thead><tr><th>음식</th><th>온도</th><th>시간</th><th>요령</th></tr></thead>
      <tbody>
{food_rows(foods, by_slug)}
      </tbody>
    </table>
  </div>
  <p class="empty" id="empty" hidden>찾는 음식이 없어요. 비슷한 음식의 시간을 참고하고, 중간에 한 번 열어 확인해 보세요.</p>
  <p class="note">밑줄 친 음식은 자세한 조리 가이드가 있습니다. 예열을 하지 않았다면 시간에 1~2분을 더하세요.</p>
</section>

<section class="guides-block">
  <h2>조리 가이드</h2>
  <ul class="cards">
{guide_cards(guides)}
  </ul>
</section>
<script src="{url('/assets/app.js')}" defer></script>
"""
    json_ld = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": SITE_URL + "/",
        "inLanguage": "ko",
    }
    write("/", layout(
        title="에어프라이어 온도·시간표",
        page_title="에어프라이어 온도·시간표 - 음식별 조리 시간 한눈에 | " + SITE_NAME,
        description="에어프라이어 음식별 온도와 조리 시간을 한 번에 찾아보세요. 냉동식품, 고기, 생선, 고구마, 계란까지 37가지 음식의 온도·시간·요령을 정리했습니다.",
        path="/", body=body, json_ld=json_ld,
    ))


def build_guides(guides):
    write("/guides/", layout(
        title="에어프라이어 조리 가이드",
        description="에어프라이어 기본 사용법부터 삼겹살, 통닭, 군고구마, 구운 계란, 청소법까지 음식별 자세한 조리 가이드 모음입니다.",
        path="/guides/",
        body=f'<h1>에어프라이어 조리 가이드</h1>\n<p class="lead">표만으로 부족할 때, 음식별로 실패하지 않는 순서와 요령을 자세히 정리했습니다.</p>\n<ul class="cards">\n{guide_cards(guides)}\n</ul>',
    ))
    for i, g in enumerate(guides):
        path = f"/guides/{g['slug']}/"
        related = [guides[(i + k) % len(guides)] for k in (1, 2, 3)]
        body = f"""
<nav class="crumbs" aria-label="위치"><a href="{url('/')}">홈</a> › <a href="{url('/guides/')}">조리 가이드</a></nav>
<article class="article">
  <h1>{esc(g['title'])}</h1>
  <p class="meta">최종 업데이트 {UPDATED}</p>
  {g['body']}
  <p class="disclaimer">이 글의 온도·시간은 일반적인 바스켓형 에어프라이어 기준입니다. 기종과 음식 양에 따라 다를 수 있으니 처음에는 중간에 확인하며 조리하세요.</p>
</article>
<aside class="related">
  <h2>함께 보면 좋은 가이드</h2>
  <ul class="cards">
{guide_cards(related)}
  </ul>
  <p><a class="btn" href="{url('/')}">전체 온도·시간표 보기</a></p>
</aside>
"""
        json_ld = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Article",
                    "headline": g["title"],
                    "description": g["description"],
                    "dateModified": UPDATED,
                    "inLanguage": "ko",
                    "mainEntityOfPage": SITE_URL + path,
                    "author": {"@type": "Organization", "name": SITE_NAME},
                },
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE_URL + "/"},
                        {"@type": "ListItem", "position": 2, "name": "조리 가이드", "item": SITE_URL + "/guides/"},
                        {"@type": "ListItem", "position": 3, "name": g["title"], "item": SITE_URL + path},
                    ],
                },
            ],
        }
        write(path, layout(title=g["title"], description=g["description"], path=path, body=body, json_ld=json_ld))


def build_static_pages():
    contact_line = (
        f'<p>이메일: <a href="mailto:{esc(CONTACT_EMAIL)}">{esc(CONTACT_EMAIL)}</a></p>'
        if CONTACT_EMAIL else "<p>이메일: 준비 중입니다.</p>"
    )
    pages = {
        "/about/": ("사이트 소개", "에어프라이어 시간표는 음식별 에어프라이어 온도와 조리 시간을 한곳에 모아, 매번 검색하는 수고를 덜기 위해 만든 사이트입니다.", f"""
<h1>사이트 소개</h1>
<p>에어프라이어로 요리할 때마다 "고구마는 몇 도에 몇 분이었지?" 하고 검색하던 불편에서 시작한 사이트입니다. 흩어져 있는 정보를 직접 정리해, 음식 이름만 입력하면 온도와 시간을 바로 확인할 수 있도록 만들었습니다.</p>
<h2>이런 정보를 제공합니다</h2>
<ul>
  <li>냉동식품, 고기, 생선, 채소, 계란·빵 등 음식별 에어프라이어 온도·시간표</li>
  <li>실패하지 않는 순서와 요령을 담은 음식별 조리 가이드</li>
  <li>예열, 종이호일 사용, 청소처럼 에어프라이어를 쓰며 자주 생기는 궁금증 정리</li>
</ul>
<h2>정보 이용 시 참고사항</h2>
<p>표와 가이드의 온도·시간은 일반적인 바스켓형 에어프라이어를 기준으로 한 참고값입니다. 제품마다 히터 출력과 용량이 달라 같은 설정이라도 결과가 다를 수 있습니다. 처음 조리하는 음식은 중간에 한 번 열어 상태를 확인하시고, 고기·생선은 속까지 충분히 익었는지 꼭 확인해 주세요. 제조사 설명서와 제품 포장의 조리법이 있다면 그 내용을 우선해 주세요.</p>
<h2>오류 제보</h2>
<p>잘못된 정보나 추가했으면 하는 음식이 있다면 <a href="{url('/contact/')}">문의 페이지</a>로 알려 주세요. 확인 후 반영하겠습니다.</p>
"""),
        "/privacy/": ("개인정보처리방침", "에어프라이어 시간표의 개인정보처리방침입니다. 수집하는 정보, 쿠키와 광고, 이용자의 권리를 안내합니다.", f"""
<h1>개인정보처리방침</h1>
<p>{esc(SITE_NAME)}(이하 '사이트')는 이용자의 개인정보를 중요하게 생각하며, 관련 법령을 준수합니다. 이 방침은 {UPDATED}부터 적용됩니다.</p>
<h2>1. 수집하는 개인정보</h2>
<p>사이트는 회원가입 기능이 없으며, 이용자가 직접 입력하는 개인정보를 수집하지 않습니다. 이메일로 문의하시는 경우 답변을 위해 보내 주신 이메일 주소와 문의 내용만을 이용하며, 답변 완료 후 지체 없이 파기합니다.</p>
<h2>2. 자동으로 수집되는 정보</h2>
<p>사이트 이용 과정에서 접속 기록, 브라우저 종류, 방문 페이지 등의 정보가 웹 서버 또는 분석·광고 도구에 의해 자동으로 생성·수집될 수 있습니다. 이 정보는 개인을 식별하지 않는 통계 목적으로만 이용됩니다.</p>
<h2>3. 쿠키와 광고</h2>
<p>사이트는 Google 애드센스를 포함한 제3자 광고 서비스를 이용할 수 있습니다. Google을 비롯한 제3자 공급업체는 쿠키를 사용하여 이용자의 이 사이트 또는 다른 웹사이트 방문 기록을 바탕으로 광고를 게재합니다. Google은 광고 쿠키를 사용하여 이용자가 이 사이트나 다른 사이트를 방문한 기록에 따라 맞춤 광고를 제공할 수 있습니다.</p>
<p>이용자는 <a href="https://adssettings.google.com" rel="nofollow noopener" target="_blank">Google 광고 설정</a>에서 맞춤 광고를 해제할 수 있으며, <a href="https://www.aboutads.info" rel="nofollow noopener" target="_blank">www.aboutads.info</a>에서 제3자 공급업체의 맞춤 광고용 쿠키 사용을 해제할 수 있습니다. 또한 브라우저 설정에서 쿠키 저장을 거부할 수 있으나, 이 경우 일부 기능 이용에 제한이 있을 수 있습니다.</p>
<h2>4. 개인정보의 제3자 제공</h2>
<p>사이트는 이용자의 개인정보를 제3자에게 제공하지 않습니다. 다만 법령에 따라 요구되는 경우는 예외로 합니다.</p>
<h2>5. 이용자의 권리</h2>
<p>이용자는 언제든지 문의 시 제공한 개인정보의 열람, 정정, 삭제를 요청할 수 있으며, <a href="{url('/contact/')}">문의 페이지</a>의 연락처로 요청하시면 지체 없이 처리합니다.</p>
<h2>6. 방침의 변경</h2>
<p>이 방침이 변경되는 경우 사이트에 게시하여 알립니다.</p>
"""),
        "/contact/": ("문의", "에어프라이어 시간표에 오류 제보, 음식 추가 요청, 기타 문의를 보내는 방법을 안내합니다.", f"""
<h1>문의</h1>
<p>정보 오류 제보, 추가했으면 하는 음식, 기타 문의는 아래 이메일로 보내 주세요. 보통 2~3일 안에 답변드립니다.</p>
{contact_line}
<p>문의 시 받은 이메일 주소는 답변에만 사용하며, 자세한 내용은 <a href="{url('/privacy/')}">개인정보처리방침</a>을 참고해 주세요.</p>
"""),
    }
    for path, (title, desc, body) in pages.items():
        write(path, layout(title=title, description=desc, path=path, body=body))

    write("/404.html", layout(
        title="페이지를 찾을 수 없습니다", description="요청하신 페이지를 찾을 수 없습니다.", path="/404.html",
        body=f'<h1>페이지를 찾을 수 없습니다</h1><p>주소가 바뀌었거나 삭제된 페이지입니다.</p><p><a class="btn" href="{url("/")}">온도·시간표로 가기</a></p>',
    ).replace('<link rel="canonical"', '<meta name="robots" content="noindex">\n<link rel="canonical"'))


def build_meta_files(guides):
    paths = ["/", "/guides/"] + [f"/guides/{g['slug']}/" for g in guides] + ["/about/", "/privacy/", "/contact/"]
    entries = "\n".join(
        f"  <url><loc>{SITE_URL}{p}</loc><lastmod>{UPDATED}</lastmod></url>" for p in paths
    )
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}\n</urlset>\n',
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    if CUSTOM_DOMAIN:
        (OUT / "CNAME").write_text(CUSTOM_DOMAIN + "\n", encoding="utf-8")
    if ADSENSE_CLIENT:
        pub = ADSENSE_CLIENT.replace("ca-", "")
        (OUT / "ads.txt").write_text(f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(SRC / "assets", OUT / "assets")
    foods = json.loads((SRC / "foods.json").read_text(encoding="utf-8"))
    guides = read_guides()
    build_index(foods, guides)
    build_guides(guides)
    build_static_pages()
    build_meta_files(guides)
    print(f"built {len(guides)} guides, {len(foods)} foods → {OUT}")


if __name__ == "__main__":
    main()
