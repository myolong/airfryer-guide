(function () {
  var q = document.getElementById('q');
  var rows = Array.prototype.slice.call(document.querySelectorAll('#food-table tbody tr'));
  var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
  var empty = document.getElementById('empty');
  var cat = '';

  function norm(s) { return s.replace(/\s+/g, '').toLowerCase(); }

  function apply() {
    var term = norm(q.value);
    var shown = 0;
    rows.forEach(function (tr) {
      var ok = (!cat || tr.dataset.cat === cat) && (!term || norm(tr.dataset.name).indexOf(term) !== -1);
      tr.hidden = !ok;
      if (ok) shown++;
    });
    empty.hidden = shown !== 0;
  }

  q.addEventListener('input', apply);
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      cat = c.dataset.cat;
      chips.forEach(function (x) { x.classList.toggle('is-on', x === c); });
      apply();
    });
  });
})();
