"use strict";

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const themes = {
  blue: ["#4b80ef", "#edf3ff", "#355da2"],
  teal: ["#2aa895", "#e8f7f2", "#28796b"],
  purple: ["#9b76d8", "#f2edfb", "#7853a7"],
  amber: ["#d9a246", "#fcf5e7", "#96702f"],
  rose: ["#d27c9a", "#fbeef3", "#a05672"],
  slate: ["#8091a9", "#eef2f7", "#5c6b80"],
};
const state = {
  rooms: [],
  bookings: [],
  week: monday(new Date()),
  room: "",
  view: "calendar",
  generation: 0,
};
let toastTimer;

function element(tag, className = "", text = "") {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== "") node.textContent = text;
  return node;
}
function icon(name) {
  const node = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  node.setAttribute("aria-hidden", "true");
  const use = document.createElementNS(node.namespaceURI, "use");
  use.setAttribute("href", `#i-${name}`);
  node.append(use);
  return node;
}
function tint(node, room) {
  const [color, background, ink] = themes[room?.color] || themes.blue;
  node.style.setProperty("--room-color", color);
  node.style.setProperty("--room-tint", background);
  node.style.setProperty("--room-ink", ink);
  return node;
}
function dot(room) {
  return tint(element("span", "dot"), room);
}
function dateISO(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}
function monday(date) {
  const d = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
  return d;
}
function plusDays(date, amount) {
  const d = new Date(date);
  d.setDate(d.getDate() + amount);
  return d;
}
function timeMinutes(value) {
  return Number(value.slice(11, 13)) * 60 + Number(value.slice(14, 16));
}
function timeString(minutes) {
  return `${String(Math.floor(minutes / 60)).padStart(2, "0")}:${String(minutes % 60).padStart(2, "0")}`;
}
function number(value) {
  return new Intl.NumberFormat("de-DE", { maximumFractionDigits: 1 }).format(value);
}
function roomOf(booking) {
  return state.rooms.find((r) => r.id === booking.room_id);
}
function activeBookings() {
  return state.bookings.filter((b) => b.status === "active");
}
function showToast(text) {
  clearTimeout(toastTimer);
  $("#toast").textContent = text;
  $("#toast").hidden = false;
  toastTimer = setTimeout(() => ($("#toast").hidden = true), 4500);
}
async function api(path, method = "GET", body) {
  const options = { method, headers: { Accept: "application/json" } };
  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.headers["X-CSRF-Token"] = $('meta[name="csrf-token"]').content;
    options.body = JSON.stringify(body);
  }
  let response;
  try {
    response = await fetch(path, options);
  } catch {
    throw new Error("Die Verbindung ist unterbrochen. Bitte prüfen, ob Raumzeit noch läuft.");
  }
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error("Die Antwort konnte nicht gelesen werden. Bitte die Seite neu laden.");
  }
  if (!response.ok) {
    const error = new Error(data.error || "Die Aktion ist fehlgeschlagen.");
    error.field = data.field;
    throw error;
  }
  return data;
}
async function load() {
  const generation = ++state.generation;
  const from = dateISO(state.week),
    to = dateISO(plusDays(state.week, 7));
  try {
    const [rooms, bookings] = await Promise.all([
      api("/api/rooms"),
      api(`/api/bookings?from=${from}&to=${to}`),
    ]);
    if (generation !== state.generation) return;
    state.rooms = rooms.rooms;
    state.bookings = bookings.bookings;
    if (!state.rooms.some((r) => r.id === state.room)) state.room = "";
    $("#global-error").hidden = true;
    render();
  } catch (error) {
    if (generation !== state.generation) return;
    $("#global-error-text").textContent = error.message;
    $("#global-error").hidden = false;
  }
}
function render() {
  const active = activeBookings();
  $("#stat-rooms").textContent = state.rooms.length;
  $("#stat-bookings").textContent = active.length;
  const hours = active.reduce(
    (sum, b) => sum + (timeMinutes(b.end) - timeMinutes(b.start)) / 60,
    0,
  );
  $("#stat-hours").textContent = number(hours);
  $("#stat-utilization").textContent =
    `${number(state.rooms.length ? (hours / (state.rooms.length * 60)) * 100 : 0)} % der verfügbaren Raumzeit`;
  $("#stat-booking-note").textContent =
    active.length === 1 ? "Ein aktiver Termin" : "Aktive Termine · Mo–Fr";
  $("#nav-count").textContent = active.length;
  const end = plusDays(state.week, 4);
  $("#calendar-title").textContent =
    `${state.week.getDate()}. – ${end.toLocaleDateString("de-DE", { day: "numeric", month: "long", year: "numeric" })}`;
  const thursday = plusDays(state.week, 3),
    first = new Date(thursday.getFullYear(), 0, 1);
  $("#week-number").textContent = `KW ${Math.ceil(((thursday - first) / 86400000 + 1) / 7)}`;
  const filter = $("#room-filter");
  filter.replaceChildren(new Option("Alle Räume", ""));
  for (const room of state.rooms) filter.add(new Option(room.name, room.id));
  filter.value = state.room;
  const side = $("#sidebar-rooms"),
    legend = $("#room-legend");
  side.replaceChildren();
  legend.replaceChildren();
  for (const room of state.rooms) {
    const button = element("button", "sidebar-room");
    button.type = "button";
    button.append(
      dot(room),
      element("span", "", room.name),
      element("small", "", `${room.capacity}`),
    );
    button.addEventListener("click", () => {
      state.room = room.id;
      location.hash = "kalender";
      render();
    });
    side.append(button);
    const label = element("span", "legend-item");
    label.append(dot(room), element("span", "", room.name));
    legend.append(label);
  }
  renderCalendar();
  renderBookingList();
  renderRooms();
}
function renderCalendar() {
  const head = $("#calendar-head"),
    axis = $("#time-axis"),
    columns = $("#day-columns"),
    agenda = $("#mobile-agenda");
  head.replaceChildren(element("div"));
  axis.replaceChildren();
  columns.replaceChildren();
  agenda.replaceChildren();
  for (let hour = 8; hour <= 20; hour++) {
    const label = element("span", "", `${String(hour).padStart(2, "0")}:00`);
    label.style.top = `${(hour - 8) * 60}px`;
    axis.append(label);
  }
  const visible = activeBookings().filter((b) => !state.room || b.room_id === state.room);
  for (let day = 0; day < 5; day++) {
    const date = plusDays(state.week, day),
      iso = dateISO(date),
      today = iso === dateISO(new Date());
    const header = element(
      "div",
      today ? "is-today" : "",
      date.toLocaleDateString("de-DE", { weekday: "short" }).replace(".", ""),
    );
    header.append(element("strong", "", date.getDate()));
    head.append(header);
    const column = element("div", `day-column${today ? " is-today" : ""}`);
    column.dataset.date = iso;
    column.addEventListener("click", (event) => {
      const minute = Math.min(
        705,
        Math.max(0, Math.floor((event.clientY - column.getBoundingClientRect().top) / 15) * 15),
      );
      openBooking(null, {
        date: iso,
        start: timeString(480 + minute),
        end: timeString(Math.min(1200, 540 + minute)),
      });
    });
    const bookings = visible.filter((b) => b.start.slice(0, 10) === iso);
    for (const { booking, lane, lanes } of layoutDay(bookings)) {
      const room = roomOf(booking),
        duration = timeMinutes(booking.end) - timeMinutes(booking.start);
      const button = tint(
        element(
          "button",
          `calendar-booking${duration <= 30 ? " compact" : ""}${duration === 15 ? " short" : ""}`,
        ),
        room,
      );
      button.style.top = `${timeMinutes(booking.start) - 480 + 2}px`;
      button.style.height = `${duration - 4}px`;
      button.style.left = `calc(${(lane * 100) / lanes}% + 4px)`;
      button.style.width = `calc(${100 / lanes}% - 8px)`;
      button.setAttribute(
        "aria-label",
        `${booking.title}, ${room.name}, ${booking.start.slice(11)} bis ${booking.end.slice(11)}, ${booking.organizer}`,
      );
      button.title = `${booking.title} · ${room.name} · ${booking.start.slice(11)}–${booking.end.slice(11)}`;
      button.append(
        element("span", "event-time", `${booking.start.slice(11)} – ${booking.end.slice(11)}`),
        element("strong", "", booking.title),
      );
      const roomLine = element("span", "event-room");
      roomLine.append(icon("door"), element("span", "", room.name));
      button.append(roomLine);
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        openBooking(booking);
      });
      column.append(button);
    }
    columns.append(column);
    const section = element("div", "agenda-day");
    section.append(
      element(
        "h3",
        "",
        date.toLocaleDateString("de-DE", { weekday: "long", day: "numeric", month: "long" }),
      ),
    );
    if (!bookings.length)
      section.append(element("p", "agenda-free", "Noch keine Buchungen – Raum für Neues."));
    for (const booking of bookings) {
      const room = roomOf(booking),
        event = tint(element("button", "agenda-event"), room),
        description = element("div");
      description.append(
        element("strong", "", booking.title),
        element("small", "", `${room.name} · ${booking.organizer}`),
      );
      event.append(
        element("span", "agenda-time", `${booking.start.slice(11)}\n${booking.end.slice(11)}`),
        description,
      );
      event.addEventListener("click", () => openBooking(booking));
      section.append(event);
    }
    agenda.append(section);
  }
}
// Intervallgruppen erhalten jeweils nur so viele Spalten wie gleichzeitig benötigt.
function layoutDay(bookings) {
  const ordered = [...bookings].sort(
    (a, b) => a.start.localeCompare(b.start) || a.end.localeCompare(b.end),
  );
  const result = [];
  let cluster = [],
    clusterEnd = "";
  function flush() {
    const ends = [],
      entries = [];
    for (const booking of cluster) {
      let lane = ends.findIndex((end) => end <= booking.start);
      if (lane < 0) lane = ends.length;
      ends[lane] = booking.end;
      entries.push({ booking, lane });
    }
    result.push(...entries.map((entry) => ({ ...entry, lanes: ends.length })));
    cluster = [];
    clusterEnd = "";
  }
  for (const booking of ordered) {
    if (cluster.length && booking.start >= clusterEnd) flush();
    cluster.push(booking);
    if (booking.end > clusterEnd) clusterEnd = booking.end;
  }
  if (cluster.length) flush();
  return result;
}
function emptyState(title, text) {
  const node = element("div", "empty-state");
  node.append(icon("calendar"), element("h3", "", title), element("p", "", text));
  return node;
}
function renderBookingList() {
  const list = $("#booking-list"),
    query = $("#booking-search").value.toLocaleLowerCase("de-DE"),
    status = $("#status-filter").value;
  list.replaceChildren();
  const bookings = state.bookings.filter(
    (b) =>
      (status === "all" || b.status === status) &&
      `${b.title} ${b.organizer}`.toLocaleLowerCase("de-DE").includes(query),
  );
  if (!bookings.length)
    list.append(
      emptyState("Hier ist noch Platz", "Für diese Auswahl wurden keine Buchungen gefunden."),
    );
  for (const booking of bookings) {
    const room = roomOf(booking),
      date = new Date(`${booking.start.slice(0, 10)}T12:00`),
      row = element("div", `booking-row${booking.status === "cancelled" ? " cancelled-row" : ""}`);
    const day = element(
      "div",
      "booking-date",
      date.toLocaleDateString("de-DE", { weekday: "short" }).replace(".", ""),
    );
    day.append(element("strong", "", date.getDate()));
    const info = element("div", "booking-info");
    info.append(
      element("strong", "", booking.title),
      element("small", "", `${booking.organizer} · ${booking.participants} Personen`),
    );
    const label = element("span", "room-label");
    label.append(dot(room), element("span", "", room.name));
    row.append(
      day,
      info,
      label,
      element("span", "booking-time", `${booking.start.slice(11)} – ${booking.end.slice(11)}`),
    );
    if (booking.status === "active") {
      const edit = element("button", "row-action", "Öffnen");
      edit.setAttribute("aria-label", `${booking.title} öffnen`);
      edit.addEventListener("click", () => openBooking(booking));
      row.append(edit);
    } else row.append(element("span", "cancelled-badge", "Storniert"));
    list.append(row);
  }
}
function renderRooms() {
  const cards = $("#room-cards");
  cards.replaceChildren();
  if (!state.rooms.length)
    cards.append(emptyState("Dein erster Raum", "Lege einen Raum an, um die Planung zu beginnen."));
  for (const room of state.rooms) {
    const card = tint(element("article", "room-card"), room),
      illustration = element("div", "room-illustration"),
      content = element("div", "room-card-content");
    illustration.setAttribute("aria-hidden", "true");
    illustration.append(element("div", "floorplan"));
    const heading = element("div", "room-card-title"),
      edit = element("button", "icon-button");
    edit.append(icon("edit"));
    edit.setAttribute("aria-label", `${room.name} bearbeiten`);
    edit.addEventListener("click", () => openRoom(room));
    heading.append(element("h3", "", room.name), edit);
    const details = element("div", "room-card-detail"),
      capacity = element("span"),
      location = element("span");
    capacity.append(icon("users"), element("span", "", `${room.capacity} Personen`));
    location.append(icon("pin"), element("span", "", room.location));
    details.append(capacity, location);
    const tags = element("div", "equipment-tags");
    for (const equipment of room.equipment) tags.append(element("span", "", equipment));
    if (!room.equipment.length) tags.append(element("span", "", "Ohne zusätzliche Ausstattung"));
    const bottom = element("div", "room-card-bottom"),
      count = activeBookings().filter((b) => b.room_id === room.id).length,
      book = element("button", "room-book-button", "Raum buchen");
    book.append(icon("arrow"));
    book.addEventListener("click", () => openBooking(null, { room_id: room.id }));
    bottom.append(
      element("span", "", `${count} ${count === 1 ? "Buchung" : "Buchungen"} diese Woche`),
      book,
    );
    content.append(heading, details, tags, bottom);
    card.append(illustration, content);
    cards.append(card);
  }
}
function switchView() {
  const routes = { "#kalender": "calendar", "#buchungen": "bookings", "#raeume": "rooms" };
  state.view = routes[location.hash] || "calendar";
  for (const view of ["calendar", "bookings", "rooms"])
    $(`#${view}-view`).hidden = view !== state.view;
  $$(".nav-link").forEach((link) => {
    const active = link.dataset.view === state.view;
    link.classList.toggle("active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  const titles = {
    calendar: [
      "Deine Woche im Überblick",
      "Finde den passenden Raum. Wir halten die Zeit für dich frei.",
      "Wochenkalender",
    ],
    bookings: [
      "Alles Wichtige an einem Ort",
      "Deine Termine, Personen und Räume – übersichtlich geplant.",
      "Alle Buchungen",
    ],
    rooms: [
      "Räume für gute Ideen",
      "Vom konzentrierten Gespräch bis zum großen Workshop.",
      "Räume verwalten",
    ],
  };
  $("#page-title").textContent = titles[state.view][0];
  $("#page-description").textContent = titles[state.view][1];
  $("#breadcrumb-view").textContent = titles[state.view][2];
}
function openBooking(booking = null, defaults = {}) {
  if (!state.rooms.length) {
    location.hash = "raeume";
    openRoom();
    showToast("Lege zuerst einen Raum an.");
    return;
  }
  const form = $("#booking-form");
  form.reset();
  $("#booking-error").hidden = true;
  const field = (name) => form.elements.namedItem(name);
  field("room_id").replaceChildren(
    ...state.rooms.map((r) => new Option(`${r.name} · ${r.capacity} Plätze`, r.id)),
  );
  field("id").value = booking?.id || "";
  field("version").value = booking?.version || "";
  field("title").value = booking?.title || "";
  field("organizer").value = booking?.organizer || "";
  field("participants").value = booking?.participants || 2;
  field("room_id").value = booking?.room_id || defaults.room_id || state.room || state.rooms[0].id;
  const today = new Date(),
    defaultDate = dateISO(
      today.getDay() === 0 || today.getDay() === 6 ? plusDays(monday(today), 7) : today,
    );
  field("date").value = booking?.start.slice(0, 10) || defaults.date || defaultDate;
  field("start_time").value = booking?.start.slice(11) || defaults.start || "09:00";
  field("end_time").value = booking?.end.slice(11) || defaults.end || "10:00";
  $("#booking-dialog-title").textContent = booking ? "Buchung bearbeiten" : "Neue Buchung";
  $("#cancel-booking").hidden = !booking;
  updateCapacityHint();
  $("#booking-dialog").showModal();
  field("title").focus();
}
function updateCapacityHint() {
  const form = $("#booking-form"),
    room = state.rooms.find((r) => r.id === form.elements.room_id.value);
  $("#room-capacity-hint").textContent = room ? `${room.capacity} Plätze · ${room.location}` : "";
}
function openRoom(room = null) {
  const form = $("#room-form");
  form.reset();
  $("#room-error").hidden = true;
  for (const key of ["id", "version", "name", "location", "color", "capacity"])
    form.elements.namedItem(key).value = room?.[key] ?? ({ capacity: 8, color: "blue" }[key] || "");
  $$("input[name=equipment]", form).forEach(
    (input) => (input.checked = room?.equipment.includes(input.value) || false),
  );
  $("#room-dialog-title").textContent = room ? "Raum bearbeiten" : "Raum hinzufügen";
  $("#room-dialog").showModal();
  form.elements.name.focus();
}
function formError(id, error) {
  const target = $(id);
  target.textContent = error.message;
  target.hidden = false;
  target.scrollIntoView({ block: "nearest" });
}
async function submitBooking(event) {
  event.preventDefault();
  const form = event.currentTarget,
    data = Object.fromEntries(new FormData(form)),
    button = $("#save-booking");
  button.disabled = true;
  $("#booking-error").hidden = true;
  const body = {
    room_id: data.room_id,
    title: data.title,
    organizer: data.organizer,
    participants: Number(data.participants),
    start: `${data.date}T${data.start_time}`,
    end: `${data.date}T${data.end_time}`,
  };
  if (data.id) body.version = Number(data.version);
  try {
    await api(
      data.id ? `/api/bookings/${data.id}` : "/api/bookings",
      data.id ? "PUT" : "POST",
      body,
    );
    $("#booking-dialog").close();
    state.week = monday(new Date(`${data.date}T12:00`));
    await load();
    showToast(data.id ? "Buchung aktualisiert." : "Dein Raum ist gebucht.");
  } catch (error) {
    formError("#booking-error", error);
  } finally {
    button.disabled = false;
  }
}
async function submitRoom(event) {
  event.preventDefault();
  const form = event.currentTarget,
    data = Object.fromEntries(new FormData(form)),
    button = $("button[type=submit]", form);
  button.disabled = true;
  const body = {
    name: data.name,
    location: data.location,
    color: data.color,
    capacity: Number(data.capacity),
    equipment: new FormData(form).getAll("equipment"),
  };
  if (data.id) body.version = Number(data.version);
  try {
    await api(data.id ? `/api/rooms/${data.id}` : "/api/rooms", data.id ? "PUT" : "POST", body);
    $("#room-dialog").close();
    await load();
    showToast(data.id ? "Raum aktualisiert." : "Dein neuer Raum ist bereit.");
  } catch (error) {
    formError("#room-error", error);
  } finally {
    button.disabled = false;
  }
}
function initialize() {
  $("#today-label").textContent = new Date().toLocaleDateString("de-DE", {
    weekday: "short",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
  for (let minute = 480; minute <= 1200; minute += 15) {
    if (minute < 1200)
      $("select[name=start_time]").add(new Option(timeString(minute), timeString(minute)));
    if (minute > 480)
      $("select[name=end_time]").add(new Option(timeString(minute), timeString(minute)));
  }
  $("#new-booking").addEventListener("click", () => openBooking());
  $("#new-room").addEventListener("click", () => openRoom());
  $("#prev-week").addEventListener("click", () => {
    state.week = plusDays(state.week, -7);
    load();
  });
  $("#next-week").addEventListener("click", () => {
    state.week = plusDays(state.week, 7);
    load();
  });
  $("#this-week").addEventListener("click", () => {
    state.week = monday(new Date());
    load();
  });
  $("#room-filter").addEventListener("change", (event) => {
    state.room = event.target.value;
    renderCalendar();
  });
  $("#booking-search").addEventListener("input", renderBookingList);
  $("#status-filter").addEventListener("change", renderBookingList);
  $("#booking-form").addEventListener("submit", submitBooking);
  $("#room-form").addEventListener("submit", submitRoom);
  $("select[name=room_id]").addEventListener("change", updateCapacityHint);
  $$(".close-dialog").forEach((button) =>
    button.addEventListener("click", () => button.closest("dialog").close()),
  );
  $("#cancel-booking").addEventListener("click", () => $("#confirm-dialog").showModal());
  $("#confirm-no").addEventListener("click", () => $("#confirm-dialog").close());
  $("#confirm-yes").addEventListener("click", async (event) => {
    event.target.disabled = true;
    const form = $("#booking-form");
    try {
      await api(`/api/bookings/${form.elements.id.value}/cancel`, "POST", {
        version: Number(form.elements.version.value),
      });
      $("#confirm-dialog").close();
      $("#booking-dialog").close();
      await load();
      showToast("Buchung storniert. Der Raum ist wieder frei.");
    } catch (error) {
      $("#confirm-dialog").close();
      formError("#booking-error", error);
    } finally {
      event.target.disabled = false;
    }
  });
  $("#retry").addEventListener("click", load);
  window.addEventListener("hashchange", switchView);
  switchView();
  load();
}
initialize();
