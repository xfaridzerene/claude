# EMERGE FM/control-de-radio.html (parcial)

```
  300    .modal-actions{display:flex; justify-content:flex-end; gap:10px; margin-top:8px;}
  301    .error-text{color:var(--pink); font-family:var(--font-mono); font-size:11px; margin-top:8px; display:none;}
  302    .shake{animation:shake .3s;}
  303    @keyframes shake{
  304      0%,100%{transform:translateX(0);} 20%{transform:translateX(-6px);} 40%{transform:translateX(6px);}
  305      60%{transform:translateX(-4px);} 80%{transform:translateX(4px);}
  306    }
  307  
  308    .confirm-modal{max-width:380px; text-align:center;}
  309    .confirm-modal p{padding:20px; font-family:var(--font-ui); font-size:15px;}
  650  const DAY_LABELS = {lunes:'Lun', martes:'Mar', miercoles:'Mié', jueves:'Jue', viernes:'Vie', sabado:'Sáb', domingo:'Dom'};
  651  const DAY_LABELS_FULL = {lunes:'Lunes', martes:'Martes', miercoles:'Miércoles', jueves:'Jueves', viernes:'Viernes', sabado:'Sábado', domingo:'Domingo'};
  652  
  653  /* La radio emite solo 80s y 90s: la paleta de géneros se reduce a esa línea editorial. */
  654  const GENRES = {
  655    'Rock':        {color:'#7CFC3C'},
  656    'Pop':         {color:'#34d8d8'},
  657    '80s':         {color:'#ff2e63'},
  658    '90s':         {color:'#b892ff'},
  659    'Misceláneo':  {color:'#ff8a3d'},
  660    'Matinal':     {color:'#ffcc00'}
  661  };
  662  
  663  /* Equivalencias para parrillas guardadas con la lista de géneros antigua. */
  664  const GENRE_MIGRATION = {
  665    'Electronica':'Misceláneo', 'Electrónica':'Misceláneo', 'Talk Show':'Misceláneo',
  666    'Urbano':'90s', 'Clasicos':'80s', 'Clásicos':'80s', 'Noticias':'Matinal'
  667  };
  668  
  669  const TYPES = ['En vivo','Grabado','Automatizado'];
  670  
  671  const STORAGE_KEY = 'controlRadio.programas.v2';
  672  const LEGACY_KEY = 'controlRadio.programas.v1';
  673  const SOUND_KEY = 'controlRadio.sonido.v1';
  674  
  675  function defaultData(){
  676    return [
  677      {name:'Matinal Emerge', host:'Elena Cruz', days:['lunes','martes','miercoles','jueves','viernes'], start:'07:00', end:'09:00', genre:'Matinal', type:'En vivo', notes:'Arranque del día: saludos, panorama y clásicos suaves.'},
  678      {name:'Ruta 80', host:'Tito Reyes', days:['lunes','miercoles','viernes'], start:'18:00', end:'20:00', genre:'80s', type:'En vivo', notes:'Lo mejor de la década de los ochenta, sin relleno.'},
  679      {name:'Década 90', host:'Caro Núñez', days:['martes','jueves'], start:'18:00', end:'20:00', genre:'90s', type:'En vivo', notes:'Los noventa en su mejor momento.'},
  680      {name:'Zona Rock', host:'Hugo Paredes', days:['jueves','viernes'], start:'21:00', end:'23:00', genre:'Rock', type:'En vivo', notes:'Rock clásico de los 80 y 90.'},
  681      {name:'Pop Total', host:'Caro Núñez', days:['lunes','martes','miercoles','jueves','viernes'], start:'15:00', end:'17:00', genre:'Pop', type:'Grabado', notes:''},
  682      {name:'Misceláneo Nocturno', host:'DJ Marín', days:['lunes','martes','miercoles','jueves'], start:'23:00', end:'01:00', genre:'Misceláneo', type:'Automatizado', notes:'Selección libre para la madrugada.'},
  683      {name:'Sábado Retro', host:'Tito Reyes', days:['sabado'], start:'10:00', end:'13:00', genre:'80s', type:'En vivo', notes:'Especial de fin de semana con pedidos del público.'},
  684      {name:'Domingo 90', host:'Hugo Paredes', days:['domingo'], start:'11:00', end:'14:00', genre:'90s', type:'Grabado', notes:''}
  685    ].map(p=>({id:crypto.randomUUID(), status:'activo', ...p}));
  686  }
  687  
  688  let data = loadData();
  689  let currentView = 'dashboard';
  690  let currentDay = todayKey();
  691  let showFullWeek = false;
  692  let deleteTargetId = null;
  693  
  694  /* Normaliza un programa: día único -> arreglo de días, géneros antiguos, tipo y estado. */
  695  function normalizeProgram(p){
  696    const days = Array.isArray(p.days) ? p.days.filter(d=>DAYS.includes(d)) : (DAYS.includes(p.day) ? [p.day] : []);
  697    let genre = p.genre;
  698    if(GENRE_MIGRATION[genre]) genre = GENRE_MIGRATION[genre];
  699    if(!GENRES[genre]) genre = 'Misceláneo';
  700    return {
  701      id: p.id || crypto.randomUUID(),
  702      name: String(p.name||'Sin nombre'),
  703      host: String(p.host||''),
  704      days: days.length ? days : [DAYS[0]],
  705      start: p.start || '00:00',
  706      end: p.end || '01:00',
  707      genre,
  708      type: TYPES.includes(p.type) ? p.type : 'En vivo',
  709      status: p.status === 'pausado' ? 'pausado' : 'activo',
  710      notes: p.notes || ''
  711    };
  712  }
  713  
  714  function loadData(){
  715    try{
  716      const raw = localStorage.getItem(STORAGE_KEY) || localStorage.getItem(LEGACY_KEY);
  717      if(!raw) return defaultData();
  718      const parsed = JSON.parse(raw);
  719      if(!Array.isArray(parsed) || parsed.length === 0) return defaultData();
  720      return parsed.map(normalizeProgram);
  721    }catch(e){ return defaultData(); }
  722  }
  723  
  724  /* ---- Helpers del modelo ---- */
  725  function programDays(p){ return Array.isArray(p.days) ? p.days : []; }
  726  function isActive(p){ return p.status !== 'pausado'; }
  727  function genreColor(g){ return (GENRES[g] && GENRES[g].color) || 'var(--gray)'; }
  728  function airsOn(p, day){ return programDays(p).includes(day); }
  729  function daysSummary(p){
```

### Cambio 2026-09-08T01:53
Antes:
```
  .grid-2{display:grid; grid-template-columns:1.3fr 1fr; gap:18px; margin-bottom:22px;}
  .grid-3{display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-bottom:22px;}
  @media (max-width:900px){.grid-2, .grid-3{grid-template-columns:1fr;}}
```
Después:
```
  .grid-2{display:grid; grid-template-columns:1.3fr 1fr; gap:18px; margin-bottom:22px;}
  .grid-3{display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-bottom:22px;}
  .grid-4{display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:22px;}
  @media (max-width:1100px){.grid-4{grid-template-columns:repeat(2,1fr);}}
  @media (max-width:900px){.grid-2, .grid-3, .grid-4{grid-template-columns:1fr;}}
```

### Cambio 2026-09-08T01:53
Antes:
```
  /* ============ MISSION BANNER ============ */
```
Después:
```
  /* ============ SELECTOR DE DÍAS (formulario) ============ */
  .preset-row{display:flex; flex-wrap:wrap; gap:6px; margin-bottom:8px;}
  .preset-btn{
    padding:5px 10px; background:var(--black); border:1px solid var(--line); color:var(--gray);
    font-family:var(--font-mono); font-size:10px; letter-spacing:1px; text-transform:uppercase;
    transition:all .15s ease;
  }
  .preset-btn:hover{color:var(--green); border-color:var(--green-dim);}
  .day-picker{display:flex; flex-wrap:wrap; gap:6px;}
  .day-chip{
    position:relative; padding:9px 13px; background:var(--black); border:1px solid var(--line);
    color:var(--gray); font-family:var(--font-ui); font-weight:700; font-size:12.5px;
    letter-spacing:1px; text-transform:uppercase; user-select:none; cursor:pointer;
    transition:all .12s ease;
  }
  .day-chip input{position:absolute; opacity:0; pointer-events:none;}
  .day-chip:hover{color:var(--white); border-color:var(--green-dim);}
  .day-chip.on{background:var(--green); color:var(--black); border-color:var(--green); box-shadow:0 0 10px rgba(124,252,60,0.35);}
  .hint{font-family:var(--font-mono); font-size:10px; color:var(--gray); letter-spacing:1px; margin-top:7px; line-height:1.5;}

  /* ============ BADGES / ETIQUETAS ============ */
  .badge{
    display:inline-block; font-family:var(--font-mono); font-size:10px; letter-spacing:1px;
    padding:3px 8px; border:1px solid currentColor; text-transform:uppercase;
    margin-top:8px; margin-right:6px;
  }
  .badge.type{color:var(--cyan);}
  .badge.paused{color:var(--orange);}
  .badge.days{color:var(--gray);}
  .badge.conflict{color:var(--pink);}
  .program-card.paused{opacity:0.6; border-left-color:var(--orange);}
  .program-card.conflict{border-left-color:var(--pink);}

  .search-input{
    padding:9px 14px; background:var(--panel-2); border:1px solid var(--line); color:var(--white);
    font-family:var(--font-ui); font-weight:600; font-size:13px; min-width:190px;
  }
  .search-input:focus{outline:none; border-color:var(--green);}
  .search-input::placeholder{color:var(--gray); text-transform:uppercase; font-size:12px; letter-spacing:1px;}

  /* ============ MISSION BANNER ============ */
```

