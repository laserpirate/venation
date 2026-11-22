/* ---------------- v03: fill rules (ridge or valley, berm or channel, plateau or basin, hill or depression), shared controls ---------------- */
/* falloff t: 1 at full strength, 0 at the edge of the influence. The six shapes are this page's; the names follow common sculpting vocabulary. */
const FONAME=['linear','ease-out','smooth','very smooth','cosine','concentrated'];
function L3fall(t,k){t=t<0?0:t>1?1:t;switch(+k){case 1:return 1-(1-t)*(1-t);case 2:return t*t*(3-2*t);case 3:return t*t*t*(t*(6*t-15)+10);case 4:return .5-.5*Math.cos(Math.PI*t);case 5:return t*t*t;default:return t}}
const L3RULES=['rv','bc','pb','hd'];
/* order of a width class: primary at vo_t1 of the greatest Murray width and over, secondary from vo_t2, finer below */
function L3order(wn){return wn>=V.vo_t1?1:wn>=V.vo_t2?2:3}
function L3mur(wn,o){if(!V.vo_mur)return 1;const up=o===1?1:o===2?V.vo_t1:Math.max(V.vo_t2,1e-6);return Math.max(.3,Math.min(1,wn/up))}
/* combine one rule into the surface: candidate C = S + w (T - S); overlap: 0 blend (that candidate), 1 highest (max of S and C), 2 lowest (min) */
function L3put(z,c,w,T,ov,flat){if(!(w>0))return;const S=z[c];const C=S+w*(T-S);if(flat){z[c]=C;return}z[c]=+ov===1?Math.max(S,C):+ov===2?Math.min(S,C):C}
function L3target(S,datum,h,tb){return (1-tb)*(datum+h)+tb*(S+h)}
function applyRules(z,G){const{inside,cls,K,cs,n,tf}=G;const N2=n*n;const datum=V.lo+(G.shift||0);const info={rv:null,bc:null,pb:null,hd:null};
 const need=V.rv_on||V.bc_on;let dC=null;
 if(need){dC=[];for(let k=1;k<=K;k++){const mk=new Uint8Array(N2);let c=0;for(let i=0;i<N2;i++)if(cls[i]===k){mk[i]=1;c++}dC[k]=c?edt(mk,n):null;if(dC[k])for(let i=0;i<N2;i++)dC[k][i]*=cs}}
 const cnt=[0,0,0,0];if(need)for(let i=0;i<N2;i++)if(cls[i])cnt[L3order(cls[i]/K)]++;
 if(V.rv_on){/* each point takes its nearest vein class within reach (nearest wins inside the rule) */const sg=+V.rv_sign;let touched=0;
  for(let i=0;i<N2;i++){if(!inside[i])continue;let best=1e9,bw=0,bT=0;for(let k=1;k<=K;k++){const D=dC[k];if(!D)continue;const d=D[i];const wn=k/K,o=L3order(wn),m=L3mur(wn,o);const half=m*V['rv_w'+o]/2;if(d>=half||d>=best)continue;best=d;bw=L3fall(1-d/half,V.rv_fo);bT=L3target(z[i],datum,sg*m*V['rv_h'+o],V.rv_tb)}
   if(bw>0){L3put(z,i,bw,bT,V.rv_ov,false);touched++}}info.rv={cells:touched}}
 if(V.bc_on){const sg=+V.bc_sign;let touched=0;
  for(let i=0;i<N2;i++){if(!inside[i])continue;let best=1e9,bw=0,bT=0;for(let k=1;k<=K;k++){const D=dC[k];if(!D)continue;const d=D[i];const wn=k/K,o=L3order(wn),m=L3mur(wn,o);const half=m*V['bc_w'+o]/2,h=m*V['bc_h'+o],s=V['bc_s'+o];const run=s>0?h*100/s:0;
    if(d>=half+run||d>=best)continue;best=d;bw=d<=half?1:L3fall(1-(d-half)/run,V.bc_fo);bT=L3target(z[i],datum,sg*h,V.bc_tb)}
   if(bw>0){L3put(z,i,bw,bT,V.bc_ov,false);touched++}}info.bc={cells:touched}}
 if(V.pb_on){/* cells: labels by point in polygon, distance to the cell wall inside each cell, a flat top inset from the wall, a side slope from the flat outward */
  const lab=new Int32Array(N2);const polys=pat.cells.map(c=>c.map(tf));let nc=0;
  polys.forEach((pg,ci)=>{let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;pg.forEach(q=>{if(q[0]<x0)x0=q[0];if(q[0]>x1)x1=q[0];if(q[1]<y0)y0=q[1];if(q[1]>y1)y1=q[1]});const i0=Math.max(0,Math.floor(x0/cs)),i1=Math.min(n-1,Math.ceil(x1/cs)),j0=Math.max(0,Math.floor(y0/cs)),j1=Math.min(n-1,Math.ceil(y1/cs));let hit=0;
   for(let j=j0;j<=j1;j++)for(let i=i0;i<=i1;i++){const x=(i+.5)*cs,y=(j+.5)*cs;let inn=false;for(let a=0,b=pg.length-1;a<pg.length;b=a++){const ya=pg[a][1],yb=pg[b][1];if((ya>y)!==(yb>y)&&x<(pg[b][0]-pg[a][0])*(y-ya)/(yb-ya)+pg[a][0])inn=!inn}if(inn&&inside[j*n+i]){lab[j*n+i]=ci+1;hit++}}if(hit)nc++});
  const wall=new Uint8Array(N2);for(let j=0;j<n;j++)for(let i=0;i<n;i++){const c=j*n+i,l=lab[c];if(!l){wall[c]=1;continue}if((i>0&&lab[c-1]!==l)||(i<n-1&&lab[c+1]!==l)||(j>0&&lab[c-n]!==l)||(j<n-1&&lab[c+n]!==l))wall[c]=1}
  const dIn=edt(wall,n);const em=new Float32Array(polys.length+1);let emx=1e-6;for(let i=0;i<N2;i++){dIn[i]*=cs;const l=lab[i];if(l&&dIn[i]>em[l])em[l]=dIn[i]}for(let l=1;l<=polys.length;l++)if(em[l]>emx)emx=em[l];
  const flat=new Uint8Array(N2);const hl=new Float32Array(polys.length+1);for(let l=1;l<=polys.length;l++)hl[l]=V.pb_h*(1-V.pb_var+V.pb_var*em[l]/emx);
  for(let i=0;i<N2;i++){const l=lab[i];if(l&&dIn[i]>=V.pb_inset)flat[i]=l}
  /* distance to the nearest flat and which flat: exact distance, nearest label spread ring by ring */
  const nf=new Uint8Array(N2);for(let i=0;i<N2;i++)nf[i]=flat[i]?1:0;const dF=edt(nf,n);const near=Int32Array.from(flat);let q=[];for(let i=0;i<N2;i++)if(near[i])q.push(i);
  for(let it=0;it<n&&q.length;it++){const nq=[];for(const c of q){const x=c%n,y=(c-x)/n;const tr=d=>{if(!near[d]){near[d]=near[c];nq.push(d)}};if(x>0)tr(c-1);if(x<n-1)tr(c+1);if(y>0)tr(c-n);if(y<n-1)tr(c+n)}q=nq}
  const sg=+V.pb_sign;let nflat=0,touched=0;
  for(let i=0;i<N2;i++){if(!inside[i])continue;const l=near[i];if(!l)continue;const h=sg*hl[l];const run=V.pb_s>0?Math.abs(h)*100/V.pb_s:0;const e=dF[i]*cs;let w;
   if(flat[i]){w=1;nflat++}else{if(e>=run)continue;w=L3fall(1-e/run,V.pb_fo)}const T=L3target(z[i],datum,h,V.pb_tb);L3put(z,i,w,T,V.pb_ov,!!(flat[i]&&V.pb_flat));touched++}
  info.pb={cells:nc,flatShare:100*nflat/Math.max(1,N2),touched,emx}}
 if(V.hd_on){/* points: cell centroids, branch points or vein nodes, thinned to the least spacing */const P=[];const res=pat.res;
  if(V.hd_pts==='cent')pat.cells.forEach(c=>{let sx=0,sy=0;c.forEach(q=>{sx+=q[0];sy+=q[1]});P.push(tf([sx/c.length,sy/c.length]))});
  else if(res.veins){const N=res.veins.nodes;const ch=new Int32Array(N.length);N.forEach(nd=>{if(nd.p>=0)ch[nd.p]++});const deg=Int32Array.from(ch);res.veins.links.forEach(([a,b])=>{deg[a]++;deg[b]++});
   N.forEach((nd,i)=>{if(V.hd_pts==='nodes'||deg[i]>=2||(V.hd_pts==='branch'&&ch[i]>=2))P.push(tf([nd.x,nd.y]))})}
  if(res.fixed&&V.hd_pts!=='cent')res.fixed.forEach(f=>{if(V.hd_pts==='nodes')f.pts.forEach(q=>P.push(tf(q)));else{P.push(tf(f.pts[0]));P.push(tf(f.pts[f.pts.length-1]))}});
  const keep=[];const sp2=V.hd_sp*V.hd_sp;const cell=Math.max(V.hd_sp,1e-3);const bins=new Map();
  P.forEach(p=>{if(p[0]<0||p[1]<0||p[0]>=G.T||p[1]>=G.T)return;const ci=Math.floor(p[0]/cs),cj=Math.floor(p[1]/cs);if(!inside[cj*n+ci])return;const bx=Math.floor(p[0]/cell),by=Math.floor(p[1]/cell);
   if(V.hd_sp>0){for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){const a=bins.get((bx+dx)+'_'+(by+dy));if(a)for(const o of a){if((o[0]-p[0])**2+(o[1]-p[1])**2<sp2)return}}}
   keep.push(p);const k=bx+'_'+by;let a=bins.get(k);if(!a){a=[];bins.set(k,a)}a.push(p)});
  const mk=new Uint8Array(N2);const idx=new Int32Array(N2).fill(-1);keep.forEach((p,i)=>{const c=Math.min(n-1,Math.floor(p[1]/cs))*n+Math.min(n-1,Math.floor(p[0]/cs));mk[c]=1;idx[c]=i});const dP=edt(mk,n);
  const sg=+V.hd_sign;let touched=0;for(let i=0;i<N2;i++){if(!inside[i])continue;const d=dP[i]*cs;if(d>=V.hd_r)continue;const w=L3fall(1-d/V.hd_r,V.hd_fo);L3put(z,i,w,L3target(z[i],datum,sg*V.hd_h,V.hd_tb),V.hd_ov,false);touched++}
  info.hd={points:keep.length,found:P.length,pts:keep,touched}}
 info.orderCells=cnt;return info}

