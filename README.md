# 살림사전 (salimdict.com)

신혼·자취 초보를 위한 살림 꿀팁 정적 사이트.

## 구조

- `src/sections/<메뉴>/section.json` — 메뉴 제목·설명·표 컬럼·분류
- `src/sections/<메뉴>/items.json` — 검색표 데이터 (항목 추가는 여기에 한 줄)
- `src/sections/<메뉴>/guides/*.html` — 가이드 글 (맨 위 `---` 사이에 title·description·order)
- `src/assets/` — CSS, JS, 아이콘
- `build.py` — `python3 build.py` 실행 시 `docs/` 에 사이트 생성
- `docs/` — 배포되는 결과물 (직접 수정하지 말고 빌드로 갱신)

## 배포

GitHub 저장소 Settings → Pages → Branch: `main`, 폴더: `/docs`.

도메인·애드센스·서치콘솔 인증값은 `build.py` 상단 설정에 넣고 다시 빌드한다.
