(function () {
  // 이달의 살림: 빌드한 달과 지금 달이 다르면 지금 달로 바꿔 보여 준다.
  var data = JSON.parse(document.getElementById('month-data').textContent);
  var box = document.getElementById('month');
  var m = String(new Date().getMonth() + 1);
  function esc(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
  if (box && box.dataset.month !== m) {
    document.getElementById('m-num').textContent = m;
    document.getElementById('m-crops').innerHTML = data.crops[m].map(function (c) { return '<li>' + esc(c) + '</li>'; }).join('');
    document.getElementById('m-todo').innerHTML = data.todo[m].map(function (t) {
      return '<li><b>' + esc(t[0]) + '</b>' + (t[2] ? '<a href="' + esc(t[2]) + '">' + esc(t[1]) + '</a>' : '<span>' + esc(t[1]) + '</span>') + '</li>';
    }).join('');
    var more = document.getElementById('m-more');
    more.href = data.seasonal + '?q=' + m + '월';
    more.textContent = m + '월 제철 전체 보기';
    box.dataset.month = m;
  }

  // 전체 메뉴 통합 검색
  var q = document.getElementById('gq');
  var list = document.getElementById('gresults');
  var empty = document.getElementById('gempty');
  var index = null, loading = false;
  function norm(s) { return s.replace(/\s+/g, '').toLowerCase(); }
  function load() {
    if (index || loading) return;
    loading = true;
    fetch(q.dataset.index).then(function (r) { return r.json(); }).then(function (rows) {
      index = rows.map(function (r) { r.t = [r.n].concat(r.k).map(norm); return r; });
      render();
    }).catch(function () { loading = false; });
  }
  function render() {
    var term = norm(q.value);
    if (!term || !index) { list.hidden = true; empty.hidden = true; return; }
    var month = /^\d{1,2}월$/.test(term);
    var hits = index.filter(function (r) {
      return month ? r.t.indexOf(term) !== -1 : r.t.some(function (t) { return t.indexOf(term) !== -1; });
    });
    hits.sort(function (a, b) { return (norm(a.n).indexOf(term) === 0 ? 0 : 1) - (norm(b.n).indexOf(term) === 0 ? 0 : 1); });
    list.innerHTML = hits.slice(0, 8).map(function (r) {
      return '<li><a href="' + esc(r.u) + '"><strong>' + esc(r.n) + '</strong><span class="where">' + esc(r.s) +
        '</span><span class="what">' + esc(r.d) + '</span></a></li>';
    }).join('');
    list.hidden = hits.length === 0;
    empty.hidden = hits.length !== 0;
  }
  q.addEventListener('focus', load);
  q.addEventListener('input', function () { load(); render(); });
})();