/* ---------------- v03: analyses (drawing aids) ---------------- */
const CMAPS=['cv_on','ws_on','tw_on','sun_on'];
function L3smooth(z,n,passes){let a=new Float32Array(z),t=new Float32Array(z.length);for(let p=0;p<passes;p++){for(let j=0;j<n;j++)for(let i=0;i<n;i++){const l=i>0?i-1:i,r=i<n-1?i+1:i;t[j*n+i]=(a[j*n+l]+2*a[j*n+i]+a[j*n+r])/4}for(let j=0;j<n;j++){const u=(j>0?j-1:j)*n,d=(j<n-1?j+1:j)*n;for(let i=0;i<n;i++)a[j*n+i]=(t[u+i]+2*t[j*n+i]+t[d+i])/4}}return a}
const CVNAME=[['nose','shoulder','hollow shoulder'],['spur side','planar slope','hollow'],['toe slope','foot slope','channel or valley floor']];
const CVCOL=[[[214,120,90],[230,170,120],[200,150,170]],[[170,190,120],[120,120,140],[110,150,200]],[[150,200,170],[90,140,170],[60,90,200]]];
function curvature(f){const n=f.n,cs=f.cs;const zs=L3smooth(f.z,n,Math.round(V.cv_sm*12));const kp=new Float32Array(n*n),kc=new Float32Array(n*n),cl=new Int8Array(n*n).fill(-1);const thr=V.cv_thr;const cnt=new Int32Array(10);
 for(let j=1;j<n-1;j++)for(let i=1;i<n-1;i++){const c=j*n+i;const p=(zs[c+1]-zs[c-1])/(2*cs),q=(zs[c+n]-zs[c-n])/(2*cs),r=(zs[c+1]-2*zs[c]+zs[c-1])/(cs*cs),t=(zs[c+n]-2*zs[c]+zs[c-n])/(cs*cs),s=(zs[c+n+1]-zs[c+n-1]-zs[c-n+1]+zs[c-n-1])/(4*cs*cs);const g2=p*p+q*q;
  if(g2<1e-6){cl[c]=9;cnt[9]++;continue}kp[c]=-(p*p*r+2*p*q*s+q*q*t)/(g2*Math.pow(1+g2,1.5));kc[c]=-(q*q*r-2*p*q*s+p*p*t)/Math.pow(g2,1.5);
  const a=kp[c]>thr?0:kp[c]<-thr?2:1;const b=kc[c]>thr?0:kc[c]<-thr?2:1;cl[c]=a*3+b;cnt[a*3+b]++}
 return{kp,kc,cl,cnt}}
