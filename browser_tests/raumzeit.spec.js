const { test, expect } = require("@playwright/test");
const fs = require("node:fs");
const path = require("node:path");

const DAY = "2026-10-26";
const SCREENSHOTS = path.resolve("output/playwright/screenshots");
const runtimeErrors = new WeakMap();

async function expectResponse(page, method, suffix, action, expectedStatus) {
  const [response] = await Promise.all([
    page.waitForResponse((item) => item.request().method() === method && item.url().endsWith(suffix)),
    action(),
  ]);
  expect(response.status()).toBe(expectedStatus);
  return response.json();
}

async function openCalendar(page) {
  await page.getByRole("link", { name: "Wochenkalender", exact: true }).click();
  await expect(page.locator("#calendar-view")).toBeVisible();
}

function eventFor(page, title, project) {
  return page.locator(project === "mobile" ? "#mobile-agenda .agenda-event" : "#day-columns .calendar-booking")
    .filter({ hasText: title });
}

async function fillBooking(page, roomName, title, start = "09:00", end = "10:00") {
  const form = page.locator("#booking-form");
  await form.locator('[name="title"]').fill(title);
  await form.locator('[name="room_id"]').selectOption({ label: `${roomName} · 10 Plätze` });
  await form.locator('[name="participants"]').fill("4");
  await form.locator('[name="organizer"]').fill("Test Person");
  await form.locator('[name="date"]').fill(DAY);
  await form.locator('[name="start_time"]').selectOption(start);
  await form.locator('[name="end_time"]').selectOption(end);
}

async function createBooking(page, roomName, title, start, end) {
  await page.getByRole("button", { name: "Neue Buchung", exact: true }).click();
  await expect(page.locator("#booking-dialog")).toBeVisible();
  await fillBooking(page, roomName, title, start, end);
  const saved = await expectResponse(page, "POST", "/api/bookings", () =>
    page.getByRole("button", { name: "Buchung speichern", exact: true }).click(), 201);
  await expect(page.locator("#booking-dialog")).not.toBeVisible();
  await openCalendar(page);
  return saved.booking;
}

async function createRoom(page, roomName) {
  await page.getByRole("link", { name: "Räume verwalten", exact: true }).click();
  await expect(page.locator("#rooms-view")).toBeVisible();
  await page.getByRole("button", { name: "Raum hinzufügen", exact: true }).click();
  const form = page.locator("#room-form");
  await form.locator('[name="name"]').fill(roomName);
  await form.locator('[name="capacity"]').fill("10");
  await form.locator('[name="location"]').fill("Testbereich");
  await form.getByRole("checkbox", { name: "Whiteboard", exact: true }).check();
  await expectResponse(page, "POST", "/api/rooms", () =>
    form.getByRole("button", { name: "Raum speichern", exact: true }).click(), 201);
  await expect(page.locator("#room-dialog")).not.toBeVisible();
  await expect(page.locator("#room-cards")).toContainText(roomName);
  await expect(page.locator("#room-cards")).toContainText("Testbereich");
  await expect(page.locator("#room-cards")).toContainText("10 Personen");
  await expect(page.locator("#room-cards")).toContainText("Whiteboard");
}

test.beforeEach(async ({ page, context }, testInfo) => {
  const errors = [];
  runtimeErrors.set(page, errors);
  const observe = (item) => item.on("pageerror", (error) => errors.push(error.message));
  observe(page);
  context.on("page", observe);
  testInfo.annotations.push({ type: "browserVersion", description: context.browser().version() });
  // Nur Date ist festgesetzt; echte Timer, HTTP und Datenbank bleiben aktiv.
  await page.clock.setFixedTime(new Date("2026-10-26T08:00:00Z"));
  await page.goto("/");
  await expect(page.locator("#stat-rooms")).not.toHaveText("–");
  const roomName = `${testInfo.title.split(" ")[0]} ${testInfo.project.name}`;
  testInfo.annotations.push({ type: "room", description: roomName });
  await createRoom(page, roomName);
});

test.afterEach(async ({ page }, testInfo) => {
  fs.mkdirSync(SCREENSHOTS, { recursive: true });
  const target = path.join(SCREENSHOTS, `${testInfo.project.name}-${testInfo.title.split(" ")[0]}.png`);
  await page.screenshot({ path: target, fullPage: true });
  await testInfo.attach("UI-Nachweis", { path: target, contentType: "image/png" });
  expect(runtimeErrors.get(page)).toEqual([]);
});

const ownRoom = (testInfo) => testInfo.annotations.find((item) => item.type === "room").description;

