"""make_land_page_v02.py : land_page_v02.src.html = land_page_v01.src.html plus ADD-2 (form and fill, three more fills, grading readouts).
v01 stays beside it. Each replacement is asserted to match exactly once. Run from the project root. No em dashes."""
import io
s = io.open('00_src/land_page_v01.src.html', encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)


def cut(a, b, new):
    """replace from the start of a up to (not including) b"""
    global s
    assert s.count(a) == 1 and s.count(b) >= 1, (s.count(a), s.count(b), a[:60], b[:60]); i = s.index(a); j = s.index(b, i); s = s[:i] + new + s[j:]


rep('<title>Venation Land v01</title>', '<title>Venation Land v02</title>')
rep("const VERSION='land v01';", "const VERSION='land v02';")
rep('<span class="sub">v01 · the four VS08 landform rules on a tile · pattern from the Lab engine</span>', '<span class="sub">v02 · a form, a profile and a pattern fill on a tile · the VS08 rules, the Lab engine</span>')
rep("const TYPNAME={berm:'berm',wave:'waveform mounds',pond:'pond cells',terr:'terraces'};", "const TYPNAME={berm:'berm',swale:'swales',wave:'waveform mounds',pond:'pond cells',terr:'terraces'};\nconst TYPLABEL={berm:'edges as ridges (berm)',swale:'edges as swales',wave:'cells as mounds (waveform mounds)',pond:'cells as basins (pond cells)',terr:'distance bands as terraces (terraces)'};\nconst NEWMODE=['xylem','radiolaria','delaunay'];")
rep("{id:'typ',g:'top',label:'Typology',type:'select',opts:Object.keys(TYPNAME).map(k=>[k,TYPNAME[k]]),def:'berm'}", "{id:'typ',g:'top',label:'Fill as relief (typology)',type:'select',opts:Object.keys(TYPLABEL).map(k=>[k,TYPLABEL[k]]),def:'berm'}")
rep("{id:'gain',g:'top',label:'Relief gain',", "{id:'gain',g:'top',label:'Relief gain (fill relief)',")
rep("{id:'src',g:'Pattern',label:'Source study',", "{id:'src',g:'Fill pattern',label:'Stored study by ID',")
rep("{id:'mode',g:'Pattern',label:'Mode',type:'select',opts:[['open','open'],['closed','closed'],['hybrid','hybrid'],['cells','cells']],re:1}", "{id:'mode',g:'Fill pattern',label:'Fill pattern',type:'select',opts:[['open','venation, open'],['closed','venation, closed'],['xylem','xylem'],['cells','Voronoi cells'],['radiolaria','radiolaria'],['delaunay','Delaunay'],['hybrid','hybrid: veins and cells']],re:1}")
rep("{id:'shape',g:'Pattern',label:'Outline',", "{id:'shape',g:'Fill pattern',label:'Outline the pattern grows in',")
rep("{id:'seed',g:'Pattern',label:'Seed',", "{id:'seed',g:'Fill pattern',label:'Seed',")
rep(" {id:'nsrc',g:'Cells and veins',", " {id:'rround',g:'Cells and veins',label:'Radiolaria: rounding passes (0 = plain weighted cells)',min:0,max:3,step:1,re:1,def:2},\n {id:'dprune',g:'Cells and veins',label:'Delaunay: drop edges over n x the median (0 = off)',min:0,max:4,step:.1,re:1,def:0},\n {id:'nsrc',g:'Cells and veins',")
FORM = """ {id:'form',g:'Form',label:'Plan shape',type:'select',opts:[['study','the study outline'],['square','square'],['rectangle','rectangle'],['triangle','triangle'],['circle','circle'],['oval','oval'],['tile','the whole tile (the ground extent)']],def:'study'},
 {id:'fw',g:'Form',fg:1,label:'Width (percent of the tile)',min:10,max:100,step:1,def:80},
 {id:'fl',g:'Form',fg:1,label:'Length (percent of the tile)',min:10,max:100,step:1,def:80},
 {id:'frad',g:'Form',fg:1,label:'Corner radius (percent of the short side)',min:0,max:100,step:1,def:0},
 {id:'frot',g:'Form',label:'Rotation (deg): the form and the profile axis',min:0,max:180,step:1,def:0},
 {id:'prof',g:'Form',label:'Landform profile',type:'select',opts:[['none','none: flat'],['berm','berm'],['mound','mound'],['terrace','terrace'],['pond','pond']],def:'none'},
 {id:'shift',g:'Form',label:'Form level shift (mm)',min:-40,max:40,step:.05,def:0},
 {id:'qL',g:'Form',pf:'berm',label:'Berm length (percent of the form length)',min:10,max:100,step:1,def:90},
 {id:'qcw',g:'Form',pf:'berm',label:'Berm crest width (mm)',min:0,max:40,step:.5,def:6},
 {id:'qh',g:'Form',pf:'berm',label:'Berm height (mm)',min:0,max:40,step:.5,def:10},
 {id:'qs1',g:'Form',pf:'berm',label:'Berm side slope, side A, 1:n',min:.5,max:8,step:.1,def:2},
 {id:'qs2',g:'Form',pf:'berm',label:'Berm side slope, side B, 1:n',min:.5,max:8,step:.1,def:3},
 {id:'mh',g:'Form',pf:'mound',label:'Mound height (mm)',min:0,max:40,step:.5,def:12},
 {id:'msharp',g:'Form',pf:'mound',label:'Dome sharpness',min:.5,max:6,step:.1,def:2},
 {id:'mflat',g:'Form',pf:'mound',label:'Flat top share',min:0,max:.9,step:.05,def:.2},
 {id:'zn',g:'Form',pf:'terrace',label:'Terrace steps',min:1,max:12,step:1,def:4},
 {id:'ztread',g:'Form',pf:'terrace',label:'Terrace tread (mm)',min:2,max:40,step:.5,def:12},
 {id:'zriser',g:'Form',pf:'terrace',label:'Terrace riser (mm)',min:.25,max:10,step:.25,def:2.5},
 {id:'dd',g:'Form',pf:'pond',label:'Pond depth (mm)',min:0,max:30,step:.5,def:8},
 {id:'dbank',g:'Form',pf:'pond',label:'Pond bank slope, 1:n',min:.5,max:8,step:.1,def:2},
 {id:'dbot',g:'Form',pf:'pond',label:'Pond bottom share',min:0,max:.9,step:.05,def:.4},
 {id:'dfree',g:'Form',pf:'pond',label:'Pond freeboard (mm)',min:0,max:10,step:.25,def:1.5},
 {id:'ew',g:'Fill relief',label:'Edge width, times the rule',min:.5,max:5,step:.1,def:1},
 {id:'fall',g:'Fill relief',label:'Fall-off toward the form edge (share of its depth)',min:0,max:1,step:.05,def:0},
 {id:'follow',g:'Fill relief',label:'Fill follows the profile slope (off: cells stay level)',type:'check',def:1},
"""
rep(" {id:'bhmin',g:'Typology',t:'berm',", FORM + " {id:'bhmin',g:'Typology',t:'berm',")
rep("g:'Typology',", "g:'Fill relief',", 18)
rep(" {id:'mask',g:'Ground',label:'Mask the pattern to the study outline',type:'check',def:1},\n", "")
rep("{id:'fit',g:'Ground',label:'Pattern size, percent of the tile',min:30,max:250,step:1,def:94}", "{id:'fit',g:'Fill pattern',label:'Pattern size, percent of the form (study outline: of the tile)',min:30,max:300,step:1,def:94}")
rep(" {id:'wl',g:'Water',", """ {id:'map',g:'Grading',label:'Map on the surface',type:'select',opts:[['none','none'],['slope','slope, three bands'],['aspect','aspect'],['elev','elevation bands']],def:'none'},
 {id:'s1',g:'Grading',label:'Slope threshold 1 (percent)',min:0,max:100,step:.5,def:5},
 {id:'s2',g:'Grading',label:'Slope threshold 2 (percent)',min:0,max:200,step:.5,def:33},
 {id:'bandh',g:'Grading',label:'Elevation band height (mm on the tile)',min:.25,max:10,step:.25,def:2},
 {id:'smo',g:'Grading',label:'Smoothing passes on the final surface',min:0,max:12,step:1,def:1},
 {id:'wl',g:'Water',""")
