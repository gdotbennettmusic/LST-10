# LST-10

Loopology Session Timer is a single-file page (`index.html`, kept identical to `Loopology_Session_Timer_LST10.html`) for Glenn's practice sessions. GitHub Pages serves it at <https://gdotbennettmusic.github.io/LST-10/>. The page does not send session data to a server. History stays in this browser under `localStorage` key `loopology-history-v1`. Screenshot bytes and audio file handles stay in IndexedDB on the device.

## What the timer does

- Start, pause, resume, and stop a session. The clock and the on-screen date use America/New_York.
- Undo and redo timer actions, notes, and loads (permanent deletes still ask first).
- Type a start and end for a session the timer did not catch. That duration is saved to history.
- Keep a notes log. Each note stores the Eastern clock time and the active elapsed time.
- Attach PNG, JPG, or WEBP screenshots, and link external audio without copying the recording into the timer.
- Save, load, edit, duplicate, and delete history in this browser.
- Show upcoming sessions in an **Upcoming / Planned** section. They are badged PLANNED, left out of the completed count and the completed active-time total, and can be started in the timer, marked done, edited, or deleted.
- Export the open session as text, PDF, or a `.lst` file, and import a `.lst` file back.
- Export every saved session as CSV, or import that CSV (or a JSON array) back into history.
- Themes, a target length, alerts, clock format, and session numbering. Settings stay in this browser.

## Session entry

Each history record is one object. Times are epoch milliseconds. Durations are milliseconds. `date` is `YYYY-MM-DD`.

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Session id, such as `S-2026-020`. Import and add-links skip a row when this id is already stored. |
| `title` | string | Session title. |
| `date` | string | Calendar date `YYYY-MM-DD`. |
| `planStatus` | `"done"` or `"planned"` | `done` counts toward completed totals. `planned` is an upcoming session and does not. Missing on older rows: treated as `done`, unless `status` is `PLANNED` or the start is still in the future and the timer status is not `COMPLETED`, `ACTIVE`, or `PAUSED`. |
| `status` | string | Timer state: `READY`, `ACTIVE`, `PAUSED`, `COMPLETED`, or `PLANNED`. |
| `start` | number or null | Start instant, epoch ms. |
| `stop` | number or null | End instant, epoch ms. Null on a plan that has not finished. |
| `activeMs` | number | Active (unpaused) time already recorded. `0` on a plan that has not been marked done. |
| `pausedMs` | number | Time spent paused. |
| `wallMs` | number | Wall time, active plus paused. `0` on a plan that has not been marked done. |
| `plannedDurationMs` | number, optional | Intended length of a planned session. Not included in the completed active-time total until the session is marked done or recorded by the timer. |
| `notes` | array | Timestamped notes. See below. |
| `attachments` | array | Screenshot metadata. The image bytes live in IndexedDB, not in the JSON. |
| `audioRefs` | array | External audio references. The recording stays in its original file. |
| `savedAt` | number | When this record was written, epoch ms. |
| `importedAt` | number, optional | When an import or add-link stored the row, epoch ms. |

A note object:

| Field | Type | Meaning |
| --- | --- | --- |
| `time` | number or null | When the note was written, epoch ms. |
| `clock` | string | Eastern clock text, such as `3:00:00 PM EDT`. |
| `elapsed` | string | Active elapsed time `HH:MM:SS` when the note was written. |
| `text` | string | The note. |
| `attachmentId` | string, optional | Screenshot this note points at. |
| `audioRefId` | string, optional | Audio reference this note points at. |

A screenshot object: `id`, `name`, `type`, `size` (bytes), `addedAt` (epoch ms), `clock`, `elapsed`, `caption`.

An audio reference: `id`, `name`, `type`, `size`, `lastModified`, `addedAt`, `clock`, `elapsed`, `durationMs`, `location`, `note`, `handleStored`, and sometimes `relinkedAt`.

The history CSV from **Export CSV** has one row per session. The columns are Session ID, Session Title, Date, Status, Plan Status (`done` or `planned`), Planned Duration, Planned Duration (ms), then started / ended / active / paused / wall / saved / imported in human, ISO, and millisecond forms, then Notes, Screenshots, and Audio Files. Older CSV files without Plan Status still import.

## Adding entries from an assistant

An assistant who cannot reach the browser can still hand Glenn a link, or a CSV/JSON file he imports himself. The page asks before it writes anything. Nothing is added silently.

### Link

Put the session JSON in the URL hash, not the query string, so the data never goes to a server:

`https://gdotbennettmusic.github.io/LST-10/#add=<base64url JSON>`

The JSON is UTF-8, then base64url (use `-` and `_`, and omit `=` padding). It may be one session object or an array of them. On load the page decodes it, fills defaults, and shows a confirm dialog:

- One upcoming session: `Add 1 planned session for Oct 20, 7:00 PM?`
- One finished session with a start time: `Add 1 session for Oct 12, 3:00 PM?`
- Several sessions: `Add N sessions to history?`

**Add** merges the rows into `loopology-history-v1`, skips any id already stored, redraws history, and clears the hash with `history.replaceState`. **Cancel** writes nothing and clears the hash. Opening the same link again reports that the session is already in history.

Fields you can send (the page stores the canonical record above):

