const $ = selector => document.querySelector(selector);
const money = paise => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(paise / 100);
// getRandomValues also works on LAN HTTP, where randomUUID is unavailable.
function bookingKey() {
  if (typeof crypto.randomUUID === 'function') return crypto.randomUUID();
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  bytes[6] = (bytes[6] & 15) | 64;
  bytes[8] = (bytes[8] & 63) | 128;
  const hex = Array.from(bytes, byte => byte.toString(16).padStart(2, '0')).join('');
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}
let shows = [], current, lastBooking, selected = new Set(), key = bookingKey();
let selectionRevision = 0, bookingInFlight = false, loading = false;

function element(tag, text = '', className) {
  const node = document.createElement(tag);
  node.textContent = text;
  if (className) node.className = className;
  return node;
}
function notice(message = '') {
  $('#notice').textContent = message;
  $('#notice').hidden = !message;
}
async function api(path, body) {
  const response = await fetch(path, body === undefined ? {} : {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(`${typeof data.detail === 'string' ? data.detail : 'This action could not be completed.'} ${data.recovery || ''}`);
  return data;
}

function updateTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const label = `Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`;
  $('#theme-toggle').setAttribute('aria-label', label);
  $('#theme-toggle').title = label;
}
updateTheme(document.documentElement.dataset.theme);
$('#theme-toggle').onclick = () => {
  const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  updateTheme(theme);
  try { localStorage.setItem('cinemaflow-theme', theme); } catch { /* The toggle also works without storage. */ }
};

function setBookingBusy(value) {
  bookingInFlight = value;
  document.querySelectorAll('.show, .provider-buttons button, #refresh, #movie-select, #theatre-select')
    .forEach(button => { button.disabled = value; });
  document.querySelectorAll('.seat').forEach(button => {
    button.disabled = value || button.dataset.available === 'false';
  });
  $('#book').setAttribute('aria-busy', String(value));
}
function summary() {
  const seats = lastBooking ? lastBooking.seat_ids : [...selected].sort();
  $('#summary-movie').textContent = current?.movie || 'Choose a movie';
  $('#summary-meta').textContent = current ? `${current.genre} · ${current.duration}` : 'Your evening, on the big screen.';
  $('#summary-theatre').textContent = current?.theatre || '—';
  $('#summary-time').textContent = current?.time || '—';
  $('#summary-seats').replaceChildren();
  if (seats.length) seats.forEach(seat => $('#summary-seats').append(element('span', seat, 'seat-chip')));
  else $('#summary-seats').textContent = 'None selected';
  $('#ticket-price').textContent = money(current?.price_paise || 0);
  $('#ticket-count').textContent = String(seats.length);
  $('#summary-total').textContent = money(lastBooking ? lastBooking.amount_paise : (current?.price_paise || 0) * seats.length);
  $('#selected-count').textContent = lastBooking ? `${seats.length} booked` : `${seats.length} selected`;
  $('#book').disabled = !selected.size || bookingInFlight;
  $('#book span').textContent = lastBooking ? 'Booking confirmed' : selected.size ? 'Confirm booking' : 'Select your seats';
}
function seatIcon() {
  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', '0 0 30 26');
  svg.setAttribute('aria-hidden', 'true');
  const path = document.createElementNS(ns, 'path');
  path.setAttribute('d', 'M7 16V6a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v10M5 11H3v10h24V11h-2v6H5Zm2 10v3m16-3v3');
  svg.append(path);
  return svg;
}
function renderSeats(seats) {
  const container = $('#seats');
  container.replaceChildren();
  const rows = new Map();
  seats.forEach(seat => {
    const row = seat.id.match(/^[A-Za-z]+/)?.[0] || '';
    if (!rows.has(row)) rows.set(row, []);
    rows.get(row).push(seat);
  });
  rows.forEach((values, label) => {
    const row = element('div', '', 'seat-row');
    const rowLabel = element('span', label, 'row-label');
    rowLabel.setAttribute('aria-hidden', 'true');
    row.append(rowLabel);
    values.forEach((seat, index) => {
      if (index === 4) { const aisle = element('span', '', 'aisle'); aisle.setAttribute('aria-hidden', 'true'); row.append(aisle); }
      const button = element('button', '', 'seat');
      button.dataset.seat = seat.id;
      button.dataset.available = String(seat.available);
      button.disabled = !seat.available;
      button.setAttribute('aria-label', `Seat ${seat.id}${seat.available ? '' : ' · unavailable'}`);
      button.setAttribute('aria-pressed', 'false');
      button.append(seatIcon(), element('span', seat.id.replace(/^[A-Za-z]+/, '')));
      button.onclick = () => {
        if (bookingInFlight) return;
        if (selected.has(seat.id)) selected.delete(seat.id);
        else if (selected.size < 8) selected.add(seat.id);
        else { notice('You can select up to 8 seats in one booking.'); return; }
        lastBooking = null;
        $('#confirmation').hidden = true;
        notice();
        button.classList.toggle('selected', selected.has(seat.id));
        button.setAttribute('aria-pressed', String(selected.has(seat.id)));
        key = bookingKey();
        summary();
      };
      row.append(button);
    });
    const endLabel = element('span', label, 'row-label');
    endLabel.setAttribute('aria-hidden', 'true');
    row.append(endLabel);
    container.append(row);
  });
  if (!seats.length) container.append(element('p', 'No seats are available for this show.', 'seat-message'));
}
async function choose(show) {
  if (bookingInFlight) return;
  const revision = ++selectionRevision;
  current = show;
  lastBooking = null;
  selected.clear();
  key = bookingKey();
  summary();
  notice();
  $('#confirmation').hidden = true;
  document.querySelectorAll('.show').forEach(node => {
    const active = node.dataset.id === show.id;
    node.classList.toggle('selected', active);
    node.setAttribute('aria-pressed', String(active));
  });
  $('#seat-title').textContent = show.movie;
  $('#selection-description').textContent = `${show.theatre} · ${show.time} · ${money(show.price_paise)} per seat`;
  $('#seats').setAttribute('aria-busy', 'true');
  $('#seats').replaceChildren(element('p', 'Finding your seats…', 'seat-message'));
  try {
    const seats = await api(`/api/shows/${encodeURIComponent(show.id)}/seats`);
    if (revision !== selectionRevision) return;
    renderSeats(seats);
  } catch (error) {
    if (revision === selectionRevision) {
      $('#seats').replaceChildren(element('p', 'Seat availability could not be loaded. Refresh to try again.', 'seat-message'));
      notice(error.message);
    }
  } finally {
    if (revision === selectionRevision) $('#seats').setAttribute('aria-busy', 'false');
  }
}
async function renderShowtimes() {
  const available = shows.filter(show => show.movie === $('#movie-select').value && show.theatre === $('#theatre-select').value);
  $('#shows').replaceChildren();
  available.forEach(show => {
    const button = element('button', show.time, 'show');
    button.dataset.id = show.id;
    button.setAttribute('aria-label', `${show.movie}, ${show.time}`);
    button.onclick = () => choose(show);
    $('#shows').append(button);
  });
  if (available.length) await choose(available.find(show => show.id === current?.id) || available[0]);
  else $('#shows').append(element('p', 'No showtimes are currently available.'));
}
function renderTheatres() {
  const theatres = [...new Set(shows.filter(show => show.movie === $('#movie-select').value).map(show => show.theatre))];
  $('#theatre-select').replaceChildren(...theatres.map(name => new Option(name, name)));
  $('#theatre-select').disabled = !theatres.length;
  return renderShowtimes();
}
$('#movie-select').onchange = renderTheatres;
$('#theatre-select').onchange = renderShowtimes;

async function load() {
  if (bookingInFlight || loading) return;
  loading = true;
  $('#refresh').disabled = true;
  try {
    const [health, providers] = await Promise.all([api('/health'), api('/api/providers')]);
    $('#revision').textContent = health.revision === 'working-files' ? 'CinemaFlow' : `Release ${health.revision.slice(0, 12)}`;
    $('#provider-list').replaceChildren();
    providers.forEach(provider => {
      const card = element('article', '', 'provider');
      card.append(element('h2', provider.id === 'payment' ? 'CinemaPay' : 'Grand Cinema'));
      card.append(element('span', provider.version ? `V${provider.version} · ${provider.status}` : 'Unreachable', `version${provider.version ? '' : ' unreachable'}`));
      card.append(element('p', provider.id === 'payment' ? 'Payment requests, exact currency amounts and transaction status.' : 'Showtimes, seat availability, reservations and booking confirmations.'));
      const controls = element('div', '', 'provider-buttons');
      [1, 2].forEach(version => {
        const button = element('button', `Use V${version}`, provider.version === version ? 'active' : '');
        button.setAttribute('aria-pressed', String(provider.version === version));
        button.onclick = async () => {
          button.disabled = true;
          try { await api(`/api/providers/${provider.id}/version`, { version }); notice(); await load(); }
          catch (error) { notice(error.message); }
          finally { button.disabled = false; }
        };
        controls.append(button);
      });
      card.append(controls);
      $('#provider-list').append(card);
    });
    shows = await api('/api/shows');
    const movies = [...new Set(shows.map(show => show.movie))];
    $('#movie-select').replaceChildren(...movies.map(name => new Option(name, name)));
    $('#movie-select').disabled = !movies.length;
    if (current && movies.includes(current.movie)) $('#movie-select').value = current.movie;
    if (movies.length) await renderTheatres();
    else {
      current = null; lastBooking = null; selected.clear(); summary();
      $('#movie-select').append(new Option('No movies available', ''));
      $('#theatre-select').replaceChildren(new Option('No theatres available', ''));
      $('#theatre-select').disabled = true;
      $('#shows').replaceChildren(element('p', 'No showtimes are currently available.'));
      $('#seats').replaceChildren(element('p', 'There are no shows to book at the moment.', 'seat-message'));
      $('#seats').setAttribute('aria-busy', 'false');
    }
  } catch (error) {
    notice(error.message);
    if ($('#seats').getAttribute('aria-busy') === 'true') {
      $('#seats').setAttribute('aria-busy', 'false');
      $('#seats').replaceChildren(element('p', 'The booking service could not be loaded. Refresh to try again.', 'seat-message'));
    }
  }
  finally { loading = false; $('#refresh').disabled = false; }
}

const tabs = [...document.querySelectorAll('[data-tab]')];
function activateTab(button) {
  tabs.forEach(tab => {
    const active = tab === button;
    tab.classList.toggle('active', active);
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
    $(`#${tab.dataset.tab}`).hidden = !active;
  });
}
tabs.forEach((button, index) => {
  button.onclick = () => activateTab(button);
  button.onkeydown = event => {
    let next;
    if (event.key === 'ArrowRight') next = tabs[(index + 1) % tabs.length];
    if (event.key === 'ArrowLeft') next = tabs[(index + tabs.length - 1) % tabs.length];
    if (event.key === 'Home') next = tabs[0];
    if (event.key === 'End') next = tabs[tabs.length - 1];
    if (next) { event.preventDefault(); activateTab(next); next.focus(); }
  };
});
$('#refresh').onclick = load;
$('#book').onclick = async () => {
  if (bookingInFlight || !selected.size || !current) return;
  setBookingBusy(true);
  $('#book').disabled = true;
  $('#book span').textContent = 'Confirming…';
  notice();
  try {
    const result = await api('/api/bookings', { show_id: current.id, seat_ids: [...selected], idempotency_key: key });
    lastBooking = result;
    const confirmation = $('#confirmation');
    confirmation.replaceChildren(element('h3', 'Booking confirmed'), element('p', `Seats ${result.seat_ids.join(', ')} · ${money(result.amount_paise)}`), element('p', `Reference ${result.booking_id.slice(0, 12)}`));
    confirmation.hidden = false;
    document.querySelectorAll('.seat').forEach(seat => {
      seat.classList.remove('selected');
      seat.setAttribute('aria-pressed', 'false');
      if (result.seat_ids.includes(seat.dataset.seat)) {
        seat.dataset.available = 'false';
        seat.setAttribute('aria-label', `Seat ${seat.dataset.seat} · unavailable`);
      }
    });
    selected.clear();
  } catch (error) { notice(error.message); }
  finally { setBookingBusy(false); summary(); }
};
load();