rep("const PAT=['mode','shape','veinset','wingpass','nde','preset','seed','nsrc','birth','kill','step','iters','ana','costb','tipb','mur','tip','maxw','ncell','grad','costal','lloyd','cw'];", "const PAT=['mode','shape','veinset','wingpass','nde','preset','seed','nsrc','birth','kill','step','iters','ana','costb','tipb','mur','tip','maxw','ncell','grad','costal','lloyd','cw','rround','dprune'];")
rep("const o={};PAT.forEach(k=>o[k]=p[k]);o.nde=String(o.nde);return o}", "const o={};PAT.forEach(k=>o[k]=p[k]!==undefined?p[k]:PID[k].def);o.nde=String(o.nde);return o}")
rep("const GROUPS=['Pattern','Cells and veins','Relief and contours','Typology','Ground','Scale','Water','Export','Pattern, more from the Lab'];", "const GROUPS=['Fill pattern','Cells and veins','Form','Fill relief','Relief and contours','Ground','Scale','Grading','Water','Export','Pattern, more from the Lab'];")
rep("  if(g==='Export'){", """  if(g==='Scale'){const x=document.createElement('p');x.className='note';x.textContent='Slope, aspect, elevation bands, cut and fill, spot elevations and grades are drawing aids on a pattern study. They show when a scale is set.';b.appendChild(x)}
  if(g==='Grading'){const x=document.createElement('div');x.innerHTML='<div class="btns"><button id="balance">Balance cut and fill</button><button id="clearspots">Clear spot elevations</button></div><p class="note" id="gstate">Click the plan to drop a spot elevation; drag to set the section line.</p><div class="key" id="mapkey"></div>';while(x.firstChild)b.appendChild(x.firstChild)}
  if(g==='Export'){""")
rep("function showTyp(){PR.forEach(p=>{if(p.t)$('row_'+p.id).style.display=p.t===V.typ?'':'none'});$('g_Typology').open=true}", "const GEO=['square','rectangle','triangle','circle','oval'];\nfunction showTyp(){PR.forEach(p=>{if(p.t)$('row_'+p.id).style.display=(p.t===V.typ||(p.t==='berm'&&V.typ==='swale'))?'':'none';if(p.pf)$('row_'+p.id).style.display=p.pf===V.prof?'':'none';if(p.fg)$('row_'+p.id).style.display=GEO.includes(V.form)?'':'none'});$('row_s1').style.display=$('row_s2').style.display=V.map==='slope'?'':'none';$('row_bandh').style.display=V.map==='elev'?'':'none'}")
rep("function hints(){const nc=V.mode==='open'||V.mode==='closed';", "function hints(){const nc=V.mode==='open'||V.mode==='closed'||V.mode==='xylem';$('hint_rround').textContent=V.mode==='radiolaria'?'':'used by radiolaria only';$('hint_dprune').textContent=V.mode==='delaunay'?'':'used by Delaunay only';$('hint_follow').textContent=(V.typ==='wave'||V.typ==='pond')?'':'edges and bands always follow the profile';$('hint_frad').textContent=(V.form==='circle'||V.form==='oval')?'not used by this shape':'';")
rep("const nv=V.mode==='cells'&&!isWing(V.shape);", "const nv=(V.mode==='cells'||V.mode==='radiolaria'||V.mode==='delaunay')&&!isWing(V.shape);")
rep("function loadTile(aid){const m=/^vena-land-(berm|wave|pond|terr)--[a-z]+-(VS\\d\\d-\\d\\d)__/.exec(aid);if(!m)return;loadSource(m[2],m[1]);", "function loadTile(aid){const m=/^vena-land-(berm|wave|pond|terr)--[a-z]+-(VS\\d\\d-\\d\\d)__/.exec(aid);if(!m)return;SPOTS.length=0;loadSource(m[2],m[1]);if(m[1]==='terr'){stored.smo=0;setV('smo',0)}")
rep("function patName(){return PATNAME[V.src]", "function patName(){if(NEWMODE.includes(V.mode))return V.mode;return PATNAME[V.src]")
# pattern: edges of the new modes
rep(" const cellsP=cellPolys(res);const veinCount=segs.length;", " const cellsP=cellPolys(res);if(res.extra==='delaunay')segs.forEach(s=>{s[4]=s[5]=.5});const veinCount=segs.length;")
rep(" if(!veinCount||cellsP.length>200){", " if(res.extra==='radiolaria'){const wl=res.cel.walls;const ar=wl.map(c=>Math.abs(area(c)));const top=ar.slice().sort((a,b)=>a-b)[Math.floor(ar.length*.9)]||1;wl.forEach((c,ci)=>{const wv=.15+.6*(1-Math.min(1,Math.sqrt(ar[ci]/top)));for(let i=0;i<c.length;i++){const a=c[i],b=c[(i+1)%c.length];segs.push([a[0],a[1],b[0],b[1],wv,wv])}})}\n else if(!veinCount||cellsP.length>200){")
rep("if(ws.length){const s=Float64Array.from(ws).sort();", "if(ws.length&&res.extra!=='delaunay'){const s=Float64Array.from(ws).sort();")