### Cambio 2026-09-08T01:54
Antes:
```
      <button class="nav-btn" id="nav-export">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12m0 0-4-4m4 4 4-4M4 21h16"/></svg>
        <span>Exportar PDF</span>
      </button>
      <div class="sidebar-footer">
```
Después:
```
      <button class="nav-btn" id="nav-export">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12m0 0-4-4m4 4 4-4M4 21h16"/></svg>
        <span>Exportar PDF</span>
      </button>
      <button class="nav-btn" id="nav-backup">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5M12 15V3"/></svg>
        <span>Guardar copia</span>
      </button>
      <button class="nav-btn" id="nav-import">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M17 8l-5-5-5 5M12 3v12"/></svg>
        <span>Restaurar copia</span>
      </button>
      <input type="file" id="import-file" accept="application/json,.json" style="display:none">
      <div class="sidebar-footer">
```

### Cambio 2026-09-08T01:54
Antes:
```
        <div class="grid-3">
          <div class="panel stat-chip"><div class="num" id="stat-total">0</div><div class="lbl">Programas totales</div></div>
          <div class="panel stat-chip"><div class="num" id="stat-hours">0h</div><div class="lbl">Horas programadas / semana</div></div>
          <div class="panel stat-chip"><div class="num" id="stat-today">0</div><div class="lbl">Programas hoy</div></div>
        </div>
```
Después:
```
        <div class="grid-4">
          <div class="panel stat-chip"><div class="num" id="stat-total">0</div><div class="lbl">Programas totales</div></div>
          <div class="panel stat-chip"><div class="num" id="stat-hours">0h</div><div class="lbl">Horas programadas / semana</div></div>
          <div class="panel stat-chip"><div class="num" id="stat-today">0</div><div class="lbl">Emisiones hoy</div></div>
          <div class="panel stat-chip"><div class="num" id="stat-coverage">0%</div><div class="lbl">Cobertura de la semana</div></div>
        </div>
```

### Cambio 2026-09-08T01:54
Antes:
```
          <div class="toolbar-actions">
            <select id="filter-genre" class="btn btn-ghost" style="padding:9px 14px;">
              <option value="">Todos los géneros</option>
            </select>
            <button class="btn" id="btn-toggle-week">
```
Después:
```
          <div class="toolbar-actions">
            <input type="search" id="search-input" class="search-input" placeholder="Buscar programa o locutor">
            <select id="filter-genre" class="btn btn-ghost" style="padding:9px 14px;">
              <option value="">Todos los géneros</option>
            </select>
            <select id="filter-type" class="btn btn-ghost" style="padding:9px 14px;">
              <option value="">Todos los tipos</option>
            </select>
            <button class="btn" id="btn-toggle-week">
```

### Cambio 2026-09-08T01:54
Antes:
```
        <div class="field">
          <label>Día</label>
          <select id="f-day" required></select>
        </div>
        <div class="field-row">
          <div class="field">
            <label>Hora de inicio</label>
            <input type="time" id="f-start" required>
          </div>
          <div class="field">
            <label>Hora de fin</label>
            <input type="time" id="f-end" required>
          </div>
        </div>
        <div class="field">
          <label>Género</label>
          <select id="f-genre" required></select>
        </div>
        <div class="field">
          <label>Notas / descripción</label>
          <textarea id="f-notes" placeholder="Detalles del segmento, invitados, etc. (opcional)"></textarea>
        </div>
```
Después:
```
        <div class="field">
          <label>Días de emisión</label>
          <div class="preset-row">
            <button type="button" class="preset-btn" data-preset="all">Todos los días</button>
            <button type="button" class="preset-btn" data-preset="weekdays">Lun a Vie</button>
            <button type="button" class="preset-btn" data-preset="weekend">Fin de semana</button>
            <button type="button" class="preset-btn" data-preset="none">Limpiar</button>
          </div>
          <div class="day-picker" id="f-days"></div>
          <div class="hint">Marca todos los días que quieras: el programa se repite en cada uno con el mismo horario.</div>
        </div>
        <div class="field-row">
          <div class="field">
            <label>Hora de inicio</label>
            <input type="time" id="f-start" required>
          </div>
          <div class="field">
            <label>Hora de fin</label>
            <input type="time" id="f-end" required>
          </div>
        </div>
        <div class="field-row">
          <div class="field">
            <label>Género</label>
            <select id="f-genre" required></select>
          </div>
          <div class="field">
            <label>Tipo de emisión</label>
            <select id="f-type"></select>
          </div>
        </div>
        <div class="field">
          <label>Estado</label>
          <select id="f-status">
            <option value="activo">Activo — sale al aire</option>
            <option value="pausado">Pausado — no sale al aire</option>
          </select>
        </div>
        <div class="field">
          <label>Notas / descripción</label>
          <textarea id="f-notes" placeholder="Detalles del segmento, invitados, etc. (opcional)"></textarea>
        </div>
```

