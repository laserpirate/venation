/* vena-shell v01 (served as vena-shell.js): group collapse memory, per-group reset buttons, the second rail at 1500 px and up,
   the sticky height on narrow screens, and a layout audit for the headless proof. One global: VSHELL. No storage APIs. */
(function(){
'use strict';
const S={opts:null,open:{},home:[]};
function q(s,r){return (r||document).querySelector(s)}
function qa(s,r){return Array.from((r||document).querySelectorAll(s))}
function decorate(d){if(d.dataset.vsh)return;d.dataset.vsh='1';const s=d.querySelector(':scope>summary');if(!s)return;
 if(!s.querySelector('.gname')){const t=document.createElement('span');t.className='gname';while(s.firstChild)t.appendChild(s.firstChild);s.appendChild(t)}
 const c=document.createElement('span');c.className='gchg';c.id='gchg_'+d.id;s.appendChild(c);
 if(d.dataset.noreset===undefined&&S.opts.groupReset){const b=document.createElement('button');b.type='button';b.className='gr';b.textContent='reset';b.title='restore this group to the loaded study';
  b.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();S.opts.groupReset(d.id)});s.appendChild(b)}
 S.open[d.id]=d.open;d.addEventListener('toggle',()=>{S.open[d.id]=d.open})}
function place(){const r1=q('#rail'),r2=q('#rail2');if(!r1)return;const wide2=window.matchMedia('(min-width:1500px)').matches;
 (S.opts.overflow||[]).forEach(id=>{const g=document.getElementById(id);if(!g)return;const h=S.home.find(x=>x.id===id);
  if(wide2&&r2){if(g.parentNode!==r2)r2.appendChild(g)}else if(h&&g.parentNode!==h.parent){h.parent.insertBefore(g,h.mark)}});
 /* keep the overflow groups in their listed order in rail 2 */
 if(wide2&&r2)(S.opts.overflow||[]).forEach(id=>{const g=document.getElementById(id);if(g)r2.appendChild(g)});
 qa('details.grp').forEach(d=>{if(d.id in S.open)d.open=S.open[d.id]});stick()}
function stick(){const st=q('.stage');if(!st)return;const narrow=window.matchMedia('(max-width:1099.98px)').matches;
 document.documentElement.style.setProperty('--vsh-stick',narrow?(Math.ceil(st.getBoundingClientRect().height)+8)+'px':'0px')}
function init(o){S.opts=o||{};qa('details.grp').forEach(decorate);
 (S.opts.overflow||[]).forEach(id=>{const g=document.getElementById(id);if(!g)return;const m=document.createComment('home '+id);g.parentNode.insertBefore(m,g);S.home.push({id,parent:g.parentNode,mark:m})});
 place();window.matchMedia('(min-width:1500px)').addEventListener('change',place);window.matchMedia('(max-width:1099.98px)').addEventListener('change',place);
 const st=q('.stage');if(st&&window.ResizeObserver)new ResizeObserver(stick).observe(st);window.addEventListener('resize',stick)}
/* changed count per group, shown on its summary line */
function marks(counts){Object.keys(counts).forEach(id=>{const e=document.getElementById('gchg_'+id);if(e)e.textContent=counts[id]?counts[id]+' changed':''})}
function remember(){qa('details.grp').forEach(d=>{S.open[d.id]=d.open})}
/* layout audit for the proof: (a) the drawing box share inside the viewport with each rail scrolled to its last control,
   (b) every control can be scrolled into view inside its rail (wide) or the page (narrow), clear of the sticky drawing */
function vis(r){const w=Math.max(0,Math.min(r.right,innerWidth)-Math.max(r.left,0)),h=Math.max(0,Math.min(r.bottom,innerHeight)-Math.max(r.top,0));const a=r.width*r.height;return a>0?w*h/a:0}
function audit(){const out={w:innerWidth,h:innerHeight,controls:0,fails:[],drawing:null,afterLast:[],pageScroll:0,tolerance_px:2};const keep={};const TOL=2;
 window.scrollTo(0,0);qa('details.grp').forEach(d=>{keep[d.id]=d.open;d.open=true});const VW=document.documentElement.clientWidth,VH=document.documentElement.clientHeight;
 const dr=q('[data-drawing]');const narrow=window.matchMedia('(max-width:1099.98px)').matches;
 const rails=qa('#rail,#rail2').filter(r=>r.offsetParent!==null||getComputedStyle(r).display!=='none');
 rails.forEach(r=>{const ctl=qa('input,select,button,textarea',r).filter(e=>e.offsetParent!==null&&e.getClientRects().length);
  ctl.forEach(e=>{out.controls++;e.scrollIntoView({block:'nearest',inline:'nearest'});const b=e.getBoundingClientRect();const rr=r.getBoundingClientRect();
   let ok=b.top>=-TOL&&b.bottom<=VH+TOL&&b.left>=-TOL&&b.right<=VW+TOL;
   if(!narrow)ok=ok&&b.top>=rr.top-TOL&&b.bottom<=rr.bottom+TOL;
   if(narrow){const sb=q('.stage').getBoundingClientRect();if(b.top<sb.bottom-TOL&&b.bottom>sb.top)ok=false}
   if(!ok)out.fails.push({id:e.id||e.name||e.textContent.slice(0,30),top:Math.round(b.top),bottom:Math.round(b.bottom)})});
  if(ctl.length){const last=ctl[ctl.length-1];last.scrollIntoView({block:'nearest'});if(!narrow)r.scrollTop=r.scrollHeight;
   const d=dr.getBoundingClientRect();out.afterLast.push({rail:r.id,last:last.id||last.textContent.slice(0,30),drawingInView:+vis(d).toFixed(3),drawing:[Math.round(d.left),Math.round(d.top),Math.round(d.width),Math.round(d.height)],pageScrollY:Math.round(scrollY)})}});
 out.drawing=dr?[Math.round(dr.getBoundingClientRect().width),Math.round(dr.getBoundingClientRect().height)]:null;
 out.hscroll=document.documentElement.scrollWidth-innerWidth;
 Object.keys(keep).forEach(id=>{const d=document.getElementById(id);if(d)d.open=keep[id]});return out}
window.VSHELL={init,place,marks,remember,audit,state:S};
})();