# ---- the field: form, profile, fill, ground, grading
NEWFIELD = r"""function fitT(res){const o=res.poly;const b0=bbox(o);const c=[(b0[0]+b0[2])/2,(b0[1]+b0[3])/2];const rot=((b0[2]-b0[0])/(b0[3]-b0[1])>2.5)?Math.PI/4:0;const co=Math.cos(rot),sn=Math.sin(rot);
 const R=q=>[(q[0]-c[0])*co-(q[1]-c[1])*sn,(q[0]-c[0])*sn+(q[1]-c[1])*co];const b=bbox(o.map(R));const ref=GEO.includes(V.form)?Math.max(V.fw,V.fl)/100*V.tile:V.tile;const s=(V.fit/100)*ref/Math.max(b[2]-b[0],b[3]-b[1]);const c2=[(b[0]+b[2])/2,(b[1]+b[3])/2];
 const f=q=>{const r=R(q);return[(r[0]-c2[0])*s+V.tile/2,(r[1]-c2[1])*s+V.tile/2]};f.s=s;f.rot=rot*180/Math.PI;return f}
const mcv=document.createElement('canvas');mcv.width=mcv.height=NG;const mctx=mcv.getContext('2d',{willReadFrequently:true});
function formMask(n,cs,outl){const inside=new Uint8Array(n*n);const F=V.form;if(F==='tile'){inside.fill(1);return inside}
 mctx.setTransform(1,0,0,1,0,0);mctx.clearRect(0,0,n,n);mctx.fillStyle='#000';mctx.strokeStyle='#000';mctx.beginPath();
 if(F==='study'){outl.forEach((q,i)=>i?mctx.lineTo(q[0]/cs,q[1]/cs):mctx.moveTo(q[0]/cs,q[1]/cs));mctx.closePath();mctx.fill()}
 else{const w=V.fw/100*n,l=V.fl/100*n;mctx.translate(n/2,n/2);mctx.rotate(V.frot*Math.PI/180);
  if(F==='circle'||F==='oval'){const rx=F==='circle'?Math.min(w,l)/2:w/2,ry=F==='circle'?Math.min(w,l)/2:l/2;mctx.ellipse(0,0,rx,ry,0,0,7);mctx.fill()}
  else if(F==='triangle'){const r=V.frad/100*Math.min(w,l)/4;const a=w/2-r,b=l/2-r;mctx.moveTo(0,-b);mctx.lineTo(a,b);mctx.lineTo(-a,b);mctx.closePath();mctx.fill();if(r>0){mctx.lineJoin='round';mctx.lineWidth=2*r;mctx.stroke()}}
  else{const ww=F==='square'?Math.min(w,l):w,ll=F==='square'?Math.min(w,l):l;const r=V.frad/100*Math.min(ww,ll)/2;mctx.roundRect(-ww/2,-ll/2,ww,ll,r);mctx.fill()}
  mctx.setTransform(1,0,0,1,0,0)}
 const im=mctx.getImageData(0,0,n,n).data;for(let i=0;i<n*n;i++)inside[i]=im[i*4+3]>127?1:0;return inside}
function computeField(opt){opt=opt||{};const shift=opt.shift!=null?opt.shift:V.shift;const n=NG,T=V.tile,cs=T/n,tf=fitT(pat.res),K=16,N2=n*n;const span=Math.max(.1,V.hi-V.lo);
 const cls=new Uint8Array(N2);const segT=[];
 for(const s of pat.segs){const a=tf([s[0],s[1]]),b=tf([s[2],s[3]]);segT.push([a[0],a[1],b[0],b[1],s[4],s[5]]);const L=Math.hypot(b[0]-a[0],b[1]-a[1]);const m=Math.max(1,Math.ceil(L/(cs*.5)));
  for(let t=0;t<=m;t++){const u=t/m;const i=Math.floor((a[0]+(b[0]-a[0])*u)/cs),j=Math.floor((a[1]+(b[1]-a[1])*u)/cs);if(i<0||j<0||i>=n||j>=n)continue;const k=1+Math.round((s[4]+(s[5]-s[4])*u)*(K-1));if(k>cls[j*n+i])cls[j*n+i]=k}}
 const outl=pat.res.poly.map(tf);const inside=formMask(n,cs,outl);
 /* depth into the form: distance from its edge (the whole tile: from the tile edge) */
 let dE;if(V.form==='tile'){dE=new Float32Array(N2);for(let j=0;j<n;j++)for(let i=0;i<n;i++)dE[j*n+i]=(Math.min(i,j,n-1-i,n-1-j)+.5)*cs}else{const nf0=new Uint8Array(N2);for(let i=0;i<N2;i++)nf0[i]=inside[i]?0:1;dE=edt(nf0,n);for(let i=0;i<N2;i++)dE[i]=inside[i]?Math.min(dE[i]*cs,T):0}
 let dEmax=1e-6,nin=0;for(let i=0;i<N2;i++){if(inside[i]){nin++;if(dE[i]>dEmax)dEmax=dE[i]}}
 const any=new Uint8Array(N2);for(let i=0;i<N2;i++)any[i]=cls[i]?1:0;const dAny=edt(any,n);for(let i=0;i<N2;i++)dAny[i]*=cs;
 const r=new Float32Array(N2);let nl=0;const typ=V.typ;let notches=[];let outside=0;let labG=null;const ew=V.ew;
 if(typ==='berm'||typ==='swale'){/* as VS08: each point takes the ridge of its nearest vein (ties within one cell take the higher) */const dmin=new Float32Array(N2).fill(1e9);for(let k=1;k<=K;k++){const mk=new Uint8Array(N2);let c=0;for(let i=0;i<N2;i++)if(cls[i]===k){mk[i]=1;c++}if(!c)continue;const d=edt(mk,n);const wn=(k-1)/(K-1);
   const h=V.bhmin+(V.bhmax-V.bhmin)*Math.pow(wn,V.bexp),half=(V.bcrest*ew/2)*(1/3+2/3*wn);for(let i=0;i<N2;i++){const dd=d[i]*cs;const v=h-Math.max(dd-half,0)/V.bslope;if(dd<dmin[i]-cs*.75){dmin[i]=dd;r[i]=v}else if(dd<dmin[i]+cs*.75){if(dd<dmin[i])dmin[i]=dd;if(v>r[i])r[i]=v}}}
  if(typ==='swale')for(let i=0;i<N2;i++)r[i]=-Math.max(0,r[i])}
 else if(typ==='terr'){const thr=V.tord==='prim'?.5:V.tord==='sec'?.25:0;const mk=new Uint8Array(N2);let c=0;const kmin=1+Math.ceil(thr*(K-1)-1e-9);for(let i=0;i<N2;i++)if(cls[i]>=kmin&&cls[i]>0){mk[i]=1;c++}
  let d=dAny;if(c>10&&thr>0){d=edt(mk,n);for(let i=0;i<N2;i++)d[i]*=cs}for(let i=0;i<N2;i++)r[i]=span-V.triser*Math.floor(d[i]/V.ttread)}
 else{const half=Math.max((typ==='wave'?V.wsw:V.pcrest)*ew/2,.75*cs);const free=new Uint8Array(N2);for(let i=0;i<N2;i++)free[i]=(dAny[i]>=half&&inside[i])?1:0;
  const L=label4(free,n);nl=L.nl;labG=L.lab;const nf=new Uint8Array(N2);for(let i=0;i<N2;i++)nf[i]=free[i]?0:1;const e=edt(nf,n);const em=new Float32Array(nl+1);
  for(let i=0;i<N2;i++){const l=L.lab[i];if(l){e[i]*=cs;if(e[i]>em[l])em[l]=e[i]}}
  const kk=typ==='wave'?V.wk:V.pk,mx=typ==='wave'?V.wmax:V.pmax;const A=new Float32Array(nl+1);for(let l=1;l<=nl;l++)A[l]=Math.max(Math.min(1,mx),Math.min(mx,kk*em[l]));
  if(typ==='wave'){for(let i=0;i<N2;i++){const l=L.lab[i];if(l){const u=Math.min(1,e[i]/Math.max(em[l],1e-6));r[i]=V.wsd+A[l]*(1-Math.cos(Math.PI*u))/2}else{const q=Math.min(1,dAny[i]/half);r[i]=V.wsd*q*q}}}
  else{outside=(V.form==='study'&&V.prof==='none')?V.pdike:0;for(let i=0;i<N2;i++){const l=L.lab[i];if(l){const u=Math.min(1,e[i]/Math.max(em[l],1e-6));r[i]=V.pdike-A[l]*(1-Math.cos(Math.PI*u))/2}else r[i]=V.pdike}
   if(V.pnotch&&nl>1){/* each basin gets one notch toward its lowest lower neighbour: nearest label spread into the dikes, then the shared boundary */
    const near=Int32Array.from(L.lab);let q=[];for(let i=0;i<N2;i++)if(near[i])q.push(i);for(let it=0;it<40&&q.length;it++){const nq=[];for(const c of q){const x=c%n,y=(c-x)/n;const tr=d=>{if(!near[d]&&inside[d]){near[d]=near[c];nq.push(d)}};if(x>0)tr(c-1);if(x<n-1)tr(c+1);if(y>0)tr(c-n);if(y<n-1)tr(c+n)}q=nq}
    const pairs=new Map();const add=(a,b,c)=>{if(!a||!b||a===b)return;const k=a*(nl+1)+b;let p=pairs.get(k);if(!p){p=[];pairs.set(k,p)}p.push(c)};
    for(let y=0;y<n;y++)for(let x=0;x<n;x++){const c=y*n+x;if(x<n-1){add(near[c],near[c+1],c);add(near[c+1],near[c],c)}if(y<n-1){add(near[c],near[c+n],c);add(near[c+n],near[c],c)}}
    const best=new Map();pairs.forEach((cells,k)=>{const a=Math.floor(k/(nl+1)),b=k%(nl+1);if(A[b]>A[a]+1e-6){const cur=best.get(a);if(!cur||A[b]>A[cur.b])best.set(a,{b,cells})}});
    best.forEach((o,a)=>{const c=o.cells[o.cells.length>>1];notches.push([c%n,(c-c%n)/n,a,o.b])})}}}
 /* the profile: the large shape, on local axes turned by the form rotation (u across, v along) */
 const P=new Float32Array(N2);const pk=V.prof;const pinfo={};const th=V.frot*Math.PI/180,co=Math.cos(th),sn=Math.sin(th);let u0=1e9,u1=-1e9,v0=1e9,v1=-1e9;
 for(let j=0;j<n;j++)for(let i=0;i<n;i++){if(!inside[j*n+i])continue;const x=(i+.5)*cs-T/2,y=(j+.5)*cs-T/2;const u=x*co+y*sn,v=-x*sn+y*co;if(u<u0)u0=u;if(u>u1)u1=u;if(v<v0)v0=v;if(v>v1)v1=v}
 if(!nin){u0=v0=-T/2;u1=v1=T/2}const uc=(u0+u1)/2,vc=(v0+v1)/2,Lu=u1-u0+cs,Lv=v1-v0+cs;pinfo.ext=[Lu,Lv];
 if(pk!=='none'){const mfl=Math.min(.95,V.mflat);const dB=Math.max(cs,(1-V.dbot)*dEmax);for(let j=0;j<n;j++)for(let i=0;i<n;i++){const c=j*n+i;if(!inside[c])continue;const x=(i+.5)*cs-T/2,y=(j+.5)*cs-T/2;const u=x*co+y*sn,v=-x*sn+y*co;
   if(pk==='berm'){const du=Math.abs(u-uc),dv=Math.max(Math.abs(v-vc)-V.qL/100*Lv/2,0);const d=dv>0?Math.hypot(du,dv):du;P[c]=Math.max(0,V.qh-Math.max(d-V.qcw/2,0)/((u-uc)<0?V.qs1:V.qs2))}
   else if(pk==='mound'){const s=Math.min(1,(dE[c]/dEmax)/(1-mfl));P[c]=V.mh*(1-Math.pow(1-s,V.msharp))}
   else if(pk==='terrace'){const k=Math.min(V.zn,Math.floor((v-v0)/V.ztread));P[c]=(V.zn-k)*V.zriser}
   else{P[c]=-Math.min(V.dd,Math.min(dE[c],dB)/V.dbank)}}
  if(pk==='terrace'){pinfo.fall=V.zn*V.zriser;pinfo.run=Math.min(Lv,V.zn*V.ztread)}if(pk==='pond'){pinfo.depth=Math.min(V.dd,dB/V.dbank);pinfo.full=V.lo+shift-V.dfree}}
 let Pb=P;if(!V.follow&&labG&&pk!=='none'){/* level: every cell of the fill stands on the mean profile height under it */const sm=new Float64Array(nl+1),ct=new Int32Array(nl+1);for(let i=0;i<N2;i++){const l=labG[i];if(l){sm[l]+=P[i];ct[l]++}}Pb=new Float32Array(P);for(let i=0;i<N2;i++){const l=labG[i];if(l)Pb[i]=sm[l]/ct[l]}}
 /* relief, ground, blend */
 const z=new Float32Array(N2),base=new Float32Array(N2);const b=V.blend,gain=V.gain;const useFile=V.ground==='file'&&fileG;const fd=V.fall>0?Math.max(cs,V.fall*dEmax):0;
 for(let j=0;j<n;j++)for(let i=0;i<n;i++){const c=j*n+i;const g=useFile?fileG.g[c]:groundAt((i+.5)/n,(j+.5)/n);base[c]=V.lo+b*V.grel*g;let add;
  if(inside[c]){const fo=fd?sstep(0,fd,dE[c]):1;add=Pb[c]+shift+gain*fo*Math.max(typ==='swale'?-span:0,Math.min(span,r[c]))}else add=gain*Math.min(span,outside);z[c]=Math.max(0,base[c]+(1-b)*add)}
 let smax=0;if(V.smo>0){const z0=new Float32Array(z);const t=new Float32Array(N2);for(let p=0;p<V.smo;p++){for(let j=0;j<n;j++)for(let i=0;i<n;i++){const a=i>0?i-1:i,c=i<n-1?i+1:i;t[j*n+i]=(z[j*n+a]+2*z[j*n+i]+z[j*n+c])/4}
   for(let j=0;j<n;j++){const a=(j>0?j-1:j)*n,c=(j<n-1?j+1:j)*n;for(let i=0;i<n;i++)z[j*n+i]=(t[a+i]+2*t[j*n+i]+t[c+i])/4}}for(let i=0;i<N2;i++){const d=Math.abs(z[i]-z0[i]);if(d>smax)smax=d}}
 if(notches.length){const lev=V.lo+(1-b)*gain*Math.max(0,V.pdike-V.pnl);const rn=Math.ceil((V.pcrest*ew/2+1.5)/cs);notches.forEach(([x,y])=>{for(let dy=-rn;dy<=rn;dy++)for(let dx=-rn;dx<=rn;dx++){if(dx*dx+dy*dy>rn*rn)continue;const xx=x+dx,yy=y+dy;if(xx<0||yy<0||xx>=n||yy>=n)continue;const c=yy*n+xx;const l2=lev+(1-b)*(Pb[c]+shift);if(z[c]>l2)z[c]=Math.max(0,l2)}})}
 /* derived numbers */
 let zmin=1e9,zmax=-1e9,cutV=0,fillV=0;for(let i=0;i<N2;i++){if(z[i]<zmin)zmin=z[i];if(z[i]>zmax)zmax=z[i];const d=z[i]-base[i];if(d>0)fillV+=d;else cutV-=d}cutV*=cs*cs;fillV*=cs*cs;
 if(opt.quick)return{net:fillV-cutV,cut:cutV,fill:fillV};
 const slp=new Float32Array(N2),asp=new Float32Array(N2);const sl=[];let smx=0,smi=0;for(let j=0;j<n;j++)for(let i=0;i<n;i++){const xa=i>0?i-1:i,xb=i<n-1?i+1:i,ya=j>0?j-1:j,yb=j<n-1?j+1:j;const gx=(z[j*n+xb]-z[j*n+xa])/((xb-xa)*cs),gy=(z[yb*n+i]-z[ya*n+i])/((yb-ya)*cs);const s=Math.hypot(gx,gy);slp[j*n+i]=s;asp[j*n+i]=Math.atan2(-gy,-gx);if(s>smx){smx=s;smi=j*n+i}if((i&1)&&(j&1))sl.push(s)}sl.sort((a,b)=>a-b);
 const raised=new Uint8Array(N2),nr=new Uint8Array(N2);for(let i=0;i<N2;i++){raised[i]=z[i]>zmin+.3?1:0;nr[i]=raised[i]?0:1}const d1=edt(nr,n);const er=new Uint8Array(N2);for(let i=0;i<N2;i++)er[i]=(raised[i]&&d1[i]*cs>=1)?1:0;const d2=edt(er,n);let thin=0;for(let i=0;i<N2;i++){if(raised[i]&&d2[i]*cs>1.0+cs*.5)thin++}
 return{z,base,n,cs,T,segT,outl,nl,notches,zmin,zmax,s50:sl[sl.length>>1]||0,s99:sl[Math.floor(sl.length*.99)]||0,thinPct:100*thin/N2,tf,inside,slp,asp,smx,smi,cut:cutV,fill:fillV,smax,pinfo,formArea:nin*cs*cs,dEmax}}
"""
cut("function fitT(res){", "function zAt(f,x,y){", NEWFIELD)