function extrema(f){const z=f.z,n=f.n;let hi=0,lo=0;for(let i=1;i<z.length;i++){if(z[i]>z[hi])hi=i;if(z[i]<z[lo])lo=i}const rg=f.zmax-f.zmin;const top=f.zmax-rg*V.ex_top/100,bot=f.zmin+rg*V.ex_bot/100;let nt=0,nb=0;for(let i=0;i<z.length;i++){if(z[i]>=top)nt++;if(z[i]<=bot)nb++}
 const lt=[],lb=[];contourLevel(f,top,lt);contourLevel(f,bot,lb);return{hi,lo,top,bot,topShare:100*nt/z.length,botShare:100*nb/z.length,lt,lb}}
function streams(f,hy){const n=f.n,N2=n*n,acc=hy.acc,dn=hy.dn;let amax=0;for(let i=0;i<N2;i++)if(acc[i]>amax)amax=acc[i];const thr=Math.max(2,V.st_thr*amax);const on=new Uint8Array(N2);const z=f.z;/* no stream on level ground: a stream cell drops toward its downstream neighbour (or, at a sink or the edge, has a slope) */
 for(let i=0;i<N2;i++)if(acc[i]>=thr&&(dn[i]>=0?z[i]-z[dn[i]]>1e-4:f.slp[i]>1e-3))on[i]=1;
 const ord=new Uint8Array(N2);const inN=new Int32Array(N2);for(let c=0;c<N2;c++)if(on[c]&&dn[c]>=0&&on[dn[c]])inN[dn[c]]++;const src=[];const mx=new Uint8Array(N2),mxc=new Uint8Array(N2);const qq=[];for(let c=0;c<N2;c++)if(on[c]&&!inN[c]){qq.push(c);src.push(c);ord[c]=1}
 const left=Int32Array.from(inN);for(let h=0;h<qq.length;h++){const c=qq[h];const d=dn[c];if(d<0||!on[d])continue;if(ord[c]>mx[d]){mx[d]=ord[c];mxc[d]=1}else if(ord[c]===mx[d])mxc[d]++;if(--left[d]===0){ord[d]=mxc[d]>=2?mx[d]+1:mx[d];qq.push(d)}}
 const seg=[],so=[];const out=[];let omax=1,ends=0;for(let c=0;c<N2;c++){if(!on[c])continue;if(ord[c]>omax)omax=ord[c];const d=dn[c];const x=c%n,y=(c-x)/n;const edge=x===0||y===0||x===n-1||y===n-1;
  if(d>=0&&on[d]){seg.push((x+.5)*f.cs,(y+.5)*f.cs,(d%n+.5)*f.cs,((d-d%n)/n+.5)*f.cs);so.push(ord[c])}if(d<0||edge)out.push(c);else if(!on[d])ends++}
 return{thr,amax,seg,so,src,out,omax,ends,cells:qq.length}}