### Cambio 2026-09-08T01:55
Antes:
```
const GENRES = {
  'Rock':        {color:'#7CFC3C'},
  'Electronica': {color:'#ff2e63'},
  'Pop':         {color:'#34d8d8'},
  'Talk Show':   {color:'#ffcc00'},
  'Noticias':    {color:'#eef1ea'},
  'Clasicos':    {color:'#ff8a3d'},
  'Urbano':      {color:'#b892ff'}
};

const STORAGE_KEY = 'controlRadio.programas.v1';
const SOUND_KEY = 'controlRadio.sonido.v1';

function defaultData(){
  return [
    {id:crypto.randomUUID(), name:'Ruta Nocturna', host:'DJ Marín', day:'lunes', start:'20:00', end:'22:00', genre:'Electronica', notes:'Sesión de música electrónica para cerrar el día.'},
    {id:crypto.randomUUID(), name:'Café y Noticias', host:'Elena Cruz', day:'lunes', start:'07:00', end:'09:00', genre:'Noticias', notes:'Resumen informativo de la mañana.'},
    {id:crypto.randomUUID(), name:'Garage Clásico', host:'Tito Reyes', day:'martes', start:'18:00', end:'20:00', genre:'Rock', notes:'Rock clásico y clásicos del garage.'},
    {id:crypto.randomUUID(), name:'Charla Libre', host:'Fabián Soto', day:'miercoles', start:'12:00', end:'14:00', genre:'Talk Show', notes:'Entrevistas y debate abierto con oyentes.'},
    {id:crypto.randomUUID(), name:'Beats del Barrio', host:'MC Renata', day:'miercoles', start:'21:00', end:'23:00', genre:'Urbano', notes:''},
    {id:crypto.randomUUID(), name:'Vintage 88', host:'Hugo Paredes', day:'jueves', start:'16:00', end:'18:00', genre:'Clasicos', notes:'Éxitos de otras décadas.'},
    {id:crypto.randomUUID(), name:'Pop Total', host:'Caro Núñez', day:'viernes', start:'15:00', end:'17:00', genre:'Pop', notes:''},
    {id:crypto.randomUUID(), name:'Fin de Semana Electro', host:'DJ Marín', day:'viernes', start:'23:00', end:'01:00', genre:'Electronica', notes:'Set especial de cierre de semana.'},
    {id:crypto.randomUUID(), name:'Mañana Deportiva', host:'Rodrigo Iban', day:'sabado', start:'09:00', end:'11:00', genre:'Talk Show', notes:'Resumen deportivo y comentarios.'},
    {id:crypto.randomUUID(), name:'Domingo Clásico', host:'Hugo Paredes', day:'domingo', start:'10:00', end:'12:00', genre:'Clasicos', notes:''}
  ];
}

let data = loadData();
let currentView = 'dashboard';
let currentDay = todayKey();
let showFullWeek = false;
let deleteTargetId = null;

function loadData(){
  try{
    const raw = localStorage.getItem(STORAGE_KEY);
    if(!raw) return defaultData();
    const parsed = JSON.parse(raw);
    if(!Array.isArray(parsed) || parsed.length === 0) return defaultData();
    return parsed;
  }catch(e){ return defaultData(); }
}
```
Después:
```
/* La radio emite solo 80s y 90s: la paleta de géneros se reduce a esa línea editorial. */
const GENRES = {
  'Rock':        {color:'#7CFC3C'},
  'Pop':         {color:'#34d8d8'},
  '80s':         {color:'#ff2e63'},
  '90s':         {color:'#b892ff'},
  'Misceláneo':  {color:'#ff8a3d'},
  'Matinal':     {color:'#ffcc00'}
};

/* Equivalencias para parrillas guardadas con la lista de géneros antigua. */
const GENRE_MIGRATION = {
  'Electronica':'Misceláneo', 'Electrónica':'Misceláneo', 'Talk Show':'Misceláneo',
  'Urbano':'90s', 'Clasicos':'80s', 'Clásicos':'80s', 'Noticias':'Matinal'
};

const TYPES = ['En vivo','Grabado','Automatizado'];

const STORAGE_KEY = 'controlRadio.programas.v2';
const LEGACY_KEY = 'controlRadio.programas.v1';
const SOUND_KEY = 'controlRadio.sonido.v1';

function defaultData(){
  return [
    {name:'Matinal Emerge', host:'Elena Cruz', days:['lunes','martes','miercoles','jueves','viernes'], start:'07:00', end:'09:00', genre:'Matinal', type:'En vivo', notes:'Arranque del día: saludos, panorama y clásicos suaves.'},
    {name:'Ruta 80', host:'Tito Reyes', days:['lunes','miercoles','viernes'], start:'18:00', end:'20:00', genre:'80s', type:'En vivo', notes:'Lo mejor de la década de los ochenta, sin relleno.'},
    {name:'Década 90', host:'Caro Núñez', days:['martes','jueves'], start:'18:00', end:'20:00', genre:'90s', type:'En vivo', notes:'Los noventa en su mejor momento.'},
    {name:'Zona Rock', host:'Hugo Paredes', days:['jueves','viernes'], start:'21:00', end:'23:00', genre:'Rock', type:'En vivo', notes:'Rock clásico de los 80 y 90.'},
    {name:'Pop Total', host:'Caro Núñez', days:['lunes','martes','miercoles','jueves','viernes'], start:'15:00', end:'17:00', genre:'Pop', type:'Grabado', notes:''},
    {name:'Misceláneo Nocturno', host:'DJ Marín', days:['lunes','martes','miercoles','jueves'], start:'23:00', end:'01:00', genre:'Misceláneo', type:'Automatizado', notes:'Selección libre para la madrugada.'},
    {name:'Sábado Retro', host:'Tito Reyes', days:['sabado'], start:'10:00', end:'13:00', genre:'80s', type:'En vivo', notes:'Especial de fin de semana con pedidos del público.'},
    {name:'Domingo 90', host:'Hugo Paredes', days:['domingo'], start:'11:00', end:'14:00', genre:'90s', type:'Grabado', notes:''}
  ].map(p=>({id:crypto.randomUUID(), status:'activo', ...p}));
}

let data = loadData();
let currentView = 'dashboard';
let currentDay = todayKey();
let showFullWeek = false;
let deleteTargetId = null;

/* Normaliza un programa: día único -> arreglo de días, géneros antiguos, tipo y estado. */
function normalizeProgram(p){
  const days = Array.isArray(p.days) ? p.days.filter(d=>DAYS.includes(d)) : (DAYS.includes(p.day) ? [p.day] : []);
  let genre = p.genre;
  if(GENRE_MIGRATION[genre]) genre = GENRE_MIGRATION[genre];
  if(!GENRES[genre]) genre = 'Misceláneo';
  return {
    id: p.id || crypto.randomUUID(),
    name: String(p.name||'Sin nombre'),
    host: String(p.host||''),
    days: days.length ? days : [DAYS[0]],
    start: p.start || '00:00',
    end: p.end || '01:00',
    genre,
    type: TYPES.includes(p.type) ? p.type : 'En vivo',
    status: p.status === 'pausado' ? 'pausado' : 'activo',
    notes: p.notes || ''
  };
}

function loadData(){
  try{
    const raw = localStorage.getItem(STORAGE_KEY) || localStorage.getItem(LEGACY_KEY);
    if(!raw) return defaultData();
    const parsed = JSON.parse(raw);
    if(!Array.isArray(parsed) || parsed.length === 0) return defaultData();
    return parsed.map(normalizeProgram);
  }catch(e){ return defaultData(); }
}

/* ---- Helpers del modelo ---- */
function programDays(p){ return Array.isArray(p.days) ? p.days : []; }
function isActive(p){ return p.status !== 'pausado'; }
function genreColor(g){ return (GENRES[g] && GENRES[g].color) || 'var(--gray)'; }
function airsOn(p, day){ return programDays(p).includes(day); }
function daysSummary(p){
  const d = programDays(p);
  if(d.length === 7) return 'Todos los días';
  if(d.length === 5 && ['lunes','martes','miercoles','jueves','viernes'].every(x=>d.includes(x))) return 'Lun a Vie';
  if(d.length === 2 && d.includes('sabado') && d.includes('domingo')) return 'Fin de semana';
  return DAYS.filter(x=>d.includes(x)).map(x=>DAY_LABELS[x]).join(' · ');
}

/* Detecta cruces de horario dentro de un mismo día. */
function conflictIdsForDay(day){
  const list = data.filter(p=>isActive(p) && airsOn(p, day)).map(p=>{
    const s = timeToMinutes(p.start);
    let e = timeToMinutes(p.end);
    if(e <= s) e += 24*60;
    return {id:p.id, s, e};
  });
  const bad = new Set();
  for(let i=0;i<list.length;i++){
    for(let j=i+1;j<list.length;j++){
      if(list[i].s < list[j].e && list[j].s < list[i].e){ bad.add(list[i].id); bad.add(list[j].id); }
    }
  }
  return bad;
}
```

### Cambio 2026-09-08T01:55
Antes:
```
function getCurrentProgram(){
  const now = new Date();
  const map = [6,0,1,2,3,4,5];
  const dayKey = DAYS[map[now.getDay()]];
  const nowMin = now.getHours()*60+now.getMinutes();
  for(const p of data){
    if(p.day !== dayKey) continue;
    const s = timeToMinutes(p.start);
    let e = timeToMinutes(p.end);
    if(e<=s) e+=24*60;
    if(nowMin>=s && nowMin<e) return p;
    // caso cruce de medianoche revisando desde el día anterior
  }
  // revisar programas que empezaron el día anterior y cruzan a hoy
  const prevIdx = (DAYS.indexOf(dayKey)+6)%7;
  const prevKey = DAYS[prevIdx];
  for(const p of data){
    if(p.day !== prevKey) continue;
    const s = timeToMinutes(p.start);
    let e = timeToMinutes(p.end);
    if(e<=s){
      e = e; // ya es hora del día siguiente en minutos absolutos desde 0
      if(nowMin < e) return p;
    }
  }
  return null;
}

function getNextProgram(){
  const now = new Date();
  const map = [6,0,1,2,3,4,5];
  const dayIdx = map[now.getDay()];
  const nowMin = now.getHours()*60+now.getMinutes();
  for(let offset=0; offset<8; offset++){
    const idx = (dayIdx+offset)%7;
    const key = DAYS[idx];
    const candidates = data.filter(p=>p.day===key).sort((a,b)=>timeToMinutes(a.start)-timeToMinutes(b.start));
    for(const p of candidates){
      if(offset===0 && timeToMinutes(p.start) <= nowMin) continue;
      return p;
    }
  }
  return null;
}
```
Después:
```
function getCurrentProgram(){
  const now = new Date();
  const map = [6,0,1,2,3,4,5];
  const dayKey = DAYS[map[now.getDay()]];
  const nowMin = now.getHours()*60+now.getMinutes();
  for(const p of data){
    if(!isActive(p) || !airsOn(p, dayKey)) continue;
    const s = timeToMinutes(p.start);
    let e = timeToMinutes(p.end);
    if(e<=s) e+=24*60;
    if(nowMin>=s && nowMin<e) return p;
  }
  // programas que empezaron el día anterior y cruzan la medianoche hacia hoy
  const prevKey = DAYS[(DAYS.indexOf(dayKey)+6)%7];
  for(const p of data){
    if(!isActive(p) || !airsOn(p, prevKey)) continue;
    const s = timeToMinutes(p.start), e = timeToMinutes(p.end);
    if(e<=s && nowMin < e) return p;
  }
  return null;
}

function getNextProgram(){
  const now = new Date();
  const map = [6,0,1,2,3,4,5];
  const dayIdx = map[now.getDay()];
  const nowMin = now.getHours()*60+now.getMinutes();
  for(let offset=0; offset<8; offset++){
    const key = DAYS[(dayIdx+offset)%7];
    const candidates = data.filter(p=>isActive(p) && airsOn(p, key))
      .sort((a,b)=>timeToMinutes(a.start)-timeToMinutes(b.start));
    for(const p of candidates){
      if(offset===0 && timeToMinutes(p.start) <= nowMin) continue;
      return {program:p, day:key};
    }
  }
  return null;
}
```