# ---- grading: maps, spots, balance
rep("/* ---------------- caption and readouts ---------------- */", r"""/* ---------------- grading aids: slope, aspect and elevation maps, spot elevations, balance ---------------- */
const veE=()=>V.ve>0?V.ve:1;const scaled=()=>V.scaleN>0;const SPOTS=[];
const RAMP=[[28,33,64],[62,70,107],[139,139,163],[230,222,255]];
function ramp(t){t=Math.max(0,Math.min(1,t))*(RAMP.length-1);const i=Math.min(RAMP.length-2,Math.floor(t)),f=t-i;return[RAMP[i][0]+(RAMP[i+1][0]-RAMP[i][0])*f,RAMP[i][1]+(RAMP[i+1][1]-RAMP[i][1])*f,RAMP[i][2]+(RAMP[i+1][2]-RAMP[i][2])*f]}
const BANDCOL=[[62,70,107],[139,139,163],[230,222,255]];
function makeMap(f){f.map=null;f.bands=null;if(V.map==='none'||!scaled())return;const N2=f.n*f.n;const m=new Uint8ClampedArray(N2*4);const put=(i,c)=>{m[i*4]=c[0];m[i*4+1]=c[1];m[i*4+2]=c[2];m[i*4+3]=235};
 if(V.map==='slope'){const a=Math.min(V.s1,V.s2)/100,b=Math.max(V.s1,V.s2)/100;const cnt=[0,0,0];for(let i=0;i<N2;i++){const s=f.slp[i]/veE();const k=s<=a?0:s<=b?1:2;cnt[k]++;put(i,BANDCOL[k])}f.bands=cnt.map(c=>100*c/N2)}
 else if(V.map==='aspect'){for(let i=0;i<N2;i++){if(f.slp[i]/veE()<.01){put(i,[7,9,14]);continue}put(i,ramp(.5+.5*Math.cos(f.asp[i]+Math.PI/2)))}}
 else{const bh=Math.max(.05,V.bandh);const k0=Math.floor(f.zmin/bh),k1=Math.max(k0+1,Math.floor(f.zmax/bh));for(let i=0;i<N2;i++)put(i,ramp((Math.floor(f.z[i]/bh)-k0)/(k1-k0)))}
 f.map=m}
function mapKey(){const sw=c=>'<svg width="22" height="12"><rect width="22" height="12" fill="rgb('+c.map(Math.round).join(',')+')"/></svg>';let h='';
 if(V.map!=='none'&&!scaled())h='<span>no scale set: the map shows when a scale is set</span>';
 else if(V.map==='slope'){const a=Math.min(V.s1,V.s2),b=Math.max(V.s1,V.s2);h='<span>'+sw(BANDCOL[0])+'slope to '+a+' % (1:'+(a>0?(100/a).toFixed(1):'level')+')</span><span>'+sw(BANDCOL[1])+a+' to '+b+' % (to 1:'+(100/b).toFixed(1)+')</span><span>'+sw(BANDCOL[2])+'over '+b+' %</span>'}
 else if(V.map==='aspect')h='<span>'+sw(ramp(1))+'faces the top of the plan</span><span>'+sw(ramp(.5))+'faces left or right</span><span>'+sw(ramp(0))+'faces the bottom of the plan</span><span>'+sw([7,9,14])+'under 1 %: level</span>';
 else if(V.map==='elev')h='<span>'+sw(ramp(0))+'lowest band</span><span>'+sw(ramp(1))+'highest band</span><span>bands of '+V.bandh+' mm on the tile'+(scaled()?' = '+gH(V.bandh):'')+'</span>';
 if(scaled()&&!(V.ve>0)&&V.map!=='none')h+='<span>vertical exaggeration not set: taken as 1</span>';$('mapkey').innerHTML=h}
function spotLabel(zmm){return scaled()?fm(zmm*V.scaleN/1000/veE())+' m ('+fm(zmm*V.scaleN/1000/veE()*M2FT)+' ft)':f1(zmm)+' mm'}
function balance(){const f=s=>computeField({shift:s,quick:true}).net;let a=-40,b=40;let fa=f(a),fb=f(b);if(fa>0||fb<0){$('gstate').textContent='balance: no level between -40 and +40 mm brings the net to zero (net at -40 mm: '+fm(fa)+' mm3, at +40 mm: '+fm(fb)+' mm3)';return null}
 for(let i=0;i<22;i++){const m=(a+b)/2;const fmid=f(m);if(fmid>0)b=m;else a=m}const s0=V.shift;const s1=Math.round((a+b)/2*20)/20;setV('shift',s1);update();const d=s1-s0;
 $('gstate').textContent='balance: form level shifted by '+(d>=0?'+':'')+d.toFixed(2)+' mm'+(scaled()?' ('+gH(Math.abs(d))+(d<0?' down':' up')+')':'')+'; net now '+fm(fld.fill-fld.cut)+' mm3'+(scaled()?' = '+gVolE(fld.fill-fld.cut):'')+' (the slider steps by 0.05 mm)';return{from:s0,to:s1,net:fld.fill-fld.cut}}
function gVolE(mm3){const k=V.scaleN/1000;const v=mm3*k*k*k/veE();return fm(v)+' m3 ('+fm(v*M2FT*M2FT*M2FT)+' cu ft)'}
function gSlopeE(s){return slopeTxt(s/veE())}

/* ---------------- caption and readouts ---------------- */""")
rep("function capLines(){const ch=changed();const L=[artId(),TYPNAME[V.typ]+' · '+patName()+'-'+srcName(),", "function capLines(){const ch=changed();const L=[artId(),TYPNAME[V.typ]+' · '+patName()+'-'+srcName()+((V.form!=='study'||V.prof!=='none')?' · form '+show(PID.form,V.form)+' · profile '+show(PID.prof,V.prof):''),")
rep(" row('pattern fit',", """ row('form',show(PID.form,V.form)+' · '+f1(f.pinfo.ext[0])+' x '+f1(f.pinfo.ext[1])+' mm across and along its axis · '+fm(f.formArea)+' mm2',gArea(f.formArea),'derived: the plan shape on the grid');
 if(V.prof==='terrace')row('terrace, overall fall',f1(f.pinfo.fall)+' mm over '+f1(f.pinfo.run)+' mm',gH(f.pinfo.fall),'derived: steps x riser, steps x tread');
 if(V.prof==='pond')row('pond',"depth reached "+f1(f.pinfo.depth)+' mm · full level '+f1(f.pinfo.full)+' mm above the tile floor',gH(f.pinfo.depth),'derived: bank slope and bottom share; full level = rim less freeboard');
 if(V.smo>0)row('smoothing','largest change '+f2(f.smax)+' mm',gH(f.smax),'derived: '+V.smo+' passes of a 3 x 3 mean on the final surface');
 const ns='no scale set';const veNote=(V.ve>0)?'':' (vertical exaggeration not set: taken as 1)';
 row('cut against the ground',scaled()?fm(f.cut)+' mm3':ns,scaled()?gVolE(f.cut):ns,'derived: surface under the chosen ground, summed'+veNote);
 row('fill against the ground',scaled()?fm(f.fill)+' mm3':ns,scaled()?gVolE(f.fill):ns,'derived: surface over the chosen ground, summed'+veNote);
 row('net (fill less cut)',scaled()?fm(f.fill-f.cut)+' mm3':ns,scaled()?gVolE(f.fill-f.cut):ns,'derived; the Balance button shifts the form level until this is zero');
 row('steepest slope',scaled()?slopeTxt(f.smx)+' on the tile at '+f1((f.smi%f.n+.5)*f.cs)+', '+f1((Math.floor(f.smi/f.n)+.5)*f.cs)+' mm':ns,scaled()?gSlopeE(f.smx):ns,'derived: heightfield gradient'+veNote);
 if(V.map==='slope')row('slope bands, share of the tile',scaled()&&f.bands?'to '+Math.min(V.s1,V.s2)+' %: '+f1(f.bands[0])+' % · to '+Math.max(V.s1,V.s2)+' %: '+f1(f.bands[1])+' % · over: '+f1(f.bands[2])+' %':ns,scaled()&&f.bands?gArea(f.T*f.T*f.bands[0]/100)+' · '+gArea(f.T*f.T*f.bands[1]/100)+' · '+gArea(f.T*f.T*f.bands[2]/100):ns,'derived: true slope (tile slope over the exaggeration) against the two thresholds');
 if(SPOTS.length)row('spot elevations',SPOTS.map((p,i)=>(i+1)+': '+spotLabel(zAt(f,p[0]*f.T,p[1]*f.T))).join(' · '),'','derived: surface height at each clicked point, above the tile floor');
 row('pattern fit',""")
