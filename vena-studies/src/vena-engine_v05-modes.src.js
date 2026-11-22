
/* ---------------- v05 additions: three modes made from the functions above. No stored study uses them. ----------------
   xylem      dense closed venation (Runions section 4 as above) with a strong thick to thin hierarchy and no free ends; the cells are the gaps.
              After the look of the Nervous System Xylem pieces; made here from this file's own growth rules, none of their code.
   radiolaria the relaxed weighted cell diagram above, each cell drawn in from its walls and rounded (corner cutting), walls thicker where
              cells are small. Our reading of that look, not their code.
   delaunay   the triangulation of the same seed points the cells mode relaxes; edges are the pattern; p.dprune (0 = off) drops edges
              longer than dprune times the median edge. */
function chaikin(c,n){for(let k=0;k<n;k++){const o=[];for(let i=0;i<c.length;i++){const a=c[i],b=c[(i+1)%c.length];o.push([a[0]*.75+b[0]*.25,a[1]*.75+b[1]*.25],[a[0]*.25+b[0]*.75,a[1]*.25+b[1]*.75])}c=o}return c}
const EXTRA_MODES={
 xylem(p){const res=build({...p,mode:'closed',nde:1,nsrc:Math.round(p.nsrc*2.2),birth:Math.max(4,p.birth*.7),kill:Math.max(2,p.kill*.7),mur:Math.min(p.mur,2.0),maxw:p.maxw*1.5});p.mm=res.p.mm;res.p=p;res.extra='xylem';return res},
 radiolaria(p){const res=build({...p,mode:'cells',lloyd:Math.max(p.lloyd,6)});p.mm=res.p.mm;res.p=p;res.extra='radiolaria';const polys=res.cel.polys;const ar=polys.map(c=>Math.abs(area(c)));
  const top=ar.slice().sort((a,b)=>a-b)[Math.floor(ar.length*.9)]||1;const round=p.rround==null?2:p.rround;
  const open=polys.map((c,i)=>{const g=centroid(c);const rin=Math.sqrt(ar[i]/Math.PI);const t=p.cw*(1.2+2.2*(1-Math.min(1,Math.sqrt(ar[i]/top))));const f=Math.max(.3,Math.min(.93,1-t/Math.max(rin,1e-6)));
   const ins=c.map(q=>[g[0]+(q[0]-g[0])*f,g[1]+(q[1]-g[1])*f]);return round>0?chaikin(ins,round):ins});
  res.cel={...res.cel,polys:open,walls:polys,rounded:round};return res},
 delaunay(p){const res=build({...p,mode:'cells'});p.mm=res.p.mm;res.p=p;res.extra='delaunay';const pts=res.cel.pts,poly=res.poly;const D=d3.Delaunay.from(pts);const T=D.triangles,HE=D.halfedges;const E=[];const len=[];
  for(let e=0;e<T.length;e++){if(HE[e]>=0&&HE[e]<e)continue;const a=T[e],b=T[e%3===2?e-2:e+1];const mx=(pts[a][0]+pts[b][0])/2,my=(pts[a][1]+pts[b][1])/2;if(!inside(poly,mx,my))continue;E.push([a,b]);len.push(Math.hypot(pts[a][0]-pts[b][0],pts[a][1]-pts[b][1]))}
  const med=len.slice().sort((a,b)=>a-b)[len.length>>1]||0;const lim=p.dprune>0?p.dprune*med:Infinity;const keep=E.filter((e,i)=>len[i]<=lim);const tris=[];
  for(let t=0;t<T.length;t+=3){const q=[pts[T[t]],pts[T[t+1]],pts[T[t+2]]];const g=[(q[0][0]+q[1][0]+q[2][0])/3,(q[0][1]+q[1][1]+q[2][1])/3];if(!inside(poly,g[0],g[1]))continue;
   let ok=true;for(let k=0;k<3;k++){const a=q[k],b=q[(k+1)%3];if(Math.hypot(a[0]-b[0],a[1]-b[1])>lim||!inside(poly,(a[0]+b[0])/2,(a[1]+b[1])/2))ok=false}if(ok)tris.push(q)}
  res.veins={nodes:pts.map(q=>({x:q[0],y:q[1],p:-1,w:p.tip,fixed:false})),links:keep,kids:pts.map(()=>0),fixedEdges:[],trunk:false,de:null,src:0};res.cel=null;res.ponds=tris;
  res.layers={fixed:res.layers.fixed,grown:[0,0],links:[p.tip<res.minV?keep.length:0,keep.length]};res.segs=res.layers.fixed[1]+keep.length;res.clamped=res.layers.fixed[0]+res.layers.links[0];res.walls=0;res.wallsClamped=0;res.dstat={edges:E.length,kept:keep.length,median:med};return res}};
