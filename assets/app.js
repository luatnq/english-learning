/* English Learning — static site. Vanilla JS, no build step. */
"use strict";

const App = {
  units: [],
  el(tag, cls, html){ const e=document.createElement(tag); if(cls)e.className=cls; if(html!=null)e.innerHTML=html; return e; },
  slug(s){ return s.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,""); },
  norm(s){ return (s||"").toLowerCase().trim().replace(/[.,!?;:]/g,"").replace(/\s+/g," "); },
  play(src){ const a=new Audio(src); a.play().catch(()=>alert("Không phát được audio:\n"+src+"\n(Trên GitHub Pages sẽ chạy bình thường.)")); },
};

async function boot(){
  try{
    App.units = await (await fetch("data/units.json")).json();
  }catch(e){ document.getElementById("app").innerHTML="<p class='wrap'>Không tải được danh sách unit.</p>"; return; }
  window.addEventListener("hashchange", route);
  route();
}

function route(){
  const h = location.hash;
  const m = h.match(/^#\/unit\/(.+)$/);
  if(m) renderUnit(decodeURIComponent(m[1]));
  else renderHome();
}

/* ---------------- HOME ---------------- */
function renderHome(){
  const app = document.getElementById("app");
  app.innerHTML="";
  const wrap = App.el("div","wrap");
  wrap.appendChild(App.el("p",null,"<b>Chọn một chủ đề để bắt đầu.</b> Nghe, làm bài và tự kiểm tra đáp án ngay trên trang. Có thể tải worksheet PDF để in."));
  const cards = App.el("div","cards");
  App.units.forEach(u=>{
    const c = App.el("div","card");
    c.innerHTML = `<span class="lvl">${u.cefr}</span>
      <h3>${u.title_en}</h3><div class="vi">${u.title_vi}</div>
      <div class="meta">${u.words} từ · 7 phần bài tập</div>`;
    c.onclick=()=>{ location.hash="#/unit/"+encodeURIComponent(u.id); };
    cards.appendChild(c);
  });
  wrap.appendChild(cards);
  app.appendChild(wrap);
  setBack(false);
}

/* ---------------- UNIT ---------------- */
async function renderUnit(id){
  const meta = App.units.find(u=>u.id===id);
  const app = document.getElementById("app");
  if(!meta){ app.innerHTML="<p class='wrap'>Không tìm thấy unit.</p>"; return; }
  let U;
  try{ U = await (await fetch(meta.json)).json(); }
  catch(e){ app.innerHTML="<p class='wrap'>Không tải được nội dung unit.</p>"; return; }
  const A = meta.audioDir; // audio base
  app.innerHTML="";
  const wrap = App.el("div","wrap");
  setBack(true);

  // head
  const head = App.el("div","unit-head");
  head.innerHTML = `<h2>Unit ${U.unit} · ${U.title_en}</h2><div class="vi">${U.title_vi}</div>
    <div class="pills">
      <span class="pill">Level ${U.cefr}</span>
      <span class="pill">${U.words.length} từ</span>
      <a class="pill dl" href="${meta.worksheet}" target="_blank">⬇ Worksheet PDF</a>
      <a class="pill dl" href="${meta.answers}" target="_blank">⬇ Answer key PDF</a>
    </div>`;
  wrap.appendChild(head);

  if(U.grammar) wrap.appendChild(grammarBox(U));
  wrap.appendChild(secA(U,A));
  wrap.appendChild(secB(U));
  wrap.appendChild(secC(U));
  wrap.appendChild(secD(U));
  wrap.appendChild(secE(U,A));
  wrap.appendChild(secF(U,A));
  wrap.appendChild(secG(U));
  app.appendChild(wrap);
  window.scrollTo(0,0);
}

function grammarBox(U){
  const g=U.grammar;
  const s=App.el("section","ex grammar");
  s.appendChild(App.el("h4",null,"📌 "+(g.title_vi||"Ngữ pháp trọng tâm")));
  if(g.intro_vi) s.appendChild(App.el("p","hint",g.intro_vi));
  const ul=App.el("div");
  (g.points||[]).forEach((p,i)=>{
    const [txt,ex]=p;
    const d=App.el("div","q");
    d.innerHTML=`<div class="prompt">${i+1}. ${txt}</div><div class="gex">▸ ${ex}</div>`;
    ul.appendChild(d);
  });
  s.appendChild(ul);
  return s;
}

function section(letter,title,hint){
  const s = App.el("section","ex");
  s.appendChild(App.el("h4",null,`${letter}. ${title}`));
  if(hint) s.appendChild(App.el("p","hint",hint));
  return s;
}
function checkBtn(onclick){ const b=App.el("button","btn","Kiểm tra"); b.onclick=onclick; return b; }

/* A — words */
function secA(U,A){
  const s = section("A","New words — Từ mới","Bấm 🔊 để nghe. Bấm vào cột nghĩa để hiện/ẩn.");
  const t = App.el("table","words");
  t.innerHTML = "<tr><th>Word</th><th>IPA</th><th></th><th>Nghĩa</th><th>Example</th></tr>";
  U.words.forEach(w=>{
    const [word,ipa,pos,mvi,ex] = w;
    const collos = w[6] || [];
    const colloHtml = collos.map(c=>`<div class="collo">▸ ${c[0]} — <span class="cvi">${c[1]}</span></div>`).join("");
    const tr = App.el("tr");
    tr.innerHTML = `<td class="w">${word}</td><td class="ipa">${ipa}</td>
      <td></td><td class="mean hidden">${mvi}</td><td>${ex}${colloHtml}</td>`;
    const pb = App.el("button","play","🔊");
    pb.onclick=()=>App.play(A+"words/"+App.slug(word)+".mp3");
    tr.children[2].appendChild(pb);
    tr.querySelector(".mean").onclick=(e)=>e.target.classList.toggle("hidden");
    t.appendChild(tr);
  });
  s.appendChild(t);
  return s;
}

/* B — matching + mcq */
function secB(U){
  const s = section("B","Match & choose — Nối và chọn");
  // matching via selects
  s.appendChild(App.el("p","prompt","<b>Nối từ với nghĩa đúng:</b>"));
  const opts = U.matching.map(m=>m[1]);
  const shuffled = shuffle(opts.slice(),7);
  const selects=[];
  U.matching.forEach((m,i)=>{
    const row = App.el("div","row");
    row.appendChild(App.el("span",null,`${i+1}. <b>${m[0]}</b>`));
    const sel = App.el("select");
    sel.innerHTML = "<option value=''>— chọn —</option>"+shuffled.map(o=>`<option>${o}</option>`).join("");
    selects.push([sel,m[1]]);
    row.appendChild(sel);
    s.appendChild(row);
  });
  const rB = App.el("span","result");
  const bB = checkBtn(()=>{ let ok=0; selects.forEach(([sel,ans])=>{
    const good = sel.value===ans; sel.classList.toggle("correct",good); sel.classList.toggle("wrong",!good&&sel.value!=="");
    if(good) ok++; });
    rB.innerHTML = `<span class="${ok===selects.length?'ok':'bad'}">${ok}/${selects.length} đúng</span>`; });
  const rowb=App.el("div","row"); rowb.append(bB,rB); s.appendChild(rowb);

  // mcq
  s.appendChild(App.el("p","prompt","<b>Chọn nghĩa đúng:</b>"));
  const mcqs=[];
  U.mcq.forEach((q,i)=>{
    const [text,options,ci]=q;
    const qd=App.el("div","q");
    qd.innerHTML=`<div class="prompt">${i+1}. ${text}</div>`;
    const od=App.el("div","opts");
    options.forEach((o,j)=>{
      const id=`mcq${i}_${j}`;
      od.innerHTML+=`<label><input type="radio" name="mcq${i}" value="${j}"> ${String.fromCharCode(97+j)}) ${o}</label>`;
    });
    qd.appendChild(od); s.appendChild(qd); mcqs.push([i,ci]);
  });
  const rM=App.el("span","result");
  const bM=checkBtn(()=>{ let ok=0; mcqs.forEach(([i,ci])=>{
    const sel=s.querySelector(`input[name=mcq${i}]:checked`);
    if(sel && +sel.value===ci) ok++; });
    rM.innerHTML=`<span class="${ok===mcqs.length?'ok':'bad'}">${ok}/${mcqs.length} đúng</span>`;
    // mark
    mcqs.forEach(([i,ci])=>{ const labs=s.querySelectorAll(`input[name=mcq${i}]`);
      labs.forEach(inp=>{ inp.parentElement.classList.remove("ok","bad");
        if(+inp.value===ci) inp.parentElement.classList.add("ok");
        else if(inp.checked) inp.parentElement.classList.add("bad"); }); });
  });
  const rowm=App.el("div","row"); rowm.append(bM,rM); s.appendChild(rowm);
  return s;
}

/* C — cloze */
function secC(U){
  const s=section("C","Fill in the blanks — Điền chỗ trống");
  s.appendChild(App.el("p","prompt","Word bank: <b>"+U.cloze.bank.join(" · ")+"</b>"));
  const inputs=[];
  U.cloze.items.forEach((it,i)=>{
    const [sent,ans]=it;
    const row=App.el("div","row");
    const parts=sent.split("______");
    const inp=App.el("input"); inp.type="text"; inp.style.minWidth="120px";
    row.appendChild(App.el("span",null,`${i+1}. ${parts[0]}`));
    row.appendChild(inp);
    row.appendChild(App.el("span",null,parts[1]||""));
    inputs.push([inp,ans]); s.appendChild(row);
  });
  const r=App.el("span","result");
  const b=checkBtn(()=>{ let ok=0; inputs.forEach(([inp,ans])=>{
    const good=App.norm(inp.value)===App.norm(ans);
    inp.classList.toggle("correct",good); inp.classList.toggle("wrong",!good&&inp.value!=="");
    if(good) ok++; });
    r.innerHTML=`<span class="${ok===inputs.length?'ok':'bad'}">${ok}/${inputs.length} đúng</span>`; });
  const row=App.el("div","row"); row.append(b,r); s.appendChild(row);
  return s;
}

/* D — word order */
function secD(U){
  const s=section("D","Put words in order — Sắp xếp từ (ngữ pháp)","Sắp các từ thành câu đúng rồi Kiểm tra để xem giải thích ngữ pháp.");
  const rows=[];
  U.word_order.forEach((wo,i)=>{
    const [toks,ans,note]=wo;
    const q=App.el("div","q");
    const chips=shuffle(toks.slice(),i+3).map(t=>`<span class="chip">${t}</span>`).join(" ");
    q.innerHTML=`<div class="tokens">${i+1}. ${chips}</div>`;
    const inp=App.el("input"); inp.type="text"; inp.placeholder="Viết câu đúng...";
    q.appendChild(inp);
    const nt=App.el("div","note",`<b>Ngữ pháp:</b> ${note}`);
    q.appendChild(nt);
    s.appendChild(q); rows.push([inp,ans,nt]);
  });
  const r=App.el("span","result");
  const b=checkBtn(()=>{ let ok=0; rows.forEach(([inp,ans,nt])=>{
    const good=App.norm(inp.value)===App.norm(ans);
    inp.classList.toggle("correct",good); inp.classList.toggle("wrong",!good&&inp.value!=="");
    nt.classList.add("show"); if(good) ok++; });
    r.innerHTML=`<span class="${ok===rows.length?'ok':'bad'}">${ok}/${rows.length} đúng</span>`; });
  const row=App.el("div","row"); row.append(b,r); s.appendChild(row);
  return s;
}

/* E — listening */
function secE(U,A){
  const s=section("E","Listening — Nghe","Bấm ▶ để nghe rồi làm bài.");
  const L=U.listening;
  // E1 dictation
  s.appendChild(App.el("p","prompt","<b>E1. Nghe và chép lại (dictation):</b>"));
  const d=[];
  L.dictation.forEach((tr,i)=>{
    const row=App.el("div","row");
    const pb=App.el("button","play wide","▶ Câu "+(i+1));
    pb.onclick=()=>App.play(A+"e1_"+(i+1)+".mp3");
    const inp=App.el("input"); inp.type="text"; inp.placeholder="Viết câu bạn nghe được...";
    row.append(pb,inp); s.appendChild(row); d.push([inp,tr]);
  });
  const r1=App.el("span","result");
  const b1=checkBtn(()=>{ let ok=0; d.forEach(([inp,tr])=>{ const good=App.norm(inp.value)===App.norm(tr);
    inp.classList.toggle("correct",good); inp.classList.toggle("wrong",!good&&inp.value!=="");
    if(good) ok++; }); r1.innerHTML=`<span class="${ok===d.length?'ok':'bad'}">${ok}/${d.length} đúng</span>`; });
  const rr1=App.el("div","row"); rr1.append(b1,r1); s.appendChild(rr1);
  // E2 choose
  s.appendChild(App.el("p","prompt","<b>E2. Nghe và chọn từ đúng:</b>"));
  const c=[];
  L.choose.forEach((ch,i)=>{
    const [ans,options]=ch;
    const q=App.el("div","q");
    const pb=App.el("button","play wide","▶ Từ "+(i+1)); pb.onclick=()=>App.play(A+"e2_"+(i+1)+".mp3");
    const rowp=App.el("div","row"); rowp.appendChild(pb); q.appendChild(rowp);
    const od=App.el("div","opts");
    options.forEach((o,j)=> od.innerHTML+=`<label><input type="radio" name="e2_${i}" value="${o}"> ${o}</label>`);
    q.appendChild(od); s.appendChild(q); c.push([i,ans]);
  });
  const r2=App.el("span","result");
  const b2=checkBtn(()=>{ let ok=0; c.forEach(([i,ans])=>{ const sel=s.querySelector(`input[name=e2_${i}]:checked`);
    const labs=s.querySelectorAll(`input[name=e2_${i}]`);
    labs.forEach(inp=>{ inp.parentElement.classList.remove("ok","bad");
      if(inp.value===ans) inp.parentElement.classList.add("ok"); else if(inp.checked) inp.parentElement.classList.add("bad"); });
    if(sel && sel.value===ans) ok++; });
    r2.innerHTML=`<span class="${ok===c.length?'ok':'bad'}">${ok}/${c.length} đúng</span>`; });
  const rr2=App.el("div","row"); rr2.append(b2,r2); s.appendChild(rr2);
  return s;
}

/* F — reading */
function secF(U,A){
  const s=section("F","Reading — Đọc hiểu");
  const pb=App.el("button","play wide","▶ Nghe đoạn đọc"); pb.onclick=()=>App.play(A+"reading.mp3");
  const rowp=App.el("div","row"); rowp.appendChild(pb); s.appendChild(rowp);
  s.appendChild(App.el("p",null,U.reading.text));
  s.appendChild(App.el("p","prompt","<b>True (T) or False (F)?</b>"));
  const qs=[];
  U.reading.questions.forEach((q,i)=>{
    const [text,val]=q;
    const qd=App.el("div","q");
    qd.innerHTML=`<div class="prompt">${i+1}. ${text}</div>
      <div class="opts"><label><input type="radio" name="rf${i}" value="T"> True</label>
      <label><input type="radio" name="rf${i}" value="F"> False</label></div>`;
    s.appendChild(qd); qs.push([i,val]);
  });
  const r=App.el("span","result");
  const b=checkBtn(()=>{ let ok=0; qs.forEach(([i,val])=>{ const sel=s.querySelector(`input[name=rf${i}]:checked`);
    const want= val?"T":"F";
    s.querySelectorAll(`input[name=rf${i}]`).forEach(inp=>{ inp.parentElement.classList.remove("ok","bad");
      if(inp.value===want) inp.parentElement.classList.add("ok"); else if(inp.checked) inp.parentElement.classList.add("bad"); });
    if(sel && sel.value===want) ok++; });
    r.innerHTML=`<span class="${ok===qs.length?'ok':'bad'}">${ok}/${qs.length} đúng</span>`; });
  const row=App.el("div","row"); row.append(b,r); s.appendChild(row);
  return s;
}

/* G — writing */
function secG(U){
  const s=section("G","Writing — Viết");
  const W=U.writing;
  s.appendChild(App.el("p","prompt",`<b>${W.prompt}</b> <i>(${W.prompt_vi})</i>`));
  if(W.questions && W.questions.length){
    s.appendChild(App.el("p","hint","Trả lời các câu hỏi gợi ý sau để viết thành đoạn:"));
    const ol=App.el("div","guide");
    W.questions.forEach((q,i)=>{
      ol.innerHTML += `<div class="guideq">${i+1}. ${q[0]} <span class="cvi">(${q[1]})</span></div>`;
    });
    s.appendChild(ol);
  }
  if(W.grammar_reminder_vi) s.appendChild(App.el("p","note show","💡 "+W.grammar_reminder_vi));
  const ta=App.el("textarea"); ta.placeholder="Viết ở đây..."; s.appendChild(ta);
  const model=App.el("div","model",`<b>Bài mẫu:</b> ${U.writing.model}`);
  const b=App.el("button","btn ghost","Xem bài mẫu"); b.onclick=()=>model.classList.toggle("show");
  const row=App.el("div","row"); row.appendChild(b); s.appendChild(row); s.appendChild(model);
  return s;
}

/* utils */
function shuffle(arr,seed){ let s=seed||1; const rnd=()=>{ s=(s*9301+49297)%233280; return s/233280; };
  for(let i=arr.length-1;i>0;i--){ const j=Math.floor(rnd()*(i+1)); [arr[i],arr[j]]=[arr[j],arr[i]]; } return arr; }
function setBack(show){ const b=document.getElementById("backBtn"); if(b) b.style.display=show?"inline-block":"none"; }

boot();