rep(" $('cap').innerHTML=capLines()", " mapKey();$('cap').innerHTML=capLines()")
# plan: map under the lines, spots on top; click drops a spot, drag sets the section
rep(" const lines=(a,w,col)=>{", " if(fld.map){const wg=mcv2.getContext('2d');wg.putImageData(new ImageData(fld.map,NG,NG),0,0);g.imageSmoothingEnabled=false;g.drawImage(mcv2,0,0,V.tile,V.tile);g.imageSmoothingEnabled=true}\n const dk=!!fld.map;const lines=(a,w,col)=>{")
rep(" lines(cont.mid,.7,C.mid);lines(cont.idx,1.3,C.idx);", " lines(cont.mid,.7,dk?'rgba(7,9,14,.5)':C.mid);lines(cont.idx,1.3,dk?'rgba(7,9,14,.85)':C.idx);")
rep("g.lineWidth=.9/k;g.strokeStyle='rgba(255,255,255,.55)';g.stroke();", "g.lineWidth=.9/k;g.strokeStyle=dk?'rgba(7,9,14,.35)':'rgba(255,255,255,.55)';g.stroke();")
rep(" g.strokeStyle=C.frame;g.lineWidth=1/k;g.strokeRect(0,0,V.tile,V.tile);", " SPOTS.forEach((p,i)=>{const x=p[0]*V.tile,y=p[1]*V.tile,r=4/k;g.beginPath();g.moveTo(x-r,y-r);g.lineTo(x+r,y+r);g.moveTo(x-r,y+r);g.lineTo(x+r,y-r);g.lineWidth=1.6/k;g.strokeStyle='#fff';g.stroke();const t=(i+1)+': '+spotLabel(zAt(fld,x,y));g.font=(14/k)+'px \"IBM Plex Mono\",monospace';const tw=g.measureText(t).width;g.fillStyle='rgba(7,9,14,.8)';g.fillRect(x+r*1.5,y-r*3.4,tw+4/k,18/k);g.fillStyle='#fff';g.fillText(t,x+r*1.5+2/k,y-r*.2)});\n g.strokeStyle=C.frame;g.lineWidth=1/k;g.strokeRect(0,0,V.tile,V.tile);")
rep("let cont=null;const wcv=document.createElement('canvas');wcv.width=wcv.height=NG;", "let cont=null;const wcv=document.createElement('canvas');wcv.width=wcv.height=NG;const mcv2=document.createElement('canvas');mcv2.width=mcv2.height=NG;")
rep("cv.addEventListener('pointerdown',e=>{drag=true;cv.setPointerCapture(e.pointerId);SEC.frac[0]=pos(e);SEC.frac[1]=pos(e)});", "let keep=null;cv.addEventListener('pointerdown',e=>{drag=true;keep=[SEC.frac[0].slice(),SEC.frac[1].slice()];cv.setPointerCapture(e.pointerId);SEC.frac[0]=pos(e);SEC.frac[1]=pos(e)});")
rep("if(Math.hypot(SEC.frac[1][0]-SEC.frac[0][0],SEC.frac[1][1]-SEC.frac[0][1])<.02){SEC.frac=[[0,.5],[1,.5]]}drawPlan();drawSec();if(view3)view3.section()})", "if(Math.hypot(SEC.frac[1][0]-SEC.frac[0][0],SEC.frac[1][1]-SEC.frac[0][1])<.02){/* a click, not a drag: a spot elevation; the section line stays */const p=SEC.frac[0];SEC.frac=keep;SPOTS.push(p);readout()}drawPlan();drawSec();if(view3)view3.section()})")
# section: grades
rep(" $('sectag').textContent='Section A to B · '+veLine()}", " let gr='no scale set';if(scaled()){const p=pr.p;const avg=Math.abs(p[p.length-1][1]-p[0][1])/Math.max(pr.L,1e-6)/veE();let st=0;const w=4;for(let i=w;i<p.length;i++){const s=Math.abs(p[i][1]-p[i-w][1])/Math.max(p[i][0]-p[i-w][0],1e-6)/veE();if(s>st)st=s}gr='average '+slopeTxt(avg)+' · steepest '+slopeTxt(st)+(V.ve>0?'':' · vertical exaggeration not set: taken as 1');SECG={avg,st}}else SECG=null;\n g.fillStyle='#b0b0c1';g.font='16px \"IBM Plex Mono\",monospace';g.fillText('grade A to B: '+gr,x0,Ht-28);\n $('sectag').textContent='Section A to B · '+veLine()}\nlet SECG=null;")
# 3D: map colours on the surface
rep("surfG.setIndex(new THREE.BufferAttribute(ix,1));", "surfG.setIndex(new THREE.BufferAttribute(ix,1));const scol=new Float32Array(n*n*3);surfG.setAttribute('color',new THREE.BufferAttribute(scol,3));const lin=v=>Math.pow(v/255,2.2);")
rep("new THREE.MeshBasicMaterial({color:0x07090e,side:THREE.DoubleSide,", "new THREE.MeshBasicMaterial({vertexColors:true,side:THREE.DoubleSide,")
rep("surfG.attributes.position.needsUpdate=true;surfG.computeBoundingSphere();", "surfG.attributes.position.needsUpdate=true;surfG.computeBoundingSphere();{const m=f.map;const g0=lin(7),g1=lin(9),g2=lin(14);for(let c=0;c<n*n;c++){if(m){scol[c*3]=lin(m[c*4])*.8;scol[c*3+1]=lin(m[c*4+1])*.8;scol[c*3+2]=lin(m[c*4+2])*.8}else{scol[c*3]=g0;scol[c*3+1]=g1;scol[c*3+2]=g2}}surfG.attributes.color.needsUpdate=true;Lmid.material.color.set(m?0x07090e:0xe6deff);Lidx.material.color.set(m?0x07090e:0xe6deff);ptsCloud.visible=!m}")
rep("sc.add(new THREE.Points(ptsG,new THREE.PointsMaterial({color:0x8b8ba3,size:1.3,sizeAttenuation:false,transparent:true,opacity:.7})));", "const ptsCloud=new THREE.Points(ptsG,new THREE.PointsMaterial({color:0x8b8ba3,size:1.3,sizeAttenuation:false,transparent:true,opacity:.7}));sc.add(ptsCloud);")
rep("function update(){if(!pat)return;fld=computeField();cont=contours(fld);", "function update(){if(!pat)return;fld=computeField();makeMap(fld);cont=contours(fld);")
rep(" if(p.id==='typ'){showTyp();proposeNN()}\n", " if(p.id==='typ'||p.id==='prof'||p.id==='form'||p.id==='map'){showTyp();proposeNN()}\n if(p.id==='form'&&released&&GEO.includes(V.form)&&V.fit<140){setV('fit',145)/* a study outline grown at 94 percent would leave the corners of a geometric form empty */}\n if(p.id==='typ'||p.id==='form')hints();\n")
# exports: spots layer, form in the sidecar
rep("body+='<g id=\"section-line\"", "body+='<g id=\"spot-elevations\" stroke-width=\"0.25\" font-family=\"IBM Plex Sans, sans-serif\" font-size=\"'+PT12+'\">'+SPOTS.map((p,i)=>{const x=p[0]*T,y=p[1]*T;return '<path d=\"M'+(x-1.2).toFixed(2)+' '+(y-1.2).toFixed(2)+'l2.4 2.4M'+(x-1.2).toFixed(2)+' '+(y+1.2).toFixed(2)+'l2.4 -2.4\"/><text x=\"'+(x+2).toFixed(2)+'\" y=\"'+(y-1.5).toFixed(2)+'\" fill=\"#000\" stroke=\"none\">'+esc((i+1)+': '+spotLabel(zAt(f,x,y)))+'</text>'}).join('')+'</g>';\n body+='<g id=\"section-line\"")
rep("['<line x1=\"0\" y1=\"-1.4\" x2=\"12\" y2=\"-1.4\" stroke=\"#000\" stroke-width=\"0.25\" stroke-dasharray=\"2 1.5\"/>','section line A to B']]", "['<line x1=\"0\" y1=\"-1.4\" x2=\"12\" y2=\"-1.4\" stroke=\"#000\" stroke-width=\"0.25\" stroke-dasharray=\"2 1.5\"/>','section line A to B'],['<path d=\"M4.8 -2.6l2.4 2.4M4.8 -0.2l2.4 -2.4\" stroke=\"#000\" stroke-width=\"0.25\"/>','spot elevation: surface height above the tile floor'+(scaled()?', ground units at the stated scale':', tile mm')]]")
rep("function allParams(){const o={};PR.forEach(p=>o[p.id]=V[p.id]);o.nn=+$('nn').value;o.section=secPts();return o}", "function allParams(){const o={};PR.forEach(p=>o[p.id]=V[p.id]);o.nn=+$('nn').value;o.section=secPts();o.spots=SPOTS.map(p=>[+(p[0]*V.tile).toFixed(2),+(p[1]*V.tile).toFixed(2)]);return o}")
rep("wet_area_mm2:wat.on?+wat.area.toFixed(1):null,", "cut_mm3:+fld.cut.toFixed(1),fill_mm3:+fld.fill.toFixed(1),form_area_mm2:+fld.formArea.toFixed(1),smoothing_largest_change_mm:+fld.smax.toFixed(3),wet_area_mm2:wat.on?+wat.area.toFixed(1):null,")
rep("d.addEventListener('drop',e=>{if(e.dataTransfer.files[0])takeFile(e.dataTransfer.files[0])});$('gtrue').onclick=trueRelief;}", "d.addEventListener('drop',e=>{if(e.dataTransfer.files[0])takeFile(e.dataTransfer.files[0])});$('gtrue').onclick=trueRelief;$('balance').onclick=balance;$('clearspots').onclick=()=>{SPOTS.length=0;update()}}")
rep("window.LAND={V,PR,set(id,v){setV(id,v);const p=PID[id];if(p.id==='typ'){showTyp();proposeNN()}", "window.LAND={V,PR,balance,SPOTS,spot(fx,fy){SPOTS.push([fx,fy]);update()},planPNG:()=>$('plan').toDataURL('image/png'),view3PNG(){if(!view3)return null;view3.render();return view3.canvas.toDataURL('image/png')},secGrade:()=>SECG,set(id,v){setV(id,v);const p=PID[id];if(p.id==='typ'||p.id==='prof'||p.id==='form'||p.id==='map'){showTyp();proposeNN();hints()}")
rep("[sw('<circle cx=\"8\" cy=\"7\" r=\"1\" fill=\"#8b8ba3\"/><circle cx=\"17\" cy=\"7\" r=\"1\" fill=\"#8b8ba3\"/><circle cx=\"26\" cy=\"7\" r=\"1\" fill=\"#8b8ba3\"/>'),'surface points (3D)']]", "[sw('<circle cx=\"8\" cy=\"7\" r=\"1\" fill=\"#8b8ba3\"/><circle cx=\"17\" cy=\"7\" r=\"1\" fill=\"#8b8ba3\"/><circle cx=\"26\" cy=\"7\" r=\"1\" fill=\"#8b8ba3\"/>'),'surface points (3D)'],[sw('<path d=\"M13 3l8 8M13 11l8 -8\" stroke=\"#fff\" stroke-width=\"1.5\"/>'),'spot elevation, numbered']]")
rep("<p class=\"note\">Every number above is set by a control or is marked derived, with what it derives from. The 3D view", "<p class=\"note\">Every number above is set by a control or is marked derived, with what it derives from. Xylem and radiolaria are this page's readings of those looks, made with the Lab engine. The 3D view")
# the pattern is drawn only where it lies in the form
rep(" return{z,base,n,cs,T,segT,outl,", " const segIn=[];segT.forEach((q,i)=>{const mx=(q[0]+q[2])/2,my=(q[1]+q[3])/2;const ci=Math.floor(mx/cs),cj=Math.floor(my/cs);if(ci>=0&&cj>=0&&ci<n&&cj<n&&inside[cj*n+ci])segIn.push([q[0],q[1],q[2],q[3],i<pat.veinCount?1:0])});\n return{z,base,n,cs,T,segT,segIn,outl,")
rep("g.beginPath();fld.segT.forEach(s=>{g.moveTo(s[0],s[1]);g.lineTo(s[2],s[3])});", "g.beginPath();fld.segIn.forEach(s=>{g.moveTo(s[0],s[1]);g.lineTo(s[2],s[3])});")
rep("const vs=[];f.segT.forEach(s=>{", "const vs=[];f.segIn.forEach(s=>{")
rep("(pat.veinCount?f.segT.slice(0,pat.veinCount).map(", "(pat.veinCount?f.segIn.filter(q=>q[4]).map(")
rep("polyl(pat.cells.map(c=>c.map(f.tf)),true)", "polyl(pat.cells.map(c=>c.map(f.tf)).filter(c=>{const gx=c.reduce((a,q)=>a+q[0],0)/c.length,gy=c.reduce((a,q)=>a+q[1],0)/c.length;const ci=Math.floor(gx/f.cs),cj=Math.floor(gy/f.cs);return ci>=0&&cj>=0&&ci<f.n&&cj<f.n&&f.inside[cj*f.n+ci]}),true)")
assert 'V.mask' not in s and "g_Typology" not in s, 'old names left'
io.open('00_src/land_page_v02.src.html', 'w', encoding='utf-8', newline='\n').write(s); print('land_page_v02.src.html', len(s))
