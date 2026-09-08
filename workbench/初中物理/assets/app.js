/* ============ 初中物理学习工作台 · 交互逻辑（中考总复习 30 天版） ============ */
(function(){
  'use strict';
  var $ = function(id){ return document.getElementById(id); };

  /* ---------- 默认设置 ---------- */
  function todayStr(){ var d=new Date(); var m=String(d.getMonth()+1).padStart(2,'0'), day=String(d.getDate()).padStart(2,'0'); return d.getFullYear()+'-'+m+'-'+day; }
  var DEF_SET = {
    know:true, quiz:true, exp:true,        // 三个模块开关
    quizNum:5,                             // 每日总题量（选择+计算）
    start:todayStr(), total:30             // 起始日（默认当天）/ 总天数
  };
  function getSet(){ try{ return Object.assign({}, DEF_SET, JSON.parse(localStorage.getItem('wbphy-set'))||{}); }catch(e){ return Object.assign({}, DEF_SET); } }
  function saveSet(s){ try{ localStorage.setItem('wbphy-set', JSON.stringify(s)); }catch(e){} }
  var SET = getSet();

  /* ---------- 进度状态 ---------- */
  function getUnlock(){ var n=parseInt(localStorage.getItem('wbphy-unlocked')||'1',10); return isNaN(n)||n<1?1:n; }
  function saveUnlock(n){ try{ localStorage.setItem('wbphy-unlocked', String(n)); }catch(e){} }
  var unlockMax = getUnlock();
  var curDay = unlockMax;

  /* ---------- 存储 ---------- */
  function user(){ try{ return JSON.parse(localStorage.getItem('wbphy-user'))||{}; }catch(e){ return {}; } }
  function saveUser(u){ try{ localStorage.setItem('wbphy-user', JSON.stringify(u)); }catch(e){} }
  function ensureUser(){ var u=user(); if(u.points==null) u.points=0; if(!u.streak) u.streak=0; if(!u.badges) u.badges=[]; saveUser(u); return u; }
  function dayRec(N){ try{ return JSON.parse(localStorage.getItem('wbphy-day-'+N))||{}; }catch(e){ return {}; } }
  function saveDay(N,d){ try{ localStorage.setItem('wbphy-day-'+N, JSON.stringify(d)); }catch(e){} }
  function reward(){ try{ return JSON.parse(localStorage.getItem('wbphy-reward'))||{coupons:[],badges:[]}; }catch(e){ return {coupons:[],badges:[]}; } }
  function saveReward(r){ try{ localStorage.setItem('wbphy-reward', JSON.stringify(r)); }catch(e){} }

  /* ---------- 错题本（方案 A：仅存引用，题干实时从 data.js 取） ---------- */
  function getWrong(){ try{ return JSON.parse(localStorage.getItem('wbphy-wrong'))||[]; }catch(e){ return []; } }
  function saveWrong(a){ try{ localStorage.setItem('wbphy-wrong', JSON.stringify(a)); }catch(e){} }
  function moduleOf(N){
    if(N<=10) return '力学';
    if(N<=13) return '热学';
    if(N<=17) return '声光';
    if(N<=25) return '电学';
    return '实验综合';
  }
  function updateWrongBadge(){ var n=getWrong().length; var b=$('wBadge'); if(b){ if(n){ b.textContent=n; b.style.display='block'; } else { b.textContent=''; b.style.display='none'; } } }
  function recordWrong(d,i,t,w){
    var list=getWrong(), key=d+'-'+t+'-'+i, f=null;
    for(var k=0;k<list.length;k++){ if(list[k].key===key){ f=list[k]; break; } }
    if(f){ f.cnt=(f.cnt||1)+1; f.w=w; f.tms=Date.now(); }
    else { list.push({key:key,d:d,i:i,t:t,w:w,cnt:1,tms:Date.now()}); }
    saveWrong(list);
  }

  /* ---------- 按天取数 ---------- */
  function clamp(v,lo,hi){ return v<lo?lo:(v>hi?hi:v); }
  function KNOWof(N){ return KNOW[clamp(N-1,0,KNOW.length-1)]; }
  function QUIZof(N){ return QUIZ[clamp(N-1,0,QUIZ.length-1)]; }
  function EXPof(N){ return EXP[clamp(N-1,0,EXP.length-1)]; }
  function dateLabel(N){
    var d=new Date(SET.start+'T00:00:00'); d.setDate(d.getDate()+(N-1));
    return (d.getMonth()+1)+'月'+d.getDate()+'日';
  }
  function countSub(sub){ var n=0; for(var i=1;i<=SET.total;i++){ if(dayRec(i)[sub]) n++; } return n; }

  /* ---------- 反馈 ---------- */
  function toast(msg){ var t=$('toast'); t.textContent=msg; t.classList.add('show'); setTimeout(function(){ t.classList.remove('show'); }, 1600); }
  function flyStar(){ var s=document.createElement('div'); s.className='fly'; s.textContent='⭐'; s.style.left='50%'; s.style.top='70%'; document.body.appendChild(s); setTimeout(function(){ s.remove(); }, 1000); }
  function addPoints(n){ var u=ensureUser(); u.points+=n; saveUser(u); renderHome(); renderReward(); }

  /* ---------- 徽章 ---------- */
  var BADGES = [
    {n:'初出茅庐', ic:'🌟'},{n:'坚持小达人', ic:'🔥'},{n:'自律之星', ic:'👑'},
    {n:'刷题小能手', ic:'🧮'},{n:'实验小达人', ic:'🔬'},{n:'公式通', ic:'📐'}
  ];
  function giveBadge(name){ var r=reward(); if(r.badges.indexOf(name)<0){ r.badges.push(name); saveReward(r); toast('🏅 获得徽章：'+name); renderReward(); } }

  /* ---------- 打卡 + 解锁（弱判定） ---------- */
  var SUB_POINT = {know:10, quiz:10, exp:10};
  function activeSubs(){ var a=[]; if(SET.know)a.push('know'); if(SET.quiz)a.push('quiz'); if(SET.exp)a.push('exp'); return a; }
  function completeSub(sub){
    if(!SET[sub]) return;
    var d=dayRec(curDay);
    if(d[sub]){ toast('这一天这一项已经打卡啦'); return; }
    d[sub]=true; saveDay(curDay, d);
    addPoints(SUB_POINT[sub]);
    toast('+'+SUB_POINT[sub]+' 积分 🎉'); flyStar();
    if(sub==='know' && countSub('know')>=15) giveBadge('公式通');
    if(sub==='exp' && countSub('exp')>=10) giveBadge('实验小达人');
    var subs=activeSubs(), all=true;
    subs.forEach(function(s){ if(!d[s]) all=false; });
    if(all && curDay===unlockMax){
      unlockMax=Math.min(curDay+1, SET.total);
      saveUnlock(unlockMax);
      if(unlockMax>curDay) toast('🎉 解锁第 '+unlockMax+' 天！');
    }
    if(all) fullDayDone();
    renderAll();
  }
  function fullDayDone(){
    var u=ensureUser();
    var key='wbphy-seq-'+curDay;
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
  function tag(id, done){ var el=$(id); el.textContent=done?'已完成':'未完成'; el.className='st '+(done?'ok':'no'); }
  function renderHome(){
    var u=ensureUser(), d=dayRec(curDay), subs=activeSubs();
    var doneN = subs.filter(function(s){ return d[s]; }).length;
    $('stDay').textContent = '第 '+curDay+' / '+SET.total+' 天';
    $('stPoint').textContent = u.points;
    $('stStreak').textContent = u.streak;
    var p = subs.length? Math.round(doneN/subs.length*100):0;
    $('ring').style.setProperty('--p', p);
    $('ringP').textContent = p+'%';
    setBar('bar-know', SET.know && !!d.know);
    setBar('bar-quiz', SET.quiz && !!d.quiz);
    setBar('bar-exp', SET.exp && !!d.exp);
    tag('go-know', SET.know && !!d.know);
    tag('go-quiz', SET.quiz && !!d.quiz);
    tag('go-exp', SET.exp && !!d.exp);
    $('heroDate').textContent = '今天是 '+dateLabel(curDay)+' · 第 '+curDay+' 天';
  }

  /* ---------- Tab 切换 ---------- */
  $('tabs').querySelectorAll('button').forEach(function(b){
    b.addEventListener('click', function(){
      $('tabs').querySelectorAll('button').forEach(function(x){x.classList.remove('active');});
      b.classList.add('active');
      document.querySelectorAll('.panel').forEach(function(p){p.classList.remove('active');});
      $('panel-'+b.dataset.tab).classList.add('active');
      if(b.dataset.tab==='calendar') renderCalendar();
      if(b.dataset.tab==='settings') renderSettings();
      if(b.dataset.tab==='wrong') renderWrong();
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

  function renderAll(){ renderHome(); renderKnow(); renderQuiz(); renderExp(); renderCalendarLight(); }

  /* ---------- 知识：知识点 + 公式卡 ---------- */
  function renderKnow(){
    var K=KNOWof(curDay), d=dayRec(curDay);
    if(!SET.know){ $('know').innerHTML='<p class="small">知识模块已关闭（可在“设置”中开启）</p>'; $('fToggle').style.display='none'; $('knowDone').style.display='none'; return; }
    $('fToggle').style.display='inline-block';
    var html='<div class="kt">📘 第 '+curDay+' 天 · '+K.topic+'</div>';
    html+='<div class="ksum">'+K.summary+'</div>';
    html+='<div class="section-t">核心要点</div><ul class="pts">'+K.points.map(function(p){return '<li>'+p+'</li>';}).join('')+'</ul>';
    html+='<div class="section-t">公式卡片</div><div class="formulas" id="fbox">'+K.formulas.map(function(f){
      return '<div class="fcard"><div class="ff">'+f.f+'</div><div class="fd">'+f.des+'</div>'+(f.unit?'<div class="fu">单位：'+f.unit+'</div>':'')+(f.note?'<div class="fn">注：'+f.note+'</div>':'')+'</div>';
    }).join('')+'</div>';
    $('know').innerHTML=html;
    var btn=$('knowDone'); btn.style.display='block';
    if(d.know){ btn.textContent='✓ 已完成（已打卡）'; btn.classList.add('done'); }
    else { btn.textContent='✓ 我掌握了，打卡 +10'; btn.classList.remove('done'); }
    btn.onclick=function(){ if(!SET.know) return; completeSub('know'); };
  }
  $('fToggle').onclick=function(){
    var box=$('fbox'); if(!box) return;
    var hide = box.style.display!=='none';
    box.style.display = hide?'none':'block';
    this.textContent = hide?'👀 显示公式':'🙈 隐藏公式';
  };

  /* ---------- 练习：每日一练（自动批改） ---------- */
  var selChoice = [];
  function renderQuiz(){
    var Q=QUIZof(curDay), d=dayRec(curDay);
    if(!SET.quiz){ $('qList').innerHTML='<p class="small">练习模块已关闭（可在“设置”中开启）</p>'; $('qCheck').style.display='none'; $('quizDone').style.display='none'; return; }
    $('qCheck').style.display='block'; $('quizDone').style.display='block';
    selChoice=[];
    var want=clamp(SET.quizNum||5, 1, 8);            // 每日总题量（选择+计算）
    var nC=Math.min(want, Q.choice.length);
    var nX=Math.min(Math.max(0, want-nC), Q.calc.length);
    var html='<div class="qsum">📌 知识点总结：'+Q.ksum+'</div>';
    html+='<div class="qlv">选择题 '+nC+' 道 · 计算题 '+nX+' 道（提交后绿对红错）</div>';
    Q.choice.slice(0,nC).forEach(function(c,i){
      html+='<div class="qcard" data-type="c" data-j="'+i+'"><div class="qt"><b>'+(i+1)+'.</b> '+c.q+' <span class="lv '+c.lv+'">'+c.lv+'</span></div><div class="opts">'+c.opt.map(function(o,v){return '<button class="opt" data-v="'+v+'">'+o+'</button>';}).join('')+'</div><div class="qans">'+c.exp+'</div></div>';
    });
    Q.calc.slice(0,nX).forEach(function(c,j){
      html+='<div class="qcard" data-type="x" data-j="'+j+'"><div class="qt"><b>'+(nC+j+1)+'.</b> '+c.q+' <span class="lv '+c.lv+'">'+c.lv+'</span></div><input class="ain" placeholder="填数值（可带单位）"><div class="qans">'+c.exp+'</div></div>';
    });
    html+='<div class="score" id="qScore"></div>';
    $('qList').innerHTML=html;
    $('qList').querySelectorAll('.qcard[data-type="c"]').forEach(function(card){
      var i=parseInt(card.dataset.j,10);
      card.querySelectorAll('.opt').forEach(function(o){
        o.onclick=function(){
          selChoice[i]=parseInt(o.dataset.v,10);
          card.querySelectorAll('.opt').forEach(function(x){ x.style.background=''; x.style.color=''; });
          o.style.background='#D6E8FF'; o.style.color='#0A5BD0';
        };
      });
    });
    var btn=$('quizDone');
    if(d.quiz){ btn.textContent='✓ 已完成（已打卡）'; btn.classList.add('done'); }
    else { btn.textContent='✓ 完成练习打卡 +10'; btn.classList.remove('done'); }
    btn.onclick=function(){ if(!SET.quiz) return; completeSub('quiz'); };
  }
  function gradeAns(expected, input){
    var nums=(input.match(/-?\d+(\.\d+)?/g)||[]).map(Number).sort(function(a,b){return a-b;});
    var exp=expected.slice().sort(function(a,b){return a-b;});
    if(nums.length!==exp.length) return false;
    for(var i=0;i<nums.length;i++){
      var a=exp[i], b=nums[i], tol=Math.max(1e-6, Math.abs(a)*0.01);
      if(Math.abs(a-b)>tol) return false;
    }
    return true;
  }
  $('qCheck').onclick=function(){
    var Q=QUIZof(curDay);
    var cards=$('qList').querySelectorAll('.qcard');
    var right=0, total=0, allRight=true, nC=clamp(SET.quizNum||5,1,Q.choice.length);
    cards.forEach(function(card){
      var type=card.dataset.type, j=parseInt(card.dataset.j,10);
      card.querySelector('.qans').classList.add('show');
      if(type==='c'){
        total++;
        var picked=selChoice[j], opts=card.querySelectorAll('.opt'), ans=Q.choice[j].ans;
        if(picked==null){ allRight=false; recordWrong(curDay, j, 'c', null); }
        else if(picked===ans){ opts[picked].classList.add('ok'); right++; }
        else { opts[picked].classList.add('bad'); opts[ans].classList.add('ok'); allRight=false; recordWrong(curDay, j, 'c', picked); }
      } else {
        total++;
        var inp=card.querySelector('.ain'), v=inp.value;
        if(v.trim()===''){ allRight=false; recordWrong(curDay, j, 'x', ''); }
        else if(gradeAns(Q.calc[j].ans, v)){ inp.classList.add('ok'); right++; }
        else { inp.classList.add('bad'); allRight=false; recordWrong(curDay, j, 'x', v); }
      }
    });
    if(allRight && total>0){
      var d=dayRec(curDay);
      if(!d.quizPerfect){ d.quizPerfect=true; saveDay(curDay,d); addPoints(5); giveBadge('刷题小能手'); toast('全对！额外 +5 🎉'); }
      $('qScore').textContent='全对啦！'+right+' / '+total+' 🎉';
    } else {
      $('qScore').textContent='已批改：对 '+right+' / '+total+'　（绿对红错）';
      if(total>0 && !allRight) toast('再看解析，订正错题');
    }
    updateWrongBadge();
  };

  /* ---------- 实验：实验探究 ---------- */
  function renderExp(){
    var E=EXPof(curDay), d=dayRec(curDay);
    if(!SET.exp){ $('exp').innerHTML='<p class="small">实验模块已关闭（可在“设置”中开启）</p>'; $('expDone').style.display='none'; return; }
    $('expDone').style.display='block';
    var html='';
    if(E.type==='exp'){
      html+='<div class="et">🔬 '+E.name+'</div>';
      html+='<div class="erow"><b>实验目的：</b>'+E.aim+'</div>';
      html+='<div class="erow"><b>实验器材：</b>'+E.tools+'</div>';
      html+='<div class="erow"><b>实验步骤：</b><ol>'+E.steps.map(function(s){return '<li>'+s+'</li>';}).join('')+'</ol></div>';
      html+='<div class="erow"><b>实验现象：</b>'+E.phen+'</div>';
      html+='<div class="erow"><b>实验结论：</b>'+E.concl+'</div>';
      html+='<div class="erow"><b>易错点：</b><span style="color:#C0392B;">'+E.pit+'</span></div>';
    } else {
      html+='<div class="et warn">⚠️ '+E.name+'</div>';
      html+='<div class="pit">'+E.pit+'</div>';
    }
    $('exp').innerHTML=html;
    var btn=$('expDone');
    if(d.exp){ btn.textContent='✓ 已完成（已打卡）'; btn.classList.add('done'); }
    else { btn.textContent='✓ 完成实验打卡 +10'; btn.classList.remove('done'); }
    btn.onclick=function(){ if(!SET.exp) return; completeSub('exp'); };
  }

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
        curDay=N; renderAll();
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
    $('setKnow').checked=s.know; $('setQuiz').checked=s.quiz; $('setExp').checked=s.exp;
    $('setQuizNum').value=s.quizNum; $('setStart').value=s.start; $('setTotal').value=s.total;
  }
  $('setSave').onclick=function(){
    var s=getSet();
    s.know=$('setKnow').checked; s.quiz=$('setQuiz').checked; s.exp=$('setExp').checked;
    s.quizNum=clamp(parseInt($('setQuizNum').value,10)||5,3,8);
    s.start=$('setStart').value||'2026-07-01';
    s.total=[5,10,15,20,30,40,60].indexOf(parseInt($('setTotal').value,10))>=0?parseInt($('setTotal').value,10):30;
    saveSet(s); SET=s;
    unlockMax=Math.min(getUnlock(), s.total); saveUnlock(unlockMax);
    if(curDay>s.total) curDay=s.total;
    toast('✅ 设置已保存');
    renderAll(); renderReward(); if($('panel-calendar').classList.contains('active')) renderCalendar();
  };
  $('setReset').onclick=function(){
    saveSet(DEF_SET); SET=Object.assign({},DEF_SET);
    toast('已恢复默认设置');
    renderAll(); renderReward(); if($('panel-calendar').classList.contains('active')) renderCalendar();
  };

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

  /* ---------- 错题本：渲染 / 重做 / 导出 ---------- */
  var wrongFilter='全部';
  function renderWrong(){
    var list=getWrong();
    var mods=['力学','热学','声光','电学','实验综合'], cnts={}; mods.forEach(function(m){cnts[m]=0;});
    list.forEach(function(x){ cnts[moduleOf(x.d)]++; });
    var f=wrongFilter||'全部', shown=(f==='全部')?list:list.filter(function(x){return moduleOf(x.d)===f;});
    var html='';
    html+='<div class="wrong-head"><div class="wcount">📕 错题 <b>'+list.length+'</b> 道</div>'
        + '<div class="wbtns"><button class="btn ghost" id="wExport">⬇️ JSON</button><button class="btn ghost" id="wImage">🖼️ 图片</button><button class="btn ghost" id="wClear">🗑️ 清空</button></div></div>';
    html+='<div class="wchips">'+['全部'].concat(mods).map(function(m){ var n=m==='全部'?list.length:cnts[m]; return '<button class="wchip'+(f===m?' on':'')+'" data-m="'+m+'">'+m+' <i>'+n+'</i></button>'; }).join('')+'</div>';
    if(shown.length===0){ html+='<div class="wempty">🎉 暂时没有错题，保持住！</div>'; }
    else { shown.forEach(function(it){ html+=wrongCardHtml(it); }); }
    $('wrong').innerHTML=html;
    $('wrong').querySelectorAll('.wchip').forEach(function(b){ b.onclick=function(){ wrongFilter=b.dataset.m; renderWrong(); }; });
    $('wExport').onclick=exportWrong;
    $('wImage').onclick=shareWrong;
    $('wClear').onclick=clearWrong;
    $('wrong').querySelectorAll('.wcard').forEach(function(card){
      var key=card.dataset.key, rb=card.querySelector('.redo'); if(rb) rb.onclick=function(){ startRedo(card, key); };
    });
    updateWrongBadge();
  }
  function wrongCardHtml(it){
    var Qd=QUIZof(it.d), isC=it.t==='c', c=isC?Qd.choice[it.i]:Qd.calc[it.i];
    var wrongTxt = isC ? (it.w==null?'（未作答）':(c.opt[it.w]!=null?c.opt[it.w]:'选项'+(it.w+1))) : (it.w===''?'（未作答）':it.w);
    var ansTxt = isC ? c.opt[c.ans] : c.ans.join('、');
    return '<div class="wcard" data-key="'+it.key+'">'
      + '<div class="wh"><span class="wday">第'+it.d+'天</span><span class="wmod">'+moduleOf(it.d)+'</span><span class="wcnt">错'+it.cnt+'次</span></div>'
      + '<div class="wt">'+c.q+' <span class="lv '+c.lv+'">'+c.lv+'</span></div>'
      + '<div class="wrow"><span class="wl">你的答案</span><span class="wv bad">'+wrongTxt+'</span></div>'
      + '<div class="wrow"><span class="wl">正确答案</span><span class="wv ok">'+ansTxt+'</span></div>'
      + '<div class="wexp">💡 '+c.exp+'</div>'
      + '<div class="wact"><button class="btn ghost redo">🔁 重做</button></div>'
      + '</div>';
  }
  function startRedo(card, key){
    var item=null, list=getWrong(); for(var k=0;k<list.length;k++){ if(list[k].key===key){ item=list[k]; break; } }
    if(!item) return;
    var Qd=QUIZof(item.d), isC=item.t==='c', c=isC?Qd.choice[item.i]:Qd.calc[item.i];
    var body='<div class="rdo">';
    if(isC){ body+='<div class="opts">'+c.opt.map(function(o,v){return '<button class="opt rdo-opt" data-v="'+v+'">'+o+'</button>';}).join('')+'</div>'; }
    else { body+='<input class="ain rdo-in" placeholder="填数值（可带单位）">'; }
    body+='<button class="btn full redo-sub">✓ 提交</button></div>';
    var act=card.querySelector('.wact'); act.innerHTML=body;
    var sel=null;
    if(isC){ act.querySelectorAll('.rdo-opt').forEach(function(o){ o.onclick=function(){ sel=parseInt(o.dataset.v,10); act.querySelectorAll('.rdo-opt').forEach(function(x){x.style.background='';x.style.color='';}); o.style.background='#D6E8FF'; o.style.color='#0A5BD0'; }; }); }
    act.querySelector('.redo-sub').onclick=function(){
      var ok = isC ? (sel===c.ans) : gradeAns(c.ans, act.querySelector('.rdo-in').value);
      if(ok){ removeWrong(key); toast('✅ 已掌握，移出错题本'); renderWrong(); }
      else {
        var L=getWrong(), it=null; for(var m=0;m<L.length;m++){ if(L[m].key===key){ it=L[m]; break; } }
        if(it){ it.cnt=(it.cnt||1)+1; it.w=isC?sel:act.querySelector('.rdo-in').value; it.tms=Date.now(); saveWrong(L); }
        toast('还不对，再看解析 😉'); renderWrong();
      }
    };
  }
  function removeWrong(key){ var list=getWrong().filter(function(x){return x.key!==key;}); saveWrong(list); updateWrongBadge(); }
  function clearWrong(){
    if(getWrong().length===0){ toast('错题本已经是空的'); return; }
    $('cText').textContent='确定清空错题本吗？已掌握的题目和记录都会被删除，此操作不可恢复。';
    $('cModal').classList.add('show');
  }
  /* 清空确认弹窗：页面内弹窗（替代原生 confirm，兼容 iframe 预览） */
  $('cOk').onclick=function(){
    $('cModal').classList.remove('show');
    saveWrong([]); updateWrongBadge(); renderWrong(); toast('已清空错题本');
  };
  $('cCancel').onclick=function(){ $('cModal').classList.remove('show'); };
  function exportWrong(){
    var list=getWrong(); if(list.length===0){ toast('还没有错题可导出'); return; }
    var out=list.map(function(x){ var Qd=QUIZof(x.d), isC=x.t==='c', c=isC?Qd.choice[x.i]:Qd.calc[x.i];
      return {day:x.d, module:moduleOf(x.d), type:isC?'选择':'计算', topic:KNOWof(x.d).topic, q:c.q, lv:c.lv,
        wrong:isC?(x.w==null?'未作答':(c.opt[x.w]!=null?c.opt[x.w]:'选项'+(x.w+1))):x.w,
        right:isC?c.opt[c.ans]:c.ans.join('、'), exp:c.exp, cnt:x.cnt, tms:x.tms}; });
    var blob=new Blob([JSON.stringify({app:'初中物理错题本', exported:new Date().toLocaleString('zh-CN'), items:out}, null, 2)], {type:'application/json'});
    var a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='初中物理错题本_'+new Date().toISOString().slice(0,10)+'.json'; a.click();
    setTimeout(function(){ try{ URL.revokeObjectURL(a.href); }catch(e){} }, 1000);
    toast('已导出 '+out.length+' 道错题 (JSON)');
  }
  function shareWrong(){
    var list=getWrong(); if(list.length===0){ toast('还没有错题可生成图片'); return; }
    var mods=['力学','热学','声光','电学','实验综合'], cnts={}; mods.forEach(function(m){cnts[m]=0;}); list.forEach(function(x){ cnts[moduleOf(x.d)]++; });
    try{
      var cv=document.createElement('canvas'); cv.width=640; cv.height=820; var x=cv.getContext('2d');
      x.fillStyle='#EEF3F8'; x.fillRect(0,0,640,820);
      x.fillStyle='#0A84FF'; x.fillRect(0,0,640,150);
      x.fillStyle='#fff'; x.font='bold 30px sans-serif'; x.fillText('林老师 · 初中物理错题本',36,72);
      x.font='17px sans-serif'; x.fillText('共 '+list.length+' 道错题 · 导出 '+new Date().toLocaleDateString('zh-CN'),36,110);
      x.fillStyle='#1F2A37'; x.font='bold 22px sans-serif'; x.fillText('模块分布',36,200);
      var maxv=Math.max(1,list.length), y=244;
      mods.forEach(function(m){ x.fillStyle='#475569'; x.font='16px sans-serif'; x.fillText(m,36,y);
        var w=Math.round(cnts[m]/maxv*420); x.fillStyle='#D6E8FF'; x.fillRect(150,y-16,420,22);
        x.fillStyle='#0A84FF'; x.fillRect(150,y-16,w,22); x.fillStyle='#1F2A37'; x.font='bold 15px sans-serif'; x.fillText(String(cnts[m]),150+w+8,y); y+=46; });
      x.fillStyle='#8A94A6'; x.font='13px sans-serif'; x.fillText('© 2026 林老师 · 免费福利版',36,798);
      var a=document.createElement('a'); a.href=cv.toDataURL('image/png'); a.download='错题统计_'+new Date().toISOString().slice(0,10)+'.png'; a.click();
      toast('已生成错题统计图片');
    }catch(e){ toast('当前环境不支持生成图片，请用「JSON」导出'); }
  }

  /* ---------- 初始化 ---------- */
  if(curDay>SET.total) curDay=SET.total;
  if(unlockMax>SET.total){ unlockMax=SET.total; saveUnlock(unlockMax); }
  renderAll(); renderReward(); updateWrongBadge();
})();