function watersheds(f,hy,st){const n=f.n,N2=n*n,dn=hy.dn;const term=new Int32Array(N2).fill(-1);const order=hy.order;for(let k=order.length-1;k>=0;k--){const c=order[k];const d=dn[c];term[c]=d<0?c:(term[d]>=0?term[d]:d)}
 for(let c=0;c<N2;c++)if(term[c]<0)term[c]=c;/* outlets of the stream network: the terminal each outlet drains to */const keyOf=new Map();st.out.forEach(c=>{let t=term[c];keyOf.set(t,(keyOf.get(t)||0)+1)});
 const area=new Map();for(let c=0;c<N2;c++){const t=term[c];if(keyOf.has(t))area.set(t,(area.get(t)||0)+1)}const list=Array.from(area.entries()).sort((a,b)=>b[1]-a[1]);const top=list.slice(0,V.ws_n);const id=new Map();top.forEach((e,i)=>id.set(e[0],i));
 const lab=new Int16Array(N2).fill(-1);for(let c=0;c<N2;c++){const t=term[c];if(id.has(t))lab[c]=id.get(t)}const a2=f.cs*f.cs;let other=0;for(let c=0;c<N2;c++)if(lab[c]<0)other++;
 return{lab,list:top.map(e=>({term:e[0],area:e[1]*a2,x:(e[0]%n+.5)*f.cs,y:((e[0]-e[0]%n)/n+.5)*f.cs})),other:other*a2,count:list.length}}
