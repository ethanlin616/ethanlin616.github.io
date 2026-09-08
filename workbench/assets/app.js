/* 学习工作台 · 通用脚本：进场动效 + 数字滚动 */
(function(){
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduce) return;
  var body = document.body;
  body.classList.add('js-anim');

  var sel = '.sec-title, .card, .feat, .formula, .calc, .quiz, .wb-card, .qr-card, .quick-bar, .hero .badge, .hero h1, .hero .sub, .hero .tag';
  var els = document.querySelectorAll(sel);
  els.forEach(function(e){ e.classList.add('reveal'); });

  function countUp(b){
    var txt = b.textContent.trim();
    var m = txt.match(/^([\d.]+)/);
    if(!m) return;
    var end = parseFloat(m[1]);
    var suffix = txt.slice(m[0].length);
    var t0 = null, dur = 1000;
    function step(ts){
      if(t0 === null) t0 = ts;
      var p = Math.min(1, (ts - t0) / dur);
      var eased = 1 - Math.pow(1 - p, 3);
      b.textContent = Math.round(end * eased) + suffix;
      if(p < 1) requestAnimationFrame(step);
      else b.textContent = (end % 1 === 0 ? end : end.toFixed(1)) + suffix;
    }
    requestAnimationFrame(step);
  }

  function onShow(el){
    el.classList.add('is-visible');
    if(el.classList.contains('quick-bar')){
      el.querySelectorAll('b').forEach(countUp);
    }
  }

  if('IntersectionObserver' in window){
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(en){
        if(en.isIntersecting){ onShow(en.target); io.unobserve(en.target); }
      });
    }, {threshold:0.12, rootMargin:'0px 0px -40px 0px'});
    els.forEach(function(e){ io.observe(e); });
  } else {
    els.forEach(onShow);
  }
})();
