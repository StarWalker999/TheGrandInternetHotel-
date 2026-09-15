// Each resident is built from its own silhouette and identifying props.
export function createResident(id,Blocks,C,T){
 const b=new Blocks(),g=new T.Group();
 const box=(x,y,z,w,h,d,c)=>b.box(x,y,z,w,h,d,c);
 const eye=(x,y,z=.51,size=.2)=>{box(x,y,z,size,size,.08,C.trim);box(x+.025,y,z+.05,size*.42,size*.5,.04,C.ink);};
 const feet=(c=C.ink,n=2)=>{for(let i=0;i<n;i++)box((i-(n-1)/2)*.36,.16,.12,.25,.3,.48,c);};
 const book=(x,y,c=C.rose)=>{box(x,y,.65,.65,.42,.25,c);box(x,y,.8,.53,.26,.04,C.trim);};
 const stem=(x,y,h,c=C.amber)=>box(x,y,0,.16,h,.16,c);
 const lantern=(x,y)=>{box(x,y,.2,.45,.6,.4,C.amber);box(x,y,.42,.27,.38,.03,0xffefba);box(x,y+.4,.2,.6,.15,.5,C.ink);};
 switch(id){
 case 'moss':box(0,.85,0,1.5,1.25,1,C.sage);box(0,1.57,0,1.1,.4,.85,C.sage);box(0,1.05,.55,1.25,.55,.12,C.ink);for(const x of [-.36,.36])eye(x,1.6,.48);eye(0,1.28,.65,.23);box(0,2.12,0,.85,.85,.7,C.orange);box(0,1.82,0,1.25,.13,.9,C.ink);for(let i=0;i<3;i++){stem(.95+i*.14,.7,.5);box(.95+i*.14,.48,.1,.22,.12,.15,C.amber);}feet(C.sage,4);break;
 case 'inkwell':box(0,1,0,.62,1.55,.6,0x576581);for(const [x,h] of [[-.45,2.5],[0,2.9],[.45,2.2]]){stem(x,(h+1.4)/2,h-1.4,0x576581);eye(x,h,.16,.3);}box(0,1.48,0,.9,.18,.8,C.blue);box(.28,.9,.5,.22,1.15,.13,C.blue);for(let i=0;i<3;i++)book(-.5,.7+i*.34,[C.orange,C.sage,C.rose][i]);feet();break;
 case 'pip':box(0,.85,0,1.1,1.2,.75,C.rose);for(const x of [-.5,.5]){box(x,1.8,0,.3,.6,.3,C.wood);box(x*1.3,2.02,0,.4,.25,.35,C.wood);eye(x*.55,1.3,.43);}box(-.15,.94,.45,.15,1,.12,C.wood);box(.7,.62,.1,.65,.7,.65,C.wood);book(-.65,.75,C.trim);feet(C.rose);break;
 case 'fern':stem(0,1.1,1.8,C.sage);for(const [x,y] of [[0,2.4],[-.5,2.1],[.5,2.1],[-.8,1.8],[.8,1.8]])box(x,y,0,.6,.65,.25,0x44734e);box(0,1.15,0,.8,.7,.65,C.trim);box(0,1.18,.37,.65,.6,.06,0x556443);eye(-.18,1.85,.26);eye(.18,1.85,.26);box(.85,1,.2,.9,.08,.6,C.amber);box(.85,1.25,.2,.35,.4,.35,C.trim);feet(C.wood);break;
 case 'tally':box(0,.9,0,1,1.25,.75,0xb78a43);box(0,1.85,0,1.3,.65,.7,0xb78a43);for(const x of [-.33,.33]){box(x,1.92,.4,.5,.4,.12,C.ink);eye(x,1.92,.5,.28);}box(0,.8,.45,.85,.9,.13,C.wood);for(const x of [-.25,.25])box(x,.8,.55,.15,.4,.1,C.amber);stem(.45,2.4,.6,C.ink);box(-.82,1,0,.55,.28,.4,C.amber);feet();break;
 case 'quill':for(let i=0;i<5;i++)box(0,.4+i*.4,0,1.3-i*.2,.42,.65-i*.08,0x4d3658);eye(-.13,1.65,.28,.14);eye(.13,1.65,.28,.14);box(0,1.2,.4,.5,.14,.1,0x863b4d);for(let i=0;i<5;i++)box(.65+i*.12,1+i*.28,.12,.35,.3,.12,C.trim);book(-.7,.8,C.trim);break;
 case 'lock':box(0,1,0,1.65,1.6,1,0x284c50);box(0,1.86,0,1.25,.5,.85,0x284c50);eye(0,1.85,.48,.48);box(0,2.22,0,1.6,.24,1.05,C.ink);for(let i=0;i<3;i++)box(.3,.6+i*.3,.56,.13,.13,.07,C.amber);lantern(1.13,.8);feet();break;
 case 'echo':for(let i=0;i<4;i++)box(i*.12,.5+i*.28,0,1.05-i*.2,.3,.55,C.trim);for(const [x,y,w] of [[-.65,1.7,.9],[.75,1.6,1.1]]){box(x,y,0,w,.65,.3,C.rose);box(x,y,.19,w*.6,.3,.06,C.ink);}box(.03,1.38,.35,.55,.07,.05,C.blue);box(0,.75,-.35,1.1,.75,.12,0xa84439);feet(C.ink,4);break;
 case 'brass':for(let i=0;i<4;i++)box(0,.4+i*.3,0,1.7-i*.3,.3,1.2-i*.18,C.amber);stem(0,1.8,.6);box(0,2.12,0,.55,.17,.5,C.amber);eye(-.3,.6,.65,.16);eye(.3,.6,.65,.16);feet();break;
 case 'vellum':stem(-.18,1.5,1.8,C.trim);box(.1,2.36,0,.55,.4,.4,C.trim);box(.48,2.35,.1,.6,.1,.18,C.orange);eye(.12,2.4,.25,.14);box(0,.95,0,1,.55,.75,C.trim);for(const x of [-.25,.25])stem(x,.4,.8,C.ink);book(.7,1,C.trim);break;
 case 'sable':box(0,1,0,.6,1.3,.6,C.ink);for(const x of [-.8,.8]){box(x,1.45,0,1.15,1.2,.15,0x333040);box(x,1.5,.13,.5,.65,.06,C.rose);}eye(-.14,1.6,.34);eye(.14,1.6,.34);feet(C.ink,4);break;
 case 'clover':box(0,.55,0,1.1,.8,.85,C.trim);stem(0,1.35,1,C.wood);for(const [x,y,w] of [[0,2.2,1.7],[-.5,1.85,1.2],[.55,1.65,1]])box(x,y,0,w,.4,.8,C.sage);eye(-.2,.65,.5);eye(.2,.65,.5);feet(C.wood,3);break;
 case 'cinder':box(0,.7,0,.75,.8,1.5,C.ink);box(0,1.35,.45,.8,.65,.65,C.ink);eye(-.22,1.5,.82);eye(.22,1.5,.82);for(let i=0;i<4;i++)box(0,1.15,-.7+i*.3,.2,.5,.22,C.orange);box(.4,.4,-.9,1,.2,.3,C.ink);feet(C.ink,4);break;
 case 'marble':box(0,1,0,1.5,1.3,1,C.trim);box(0,1.9,0,1.3,.7,1,C.trim);box(0,1.6,.6,1.1,.4,.4,C.stone);eye(-.3,2,.55);eye(.3,2,.55);for(const x of [-.85,.85])box(x,1.5,-.2,.65,.65,.2,C.stone);feet(C.trim);break;
 case 'lumen':box(0,1.9,0,.9,1,.7,C.amber);box(0,1.9,.4,.65,.7,.05,0xffedb4);box(0,1,0,.4,1,.4,C.wood);for(const x of [-.65,.65])box(x,1.2,-.2,.8,1,.12,C.blue);feet(C.ink,4);break;
 case 'rue':for(let i=0;i<6;i++)box(Math.sin(i)*.48,.4+i*.3,0,.35,.36,.22,0xa98cab);box(0,1.3,0,1.6,.28,.25,C.rose);eye(-.1,1.9,.2,.13);eye(.16,1.9,.2,.13);break;
 case 'cobalt':box(0,.85,0,1.5,.7,1,0x537f9d);box(0,1.25,0,1.65,.12,1.1,C.amber);for(const x of [-.35,.35])eye(x,1.08,.55);box(-1,1.1,.2,.65,.9,.5,C.blue);feet(C.blue,6);break;
 case 'osier':box(0,1,0,1.1,1.5,.7,C.wood);for(let i=0;i<6;i++)box(0,.4+i*.25,.4,1.2,.05,.06,C.amber);stem(-.4,2,.6);stem(.4,2,.6);box(0,2.3,0,.95,.1,.15,C.amber);eye(-.2,1.4,.47);eye(.2,1.4,.47);feet(C.wood);break;
 case 'thimble':box(0,.65,0,.8,1,.65,0xbb7d58);box(0,1.5,0,.5,.6,.5,C.wood);for(const y of [1.2,1.8])box(0,y,0,.8,.12,.7,C.amber);eye(-.12,1.55,.3,.14);eye(.12,1.55,.3,.14);box(0,1.4,.7,.07,.07,.9,C.ink);feet(C.rose);break;
 case 'morrow':box(0,1,0,.8,1.2,.65,0x41445c);for(const x of [-.65,.65]){box(x,1.3,0,.8,1.3,.15,0x41445c);box(x*.6,2,0,.3,.85,.25,C.rose);}eye(-.2,1.55,.4,.28);eye(.2,1.55,.4,.28);feet();break;
 case 'juniper':stem(0,1.1,1.8,0x527646);box(0,2.1,0,1.05,.5,.3,C.sage);eye(-.35,2.1,.22,.25);eye(.35,2.1,.22,.25);for(const x of [-.6,.6]){box(x,1.2,0,.15,1,.15,C.sage);box(x,.75,.2,.5,.14,.5,C.sage);}feet(C.sage,4);break;
 case 'fable':for(const x of [-.55,.55]){box(x,1.3,0,1.05,1.7,.22,0x8b3d39);box(x,1.3,.15,.9,1.5,.06,C.trim);}eye(-.2,1.6,.23);eye(.2,1.6,.23);box(.1,.3,-.2,.15,.6,.1,C.orange);feet();break;
 case 'gasket':box(0,.9,0,1.5,1.15,1.25,C.amber);box(0,1.55,.3,.8,.5,.6,C.wood);eye(.15,1.6,.65,.4);for(const x of [-.85,.85])box(x,.55,0,.45,.5,.6,C.ink);feet(C.ink,4);break;
 case 'opal':box(0,.5,.3,1.4,.55,1.2,0xc4b9ba);for(let i=0;i<3;i++)box(-.3+i*.3,1+i*.3,-.15,1-i*.2,.9,.85,C.trim);for(const x of [-.4,.4]){stem(x,1.4,.7,C.rose);eye(x,1.8,.3,.2);}break;
 case 'briar':stem(0,1.1,1.8,0x586143);for(const [x,y] of [[0,2.4],[-.45,2.1],[.45,2.1],[0,1.75]])box(x,y,0,.6,.6,.45,0x893e50);eye(-.16,2.1,.3,.15);eye(.16,2.1,.3,.15);feet(C.sage,3);break;
 case 'selkie':box(0,.6,0,1.3,.8,1.2,C.stone);box(.2,1.35,0,.55,1,.55,C.stone);box(.35,1.98,.2,.85,.5,.65,C.stone);eye(.12,2,.57);eye(.55,2,.57);box(.2,1.6,0,.75,.15,.75,C.blue);book(-.7,.8,C.trim);break;
 case 'filigree':stem(0,1.3,1.5);box(0,2.1,.2,.5,.5,.5,C.trim);eye(-.1,2.15,.5,.14);eye(.12,2.15,.5,.14);for(let i=-2;i<=2;i++)box(i*.42,1.65-Math.abs(i)*.18,-.3,.18,1.6,.12,C.amber);feet(C.amber);break;
 case 'truffle':box(0,.8,0,.75,1.3,.65,C.trim);box(0,1.65,0,1.8,.4,1.3,0x955543);box(0,1.95,0,1.2,.3,.95,0x955543);eye(-.18,1.35,.39,.17);eye(.18,1.35,.39,.17);stem(.95,1,1.5,C.wood);box(.95,1.9,0,.45,.6,.2,C.wood);feet(C.trim,4);break;
 case 'patch':box(0,1,0,1.6,1.5,.7,0x78474a);for(const x of [-.55,.55])box(x,1,.4,.14,1.5,.08,C.amber);eye(-.35,1.25,.47,.23);eye(.3,1.35,.47,.18);box(0,.8,.45,.6,.15,.1,C.amber);box(0,1.9,0,.7,.2,.3,C.wood);feet();break;
 case 'gossamer':box(0,1.65,0,1.5,.65,1,C.trim);box(0,2.1,0,1,.3,.75,0xa7c6b5);for(let i=0;i<5;i++)box((i-2)*.28,.7+Math.sin(i)*.12,0,.12,1.1,.14,0xa7c6b5);eye(-.25,1.7,.55,.17);eye(.25,1.7,.55,.17);break;
 case 'rook':box(0,1,0,1,1.65,.8,C.ink);box(0,1.95,0,1.4,.35,1,C.ink);for(const x of [-.5,0,.5])box(x,2.25,0,.3,.3,.8,C.ink);eye(-.23,1.7,.46,.16);eye(.23,1.7,.46,.16);book(.8,.8,0x893e50);feet();break;
 case 'dulse':for(let i=0;i<5;i++)box(Math.sin(i*.8)*.4,.4+i*.35,0,.5,.4,.45,0xb56551);box(.35,2.1,.2,.6,.5,.55,C.rose);box(.35,2,.6,.25,.2,.55,C.rose);eye(.18,2.2,.49,.14);book(-.65,1,C.trim);break;
 case 'nacre':box(0,1.3,0,1.6,1.8,.22,C.rose);box(0,1.3,.15,1.35,1.55,.15,C.trim);box(0,1.4,.3,.6,.85,.3,C.ink);eye(-.14,1.55,.5,.15);eye(.14,1.55,.5,.15);box(0,.8,.65,1.3,.5,.35,C.wood);for(let i=-2;i<=2;i++)box(i*.2,.8,.86,.08,.5,.05,C.trim);feet();break;
 case 'tinsel':box(0,1.1,0,.7,1.3,.75,C.ink);box(0,1.85,0,.7,.6,.6,C.trim);box(0,1.8,.65,.25,.2,.9,C.ink);eye(-.23,1.98,.35,.18);eye(.23,1.98,.35,.18);for(const x of [-.55,.55])box(x,1.1,0,.5,1,.18,C.ink);feet(C.amber);break;
 case 'mistral':for(const [x,y,w] of [[0,1.2,1.4],[-.5,1.6,.8],[.3,1.9,.9],[.65,1.3,.7]])box(x,y,0,w,.6,.65,C.blue);eye(-.2,1.6,.4);eye(.2,1.6,.4);stem(1,1.3,1.6,C.ink);box(1,2.2,0,1.3,.2,.9,C.rose);feet(C.trim);break;
 case 'saffron':box(0,1,0,.6,1.35,.6,0xc6a346);box(0,1.9,0,1,.6,.6,0xc6a346);eye(-.3,2,.36,.32);eye(.3,2,.36,.32);box(0,1,.35,.65,.75,.1,0x61465b);box(.6,.35,-.4,1,.18,.22,0xc6a346);feet();break;
 case 'tock':box(0,1,0,1.15,1.6,.75,C.wood);box(0,.9,.45,.75,.75,.08,C.trim);box(0,1,.51,.05,.35,.04,C.ink);for(const x of [-.4,.4]){box(x,2,0,.5,.6,.5,C.wood);eye(x,1.9,.4,.3);}stem(0,.4,.6,C.amber);feet();break;
 case 'wisp':for(let i=0;i<5;i++)box(Math.sin(i)*.12,.4+i*.33,0,1.3-i*.2,.36,.75-i*.1,C.trim);eye(-.14,1.55,.3,.2);eye(.15,1.55,.3,.2);stem(.8,.8,.8,C.sage);box(.8,1.35,0,.4,.35,.35,C.rose);break;
 case 'auburn':box(0,.8,0,1,1.1,1.3,0xa3593d);box(0,1.5,.3,.7,.6,.6,0xa3593d);eye(-.2,1.6,.65);eye(.2,1.6,.65);box(-1,1,.2,.85,1,.65,C.rose);for(let i=0;i<3;i++)box(.8,.6+i*.3,.3,.8,.26,.6,C.trim);feet(C.wood,4);break;
 case 'mim':box(0,.8,0,.7,1,.6,C.trim);box(0,1.6,0,1,.6,.65,C.trim);for(const x of [-.4,.4]){box(x,2.1,0,.25,.6,.25,C.trim);eye(x*.6,1.7,.38,.16);}box(.6,.5,-.35,.9,.3,.3,C.trim);book(0,.8,C.sage);feet(C.trim);break;
 case 'periwinkle':for(let i=0;i<4;i++)box(0,1.2,0,1.7-i*.34,1.7-i*.34,.35+i*.16,[0x8d789d,C.rose,C.trim,C.ink][i]);eye(-.2,.65,.72,.16);eye(.2,.65,.72,.16);book(.8,1.7,C.blue);feet(C.rose,6);break;
 default:return createResident('moss',Blocks,C,T);
 }
 g.add(b.finish());g.userData.character=id;return g;
}
