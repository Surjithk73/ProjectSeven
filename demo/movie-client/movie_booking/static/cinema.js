const $ = selector => document.querySelector(selector);
let shows = [], current, selected = new Set(), key = crypto.randomUUID(), selectionRevision = 0, bookingInFlight = false;
function setBookingBusy(value){bookingInFlight=value;document.querySelectorAll(".show").forEach(button=>button.disabled=value);document.querySelectorAll(".seats button").forEach(button=>button.disabled=value||button.dataset.available==="false");}
const money = paise => new Intl.NumberFormat('en-IN', {style:'currency',currency:'INR'}).format(paise / 100);
function notice(message='') { $('#notice').textContent = message; $('#notice').hidden = !message; }
async function api(path, body) {
  const response = await fetch(path, body === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) throw new Error(`${typeof data.detail === 'string' ? data.detail : 'This action could not be completed.'} ${data.recovery || ''}`);
  return data;
}
function element(tag, text, className) { const node = document.createElement(tag); node.textContent=text; if(className) node.className=className; return node; }
function summary() {
  $('#summary-movie').textContent=current?.movie || 'Choose a movie';
  $('#summary-time').textContent=current?.time || '—';
  $('#summary-seats').textContent=[...selected].sort().join(', ') || 'None selected';
  $('#summary-total').textContent=money((current?.price_paise || 0)*selected.size);
  $('#book').disabled=!selected.size;
}
async function choose(show) {
  if(bookingInFlight)return;
  const revision=++selectionRevision;
  current=show; selected.clear(); key=crypto.randomUUID(); summary(); notice(); $('#confirmation').hidden=true;
  document.querySelectorAll('.show').forEach(node=>node.classList.toggle('selected',node.dataset.id===show.id));
  $('#selection-description').textContent=`${show.theatre} · ${show.time} · ${money(show.price_paise)} per seat`;
  $('#seats').replaceChildren(element('p','Loading seats…'));
  try {
    const seats=await api(`/api/shows/${encodeURIComponent(show.id)}/seats`);
    if(revision!==selectionRevision)return;
    $('#seats').replaceChildren();
    seats.forEach(seat=>{const button=element('button',seat.id);button.disabled=!seat.available;button.dataset.available=String(seat.available);button.setAttribute('aria-label',`Seat ${seat.id}${seat.available?'':' · unavailable'}`);button.setAttribute('aria-pressed','false');button.onclick=()=>{if(selected.has(seat.id))selected.delete(seat.id);else if(selected.size<8)selected.add(seat.id);button.classList.toggle('selected',selected.has(seat.id));button.setAttribute('aria-pressed',String(selected.has(seat.id)));key=crypto.randomUUID();summary();};$('#seats').append(button);});
  } catch(error){if(revision===selectionRevision){$('#seats').replaceChildren();notice(error.message);}}
}
async function load() {
  try {
    const [health, providers] = await Promise.all([api('/health'),api('/api/providers')]);
    $('#revision').textContent=`Release ${health.revision.slice(0,12)}`;
    $('#provider-list').replaceChildren();
    providers.forEach(provider=>{
      const card=element('article','','provider');card.append(element('h2',provider.id==='payment'?'CinemaPay':'Grand Cinema'));
      card.append(element('span',provider.version?`V${provider.version} · ${provider.status}`:'Unreachable','version'));
      card.append(element('p',provider.id==='payment'?'Simulated GPay-style payments, exact paise and idempotent transactions.':'Showtimes, available seats, time-limited holds and booking confirmations.'));
      const controls=element('div','','provider-buttons');
      [1,2].forEach(version=>{const button=element('button',`Use V${version}`,provider.version===version?'active':'');button.onclick=async()=>{button.disabled=true;try{await api(`/api/providers/${provider.id}/version`,{version});notice();await load();}catch(error){notice(error.message);}finally{button.disabled=false;}};controls.append(button);});card.append(controls);$('#provider-list').append(card);
    });
    shows=await api('/api/shows');$('#shows').replaceChildren();
    shows.forEach(show=>{const button=element('button','','show');button.dataset.id=show.id;const poster=element('div','','poster');poster.append(element('small','GRAND CINEMA PRESENTS'),element('strong',show.movie));const info=element('div','','show-info');info.append(element('strong',show.movie),element('p',`${show.genre} · ${show.duration}`),element('b',`${show.time} · ${money(show.price_paise)}`));button.append(poster,info);button.onclick=()=>choose(show);$('#shows').append(button);});
    if(shows.length)await choose(shows.find(show=>show.id===current?.id)||shows[0]);
  }catch(error){notice(error.message);}
}
document.querySelectorAll('[data-tab]').forEach(button=>button.onclick=()=>{document.querySelectorAll('[data-tab]').forEach(tab=>{tab.classList.toggle('active',tab===button);tab.setAttribute('aria-selected',String(tab===button));});$('#client').hidden=button.dataset.tab!=='client';$('#providers').hidden=button.dataset.tab!=='providers';});
$('#refresh').onclick=load;
$('#book').onclick=async()=>{const button=$('#book');setBookingBusy(true);button.disabled=true;button.textContent='Confirming your booking…';notice();try{const result=await api('/api/bookings',{show_id:current.id,seat_ids:[...selected],idempotency_key:key});const confirmation=$('#confirmation');confirmation.replaceChildren(element('h3','You’re going to the movies.'),element('p',`Seats ${result.seat_ids.join(', ')} · ${money(result.amount_paise)}`),element('p',`Confirmation ${result.booking_id.slice(0,12)}`));confirmation.hidden=false;document.querySelectorAll('.seats button').forEach(seat=>{seat.classList.remove('selected');seat.setAttribute('aria-pressed','false');if(result.seat_ids.includes(seat.textContent)){seat.dataset.available='false';seat.setAttribute('aria-label',`Seat ${seat.textContent} · unavailable`);}});selected.clear();summary();}catch(error){notice(error.message);}finally{setBookingBusy(false);button.textContent='Continue to payment';button.disabled=!selected.size;}};
load();