| Input | Notes |
| --- | --- |
| `id` | Optional. If omitted, the next `S-YYYY-NNN` id is assigned. |
| `title` | Optional. Default `Loopology Session`. |
| `date` | `YYYY-MM-DD`. Default is the America/New_York date of `start`, or today. |
| `time` | With `date`: `7:00 PM`, `19:00`, or `19:00:00`. Read as America/New_York. |
| `start`, `startISO`, `started` | Epoch ms, or ISO 8601. A value with `Z` or a numeric offset is used as written. A value with no zone, such as `2026-10-20T19:00:00`, is America/New_York. A 10-digit number is epoch seconds. |
| `end`, `stop`, `ended` | Same forms as `start`. |
| `duration` | `HH:MM:SS`, `MM:SS`, `90m`, `1h30m`, or a number of **seconds**. |
| `durationMs`, `activeMs`, `pausedMs`, `wallMs`, `plannedDurationMs` | Milliseconds. |
| `planStatus` | `"done"` or `"planned"`. Also accepted: `plan`, or `planned: true` / `false`. If you put `"done"` or `"planned"` in `status`, that is read as `planStatus` too. |
| `status` | Timer state when it is `READY`, `ACTIVE`, `PAUSED`, `COMPLETED`, or `PLANNED`. |
| `notes` or `note` | A string, a list of strings, or a list of note objects. |
| `attachments`, `audioRefs` | Optional metadata only. Do not put image or audio bytes in a link. |
| `savedAt` | Optional epoch ms. Default is the moment the row is prepared. |

Defaults when a field is missing:

- `planStatus` is `planned` when the start is in the future, otherwise `done`. An explicit `planStatus` always wins, so a plan stays planned after that clock time until someone marks it done or runs it.
- A done row with a duration and no end gets `activeMs` and `wallMs` from that duration, `pausedMs` 0, and `stop = start + wallMs`.
- A planned row stores the duration in `plannedDurationMs`, leaves `activeMs` and `wallMs` at 0, and leaves `stop` empty unless an end was sent. The completed total ignores it.
- `status` becomes `PLANNED` or `COMPLETED` to match.
- `notes` defaults to an empty list.

Planned rows show under **Upcoming / Planned** with a PLANNED badge. **Start** runs the timer now under that id and title (notes come along). **Stop** saves a completed session and removes the plan with the same id. **Mark Done** moves it into completed history and, when no active time was recorded yet, uses `plannedDurationMs` as the active and wall time. **Delete** removes it after a confirm. Completed rows keep Load, Edit, Duplicate, and Delete.

The same confirm and id check are used by **Import**, next to **Export CSV**. That button accepts this app's history CSV and a JSON array (or one JSON object) of the same shape. A `.lst` file still goes through **Import Session** at the bottom of the page.

Very long notes belong in a JSON file rather than a link. One add can include at most 100 sessions, and the browser keeps the newest 100 history rows.

### Helper

`tools/make-entry-link.py` prints a ready-to-open link.

```bash
python3 tools/make-entry-link.py \
  --id S-2026-020 --title "Evening loops" \
  --date 2026-10-20 --time "7:00 PM" --duration 01:30:00 \
  --plan planned --note "Bring the new motif"
```

`--json sessions.json` encodes an object or array instead of the flags. `--base` changes the page URL. The default base is `https://gdotbennettmusic.github.io/LST-10/`.

### Worked examples

Planned session. The dialog reads **Add 1 planned session for Oct 20, 7:00 PM?**

```json
{
  "id": "S-2026-020",
  "title": "Evening loops",
  "date": "2026-10-20",
  "time": "7:00 PM",
  "duration": "01:30:00",
  "planStatus": "planned",
  "notes": ["Bring the new motif"]
}
```

<https://gdotbennettmusic.github.io/LST-10/#add=eyJpZCI6IlMtMjAyNi0wMjAiLCJ0aXRsZSI6IkV2ZW5pbmcgbG9vcHMiLCJkYXRlIjoiMjAyNi0xMC0yMCIsInRpbWUiOiI3OjAwIFBNIiwiZHVyYXRpb24iOiIwMTozMDowMCIsIm5vdGVzIjpbIkJyaW5nIHRoZSBuZXcgbW90aWYiXSwicGxhblN0YXR1cyI6InBsYW5uZWQifQ>

Backdated session the timer did not catch (12 Oct 2026, 3:00 PM Eastern, 45 minutes). The dialog reads **Add 1 session for Oct 12, 3:00 PM?**

```json
{
  "id": "S-2026-012",
  "title": "Afternoon practice",
  "date": "2026-10-12",
  "time": "3:00 PM",
  "duration": "00:45:00",
  "planStatus": "done",
  "notes": ["Backdated: he said \"hello\", then kept going"]
}
```

<https://gdotbennettmusic.github.io/LST-10/#add=eyJpZCI6IlMtMjAyNi0wMTIiLCJ0aXRsZSI6IkFmdGVybm9vbiBwcmFjdGljZSIsImRhdGUiOiIyMDI2LTEwLTEyIiwidGltZSI6IjM6MDAgUE0iLCJkdXJhdGlvbiI6IjAwOjQ1OjAwIiwibm90ZXMiOlsiQmFja2RhdGVkOiBoZSBzYWlkIFwiaGVsbG9cIiwgdGhlbiBrZXB0IGdvaW5nIl0sInBsYW5TdGF0dXMiOiJkb25lIn0>