const WSCOL=[[86,180,233],[230,159,0],[0,158,115],[240,228,66],[204,121,167],[213,94,0],[0,114,178],[160,160,160],[120,200,160],[200,120,90],[150,130,220],[220,200,140]];
function wetness(f,hy){const n=f.n,N2=n*n;const w=new Float32Array(N2);const s=[];for(let i=0;i<N2;i++){const a=hy.acc[i]*f.cs;const tb=Math.max(f.slp[i],1e-3);w[i]=Math.log(a/tb);s.push(w[i])}s.sort((a,b)=>a-b);return{w,lo:s[Math.floor(N2*.01)],hi:s[Math.floor(N2*.99)],med:s[N2>>1]}}
function sunShade(f){const n=f.n,cs=f.cs,z=f.z;const az=V.sun_az*Math.PI/180,al=V.sun_alt*Math.PI/180;/* plan: x right, y down; azimuth 0 = toward the top of the plan, clockwise */const lx=Math.sin(az),ly=-Math.cos(az);const tanA=Math.tan(al);
 const L=[lx*Math.cos(al),ly*Math.cos(al),Math.sin(al)];const sh=new Float32Array(n*n);const shadow=new Uint8Array(n*n);let ns=0;const step=.7;
 for(let j=0;j<n;j++)for(let i=0;i<n;i++){const c=j*n+i;const xa=i>0?i-1:i,xb=i<n-1?i+1:i,ya=j>0?j-1:j,yb=j<n-1?j+1:j;const gx=(z[j*n+xb]-z[j*n+xa])/((xb-xa)*cs),gy=(z[yb*n+i]-z[ya*n+i])/((yb-ya)*cs);const nl=Math.hypot(gx,gy,1);
  sh[c]=Math.max(0,(-gx*L[0]-gy*L[1]+L[2])/nl);let x=i+.5,y=j+.5,h=z[c];for(let k=1;k<n*1.5;k++){x+=lx*step;y+=ly*step;h+=tanA*step*cs;if(x<0||y<0||x>=n||y>=n||h>f.zmax)break;const zz=z[Math.floor(y)*n+Math.floor(x)];if(zz>h){shadow[c]=1;ns++;break}}}
 return{sh,shadow,share:100*ns/(n*n)}}
function analyses(f){const A={};const hyNeed=V.rain||V.st_on||V.ws_on||V.tw_on;A.hy=hyNeed?rainRun(f):null;if(V.cv_on)A.cv=curvature(f);if(V.ex_on)A.ex=extrema(f);if(V.st_on||V.ws_on)A.st=streams(f,A.hy);if(V.ws_on)A.ws=watersheds(f,A.hy,A.st);if(V.tw_on)A.tw=wetness(f,A.hy);if(V.sun_on)A.sun=sunShade(f);return A}
function anaMap(f,A){const N2=f.n*f.n;const m=new Uint8ClampedArray(N2*4);const put=(i,c,a)=>{m[i*4]=c[0];m[i*4+1]=c[1];m[i*4+2]=c[2];m[i*4+3]=a==null?235:a};
 if(V.cv_on&&A.cv){const cv=A.cv;if(V.cv_show==='class'){for(let i=0;i<N2;i++){const k=cv.cl[i];put(i,k<0||k===9?[20,22,30]:CVCOL[Math.floor(k/3)][k%3])}}
  else{const a=V.cv_show==='prof'?cv.kp:cv.kc;const s=V.cv_thr*4;for(let i=0;i<N2;i++){const v=Math.max(-1,Math.min(1,a[i]/s));put(i,v>=0?[230,230-140*v,200-170*v]:[230+170*v,230+120*v,240])}}return m}
 if(V.ws_on&&A.ws){for(let i=0;i<N2;i++){const l=A.ws.lab[i];put(i,l<0?[30,32,40]:WSCOL[l%WSCOL.length])}return m}
 if(V.tw_on&&A.tw){const t=A.tw;for(let i=0;i<N2;i++)put(i,ramp((t.w[i]-t.lo)/Math.max(1e-6,t.hi-t.lo)));return m}
 if(V.sun_on&&A.sun){for(let i=0;i<N2;i++){const v=A.sun.shadow[i]?.18*A.sun.sh[i]+.04:A.sun.sh[i];const g=Math.round(30+215*v);put(i,A.sun.shadow[i]?[g*.7,g*.75,g+25]:[g,g,g*.95])}return m}
 return null}

/* ---------------- v03: units ---------------- */
function slopeAll(s){if(!(s>1e-6))return '0 % · 0 deg · level';const pc=(100*s).toFixed(s<.1?1:0)+' %',dg=(Math.atan(s)*180/Math.PI).toFixed(1)+' deg',ra='1:'+(1/s).toFixed(1);const o={pct:[pc,dg,ra],deg:[dg,pc,ra],ratio:[ra,pc,dg]}[V.su]||[pc,dg,ra];return o.join(' · ')}
function sideTxt(pct){if(!(pct>0))return 'vertical wall';const r=100/pct;return pct+' % = '+r.toFixed(2)+':1 (H:V) · '+(Math.atan(pct/100)*180/Math.PI).toFixed(1)+' deg'}