### Cambio 2026-09-08T01:55
Antes:
```
    onairMeta.innerHTML = live.host+' · '+live.start+' – '+live.end+' <span class="genre-tag" style="color:'+GENRES[live.genre].color+'">'+live.genre+'</span>';
```
Después:
```
    onairMeta.innerHTML = live.host+' · '+live.start+' – '+live.end
      +' <span class="genre-tag" style="color:'+genreColor(live.genre)+'">'+live.genre+'</span>'
      +' <span class="genre-tag" style="color:var(--cyan)">'+live.type+'</span>';
```

### Cambio 2026-09-08T01:55
Antes:
```
  const next = getNextProgram();
  document.getElementById('next-name').textContent = next ? next.name : '—';
  document.getElementById('next-meta').innerHTML = next
    ? next.host+' · '+DAY_LABELS_FULL[next.day]+' '+next.start
    : 'No hay más programas esta semana.';

  document.getElementById('stat-total').textContent = data.length;
  const totalMins = data.reduce((sum,p)=>sum+minutesBetween(p.start,p.end),0);
  document.getElementById('stat-hours').textContent = Math.round(totalMins/60)+'h';
  const todK = todayKey();
  document.getElementById('stat-today').textContent = data.filter(p=>p.day===todK).length;
}
```
Después:
```
  const next = getNextProgram();
  document.getElementById('next-name').textContent = next ? next.program.name : '—';
  document.getElementById('next-meta').innerHTML = next
    ? next.program.host+' · '+DAY_LABELS_FULL[next.day]+' '+next.program.start
    : 'No hay más programas esta semana.';

  document.getElementById('stat-total').textContent = data.length;
  const totalMins = weeklyMinutes();
  document.getElementById('stat-hours').textContent = Math.round(totalMins/60)+'h';
  const todK = todayKey();
  document.getElementById('stat-today').textContent = data.filter(p=>isActive(p) && airsOn(p, todK)).length;
  document.getElementById('stat-coverage').textContent = Math.min(100, Math.round(totalMins/(7*24*60)*100))+'%';
}

/* Minutos al aire en toda la semana (cada día de emisión suma su duración). */
function weeklyMinutes(){
  return data.filter(isActive).reduce((sum,p)=>sum+minutesBetween(p.start,p.end)*programDays(p).length, 0);
}
```

### Cambio 2026-09-08T01:55
Antes:
```
function populateGenreSelects(){
  const filterSel = document.getElementById('filter-genre');
  const formSel = document.getElementById('f-genre');
  [filterSel, formSel].forEach(sel=>{
    const keepFirst = sel===filterSel;
    sel.innerHTML = keepFirst ? '<option value="">Todos los géneros</option>' : '';
    Object.keys(GENRES).forEach(g=>{
      const opt = document.createElement('option');
      opt.value = g; opt.textContent = g;
      sel.appendChild(opt);
    });
  });
  const daySel = document.getElementById('f-day');
  daySel.innerHTML = '';
  DAYS.forEach(d=>{
    const opt = document.createElement('option');
    opt.value = d; opt.textContent = DAY_LABELS_FULL[d];
    daySel.appendChild(opt);
  });
}
```
Después:
```
function populateSelects(){
  const filterSel = document.getElementById('filter-genre');
  const formSel = document.getElementById('f-genre');
  [filterSel, formSel].forEach(sel=>{
    const keepFirst = sel===filterSel;
    sel.innerHTML = keepFirst ? '<option value="">Todos los géneros</option>' : '';
    Object.keys(GENRES).forEach(g=>{
      const opt = document.createElement('option');
      opt.value = g; opt.textContent = g;
      sel.appendChild(opt);
    });
  });

  const typeFilter = document.getElementById('filter-type');
  const typeForm = document.getElementById('f-type');
  typeFilter.innerHTML = '<option value="">Todos los tipos</option>';
  typeForm.innerHTML = '';
  TYPES.forEach(t=>{
    [typeFilter, typeForm].forEach(sel=>{
      const opt = document.createElement('option');
      opt.value = t; opt.textContent = t;
      sel.appendChild(opt);
    });
  });
}

/* Casillas de días del formulario: permiten elegir varios de una vez. */
function buildDayPicker(){
  const box = document.getElementById('f-days');
  box.innerHTML = '';
  DAYS.forEach(d=>{
    const label = document.createElement('label');
    label.className = 'day-chip';
    label.innerHTML = '<input type="checkbox" value="'+d+'">'+DAY_LABELS_FULL[d];
    const input = label.querySelector('input');
    input.addEventListener('change', ()=>{
      label.classList.toggle('on', input.checked);
      playClick();
    });
    box.appendChild(label);
  });
}
function getSelectedDays(){
  return Array.from(document.querySelectorAll('#f-days input:checked')).map(i=>i.value);
}
function setSelectedDays(days){
  document.querySelectorAll('#f-days input').forEach(i=>{
    i.checked = days.includes(i.value);
    i.parentElement.classList.toggle('on', i.checked);
  });
}
document.querySelectorAll('.preset-btn').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    playClick();
    const preset = btn.dataset.preset;
    if(preset==='all') setSelectedDays(DAYS.slice());
    else if(preset==='weekdays') setSelectedDays(['lunes','martes','miercoles','jueves','viernes']);
    else if(preset==='weekend') setSelectedDays(['sabado','domingo']);
    else setSelectedDays([]);
  });
});
```

### Cambio 2026-09-08T01:55
Antes:
```
function renderSchedule(){
  const container = document.getElementById('schedule-container');
  const genreFilter = document.getElementById('filter-genre').value;
  container.innerHTML = '';

  const daysToShow = showFullWeek ? DAYS : [currentDay];

  daysToShow.forEach(day=>{
    let programs = data.filter(p=>p.day===day);
    if(genreFilter) programs = programs.filter(p=>p.genre===genreFilter);
    programs.sort((a,b)=>timeToMinutes(a.start)-timeToMinutes(b.start));
```
Después:
```
function renderSchedule(){
  const container = document.getElementById('schedule-container');
  const genreFilter = document.getElementById('filter-genre').value;
  const typeFilter = document.getElementById('filter-type').value;
  const search = document.getElementById('search-input').value.trim().toLowerCase();
  container.innerHTML = '';

  const daysToShow = showFullWeek ? DAYS : [currentDay];

  daysToShow.forEach(day=>{
    const conflicts = conflictIdsForDay(day);
    let programs = data.filter(p=>airsOn(p, day));
    if(genreFilter) programs = programs.filter(p=>p.genre===genreFilter);
    if(typeFilter) programs = programs.filter(p=>p.type===typeFilter);
    if(search) programs = programs.filter(p=>(p.name+' '+p.host+' '+(p.notes||'')).toLowerCase().includes(search));
    programs.sort((a,b)=>timeToMinutes(a.start)-timeToMinutes(b.start));
```