test("E01 Buchung anlegen und nach Neuladen erhalten", async ({ page }, testInfo) => {
  const title = `Projektbesprechung ${testInfo.project.name}`;
  const booking = await createBooking(page, ownRoom(testInfo), title);
  expect(booking.version).toBe(1);
  await expect(eventFor(page, title, testInfo.project.name)).toBeVisible();
  await page.reload();
  await expect(eventFor(page, title, testInfo.project.name)).toBeVisible();
  if (testInfo.project.name === "mobile") {
    await expect(page.locator("#mobile-agenda")).toBeVisible();
    await expect(page.locator(".calendar-scroll")).not.toBeVisible();
    const geometry = await page.evaluate(() => ({
      content: document.documentElement.scrollWidth, viewport: window.innerWidth,
    }));
    expect(geometry.content).toBeLessThanOrEqual(geometry.viewport);
  }
});

test("E02 Überschneidung ablehnen und Bestand erhalten", async ({ page }, testInfo) => {
  const original = await createBooking(page, ownRoom(testInfo), "Bestehender Termin");
  await page.getByRole("button", { name: "Neue Buchung", exact: true }).click();
  await fillBooking(page, ownRoom(testInfo), "Unzulässige Überschneidung", "09:15", "09:45");
  const result = await expectResponse(page, "POST", "/api/bookings", () =>
    page.getByRole("button", { name: "Buchung speichern", exact: true }).click(), 409);
  expect(result.code).toBe("conflict");
  await expect(page.locator("#booking-error")).toContainText("bereits gebucht");
  await expect(page.locator("#booking-dialog")).toBeVisible();
  const stored = await page.request.get(`/api/bookings?from=${DAY}&to=2026-10-27&room_id=${original.room_id}`);
  expect((await stored.json()).bookings).toEqual([original]);
});

test("E03 Buchung bearbeiten und stornieren", async ({ page }, testInfo) => {
  const before = `Termin vorher ${testInfo.project.name}`;
  const after = `Termin geändert ${testInfo.project.name}`;
  const original = await createBooking(page, ownRoom(testInfo), before);
  await eventFor(page, before, testInfo.project.name).click();
  await fillBooking(page, ownRoom(testInfo), after, "10:00", "11:00");
  const updated = await expectResponse(page, "PUT", `/api/bookings/${original.id}`, () =>
    page.getByRole("button", { name: "Buchung speichern", exact: true }).click(), 200);
  expect(updated.booking.version).toBe(2);
  await expect(page.locator("#booking-dialog")).not.toBeVisible();
  await expect(eventFor(page, after, testInfo.project.name)).toBeVisible();
  await eventFor(page, after, testInfo.project.name).click();
  await page.getByRole("button", { name: "Buchung stornieren", exact: true }).click();
  await expect(page.locator("#confirm-dialog")).toBeVisible();
  const cancelled = await expectResponse(page, "POST", `/api/bookings/${original.id}/cancel`, () =>
    page.getByRole("button", { name: "Jetzt stornieren", exact: true }).click(), 200);
  expect(cancelled.booking.status).toBe("cancelled");
  expect(cancelled.booking.version).toBe(3);
  await expect(page.locator("#booking-dialog")).not.toBeVisible();
  await expect(eventFor(page, after, testInfo.project.name)).toHaveCount(0);
  await page.getByRole("link", { name: /^Alle Buchungen/ }).click();
  await page.locator("#status-filter").selectOption("cancelled");
  await page.locator("#booking-search").fill(after);
  await expect(page.locator("#booking-list")).toContainText("Storniert");
  await expect(page.locator("#booking-list .booking-row")).toHaveCount(1);
});

test("E04 15-Minuten-Termin lesbar öffnen", async ({ page }, testInfo) => {
  const title = `Viertelstunde ${testInfo.project.name}`;
  await createBooking(page, ownRoom(testInfo), title, "10:00", "10:15");
  const event = eventFor(page, title, testInfo.project.name);
  await expect(event).toBeVisible();
  await expect(event.locator("strong")).toBeVisible();
  if (testInfo.project.name === "desktop") {
    await expect(event).toHaveClass(/short/);
    await expect(event.locator(".event-time")).not.toBeVisible();
    const geometry = await event.evaluate((node) => {
      const title = node.querySelector("strong");
      return { titleHeight: title.scrollHeight, availableHeight: node.clientHeight };
    });
    expect(geometry.titleHeight).toBeLessThanOrEqual(geometry.availableHeight);
    await expect(event).toHaveAccessibleName(/10:00 bis 10:15/);
  }
  fs.mkdirSync(SCREENSHOTS, { recursive: true });
  await page.screenshot({ path: path.join(SCREENSHOTS, `${testInfo.project.name}-E04-Kurztermin.png`), fullPage: true });
  await event.focus();
  await event.press("Enter");
  await expect(page.locator("#booking-dialog")).toBeVisible();
  await expect(page.locator('#booking-form [name="start_time"]')).toHaveValue("10:00");
  await expect(page.locator('#booking-form [name="end_time"]')).toHaveValue("10:15");
  if (testInfo.project.name === "mobile") {
    const box = await page.locator("#booking-dialog").boundingBox();
    expect(box.x).toBeGreaterThanOrEqual(0);
    expect(box.width).toBeLessThanOrEqual(390);
    expect(box.height).toBeLessThanOrEqual(844);
  }
});