/* ---------------- v03: export for Grasshopper: ASCII grids, a DXF in layers, a CSV per layer, a README; one zip ---------------- */
function ascGrid(z,f,note){const n=f.n;let s='ncols '+n+'\nnrows '+n+'\nxllcorner 0\nyllcorner 0\ncellsize '+f.cs.toFixed(6)+'\nNODATA_value -9999\n';const rows=[];for(let j=0;j<n;j++){const r=new Array(n);for(let i=0;i<n;i++)r[i]=z[j*n+i].toFixed(4);rows.push(r.join(' '))}return s+rows.join('\n')+'\n'}
function ghCurves(f){/* vein polylines by order: the pattern's vein segments joined end to end, split where the order changes */const segs=pat.segs.slice(0,pat.veinCount);const by={1:[],2:[],3:[]};const wmap={1:new Map(),2:new Map(),3:new Map()};const key=(x,y)=>Math.round(x*200)+'_'+Math.round(y*200);
 segs.forEach(s=>{const a=f.tf([s[0],s[1]]),b=f.tf([s[2],s[3]]);const wn=(s[4]+s[5])/2;const o=L3order(wn);const mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2;const ci=Math.floor(mx/f.cs),cj=Math.floor(my/f.cs);if(ci<0||cj<0||ci>=f.n||cj>=f.n||!f.inside[cj*f.n+ci])return;
  by[o].push(a[0],a[1],b[0],b[1]);[[a,s[4]],[b,s[5]]].forEach(([p,w])=>{const k=key(p[0],p[1]);const m=wmap[o];const e=m.get(k);if(e){e[0]+=w;e[1]++}else m.set(k,[w,1])})});
 const out={};[1,2,3].forEach(o=>{out[o]=chain(Float32Array.from(by[o])).filter(p=>p.length>=2).map(p=>{let sw=0,nw=0;p.forEach(q=>{const e=wmap[o].get(key(q[0],q[1]));if(e){sw+=e[0]/e[1];nw++}});return{pts:p,wn:nw?sw/nw:0}})});return out}