### Cambio 2026-09-08T01:56
Antes:
```
    if(programs.length===0){
      const empty = document.createElement('div');
      empty.className = 'empty-msg';
      empty.textContent = 'No hay programas asignados para este día.';
      list.appendChild(empty);
    }else{
      const live = getCurrentProgram();
      programs.forEach(p=>{
        const card = document.createElement('div');
        card.className = 'program-card'+(live && live.id===p.id ? ' live':'');
        card.innerHTML = `
          <div class="program-time">${p.start} – ${p.end}<small>${formatHoursLabel(minutesBetween(p.start,p.end))}</small></div>
          <div class="program-info">
            <h4>${escapeHtml(p.name)}</h4>
            <div class="host">${escapeHtml(p.host)}</div>
            ${p.notes ? `<div class="notes">${escapeHtml(p.notes)}</div>` : ''}
            <span class="genre-tag" style="color:${GENRES[p.genre].color}">${p.genre}</span>
          </div>
          <div class="program-actions">
            <button class="icon-btn" data-action="edit" data-id="${p.id}" title="Editar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
            </button>
            <button class="icon-btn" data-action="delete" data-id="${p.id}" title="Eliminar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M8 6V4h8v2m-1 0v14H9V6h6zM10 11v6M14 11v6"/></svg>
            </button>
          </div>`;
        list.appendChild(card);
      });
    }
    container.appendChild(list);
  });

  container.querySelectorAll('[data-action="edit"]').forEach(b=>b.addEventListener('click', ()=>{ playClick(); openEditModal(b.dataset.id); }));
  container.querySelectorAll('[data-action="delete"]').forEach(b=>b.addEventListener('click', ()=>{ playClick(); openConfirmDelete(b.dataset.id); }));
}
```
Después:
```
    if(programs.length===0){
      const empty = document.createElement('div');
      empty.className = 'empty-msg';
      empty.textContent = (genreFilter || typeFilter || search)
        ? 'Ningún programa coincide con el filtro en este día.'
        : 'No hay programas asignados para este día.';
      list.appendChild(empty);
    }else{
      const live = getCurrentProgram();
      programs.forEach(p=>{
        const inConflict = conflicts.has(p.id);
        const card = document.createElement('div');
        card.className = 'program-card'
          + (live && live.id===p.id ? ' live':'')
          + (isActive(p) ? '' : ' paused')
          + (inConflict ? ' conflict':'');
        card.innerHTML = `
          <div class="program-time">${p.start} – ${p.end}<small>${formatHoursLabel(minutesBetween(p.start,p.end))}</small></div>
          <div class="program-info">
            <h4>${escapeHtml(p.name)}</h4>
            <div class="host">${escapeHtml(p.host)}</div>
            ${p.notes ? `<div class="notes">${escapeHtml(p.notes)}</div>` : ''}
            <span class="genre-tag" style="color:${genreColor(p.genre)}">${escapeHtml(p.genre)}</span>
            <span class="badge type">${escapeHtml(p.type)}</span>
            <span class="badge days">${escapeHtml(daysSummary(p))}</span>
            ${isActive(p) ? '' : '<span class="badge paused">Pausado</span>'}
            ${inConflict ? '<span class="badge conflict">Cruce de horario</span>' : ''}
          </div>
          <div class="program-actions">
            <button class="icon-btn" data-action="toggle" data-id="${p.id}" title="${isActive(p)?'Pausar':'Reactivar'}">
              ${isActive(p)
                ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 4v16M14 4v16"/></svg>'
                : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 4l14 8-14 8V4z"/></svg>'}
            </button>
            <button class="icon-btn" data-action="duplicate" data-id="${p.id}" title="Duplicar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="12" height="12" rx="1"/><path d="M5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1"/></svg>
            </button>
            <button class="icon-btn" data-action="edit" data-id="${p.id}" title="Editar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
            </button>
            <button class="icon-btn" data-action="delete" data-id="${p.id}" title="Eliminar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M8 6V4h8v2m-1 0v14H9V6h6zM10 11v6M14 11v6"/></svg>
            </button>
          </div>`;
        list.appendChild(card);
      });
    }
    container.appendChild(list);
  });

  container.querySelectorAll('[data-action="edit"]').forEach(b=>b.addEventListener('click', ()=>{ playClick(); openEditModal(b.dataset.id); }));
  container.querySelectorAll('[data-action="delete"]').forEach(b=>b.addEventListener('click', ()=>{ playClick(); openConfirmDelete(b.dataset.id); }));
  container.querySelectorAll('[data-action="duplicate"]').forEach(b=>b.addEventListener('click', ()=>{ playClick(); duplicateProgram(b.dataset.id); }));
  container.querySelectorAll('[data-action="toggle"]').forEach(b=>b.addEventListener('click', ()=>{ playClick(); toggleProgramStatus(b.dataset.id); }));
}

/* Duplica un programa y abre el formulario para ajustar la copia. */
function duplicateProgram(id){
  const p = data.find(x=>x.id===id);
  if(!p) return;
  const copy = {...p, id:crypto.randomUUID(), days:programDays(p).slice(), name:p.name+' (copia)'};
  data.push(copy);
  saveData();
  renderSchedule();
  renderDashboard();
  showMissionBanner('PROGRAMA DUPLICADO');
  openEditModal(copy.id);
}

function toggleProgramStatus(id){
  const p = data.find(x=>x.id===id);
  if(!p) return;
  p.status = isActive(p) ? 'pausado' : 'activo';
  saveData();
  renderSchedule();
  renderDashboard();
  showMissionBanner(isActive(p) ? 'PROGRAMA REACTIVADO' : 'PROGRAMA PAUSADO');
}
```

### Cambio 2026-09-08T01:56
Antes:
```
function renderStats(){
  const dayCounts = DAYS.map(d=>({day:d, count:data.filter(p=>p.day===d).length}));
```
Después:
```
function renderStats(){
  const dayCounts = DAYS.map(d=>({day:d, count:data.filter(p=>airsOn(p,d)).length}));
```

### Cambio 2026-09-08T01:56
Antes:
```
  data.forEach(p=>{ genreHours[p.genre] = (genreHours[p.genre]||0) + minutesBetween(p.start,p.end); });
```
Después:
```
  data.forEach(p=>{
    genreHours[p.genre] = (genreHours[p.genre]||0) + minutesBetween(p.start,p.end)*programDays(p).length;
  });
```

### Cambio 2026-09-08T01:56
Antes:
```
    barsGenre.innerHTML += `<div class="bar-row">
      <div class="bar-label" style="color:${GENRES[g].color}">${g}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${(mins/maxGenre*100)}%; background:${GENRES[g].color}"></div></div>
```
Después:
```
    barsGenre.innerHTML += `<div class="bar-row">
      <div class="bar-label" style="color:${genreColor(g)}">${g}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${(mins/maxGenre*100)}%; background:${genreColor(g)}"></div></div>
```

### Cambio 2026-09-08T01:56
Antes:
```
function openAddModal(){
  document.getElementById('form-title').textContent = 'NUEVO PROGRAMA';
  document.getElementById('program-form').reset();
  document.getElementById('f-id').value = '';
  document.getElementById('f-day').value = currentDay;
  document.getElementById('form-error').style.display='none';
  document.getElementById('form-overlay').classList.add('show');
}
function openEditModal(id){
  const p = data.find(x=>x.id===id);
  if(!p) return;
  document.getElementById('form-title').textContent = 'EDITAR PROGRAMA';
  document.getElementById('f-id').value = p.id;
  document.getElementById('f-name').value = p.name;
  document.getElementById('f-host').value = p.host;
  document.getElementById('f-day').value = p.day;
  document.getElementById('f-start').value = p.start;
  document.getElementById('f-end').value = p.end;
  document.getElementById('f-genre').value = p.genre;
  document.getElementById('f-notes').value = p.notes||'';
  document.getElementById('form-error').style.display='none';
  document.getElementById('form-overlay').classList.add('show');
}
```
Después:
```
function openAddModal(){
  document.getElementById('form-title').textContent = 'NUEVO PROGRAMA';
  document.getElementById('program-form').reset();
  document.getElementById('f-id').value = '';
  document.getElementById('f-type').value = TYPES[0];
  document.getElementById('f-status').value = 'activo';
  setSelectedDays([currentDay]);
  document.getElementById('form-error').style.display='none';
  document.getElementById('form-overlay').classList.add('show');
}
function openEditModal(id){
  const p = data.find(x=>x.id===id);
  if(!p) return;
  document.getElementById('form-title').textContent = 'EDITAR PROGRAMA';
  document.getElementById('f-id').value = p.id;
  document.getElementById('f-name').value = p.name;
  document.getElementById('f-host').value = p.host;
  setSelectedDays(programDays(p));
  document.getElementById('f-start').value = p.start;
  document.getElementById('f-end').value = p.end;
  document.getElementById('f-genre').value = p.genre;
  document.getElementById('f-type').value = p.type;
  document.getElementById('f-status').value = p.status;
  document.getElementById('f-notes').value = p.notes||'';
  document.getElementById('form-error').style.display='none';
  document.getElementById('form-overlay').classList.add('show');
}
```

### Cambio 2026-09-08T01:56
Antes:
```
  const id = document.getElementById('f-id').value;
  const name = document.getElementById('f-name').value.trim();
  const host = document.getElementById('f-host').value.trim();
  const day = document.getElementById('f-day').value;
  const start = document.getElementById('f-start').value;
  const end = document.getElementById('f-end').value;
  const genre = document.getElementById('f-genre').value;
  const notes = document.getElementById('f-notes').value.trim();
  const errorBox = document.getElementById('form-error');

  if(!name || !host || !start || !end){
    errorBox.textContent = 'COMPLETA TODOS LOS CAMPOS OBLIGATORIOS.';
    errorBox.style.display = 'block';
    document.getElementById('form-modal').classList.add('shake');
    setTimeout(()=>document.getElementById('form-modal').classList.remove('shake'),300);
    playError();
    return;
  }
  if(start === end){
    errorBox.textContent = 'LA HORA DE INICIO Y FIN NO PUEDEN SER IGUALES.';
    errorBox.style.display = 'block';
    playError();
    return;
  }

  if(id){
    const p = data.find(x=>x.id===id);
    Object.assign(p, {name,host,day,start,end,genre,notes});
  }else{
    data.push({id:crypto.randomUUID(), name,host,day,start,end,genre,notes});
  }
  saveData();
  closeFormModal();
  currentDay = day;
  buildDayTabs();
  renderSchedule();
  renderDashboard();
  showMissionBanner(id ? 'PROGRAMA ACTUALIZADO' : 'PROGRAMA AÑADIDO');
});
```
Después:
```
  const id = document.getElementById('f-id').value;
  const name = document.getElementById('f-name').value.trim();
  const host = document.getElementById('f-host').value.trim();
  const days = getSelectedDays();
  const start = document.getElementById('f-start').value;
  const end = document.getElementById('f-end').value;
  const genre = document.getElementById('f-genre').value;
  const type = document.getElementById('f-type').value;
  const status = document.getElementById('f-status').value;
  const notes = document.getElementById('f-notes').value.trim();
  const errorBox = document.getElementById('form-error');

  const fail = (msg)=>{
    errorBox.textContent = msg;
    errorBox.style.display = 'block';
    document.getElementById('form-modal').classList.add('shake');
    setTimeout(()=>document.getElementById('form-modal').classList.remove('shake'),300);
    playError();
  };

  if(!name || !host || !start || !end){ fail('COMPLETA TODOS LOS CAMPOS OBLIGATORIOS.'); return; }
  if(days.length === 0){ fail('SELECCIONA AL MENOS UN DÍA DE EMISIÓN.'); return; }
  if(start === end){ fail('LA HORA DE INICIO Y FIN NO PUEDEN SER IGUALES.'); return; }

  if(id){
    const p = data.find(x=>x.id===id);
    Object.assign(p, {name,host,days,start,end,genre,type,status,notes});
  }else{
    data.push({id:crypto.randomUUID(), name,host,days,start,end,genre,type,status,notes});
  }
  saveData();
  closeFormModal();
  if(!days.includes(currentDay)) currentDay = days[0];
  buildDayTabs();
  renderSchedule();
  renderDashboard();
  renderStats();

  // Aviso si el nuevo horario choca con otro programa en alguno de sus días
  const savedId = id || data[data.length-1].id;
  const clashDays = days.filter(d=>conflictIdsForDay(d).has(savedId));
  if(clashDays.length){
    showMissionBanner('CRUCE DE HORARIO EN '+clashDays.map(d=>DAY_LABELS[d].toUpperCase()).join(', '));
  }else{
    showMissionBanner(id ? 'PROGRAMA ACTUALIZADO' : 'PROGRAMA AÑADIDO EN '+days.length+(days.length===1?' DÍA':' DÍAS'));
  }
});
```

### Cambio 2026-09-08T01:56
Antes:
```
  DAYS.forEach(day=>{
    const programs = data.filter(p=>p.day===day).sort((a,b)=>timeToMinutes(a.start)-timeToMinutes(b.start));
```
Después:
```
  DAYS.forEach(day=>{
    const programs = data.filter(p=>airsOn(p, day)).sort((a,b)=>timeToMinutes(a.start)-timeToMinutes(b.start));
```

### Cambio 2026-09-08T01:57
Antes:
```
        doc.setFont('helvetica','normal');
        doc.setFontSize(9);
        doc.setTextColor(100,100,100);
        doc.text('('+p.genre+')', marginX+320, y);
        y += 13;
        doc.setFontSize(9.5);
        doc.setTextColor(70,70,70);
        doc.text('Locutor: '+p.host, marginX+100, y);
        y += 12;
```
Después:
```
        doc.setFont('helvetica','normal');
        doc.setFontSize(9);
        doc.setTextColor(100,100,100);
        doc.text('('+p.genre+' · '+p.type+(isActive(p)?'':' · PAUSADO')+')', marginX+320, y);
        y += 13;
        doc.setFontSize(9.5);
        doc.setTextColor(70,70,70);
        doc.text('Locutor: '+p.host+'   ·   Emite: '+daysSummary(p), marginX+100, y);
        y += 12;
```

### Cambio 2026-09-08T01:57
Antes:
```
  const totalMins = data.reduce((s,p)=>s+minutesBetween(p.start,p.end),0);
  if(y > 740){ doc.addPage(); y = 50; }
  doc.setDrawColor(120,220,60);
  doc.line(marginX, y, pageWidth-marginX, y);
  y += 18;
  doc.setFont('helvetica','bold');
  doc.setFontSize(10);
  doc.setTextColor(20,20,20);
  doc.text('Total de programas: '+data.length+'   ·   Horas programadas: '+Math.round(totalMins/60)+'h', marginX, y);

  doc.save('programacion-radio-'+dateFile+'.pdf');
  showMissionBanner('PDF EXPORTADO');
}
```
Después:
```
  const totalMins = weeklyMinutes();
  if(y > 740){ doc.addPage(); y = 50; }
  doc.setDrawColor(120,220,60);
  doc.line(marginX, y, pageWidth-marginX, y);
  y += 18;
  doc.setFont('helvetica','bold');
  doc.setFontSize(10);
  doc.setTextColor(20,20,20);
  doc.text('Total de programas: '+data.length+'   ·   Horas al aire por semana: '+Math.round(totalMins/60)+'h', marginX, y);

  doc.save('programacion-radio-'+dateFile+'.pdf');
  showMissionBanner('PDF EXPORTADO');
}

/* =========================================================
   COPIA DE SEGURIDAD (JSON)
========================================================= */
function exportJSON(){
  const blob = new Blob([JSON.stringify(data, null, 2)], {type:'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'parrilla-radio-'+new Date().toISOString().slice(0,10)+'.json';
  a.click();
  URL.revokeObjectURL(url);
  showMissionBanner('COPIA GUARDADA');
}

function importJSON(file){
  const reader = new FileReader();
  reader.onload = ()=>{
    try{
      const parsed = JSON.parse(reader.result);
      if(!Array.isArray(parsed) || parsed.length===0) throw new Error('formato');
      data = parsed.map(normalizeProgram);
      saveData();
      buildDayTabs();
      renderSchedule();
      renderDashboard();
      renderStats();
      showMissionBanner('PARRILLA RESTAURADA');
    }catch(e){
      playError();
      showMissionBanner('ARCHIVO NO VÁLIDO');
    }
  };
  reader.readAsText(file);
}
```

### Cambio 2026-09-08T01:57
Antes:
```
document.getElementById('filter-genre').addEventListener('change', renderSchedule);
```
Después:
```
document.getElementById('filter-genre').addEventListener('change', renderSchedule);
document.getElementById('filter-type').addEventListener('change', renderSchedule);
document.getElementById('search-input').addEventListener('input', renderSchedule);

document.getElementById('nav-backup').addEventListener('click', ()=>{ playNav(); exportJSON(); });
document.getElementById('nav-import').addEventListener('click', ()=>{ playNav(); document.getElementById('import-file').click(); });
document.getElementById('import-file').addEventListener('change', (e)=>{
  if(e.target.files[0]) importJSON(e.target.files[0]);
  e.target.value = '';
});
```

### Cambio 2026-09-08T01:57
Antes:
```
function init(){
  populateGenreSelects();
  buildDayTabs();
```
Después:
```
function init(){
  populateSelects();
  buildDayPicker();
  buildDayTabs();
```

### Cambio 2026-09-08T02:03
Antes:
```
  .hint{font-family:var(--font-mono); font-size:10px; color:var(--gray); letter-spacing:1px; margin-top:7px; line-height:1.5;}
```
Después:
```
  .hint{font-family:var(--font-mono); font-size:10px; color:var(--gray); letter-spacing:1px; margin-top:7px; line-height:1.5;}

  /* ============ SELECTOR DE ETIQUETAS (géneros) ============ */
  .tag-picker{display:flex; flex-wrap:wrap; gap:6px;}
  .tag-chip{
    position:relative; padding:8px 12px; background:var(--black); border:1px solid var(--line);
    color:var(--gray); font-family:var(--font-mono); font-size:11px; letter-spacing:1px;
    text-transform:uppercase; user-select:none; cursor:pointer; transition:all .12s ease;
  }
  .tag-chip input{position:absolute; opacity:0; pointer-events:none;}
  .tag-chip:hover{color:var(--c); border-color:var(--c);}
  .tag-chip.on{background:var(--c); border-color:var(--c); color:var(--black); font-weight:bold;}
```

### Cambio 2026-09-08T02:03
Antes:
```
        <div class="field-row">
          <div class="field">
            <label>Género</label>
            <select id="f-genre" required></select>
          </div>
          <div class="field">
            <label>Tipo de emisión</label>
            <select id="f-type"></select>
          </div>
        </div>
        <div class="field">
          <label>Estado</label>
          <select id="f-status">
            <option value="activo">Activo — sale al aire</option>
            <option value="pausado">Pausado — no sale al aire</option>
          </select>
        </div>
```
Después:
```
        <div class="field">
          <label>Géneros / etiquetas</label>
          <div class="tag-picker" id="f-genres"></div>
          <div class="hint">Marca todas las etiquetas que apliquen: un programa puede ser 80s y Conversación a la vez.</div>
        </div>
        <div class="field-row">
          <div class="field">
            <label>Tipo de emisión</label>
            <select id="f-type"></select>
          </div>
          <div class="field">
            <label>Estado</label>
            <select id="f-status">
              <option value="activo">Activo — sale al aire</option>
              <option value="pausado">Pausado — no sale al aire</option>
            </select>
          </div>
        </div>
```

### Cambio 2026-09-08T02:03
Antes:
```
/* La radio emite solo 80s y 90s: la paleta de géneros se reduce a esa línea editorial. */
const GENRES = {
  'Rock':        {color:'#7CFC3C'},
  'Pop':         {color:'#34d8d8'},
  '80s':         {color:'#ff2e63'},
  '90s':         {color:'#b892ff'},
  'Misceláneo':  {color:'#ff8a3d'},
  'Matinal':     {color:'#ffcc00'}
};

/* Equivalencias para parrillas guardadas con la lista de géneros antigua. */
const GENRE_MIGRATION = {
  'Electronica':'Misceláneo', 'Electrónica':'Misceláneo', 'Talk Show':'Misceláneo',
  'Urbano':'90s', 'Clasicos':'80s', 'Clásicos':'80s', 'Noticias':'Matinal'
};
```
Después:
```
/* Etiquetas disponibles. Un programa puede llevar varias a la vez. */
const GENRES = {
  'Rock':         {color:'#7CFC3C'},
  'Pop':          {color:'#34d8d8'},
  '80s':          {color:'#ff2e63'},
  '90s':          {color:'#b892ff'},
  'Conversación': {color:'#eef1ea'},
  'Deportes':     {color:'#5aa9ff'},
  'Noticias':     {color:'#ff4fd8'},
  'Misceláneo':   {color:'#ff8a3d'},
  'Matinal':      {color:'#ffcc00'}
};

/* Equivalencias para parrillas guardadas con la lista de géneros antigua. */
const GENRE_MIGRATION = {
  'Electronica':'Misceláneo', 'Electrónica':'Misceláneo',
  'Talk Show':'Conversación', 'Urbano':'90s', 'Clasicos':'80s', 'Clásicos':'80s'
};
```

### Cambio 2026-09-08T02:03
Antes:
```
    {name:'Matinal Emerge', host:'Elena Cruz', days:['lunes','martes','miercoles','jueves','viernes'], start:'07:00', end:'09:00', genre:'Matinal', type:'En vivo', notes:'Arranque del día: saludos, panorama y clásicos suaves.'},
    {name:'Ruta 80', host:'Tito Reyes', days:['lunes','miercoles','viernes'], start:'18:00', end:'20:00', genre:'80s', type:'En vivo', notes:'Lo mejor de la década de los ochenta, sin relleno.'},
    {name:'Década 90', host:'Caro Núñez', days:['martes','jueves'], start:'18:00', end:'20:00', genre:'90s', type:'En vivo', notes:'Los noventa en su mejor momento.'},
    {name:'Zona Rock', host:'Hugo Paredes', days:['jueves','viernes'], start:'21:00', end:'23:00', genre:'Rock', type:'En vivo', notes:'Rock clásico de los 80 y 90.'},
    {name:'Pop Total', host:'Caro Núñez', days:['lunes','martes','miercoles','jueves','viernes'], start:'15:00', end:'17:00', genre:'Pop', type:'Grabado', notes:''},
    {name:'Misceláneo Nocturno', host:'DJ Marín', days:['lunes','martes','miercoles','jueves'], start:'23:00', end:'01:00', genre:'Misceláneo', type:'Automatizado', notes:'Selección libre para la madrugada.'},
    {name:'Sábado Retro', host:'Tito Reyes', days:['sabado'], start:'10:00', end:'13:00', genre:'80s', type:'En vivo', notes:'Especial de fin de semana con pedidos del público.'},
    {name:'Domingo 90', host:'Hugo Paredes', days:['domingo'], start:'11:00', end:'14:00', genre:'90s', type:'Grabado', notes:''}
```
Después:
```
    {name:'Matinal Emerge', host:'Elena Cruz', days:['lunes','martes','miercoles','jueves','viernes'], start:'07:00', end:'09:00', genres:['Matinal','Conversación','Noticias'], type:'En vivo', notes:'Arranque del día: saludos, panorama y clásicos suaves.'},
    {name:'Ruta 80', host:'Tito Reyes', days:['lunes','miercoles','viernes'], start:'18:00', end:'20:00', genres:['80s'], type:'En vivo', notes:'Lo mejor de la década de los ochenta, sin relleno.'},
    {name:'Década 90', host:'Caro Núñez', days:['martes','jueves'], start:'18:00', end:'20:00', genres:['90s','Pop'], type:'En vivo', notes:'Los noventa en su mejor momento.'},
    {name:'Zona Rock', host:'Hugo Paredes', days:['jueves','viernes'], start:'21:00', end:'23:00', genres:['Rock','80s','90s'], type:'En vivo', notes:'Rock clásico de los 80 y 90.'},
    {name:'Pop Total', host:'Caro Núñez', days:['lunes','martes','miercoles','jueves','viernes'], start:'15:00', end:'17:00', genres:['Pop'], type:'Grabado', notes:''},
    {name:'Tiempo Extra', host:'Rodrigo Iban', days:['lunes','miercoles','viernes'], start:'13:00', end:'14:00', genres:['Deportes','Conversación'], type:'En vivo', notes:'Comentario deportivo y llamados del público.'},
    {name:'Misceláneo Nocturno', host:'DJ Marín', days:['lunes','martes','miercoles','jueves'], start:'23:00', end:'01:00', genres:['Misceláneo'], type:'Automatizado', notes:'Selección libre para la madrugada.'},
    {name:'Sábado Retro', host:'Tito Reyes', days:['sabado'], start:'10:00', end:'13:00', genres:['80s','90s'], type:'En vivo', notes:'Especial de fin de semana con pedidos del público.'},
    {name:'Domingo 90', host:'Hugo Paredes', days:['domingo'], start:'11:00', end:'14:00', genres:['90s'], type:'Grabado', notes:''}
```

### Cambio 2026-09-08T02:03
Antes:
```
/* Normaliza un programa: día único -> arreglo de días, géneros antiguos, tipo y estado. */
function normalizeProgram(p){
  const days = Array.isArray(p.days) ? p.days.filter(d=>DAYS.includes(d)) : (DAYS.includes(p.day) ? [p.day] : []);
  let genre = p.genre;
  if(GENRE_MIGRATION[genre]) genre = GENRE_MIGRATION[genre];
  if(!GENRES[genre]) genre = 'Misceláneo';
  return {
    id: p.id || crypto.randomUUID(),
    name: String(p.name||'Sin nombre'),
    host: String(p.host||''),
    days: days.length ? days : [DAYS[0]],
    start: p.start || '00:00',
    end: p.end || '01:00',
    genre,
    type: TYPES.includes(p.type) ? p.type : 'En vivo',
    status: p.status === 'pausado' ? 'pausado' : 'activo',
    notes: p.notes || ''
  };
}
```
Después:
```
/* Normaliza un programa: día único -> arreglo de días, género único -> arreglo de etiquetas. */
function normalizeProgram(p){
  const days = Array.isArray(p.days) ? p.days.filter(d=>DAYS.includes(d)) : (DAYS.includes(p.day) ? [p.day] : []);
  const raw = Array.isArray(p.genres) ? p.genres : (p.genre ? [p.genre] : []);
  const genres = [...new Set(raw.map(g=>GENRE_MIGRATION[g] || g).filter(g=>GENRES[g]))];
  return {
    id: p.id || crypto.randomUUID(),
    name: String(p.name||'Sin nombre'),
    host: String(p.host||''),
    days: days.length ? days : [DAYS[0]],
    start: p.start || '00:00',
    end: p.end || '01:00',
    genres: genres.length ? sortGenres(genres) : ['Misceláneo'],
    type: TYPES.includes(p.type) ? p.type : 'En vivo',
    status: p.status === 'pausado' ? 'pausado' : 'activo',
    notes: p.notes || ''
  };
}
```

### Cambio 2026-09-08T02:03
Antes:
```
/* ---- Helpers del modelo ---- */
function programDays(p){ return Array.isArray(p.days) ? p.days : []; }
function isActive(p){ return p.status !== 'pausado'; }
function genreColor(g){ return (GENRES[g] && GENRES[g].color) || 'var(--gray)'; }
```
Después:
```
/* ---- Helpers del modelo ---- */
function programDays(p){ return Array.isArray(p.days) ? p.days : []; }
function programGenres(p){ return Array.isArray(p.genres) ? p.genres : (p.genre ? [p.genre] : []); }
function sortGenres(list){ return Object.keys(GENRES).filter(g=>list.includes(g)); }
function hasGenre(p, g){ return programGenres(p).includes(g); }
function genresTagsHtml(p){
  return programGenres(p)
    .map(g=>`<span class="genre-tag" style="color:${genreColor(g)}">${escapeHtml(g)}</span>`)
    .join('');
}
function isActive(p){ return p.status !== 'pausado'; }
function genreColor(g){ return (GENRES[g] && GENRES[g].color) || 'var(--gray)'; }
```

### Cambio 2026-09-08T02:04
Antes:
```
    padding:3px 9px; border:1px solid currentColor; margin-top:8px; text-transform:uppercase;
```
Después:
```
    padding:3px 9px; border:1px solid currentColor; margin-top:8px; margin-right:6px; text-transform:uppercase;
```

### Cambio 2026-09-08T02:04
Antes:
```
function populateSelects(){
  const filterSel = document.getElementById('filter-genre');
  const formSel = document.getElementById('f-genre');
  [filterSel, formSel].forEach(sel=>{
    const keepFirst = sel===filterSel;
    sel.innerHTML = keepFirst ? '<option value="">Todos los géneros</option>' : '';
    Object.keys(GENRES).forEach(g=>{
      const opt = document.createElement('option');
      opt.value = g; opt.textContent = g;
      sel.appendChild(opt);
    });
  });

  const typeFilter
```
Después:
```
function populateSelects(){
  const filterSel = document.getElementById('filter-genre');
  filterSel.innerHTML = '<option value="">Todas las etiquetas</option>';
  Object.keys(GENRES).forEach(g=>{
    const opt = document.createElement('option');
    opt.value = g; opt.textContent = g;
    filterSel.appendChild(opt);
  });

  const typeFilter
```

### Cambio 2026-09-08T02:04
Antes:
```
function getSelectedDays(){
  return Array.from(document.querySelectorAll('#f-days input:checked')).map(i=>i.value);
}
```
Después:
```
/* Casillas de etiquetas del formulario: un programa puede llevar varias. */
function buildGenrePicker(){
  const box = document.getElementById('f-genres');
  box.innerHTML = '';
  Object.keys(GENRES).forEach(g=>{
    const label = document.createElement('label');
    label.className = 'tag-chip';
    label.style.setProperty('--c', GENRES[g].color);
    label.innerHTML = '<input type="checkbox" value="'+g+'">'+g;
    const input = label.querySelector('input');
    input.addEventListener('change', ()=>{
      label.classList.toggle('on', input.checked);
      playClick();
    });
    box.appendChild(label);
  });
}
function getSelectedGenres(){
  return Array.from(document.querySelectorAll('#f-genres input:checked')).map(i=>i.value);
}
function setSelectedGenres(genres){
  document.querySelectorAll('#f-genres input').forEach(i=>{
    i.checked = genres.includes(i.value);
    i.parentElement.classList.toggle('on', i.checked);
  });
}

function getSelectedDays(){
  return Array.from(document.querySelectorAll('#f-days input:checked')).map(i=>i.value);
}
```

### Cambio 2026-09-08T02:04
Antes:
```
      +' <span class="genre-tag" style="color:'+genreColor(live.genre)+'">'+live.genre+'</span>'
      +' <span class="genre-tag" style="color:var(--cyan)">'+live.type+'</span>';
```
Después:
```
      +' ' + genresTagsHtml(live)
      +'<span class="genre-tag" style="color:var(--cyan)">'+live.type+'</span>';
```

### Cambio 2026-09-08T02:04
Antes:
```
    if(genreFilter) programs = programs.filter(p=>p.genre===genreFilter);
```
Después:
```
    if(genreFilter) programs = programs.filter(p=>hasGenre(p, genreFilter));
```

### Cambio 2026-09-08T02:04
Antes:
```
            <span class="genre-tag" style="color:${genreColor(p.genre)}">${escapeHtml(p.genre)}</span>
            <span class="badge type">${escapeHtml(p.type)}</span>
```
Después:
```
            ${genresTagsHtml(p)}
            <span class="badge type">${escapeHtml(p.type)}</span>
```

### Cambio 2026-09-08T02:04
Antes:
```
  data.forEach(p=>{
    genreHours[p.genre] = (genreHours[p.genre]||0) + minutesBetween(p.start,p.end)*programDays(p).length;
  });
```
Después:
```
  // Un programa con varias etiquetas suma sus horas en cada una de ellas.
  data.forEach(p=>{
    const mins = minutesBetween(p.start,p.end)*programDays(p).length;
    programGenres(p).forEach(g=>{ genreHours[g] = (genreHours[g]||0) + mins; });
  });
```

### Cambio 2026-09-08T02:04
Antes:
```
  document.getElementById('f-genre').value = p.genre;
  document.getElementById('f-type').value = p.type;
```
Después:
```
  setSelectedGenres(programGenres(p));
  document.getElementById('f-type').value = p.type;
```

### Cambio 2026-09-08T02:04
Antes:
```
  document.getElementById('f-type').value = TYPES[0];
  document.getElementById('f-status').value = 'activo';
  setSelectedDays([currentDay]);
```
Después:
```
  document.getElementById('f-type').value = TYPES[0];
  document.getElementById('f-status').value = 'activo';
  setSelectedDays([currentDay]);
  setSelectedGenres([]);
```

### Cambio 2026-09-08T02:04
Antes:
```
  const genre = document.getElementById('f-genre').value;
  const type = document.getElementById('f-type').value;
```
Después:
```
  const genres = sortGenres(getSelectedGenres());
  const type = document.getElementById('f-type').value;
```

### Cambio 2026-09-08T02:04
Antes:
```
  if(days.length === 0){ fail('SELECCIONA AL MENOS UN DÍA DE EMISIÓN.'); return; }
```
Después:
```
  if(days.length === 0){ fail('SELECCIONA AL MENOS UN DÍA DE EMISIÓN.'); return; }
  if(genres.length === 0){ fail('SELECCIONA AL MENOS UNA ETIQUETA DE GÉNERO.'); return; }
```

### Cambio 2026-09-08T02:04
Antes:
```
name,host,days,start,end,genre,type,status,notes
```
Después:
```
name,host,days,start,end,genres,type,status,notes
```

### Cambio 2026-09-08T02:04
Antes:
```
  const copy = {...p, id:crypto.randomUUID(), days:programDays(p).slice(), name:p.name+' (copia)'};
```
Después:
```
  const copy = {...p, id:crypto.randomUUID(), days:programDays(p).slice(), genres:programGenres(p).slice(), name:p.name+' (copia)'};
```

### Cambio 2026-09-08T02:04
Antes:
```
        doc.text('('+p.genre+' · '+p.type+(isActive(p)?'':' · PAUSADO')+')', marginX+320, y);
```
Después:
```
        doc.text('('+programGenres(p).join(' · ')+' · '+p.type+(isActive(p)?'':' · PAUSADO')+')', marginX+320, y);
```

### Cambio 2026-09-08T02:04
Antes:
```
  populateSelects();
  buildDayPicker();
```
Después:
```
  populateSelects();
  buildDayPicker();
  buildGenrePicker();
```