test("E05 Veralteter Raumdialog überschreibt keine Änderung", async ({ page, context }, testInfo) => {
  const roomName = ownRoom(testInfo);
  await page.getByRole("button", { name: `${roomName} bearbeiten`, exact: true }).click();
  const roomId = await page.locator('#room-form [name="id"]').inputValue();
  const second = await context.newPage();
  await second.clock.setFixedTime(new Date("2026-10-26T08:00:00Z"));
  await second.goto("/#raeume");
  await second.getByRole("button", { name: `${roomName} bearbeiten`, exact: true }).click();
  await expect(second.locator('#room-form [name="version"]')).toHaveValue("1");
  await page.locator('#room-form [name="location"]').fill("Neuer Standort");
  const current = await expectResponse(page, "PUT", `/api/rooms/${roomId}`, () =>
    page.locator("#room-form").getByRole("button", { name: "Raum speichern", exact: true }).click(), 200);
  expect(current.room.version).toBe(2);
  await second.locator('#room-form [name="location"]').fill("Veralteter Standort");
  const stale = await expectResponse(second, "PUT", `/api/rooms/${roomId}`, () =>
    second.locator("#room-form").getByRole("button", { name: "Raum speichern", exact: true }).click(), 409);
  expect(stale.code).toBe("stale");
  await expect(second.locator("#room-error")).toContainText("zwischenzeitlich geändert");
  const response = await page.request.get("/api/rooms");
  const actual = (await response.json()).rooms.find((room) => room.id === roomId);
  expect(actual).toEqual(current.room);
  fs.mkdirSync(SCREENSHOTS, { recursive: true });
  await second.screenshot({ path: path.join(SCREENSHOTS, `${testInfo.project.name}-E05-Konflikt.png`) });
  await second.close();
});

test("E06 Wochennavigation Raumfilter und Suche", async ({ page }, testInfo) => {
  const title = `Suche E06 ${testInfo.project.name}`;
  const comparisonRoom = `Vergleich E06 ${testInfo.project.name}`;
  const comparisonTitle = `Vergleichstermin E06 ${testInfo.project.name}`;
  // Beide Vergleichsdaten gehören zu diesem Fall, auch beim isolierten Erstlauf.
  await createRoom(page, comparisonRoom);
  await createBooking(page, comparisonRoom, comparisonTitle, "11:00", "12:00");
  await createBooking(page, ownRoom(testInfo), title);
  await page.getByRole("button", { name: "Nächste Woche", exact: true }).click();
  await expect(page.locator("#calendar-title")).toHaveText("2. – 6. November 2026");
  await expect(eventFor(page, title, testInfo.project.name)).toHaveCount(0);
  await page.getByRole("button", { name: "Vorherige Woche", exact: true }).click();
  await expect(page.locator("#calendar-title")).toHaveText("26. – 30. Oktober 2026");
  await page.getByRole("button", { name: "Vorherige Woche", exact: true }).click();
  await expect(page.locator("#calendar-title")).toHaveText("19. – 23. Oktober 2026");
  await page.getByRole("button", { name: "Heute", exact: true }).click();
  await expect(page.locator("#calendar-title")).toHaveText("26. – 30. Oktober 2026");
  await page.locator("#room-filter").selectOption({ label: ownRoom(testInfo) });
  await expect(page.locator("#day-columns .calendar-booking")).toHaveCount(1);
  await expect(eventFor(page, title, testInfo.project.name)).toBeVisible();
  await expect(eventFor(page, comparisonTitle, testInfo.project.name)).toHaveCount(0);
  await page.locator("#room-filter").selectOption("");
  await expect(eventFor(page, title, testInfo.project.name)).toBeVisible();
  await expect(eventFor(page, comparisonTitle, testInfo.project.name)).toBeVisible();
  await page.getByRole("link", { name: /^Alle Buchungen/ }).click();
  await page.locator("#booking-search").fill("TEST PERSON");
  await expect(page.locator("#booking-list .booking-row").filter({ hasText: title })).toBeVisible();
  await expect(page.locator("#booking-list .booking-row").filter({ hasText: comparisonTitle })).toBeVisible();
  await page.locator("#booking-search").fill(title.toUpperCase());
  await expect(page.locator("#booking-list .booking-row")).toHaveCount(1);
  await expect(page.locator("#booking-list")).toContainText(title);
  await page.locator("#booking-search").fill("nicht-vorhanden-xyz-raumzeit");
  await expect(page.locator("#booking-list .booking-row")).toHaveCount(0);
  await expect(page.locator("#booking-list")).toContainText("keine Buchungen gefunden");
});