function ghSet(){const f=fld;const T=f.T;const base=f.zb||f.z;const zB=(x,y)=>{const t={n:f.n,cs:f.cs,z:base};return zAt(t,x,y)};const Y=y=>T-y;const st=stem();const ve=V.ve>0?V.ve:1;
 const cur=ghCurves(f);const cells=pat.cells.map(c=>c.map(f.tf)).filter(c=>{const gx=c.reduce((a,q)=>a+q[0],0)/c.length,gy=c.reduce((a,q)=>a+q[1],0)/c.length;const ci=Math.floor(gx/f.cs),cj=Math.floor(gy/f.cs);return ci>=0&&cj>=0&&ci<f.n&&cj<f.n&&f.inside[cj*f.n+ci]});
 const pts=f.rules&&f.rules.hd?f.rules.hd.pts:[];
 const vh=(o,m)=>V.bc_on?+V.bc_sign*m*V['bc_h'+o]:V.rv_on?+V.rv_sign*m*V['rv_h'+o]:0;
 let dx='0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nLAYER\n70\n5\n';['veins_1','veins_2','veins_3','cells','points'].forEach((l,i)=>{dx+='0\nLAYER\n2\n'+l+'\n70\n0\n62\n'+(i+1)+'\n6\nCONTINUOUS\n'});dx+='0\nENDTAB\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n';
 const v3=(l,x,y,zz)=>'0\nVERTEX\n8\n'+l+'\n10\n'+x.toFixed(4)+'\n20\n'+Y(y).toFixed(4)+'\n30\n'+zz.toFixed(4)+'\n70\n32\n';
 const pl=(l,p,closed,zf)=>{let s='0\nPOLYLINE\n8\n'+l+'\n66\n1\n70\n'+(closed?9:8)+'\n10\n0\n20\n0\n30\n0\n';p.forEach(q=>{s+=v3(l,q[0],q[1],zf(q))});return s+'0\nSEQEND\n8\n'+l+'\n'};
 const FO=v=>FONAME[+v],OVN=v=>['blend','highest','lowest'][+v];const csv={};const counts={veins_1:0,veins_2:0,veins_3:0,cells:0,points:0};
 [1,2,3].forEach(o=>{const L='veins_'+o;const rows=['curve,vertices,length_mm,order,murray_width_share,scale_by_murray,ridge_valley_on,ridge_valley_width_mm,ridge_valley_height_mm,berm_channel_on,berm_channel_width_mm,berm_channel_height_mm,berm_channel_side_slope_pct,falloff_ridge_valley,falloff_berm_channel,topo_blend_ridge_valley,topo_blend_berm_channel,overlap_ridge_valley,overlap_berm_channel'];
  cur[o].forEach((c,i)=>{const m=L3mur(c.wn,o);let len=0;for(let k=1;k<c.pts.length;k++)len+=Math.hypot(c.pts[k][0]-c.pts[k-1][0],c.pts[k][1]-c.pts[k-1][1]);dx+=pl(L,c.pts,false,q=>zB(q[0],q[1])+vh(o,m));counts[L]++;
   rows.push([i,c.pts.length,len.toFixed(3),o,c.wn.toFixed(4),V.vo_mur?1:0,V.rv_on?1:0,(m*V['rv_w'+o]).toFixed(3),(+V.rv_sign*m*V['rv_h'+o]).toFixed(3),V.bc_on?1:0,(m*V['bc_w'+o]).toFixed(3),(+V.bc_sign*m*V['bc_h'+o]).toFixed(3),V['bc_s'+o],FO(V.rv_fo),FO(V.bc_fo),V.rv_tb,V.bc_tb,OVN(V.rv_ov),OVN(V.bc_ov)].join(','))});csv[L]=rows.join('\n')+'\n'});
 {const rows=['curve,vertices,area_mm2,plateau_basin_on,height_mm,side_slope_pct,flat_inset_mm,prioritize_flat,falloff,topo_blend,overlap'];const h=+V.pb_sign*V.pb_h;
  cells.forEach((c,i)=>{dx+=pl('cells',c,true,q=>zB(q[0],q[1])+(V.pb_on?h:0));counts.cells++;let a=0;for(let k=0,j=c.length-1;k<c.length;j=k++)a+=(c[j][0]*c[k][1]-c[k][0]*c[j][1]);rows.push([i,c.length,Math.abs(a/2).toFixed(3),V.pb_on?1:0,h.toFixed(3),V.pb_s,V.pb_inset,V.pb_flat?1:0,FO(V.pb_fo),V.pb_tb,OVN(V.pb_ov)].join(','))});csv.cells=rows.join('\n')+'\n'}
 {const rows=['point,x_mm,y_mm,z_mm,hill_depression_on,radius_mm,height_mm,falloff,topo_blend,overlap,source'];pts.forEach((p,i)=>{const zz=zB(p[0],p[1]);dx+='0\nPOINT\n8\npoints\n10\n'+p[0].toFixed(4)+'\n20\n'+Y(p[1]).toFixed(4)+'\n30\n'+zz.toFixed(4)+'\n';counts.points++;
   rows.push([i,p[0].toFixed(4),Y(p[1]).toFixed(4),zz.toFixed(4),V.hd_on?1:0,V.hd_r,(+V.hd_sign*V.hd_h).toFixed(3),FO(V.hd_fo),V.hd_tb,OVN(V.hd_ov),show(PID.hd_pts,V.hd_pts)].join(','))});csv.points=rows.join('\n')+'\n'}
 dx+='0\nENDSEC\n0\nEOF\n';
 const rd=['README_grasshopper.txt · '+artId(),'',
  'What is in this set (units: millimetres on the tile; x to the right, y up the plan, z up; the tile is '+T+' x '+T+' mm'+(V.scaleN>0?', scale 1:'+V.scaleN:'')+')',
  '  '+st+'_base.asc      the surface before the fill rules (form, profile, ground and the VS08 fill), Esri ASCII grid, '+f.n+' x '+f.n+' cells of '+f.cs.toFixed(4)+' mm',
  '  '+st+'_surface.asc   the surface as shown on the page, with the fill rules, same grid',
  '  '+st+'_pattern.dxf   layers veins_1, veins_2, veins_3 (open 3D polylines by vein order), cells (closed 3D polylines), points (3D points)',
  '  '+st+'_<layer>.csv   one row per curve or point, in the order the DXF holds them on that layer',
  '','Heights in the DXF: each vertex sits on the base surface plus the height its rule gives it (berm or channel if on, else ridge or valley; plateau or basin on cells; hill or depression on points). With no rule on, it sits on the base surface.',
  'Vertical exaggeration on the page: '+ve+'x; it stretches the page view only. Every number in this set is at true height.','',
  'Which list goes to which kind of input on a terrain sculpting component',
  '  points with radii and heights            layer points; radius_mm and height_mm from points.csv',
  '  open curves with widths and heights      layers veins_1 to veins_3; ridge_valley_width_mm and ridge_valley_height_mm',
  '  path curves with widths and side slopes  layers veins_1 to veins_3; berm_channel_width_mm and berm_channel_side_slope_pct (the curve elevation sets raised or lowered)',
  '  closed boundaries with side slopes       layer cells; side_slope_pct and prioritize_flat from cells.csv (the boundary elevation sets the plateau or basin level)',
  '  falloff, topo blend, overlap             the columns of the same names; falloff by name: 0 linear, 1 ease-out, 2 smooth, 3 very smooth, 4 cosine, 5 concentrated; overlap 0 blend, 1 highest, 2 lowest',
  '  terrain mesh                             '+st+'_base.asc into a component that reads an ASCII grid into a mesh',
  '','Side slope in percent: 0 is a vertical wall, 50 is 2:1, 100 is 1:1, 200 is 0.5:1 (horizontal to vertical).',
  'The page combines features in its own way (nearest feature inside a rule, then the overlap mode against the surface below); a sculpting component run on the same lists will not match it cell for cell.',
  'Counts: veins_1 '+counts.veins_1+', veins_2 '+counts.veins_2+', veins_3 '+counts.veins_3+', cells '+counts.cells+', points '+counts.points+'.'];
 const files={};files[st+'_base.asc']=ascGrid(base,f);files[st+'_surface.asc']=ascGrid(f.z,f);files[st+'_pattern.dxf']=dx;['veins_1','veins_2','veins_3','cells','points'].forEach(l=>files[st+'_'+l+'.csv']=csv[l]);files['README_grasshopper.txt']=rd.join('\n')+'\n';
 return{files,counts,name:st+'_grasshopper.zip'}}
