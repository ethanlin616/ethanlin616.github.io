/* ============ 四升五暑假学习工作台 · 交互逻辑（30 天版） ============ */
(function(){
  'use strict';
  var $ = function(id){ return document.getElementById(id); };

  /* ---------- 默认设置（可被“设置”面板覆盖） ---------- */
  function todayStr(){ var d=new Date(); var m=String(d.getMonth()+1).padStart(2,'0'), day=String(d.getDate()).padStart(2,'0'); return d.getFullYear()+'-'+m+'-'+day; }
  var DEF_SET = {
    chinese:true, drill:true, daily:true, english:true, // 四个模块开关
    drillNum:10, wordNum:10, duration:30,               // 参数
    start:todayStr(), total:30                          // 起始日（默认当天）/ 总天数
  };
  function getSet(){ try{ return Object.assign({}, DEF_SET, JSON.parse(localStorage.getItem('wb45-set'))||{}); }catch(e){ return Object.assign({}, DEF_SET); } }
  function saveSet(s){ try{ localStorage.setItem('wb45-set', JSON.stringify(s)); }catch(e){} }
  var SET = getSet();

  /* ---------- 进度状态 ---------- */
  function getUnlock(){ var n=parseInt(localStorage.getItem('wb45-unlocked')||'1',10); return isNaN(n)||n<1?1:n; }
  function saveUnlock(n){ try{ localStorage.setItem('wb45-unlocked', String(n)); }catch(e){} }
  var unlockMax = getUnlock();                 // 已解锁到的最高天
  var curDay = unlockMax;                       // 当前操作天（回看时改变）

  /* ---------- 存储 ---------- */
  function user(){ try{ return JSON.parse(localStorage.getItem('wb45-user'))||{}; }catch(e){ return {}; } }
  function saveUser(u){ try{ localStorage.setItem('wb45-user', JSON.stringify(u)); }catch(e){} }
  function ensureUser(){ var u=user(); if(u.points==null) u.points=0; if(!u.streak) u.streak=0; if(!u.badges) u.badges=[]; saveUser(u); return u; }
  function dayRec(N){ try{ return JSON.parse(localStorage.getItem('wb45-day-'+N))||{}; }catch(e){ return {}; } }
  function saveDay(N,d){ try{ localStorage.setItem('wb45-day-'+N, JSON.stringify(d)); }catch(e){} }
  function reward(){ try{ return JSON.parse(localStorage.getItem('wb45-reward'))||{coupons:[],badges:[]}; }catch(e){ return {coupons:[],badges:[]}; } }
  function saveReward(r){ try{ localStorage.setItem('wb45-reward', JSON.stringify(r)); }catch(e){} }

  /* ---------- 按天取数 ---------- */
  function clamp(v,lo,hi){ return v<lo?lo:(v>hi?hi:v); }
  function poemOf(N){ return POEMS[clamp(N-1,0,POEMS.length-1)]; }
  function dailyOf(N){ return DAILY[clamp(N-1,0,DAILY.length-1)]; }
  function wordsOf(N, num){
    var arr=WORDS.slice();
    for(var i=arr.length-1;i>0;i--){ var j=(i*7+N*13+5)%(i+1); var t=arr[i]; arr[i]=arr[j]; arr[j]=t; }
    return arr.slice(0, clamp(num,1,arr.length));
  }
  function dateLabel(N){
    var d=new Date(SET.start+'T00:00:00'); d.setDate(d.getDate()+(N-1));
    return (d.getMonth()+1)+'月'+d.getDate()+'日';
  }

  /* ---------- 反馈 ---------- */
  function toast(msg){ var t=$('toast'); t.textContent=msg; t.classList.add('show'); setTimeout(function(){ t.classList.remove('show'); }, 1500); }
  function flyStar(){ var s=document.createElement('div'); s.className='fly'; s.textContent='⭐'; s.style.left='50%'; s.style.top='70%'; document.body.appendChild(s); setTimeout(function(){ s.remove(); }, 1000); }
  function addPoints(n){ var u=ensureUser(); u.points+=n; saveUser(u); renderHome(); renderReward(); }

  /* ---------- 徽章 ---------- */
  var BADGES = [
    {n:'初出茅庐', ic:'🌟'},{n:'坚持小达人', ic:'🔥'},{n:'自律之星', ic:'👑'},
    {n:'口算小能手', ic:'🧮'},{n:'单词小达人', ic:'🔤'}
  ];
  function giveBadge(name){ var r=reward(); if(r.badges.indexOf(name)<0){ r.badges.push(name); saveReward(r); toast('🏅 获得徽章：'+name); renderReward(); } }

  /* ---------- 打卡 + 解锁（弱判定：点完成即算） ---------- */
  var SUB_KEY = {chinese:'chinese', drill:'drill', daily:'daily', english:'english'};
  var SUB_POINT = {chinese:10, drill:10, daily:10, english:10};
  function activeSubs(){ var a=[]; if(SET.chinese)a.push('chinese'); if(SET.drill)a.push('drill'); if(SET.daily)a.push('daily'); if(SET.english)a.push('english'); return a; }
  function completeSub(sub){
    var d=dayRec(curDay);
    if(d[sub]){ toast('这一天这一项已经打卡啦'); return; }
    d[sub]=true; saveDay(curDay, d);
    addPoints(SUB_POINT[sub]);
    toast('+'+SUB_POINT[sub]+' 积分 🎉'); flyStar();
    if(sub==='drill') giveBadge('口算小能手');
    if(sub==='english') giveBadge('单词小达人');
    // 当天所有开启模块都完成 → 解锁下一天
    var subs=activeSubs(), all=true;
    subs.forEach(function(s){ if(!d[s]) all=false; });
    if(all && curDay===unlockMax){
      unlockMax=Math.min(curDay+1, SET.total);
      saveUnlock(unlockMax);
      if(unlockMax>curDay) toast('🎉 解锁第 '+unlockMax+' 天！');
    }
    // 连续天数（基于“当天整组完成”）
    if(all) fullDayDone();
    renderAll();
    // 刷新数学两块完成按钮状态（闭包内渲染不会被 renderAll 覆盖）
    var dn=dayRec(curDay);
    if($('drillDone')){ if(dn.drill){ $('drillDone').textContent='✓ 已完成（已打卡）'; $('drillDone').classList.add('done'); } else { $('drillDone').textContent='✓ 完成口算打卡'; $('drillDone').classList.remove('done'); } }
    if($('dailyDone')){ if(dn.daily){ $('dailyDone').textContent='✓ 已完成（已打卡）'; $('dailyDone').classList.add('done'); } else { $('dailyDone').textContent='✓ 完成每日一题'; $('dailyDone').classList.remove('done'); } }
  }
  function fullDayDone(){
    var u=ensureUser();
    var key='wb45-seq-'+curDay;
    if(localStorage.getItem(key)) return;
    localStorage.setItem(key,'1');
    if(u.lastDay===(curDay-1)) u.streak+=1; else u.streak=1;
    u.lastDay=curDay;
    if(u.streak>=3 && !u.bonus3){ u.bonus3=true; addPoints(20); toast('连续 3 天 🔥 +20'); giveBadge('坚持小达人'); }
    if(u.streak>=7 && !u.bonus7){ u.bonus7=true; addPoints(50); toast('连续 7 天 👑 +50'); giveBadge('自律之星'); }
    if(u.badges.indexOf('初出茅庐')<0) giveBadge('初出茅庐');
    saveUser(u); renderHome();
  }

  /* ---------- 首页渲染 ---------- */
  function setBar(id, done){
    var bar=$(id); bar.querySelector('.fill').style.width = done?'100%':'0%';
    bar.querySelector('.top b').textContent = done?'100%':'0%';
    if(done) bar.classList.add('done'); else bar.classList.remove('done');
  }
  function renderHome(){
    var u=ensureUser(), d=dayRec(curDay), subs=activeSubs();
    var doneN = subs.filter(function(s){ return d[s]; }).length;
    $('stDay').textContent = '第 '+curDay+' / '+SET.total+' 天';
    $('stPoint').textContent = u.points;
    $('stStreak').textContent = u.streak;
    var p = subs.length? Math.round(doneN/subs.length*100):0;
    $('ring').style.setProperty('--p', p);
    $('ringP').textContent = p+'%';
    setBar('bar-chinese', SET.chinese && !!d.chinese);
    setBar('bar-math', (SET.drill&&!!d.drill) || (SET.daily&&!!d.daily));
    setBar('bar-english', SET.english && !!d.english);
    tag('go-chinese', SET.chinese && !!d.chinese);
    tag('go-math', (SET.drill&&!!d.drill) || (SET.daily&&!!d.daily));
    tag('go-english', SET.english && !!d.english);
    $('heroDate').textContent = '今天是 '+dateLabel(curDay)+' · 第 '+curDay+' 天';
  }
  function tag(id, done){ var el=$(id); el.textContent=done?'已完成':'未完成'; el.className='st '+(done?'ok':'no'); }

  /* ---------- Tab 切换 ---------- */
  $('tabs').querySelectorAll('button').forEach(function(b){
    b.addEventListener('click', function(){
      $('tabs').querySelectorAll('button').forEach(function(x){x.classList.remove('active');});
      b.classList.add('active');
      document.querySelectorAll('.panel').forEach(function(p){p.classList.remove('active');});
      $('panel-'+b.dataset.tab).classList.add('active');
      if(b.dataset.tab==='calendar') renderCalendar();
      if(b.dataset.tab==='settings') renderSettings();
      window.scrollTo(0,0);
    });
  });
  document.querySelectorAll('.taskcard').forEach(function(c){
    c.addEventListener('click', function(){ var t=c.dataset.go;
      $('tabs').querySelectorAll('button').forEach(function(x){x.classList.remove('active');});
      $('tabs').querySelector('button[data-tab="'+t+'"]').classList.add('active');
      document.querySelectorAll('.panel').forEach(function(p){p.classList.remove('active');});
      $('panel-'+t).classList.add('active'); window.scrollTo(0,0);
    });
  });

  function renderAll(){ renderHome(); renderChinese(); renderEnglish(); renderCalendarLight(); }

  /* ---------- 语文：古诗 ---------- */
  function renderChinese(){
    var p=poemOf(curDay), d=dayRec(curDay);
    $('poem').innerHTML = '<div class="t">'+p.t+'</div><div class="a">'+p.a+' · '+dateLabel(curDay)+'</div>'+
      p.lines.map(function(l){ return '<div class="l"><div class="py">'+l.p+'</div><div class="tx">'+l.t+'</div></div>'; }).join('')+
      '<div class="note" id="poemNote">'+p.note+'</div>';
    var showPy=true;
    $('pyToggle').onclick=function(){ showPy=!showPy; document.querySelectorAll('.poem .py').forEach(function(el){ el.style.display=showPy?'block':'none'; }); this.textContent=showPy?'🙈 隐藏拼音':'👀 显示拼音'; };
    $('noteToggle').onclick=function(){ var n=$('poemNote'); n.classList.toggle('show'); this.textContent=n.classList.contains('show')?'💡 收起注释':'💡 看注释'; };
    var btn=$('poemDone');
    btn.style.display = SET.chinese? 'block':'none';
    if(d.chinese){ btn.textContent='✓ 已完成（已打卡）'; btn.classList.add('done'); }
    else { btn.textContent='✓ 我已经背熟啦'; btn.classList.remove('done'); }
    btn.onclick=function(){ if(!SET.chinese) return; completeSub('chinese'); };
  }

  /* ---------- 数学：口算 ---------- */
  var drillQs=[];
  function genDrill(){
    var n=SET.drillNum||10, html=''; drillQs=[];
    function rnd(a,b){ return Math.floor(Math.random()*(b-a+1))+a; }
    var wrap=$('drill');
    if(!SET.drill){ wrap.innerHTML='<p class="small">口算模块已关闭（可在“设置”中开启）</p>'; $('drillScore').textContent=''; $('drillDone').style.display='none'; return; }
    for(var i=0;i<n;i++){
      var type=rnd(0,3), ex='', ans=0, a,b;
      if(type===0){ a=rnd(20,999); b=rnd(10,999); ex=a+'+'+b; ans=a+b; }
      else if(type===1){ a=rnd(100,999); b=rnd(10,a); ex=a+'−'+b; ans=a-b; }
      else if(type===2){ a=rnd(2,9); b=rnd(2,9); ex=a+'×'+b; ans=a*b; }
      else { b=rnd(2,9); ans=rnd(2,9); a=b*ans; ex=a+'÷'+b; }
      drillQs.push(ans);
      html += '<div class="p"><span class="ex">'+ex+' =</span><input inputmode="numeric"></div>';
    }
    wrap.innerHTML=html; $('drillScore').textContent='';
    $('drillDone').style.display='block';
    var d=dayRec(curDay);
    if(d.drill){ $('drillDone').textContent='✓ 已完成（已打卡）'; $('drillDone').classList.add('done'); }
    else { $('drillDone').textContent='✓ 完成口算打卡'; $('drillDone').classList.remove('done'); }
  }
  (function(){
    var t=15*60, timer=null;
    function fmt(s){ var m=Math.floor(s/60), ss=s%60; return (m<10?'0':'')+m+':'+(ss<10?'0':'')+ss; }
    genDrill();
    $('drillGen').onclick=function(){ genDrill(); };
    $('drillCheck').onclick=function(){
      var ins=$('drill').querySelectorAll('input'), right=0, allFilled=true;
      ins.forEach(function(inp,i){ var v=parseInt(inp.value,10); inp.classList.remove('ok','bad');
        if(inp.value===''){ allFilled=false; return; }
        if(v===drillQs[i]){ right++; inp.classList.add('ok'); } else { inp.classList.add('bad'); }
      });
      if(!allFilled){ $('drillScore').textContent='还有题没填哦'; return; }
      $('drillScore').textContent='得分：'+right+' / '+ins.length+'　（绿对红错）'+(right===ins.length?'　全对啦！':'');
    };
    $('drillStart').onclick=function(){ if(timer) return; timer=setInterval(function(){ t--; if(t<0){clearInterval(timer);timer=null;t=0;} $('drillT').textContent=fmt(t); },1000); };
    $('drillReset').onclick=function(){ if(timer){clearInterval(timer);timer=null;} t=15*60; $('drillT').textContent=fmt(t); };
    $('drillDone').onclick=function(){ if(!SET.drill) return; completeSub('drill'); };
  })();

  /* ---------- 数学：每日一题 ---------- */
  function renderDaily(){
    var q=dailyOf(curDay);
    var d=dayRec(curDay);
    if(!SET.daily){ $('dailyQ').innerHTML='<p class="small">每日一题模块已关闭（可在“设置”中开启）</p>'; $('dailyDone').style.display='none'; return; }
    $('dailyQ').innerHTML = '<div class="qt">'+q.q+'</div>'+
      '<input class="ain" id="dqIn" placeholder="写下你的答案（多个数用空格分开）">'+
      '<div style="display:flex;gap:8px;"><button class="btn" id="dqCheck" style="flex:1;">✓ 批改</button><button class="btn ghost" id="dqAns" style="flex:1;">看思路</button></div>'+
      '<div class="qans" id="dqA">'+q.a+'</div>';
    function gradeAns(expected, input){
      var nums=(input.match(/-?\d+(\.\d+)?/g)||[]).map(Number).sort(function(a,b){return a-b;});
      var exp=expected.slice().sort(function(a,b){return a-b;});
      if(nums.length!==exp.length) return false;
      for(var i=0;i<nums.length;i++){ if(Math.abs(nums[i]-exp[i])>1e-6) return false; }
      return true;
    }
    $('dqCheck').onclick=function(){ var v=$('dqIn').value; if(!v.trim()){ toast('先写下答案'); return; }
      if(gradeAns(q.ans, v)){ $('dqIn').style.borderColor='var(--ok)'; toast('✅ 答对了！'); } else { $('dqIn').style.borderColor='var(--err)'; toast('❌ 再想想，点“看思路”'); } };
    $('dqAns').onclick=function(){ var el=$('dqA'); el.classList.toggle('show'); this.textContent=el.classList.contains('show')?'收起思路':'看思路'; };
    $('dailyDone').style.display='block';
    if(d.daily){ $('dailyDone').textContent='✓ 已完成（已打卡）'; $('dailyDone').classList.add('done'); }
    else { $('dailyDone').textContent='✓ 完成每日一题'; $('dailyDone').classList.remove('done'); }
  }
  (function(){
    renderDaily();
    $('dailyDone').onclick=function(){ if(!SET.daily) return; completeSub('daily'); };
  })();

  /* ---------- 英语：单词 ---------- */
  function renderEnglish(){
    var list=wordsOf(curDay, SET.wordNum||10);
    var key='wb45-words-'+curDay;
    var done={}; try{ done=JSON.parse(localStorage.getItem(key)||'{}'); }catch(e){}
    function draw(){
      $('wlist').innerHTML = list.map(function(w,i){
        return '<div class="w '+(done[i]?'done':'')+'" data-i="'+i+'"><span class="sp" data-en="'+w[0]+'">🔊</span><span style="flex:1;"><span class="en">'+w[0]+'</span><br><span class="ph">'+w[1]+'</span> <span class="cn">'+w[2]+'</span></span></div>';
      }).join('');
      $('wlist').querySelectorAll('.w').forEach(function(el){
        var i=el.dataset.i;
        el.querySelector('.sp').onclick=function(e){ e.stopPropagation(); speak(list[i][0]); };
        el.onclick=function(){ done[i]=!done[i]; try{ localStorage.setItem(key, JSON.stringify(done)); }catch(e){} draw(); checkAll(); };
      });
      $('wTitle').textContent='🔤 每日单词（'+list.length+' 个）';
    }
    function checkAll(){ var all=true; for(var i=0;i<list.length;i++){ if(!done[i]) all=false; } $('wordDone').style.opacity=all?1:.5; }
    if(!SET.english){ $('wTitle').textContent='🔤 英语模块已关闭'; $('wlist').innerHTML='<p class="small">可在“设置”中开启英语单词</p>'; $('wordDone').style.display='none'; return; }
    draw(); checkAll();
    var d=dayRec(curDay);
    $('wordDone').style.display='block';
    if(d.english){ $('wordDone').textContent='✓ 已完成（已打卡）'; $('wordDone').classList.add('done'); }
    else { $('wordDone').textContent='✓ 单词打卡 +10'; $('wordDone').classList.remove('done'); }
    $('wordDone').onclick=function(){ if(!SET.english) return; completeSub('english'); };
  }
  renderEnglish();
  function speak(text){ try{ if(!('speechSynthesis' in window)) return; var u=new SpeechSynthesisUtterance(text); u.lang='en-US'; u.rate=0.9; speechSynthesis.cancel(); speechSynthesis.speak(u); }catch(e){} }

  /* ---------- 日历 ---------- */
  function renderCalendar(){
    var total=SET.total, html='';
    for(var N=1; N<=total; N++){
      var cls='cday', label='', d=dayRec(N);
      var subs=activeSubs(), doneN=subs.filter(function(s){return d[s];}).length, all=(subs.length>0 && doneN===subs.length);
      if(N<unlockMax){ cls+=' done'; label='✓'; }
      else if(N===unlockMax){ cls+=' today'; label=String(N); }
      else { cls+=' lock'; label='🔒'; }
      html += '<div class="'+cls+'" data-n="'+N+'"><b>'+N+'</b><span>'+label+'</span></div>';
    }
    $('calendar').innerHTML=html;
    $('calInfo').textContent='第 '+curDay+' 天 · '+dateLabel(curDay)+(curDay<unlockMax?'（回看）':(curDay===unlockMax?'（进行中）':''));
    $('calendar').querySelectorAll('.cday').forEach(function(el){
      el.onclick=function(){
        var N=parseInt(el.dataset.n,10);
        if(N>unlockMax){ toast('🔒 先完成第 '+unlockMax+' 天，才能解锁'); return; }
        curDay=N; renderAll(); genDrill(); renderDaily(); renderEnglish();
        $('tabs').querySelectorAll('button').forEach(function(x){x.classList.remove('active');});
        $('tabs').querySelector('button[data-tab="home"]').classList.add('active');
        document.querySelectorAll('.panel').forEach(function(p){p.classList.remove('active');});
        $('panel-home').classList.add('active'); window.scrollTo(0,0);
      };
    });
  }
  function renderCalendarLight(){ if($('panel-calendar').classList.contains('active')) renderCalendar(); }

  /* ---------- 设置 ---------- */
  function renderSettings(){
    var s=getSet();
    $('setChinese').checked=s.chinese; $('setDrill').checked=s.drill; $('setDaily').checked=s.daily; $('setEnglish').checked=s.english;
    $('setDrillNum').value=s.drillNum; $('setWordNum').value=s.wordNum; $('setDuration').value=s.duration;
    $('setStart').value=s.start; $('setTotal').value=s.total;
  }
  (function(){
    $('setSave').onclick=function(){
      var s=getSet();
      s.chinese=$('setChinese').checked; s.drill=$('setDrill').checked; s.daily=$('setDaily').checked; s.english=$('setEnglish').checked;
      s.drillNum=clamp(parseInt($('setDrillNum').value,10)||10,5,30);
      s.wordNum=clamp(parseInt($('setWordNum').value,10)||10,5,30);
      s.duration=clamp(parseInt($('setDuration').value,10)||30,5,60);
      s.start=$('setStart').value||todayStr();
      s.total=[5,10,15,20,30,40,60].indexOf(parseInt($('setTotal').value,10))>=0?parseInt($('setTotal').value,10):30;
      saveSet(s); SET=s;
      unlockMax=Math.min(getUnlock(), s.total); saveUnlock(unlockMax);
      if(curDay>s.total) curDay=s.total;
      toast('✅ 设置已保存'); renderAll(); genDrill(); renderDaily(); renderReward();
      if($('panel-calendar').classList.contains('active')) renderCalendar();
    };
    $('setReset').onclick=function(){
      saveSet(DEF_SET); SET=Object.assign({},DEF_SET);
      toast('已恢复默认设置'); renderAll(); renderReward();
    };
  })();

  /* ---------- 奖励 ---------- */
  var REWARDS = [
    ['看电视 20 分钟','📺',50],['免做家务一次','🧹',50],['吃冰淇淋','🍦',50],
    ['去公园玩','🌳',100],['看一场电影','🎬',150],['一个心愿奖励','💝',200]
  ];
  var pend=null;
  function renderReward(){
    var u=ensureUser(), r=reward();
    $('coinNum').textContent = u.points;
    $('mall').innerHTML = REWARDS.map(function(rw,i){
      var can=u.points>=rw[2];
      return '<div class="r '+(can?'':'cant')+'" data-i="'+i+'"><div class="ic">'+rw[1]+'</div><div class="nm">'+rw[0]+'</div><div class="pt">🪙 '+rw[2]+'</div></div>';
    }).join('');
    $('mall').querySelectorAll('.r').forEach(function(el){
      el.onclick=function(){
        var rw=REWARDS[el.dataset.i];
        if(u.points<rw[2]){ toast('金币不够，先去打卡赚积分吧'); return; }
        pend=rw; $('mTitle').textContent='兑换「'+rw[0]+'」'; $('mText').textContent='需要 🪙 '+rw[2]+' 金币，确定兑换吗？'; $('modal').classList.add('show');
      };
    });
    if(r.coupons.length===0){ $('coupons').innerHTML='<p class="small" style="margin:4px 2px;">还没有兑换奖励，去上面挑一个吧！</p>'; }
    else {
      $('coupons').innerHTML = r.coupons.slice().reverse().map(function(c,i){
        return '<div class="coupon"><div class="ic">'+iconOf(c.name)+'</div><div class="tx"><b>'+c.name+'</b><span>'+c.date+(c.used?' · 已核销':' · 待家长确认')+'</span></div>'+(c.used?'<span class="used">已用</span>':'<button data-i="'+i+'">核销</button>')+'</div>';
      }).join('');
      $('coupons').querySelectorAll('button').forEach(function(b){
        b.onclick=function(){ var rr=reward(); var idx=rr.coupons.length-1-parseInt(b.dataset.i,10); rr.coupons[idx].used=true; saveReward(rr); toast('已核销 ✅'); renderReward(); };
      });
    }
    $('badges').innerHTML = BADGES.map(function(b){ var got=u.badges.indexOf(b.n)>=0; return '<div class="badge '+(got?'got':'')+'"><div class="bic">'+b.ic+'</div><div class="bn">'+b.n+'</div></div>'; }).join('');
  }
  function iconOf(name){ var m={'看电视 20 分钟':'📺','免做家务一次':'🧹','吃冰淇淋':'🍦','去公园玩':'🌳','看一场电影':'🎬','一个心愿奖励':'💝'}; return m[name]||'🎁'; }
  $('mOk').onclick=function(){ if(!pend) return; var r=reward(); r.coupons.push({name:pend[0],date:new Date().toLocaleDateString('zh-CN'),used:false}); saveReward(r); var u=ensureUser(); u.points-=pend[2]; saveUser(u); renderReward(); $('modal').classList.remove('show'); toast('兑换成功，出示此券给家长 ✅'); pend=null; };
  $('mCancel').onclick=function(){ $('modal').classList.remove('show'); pend=null; };
  function renderRewardInit(){ renderReward(); }

  /* ---------- 初始化 ---------- */
  if(curDay>SET.total) curDay=SET.total;
  renderAll(); renderReward();
  if(unlockMax>SET.total){ unlockMax=SET.total; saveUnlock(unlockMax); }
})();