function zipStore(files){/* a zip with stored (uncompressed) entries */const enc=new TextEncoder();const parts=[],cen=[];let off=0;const u16=v=>[v&255,(v>>8)&255],u32=v=>[v&255,(v>>>8)&255,(v>>>16)&255,(v>>>24)&255];
 Object.keys(files).forEach(name=>{const nb=enc.encode(name),db=enc.encode(files[name]);const c=crc(db);const lh=new Uint8Array([0x50,0x4b,3,4,20,0,0,0,0,0,0,0,0x21,0,...u32(c),...u32(db.length),...u32(db.length),...u16(nb.length),0,0]);parts.push(lh,nb,db);
  cen.push(new Uint8Array([0x50,0x4b,1,2,20,0,20,0,0,0,0,0,0,0,0x21,0,...u32(c),...u32(db.length),...u32(db.length),...u16(nb.length),0,0,0,0,0,0,0,0,0,0,0,0,...u32(off)]),nb);off+=lh.length+nb.length+db.length});
 let cl=0;cen.forEach(a=>cl+=a.length);const n=Object.keys(files).length;const end=new Uint8Array([0x50,0x4b,5,6,0,0,0,0,...u16(n),...u16(n),...u32(cl),...u32(off),0,0]);return new Blob([...parts,...cen,end],{type:'application/zip'})}
/* falloff icons: six curves with their names, the selected one marked; a click selects */
function foIcon(k,on){let d='';for(let i=0;i<=20;i++){const x=i/20;const y=L3fall(1-x,k);d+=(i?'L':'M')+(2+x*30).toFixed(1)+' '+(20-y*16).toFixed(1)}return '<svg width="34" height="22" viewBox="0 0 34 22"><rect x=".5" y=".5" width="33" height="21" fill="none" stroke="'+(on?'var(--acc2)':'var(--line)')+'"/><path d="'+d+'" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>'}
function foKeys(){L3RULES.forEach(r=>{const id=r+'_fo';const row=$('row_'+id);if(!row)return;const k=document.createElement('div');k.className='fokey';k.id='fokey_'+id;row.after(k);drawFoKey(id)})}
function drawFoKey(id){const k=$('fokey_'+id);if(!k)return;k.innerHTML=FONAME.map((nm,i)=>'<button type="button" class="fo'+(String(V[id])===String(i)?' on':'')+'" data-v="'+i+'" title="'+i+' '+nm+'">'+foIcon(i,String(V[id])===String(i))+'<span>'+i+' '+nm+'</span></button>').join('');
 k.querySelectorAll('button').forEach(b=>b.onclick=()=>{setV(id,b.dataset.v);onChange(PID[id],true);drawFoKey(id)})}
