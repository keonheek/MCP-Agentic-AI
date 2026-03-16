/**
 * SDC Application Auto-Grader v2
 * Google Apps Script — runs automatically on new Gmail
 *
 * Changes from v1:
 *   - Q4: 35 → 25 pts, Activities: 10 → 20 pts (total still 100)
 *   - Calibration clause + tier anchors to prevent score clustering
 *   - Per-question reasoning fields (q1_reason … activities_reason)
 *   - Interview schedule extraction: 3/14 (토) and 3/15 (일) fixed slots
 *   - New "Interview Schedule" sheet with dropdown for slot assignment
 *
 * Setup:
 *   1. Open script.google.com → New project → paste this code
 *   2. Set CLAUDE_API_KEY and SHEET_ID in Project Settings > Script Properties
 *   3. Run setupTrigger() once to install the Gmail trigger
 *   4. Grant Gmail + Sheets permissions when prompted
 *
 * Re-processing existing emails:
 *   Remove the "SDC-Applications" label from a Gmail thread to allow re-grading.
 *
 * Output — Applications sheet (21 columns):
 *   Timestamp | Name | Email | Major | Total Score |
 *   Q1 (20) | Q2 (15) | Q3 (20) | Q4 (25) | Activities (20) |
 *   Recommendation | Strengths | Weaknesses |
 *   Availability Flag | Availability Note | Summary |
 *   Q1 이유 | Q2 이유 | Q3 이유 | Q4 이유 | Activities 이유
 *
 * Output — Interview Schedule sheet (7 columns):
 *   Name | Email | 3/14 가능 슬롯 | 3/15 가능 슬롯 | 불가 슬롯 | 정기세션 비고 | 배정 슬롯
 */

// ─── Config ───────────────────────────────────────────────────────────────────

const CONFIG = {
  GMAIL_LABEL: "SDC-Applications",
  SEARCH_QUERY: "has:attachment -label:SDC-Applications",
  SHEET_NAME: "Applications",
  SCHEDULE_SHEET_NAME: "Interview Schedule",
  CLAUDE_MODEL: "claude-haiku-4-5-20251001",
};

// ─── Fixed interview slots ─────────────────────────────────────────────────────
// UPDATE these arrays for each new recruiting cycle.

const SLOTS_SAT = [
  "3/14 11:00~11:20", "3/14 11:25~11:45", "3/14 11:50~12:10",
  "3/14 12:15~12:35", "3/14 12:40~13:00", "3/14 13:05~13:25",
  "3/14 13:30~13:50", "3/14 13:55~14:15", "3/14 14:20~14:40",
  "3/14 14:45~15:05", "3/14 15:10~15:30", "3/14 15:35~15:55",
  "3/14 16:00~16:20", "3/14 16:25~16:45"
];

const SLOTS_SUN = [
  "3/15 10:00~10:20", "3/15 10:25~10:45", "3/15 10:50~11:10",
  "3/15 11:15~11:35", "3/15 11:40~12:00", "3/15 12:05~12:25",
  // 12:30~13:30 = 점심시간, excluded
  "3/15 13:30~13:50", "3/15 13:55~14:15", "3/15 14:20~14:40",
  "3/15 14:45~15:05", "3/15 15:10~15:30", "3/15 15:35~15:55",
  "3/15 16:00~16:20", "3/15 16:25~16:45", "3/15 16:50~17:10",
  "3/15 17:15~17:35"
];

const ALL_SLOTS = SLOTS_SAT.concat(SLOTS_SUN);

// ─── Entry point ──────────────────────────────────────────────────────────────

function processNewApplications() {
  const props = PropertiesService.getScriptProperties();
  const CLAUDE_API_KEY = props.getProperty("CLAUDE_API_KEY");
  const SHEET_ID = props.getProperty("SHEET_ID");

  if (!CLAUDE_API_KEY || !SHEET_ID) {
    console.error("Missing CLAUDE_API_KEY or SHEET_ID in Script Properties");
    return;
  }

  const spreadsheet = SpreadsheetApp.openById(SHEET_ID);
  const sheet = spreadsheet.getSheetByName(CONFIG.SHEET_NAME);
  if (!sheet) {
    console.error('Sheet "' + CONFIG.SHEET_NAME + '" not found');
    return;
  }

  ensureHeader(sheet);
  const scheduleSheet = ensureScheduleSheet(spreadsheet);

  const threads = GmailApp.search(CONFIG.SEARCH_QUERY);
  console.log("Found " + threads.length + " unprocessed application(s)");

  let label = GmailApp.getUserLabelByName(CONFIG.GMAIL_LABEL);
  if (!label) label = GmailApp.createLabel(CONFIG.GMAIL_LABEL);

  for (const thread of threads) {
    let success = false;
    try {
      // Find the FIRST message in the thread that has a PDF — process only that one.
      // Prevents duplicates when a thread has multiple messages (reply chain, forwards).
      const messages = thread.getMessages();
      let pdfAttachment = null;
      let senderEmail   = null;
      let messageDate   = null;

      for (const message of messages) {
        const attachments = message.getAttachments({ includeInlineImages: false });
        const pdf = attachments.find(function(a) {
          return a.getName().toLowerCase().endsWith(".pdf");
        });
        if (pdf) {
          pdfAttachment = pdf;
          senderEmail   = message.getFrom();
          messageDate   = message.getDate();
          break; // stop after first PDF — one applicant per thread
        }
      }

      if (!pdfAttachment) {
        label.addToThread(thread);
        continue;
      }

      console.log("Grading application from: " + senderEmail);

      const result = gradeApplication(pdfAttachment, senderEmail, CLAUDE_API_KEY);
      appendToSheet(sheet, result, messageDate);
      appendToScheduleSheet(scheduleSheet, result);

      console.log(
        "Graded: " + result.name +
        " → " + result.total_score + "/100 (" + result.recommendation + ")" +
        " | Available slots: " + (result.available_slots || []).length + "/" + ALL_SLOTS.length
      );

      // Pause between applications to stay under the 50K tokens/min rate limit.
      Utilities.sleep(5000);
      success = true;

    } catch (err) {
      console.error("Error processing thread: " + err.toString());
    }

    // Only label the thread as processed if grading succeeded.
    // If an error occurred, leave it unlabeled so it will be retried next run.
    if (success) label.addToThread(thread);
  }

  // Sort Applications sheet by Total Score descending after all grading is done.
  sortByScore(sheet);
}

// ─── Claude grading ───────────────────────────────────────────────────────────

function gradeApplication(attachment, senderEmail, apiKey) {
  const pdfBase64 = Utilities.base64Encode(attachment.getBytes());

  const response = UrlFetchApp.fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json",
    },
    payload: JSON.stringify({
      model: CONFIG.CLAUDE_MODEL,
      max_tokens: 4000,
      messages: [{
        role: "user",
        content: [
          {
            type: "document",
            source: {
              type: "base64",
              media_type: "application/pdf",
              data: pdfBase64
            }
          },
          {
            type: "text",
            text: buildGradingPrompt()
          }
        ]
      }]
    }),
    muteHttpExceptions: true,
  });

  let body = JSON.parse(response.getContentText());

  // Rate limit hit — wait 65 seconds and retry once
  if (response.getResponseCode() === 429) {
    console.warn("Rate limited. Waiting 65 seconds before retry...");
    Utilities.sleep(65000);

    const retry = UrlFetchApp.fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      payload: JSON.stringify({
        model: CONFIG.CLAUDE_MODEL,
        max_tokens: 4000,
        messages: [{
          role: "user",
          content: [
            { type: "document", source: { type: "base64", media_type: "application/pdf", data: pdfBase64 } },
            { type: "text", text: buildGradingPrompt() }
          ]
        }]
      }),
      muteHttpExceptions: true,
    });

    body = JSON.parse(retry.getContentText());
    if (retry.getResponseCode() !== 200) {
      throw new Error("Claude API error after retry: " + JSON.stringify(body));
    }
  } else if (response.getResponseCode() !== 200) {
    throw new Error("Claude API error: " + JSON.stringify(body));
  }

  const raw = body.content[0].text.replace(/^```json\s*/i, "").replace(/```\s*$/, "").trim();
  const jsonMatch = raw.match(/\{[\s\S]*\}/);
  if (!jsonMatch) throw new Error("Could not parse JSON from Claude response: " + raw);

  const parsed = JSON.parse(jsonMatch[0]);
  parsed.sender_email = senderEmail;

  // Recalculate total from parts — don't trust Claude's math
  parsed.total_score = (parsed.q1_score || 0) + (parsed.q2_score || 0) +
                       (parsed.q3_score || 0) + (parsed.q4_score || 0) +
                       (parsed.activities_score || 0);

  // Enforce recommendation thresholds — Apps Script controls this, not Claude
  const s = parsed.total_score;
  if      (s >= 85) parsed.recommendation = "Strong Pass";
  else if (s >= 75) parsed.recommendation = "Pass";
  else if (s >= 65) parsed.recommendation = "Borderline";
  else              parsed.recommendation = "Reject";

  // Ensure slot arrays exist
  parsed.available_slots   = parsed.available_slots   || [];
  parsed.unavailable_slots = parsed.unavailable_slots || [];

  return parsed;
}

function buildGradingPrompt() {
  const slotList = ALL_SLOTS.join(", ");

  return [
    "You are an evaluator for SDC (SKKU-Deloitte Consulting), a prestigious university consulting club at SKKU.",
    "The attached PDF is a membership application. Grade it based on the rubric below.\n",

    "CALIBRATION: Assume a typical SDC applicant scores 60-65 out of 100.",
    "A score of 70+ requires clearly above-average answers. Scores of 80+ should be uncommon.",
    "90+ is reserved for exceptional, near-publication-quality analysis.",
    "Do NOT cluster scores in the 75-85 range. Use the full 0-100 scale to differentiate applicants.\n",

    "GRADING RUBRIC (total 100 pts):\n",

    "Q4 Business Case Analysis (25 pts):",
    "  20-25: MECE structure applied; root cause identified + 2 or more distinct external/internal factors;",
    "         recommendations are specific and differentiated (NOT generic like 'invest in marketing' or 'improve UX')",
    "  13-19: Decent structure but missing MECE rigor, OR recommendations are generic without clear logic",
    "  7-12:  Lists problems without analytical framework; no structured issue tree",
    "  0-6:   Bullet points with no real analysis, or misunderstands the question entirely",
    "  Penalize -2 for each: vague/generic recommendation, no data or example cited,",
    "    logical gap between analysis and conclusion, stated constraints ignored\n",

    "Q1 Motivation & Fit (20 pts):",
    "  IMPORTANT: SDC is currently recruiting for the first time. Applicants cannot be expected to",
    "  name past SDC projects or members. Score based on consulting understanding and genuine fit.",
    "  17-20: Demonstrates a clear, specific understanding of what consulting involves",
    "         (structured problem-solving, client engagement, hypothesis-driven analysis, etc.);",
    "         explains a concrete personal reason to join a consulting club that goes beyond",
    "         'I want to develop skills'; shows how their background or experiences connect to",
    "         consulting-type work in a way that feels genuine and specific to them",
    "  11-16: Shows genuine interest in consulting with a plausible personal motivation;",
    "         some understanding of what consulting work looks like, but the connection is mostly",
    "         asserted rather than demonstrated with examples or reasoning",
    "  5-10:  Generic motivation ('I want to grow', 'I want consulting experience') with no real",
    "         understanding of what consulting involves or what makes a consulting club valuable",
    "  0-4:   No motivation stated, or a copy-paste answer with no personal connection",
    "  Penalize -2: answer would work equally well for any business, marketing, or finance club",
    "    without changing a single word\n",

    "Q3 Differentiated Strengths (20 pts):",
    "  17-20: Strength is specific and non-obvious; backed by a concrete story; directly maps to consulting work",
    "  11-16: Clear strength identified, but example is vague or consulting relevance is assumed not shown",
    "  5-10:  Generic strength (e.g., 'leadership', 'hard worker', 'communication') without concrete evidence",
    "  0-4:   No distinct strength identified, or answer is entirely generic",
    "  Penalize -2 for each: same example recycled from another answer,",
    "    strength is common/expected at student level (e.g., basic teamwork)\n",

    "Q2 Collaboration Experience (15 pts):",
    "  13-15: Specific team/project named; clear personal contribution; concrete outcome or learning stated",
    "  8-12:  Describes a group experience but personal role is vague or outcome unclear",
    "  4-7:   Mentions 'teamwork' as a concept without a real example",
    "  0-3:   No collaboration example, or example is completely irrelevant",
    "  Penalize -2 for each: passive role described ('I helped out', 'I participated'),",
    "    outcome is not stated, no genuine learning or reflection included\n",

    "Activities & Experience (20 pts) — TWO COMPONENTS, add them together:\n",

    "COMPONENT A — Activity breadth and leadership (0-12 pts):",
    "  10-12: 6 or more activities, with at least one formal leadership role",
    "         (club president, vice president, event organizer, team lead, project manager)",
    "  7-9:   4-5 activities with a leadership role, OR 2-3 activities with high consulting relevance",
    "         (case competition participant, strategy/consulting intern, startup co-founder)",
    "  4-6:   2-3 activities at member level with some business or consulting relevance",
    "  0-3:   1 activity, or activities with no connection to consulting or business",
    "  Diversity and leadership weigh more than raw count.\n",

    "COMPONENT B — Skill self-ratings from the PDF (0-8 pts):",
    "  The PDF contains a self-rating table with five skills (scale 1-5 each):",
    "  AI skills, PPT, Research, Python, Excel.",
    "  Sum all five ratings (minimum 5 if all rated 1, maximum 25 if all rated 5).",
    "  Map the sum to a Component B score:",
    "    Sum 23-25 → 8 pts",
    "    Sum 19-22 → 7 pts",
    "    Sum 15-18 → 6 pts",
    "    Sum 11-14 → 5 pts",
    "    Sum  8-10 → 4 pts",
    "    Sum  5-7  → 2 pts",
    "  If a skill is not rated or missing, treat it as 1.",
    "  Self-ratings cannot be verified — accept them at face value.\n",

    "  activities_score = Component A + Component B (maximum 20).\n",

    "RECOMMENDATION — apply these thresholds strictly based on total_score:",
    "  Strong Pass: >= 85",
    "  Pass:         75-84",
    "  Borderline:   65-74",
    "  Reject:        < 65\n",

    "INTERVIEW SCHEDULE EXTRACTION:",
    "The last pages of the PDF have a section titled '인터뷰 참석 불가 시간'.",
    "It contains two tables: one for 3/14 (토) and one for 3/15 (일).",
    "Each row is a time slot. If the applicant wrote X in the right column, they are NOT available.",
    "Empty or blank = AVAILABLE for interview.",
    "Note: '12:30~13:30' on 3/15 is 점심시간 (lunch break) — skip it, it is not an interview slot.",
    "The complete list of valid slots is: " + slotList,
    "Use ONLY these exact slot labels in your response (e.g. '3/14 11:00~11:20').\n",

    "REGULAR SESSION: Also check if the applicant marked unavailability for Wednesday 6-8pm (정기세션).",
    "Set availability_flag to true if they cannot attend 정기세션.\n",

    "Respond ONLY with a JSON object — no text before or after:\n",
    "{",
    '  "name": "applicant name from 성명 field",',
    '  "major": "전공/복수전공",',
    '  "q1_score": integer 0-20,',
    '  "q2_score": integer 0-15,',
    '  "q3_score": integer 0-20,',
    '  "q4_score": integer 0-25,',
    '  "activities_score": integer 0-20,',
    '  "total_score": sum of above,',
    '  "recommendation": "Strong Pass" or "Pass" or "Borderline" or "Reject",',
    '  "strengths": "2-3가지 핵심 강점 (한국어로 작성)",',
    '  "weaknesses": "2-3가지 약점 또는 면접에서 확인할 사항 (한국어로 작성)",',
    '  "q1_reason": "Q1 점수 근거 1문장 (한국어)",',
    '  "q2_reason": "Q2 점수 근거 1문장 (한국어)",',
    '  "q3_reason": "Q3 점수 근거 1문장 (한국어)",',
    '  "q4_reason": "Q4 점수 근거 1문장 (한국어)",',
    '  "activities_reason": "Activities 점수 근거 1문장 (한국어)",',
    '  "available_slots": ["3/14 11:00~11:20", ...],',
    '  "unavailable_slots": ["3/14 13:30~13:50", ...],',
    '  "availability_flag": true or false,',
    '  "availability_note": "정기세션 불가 사유, 없으면 빈 문자열",',
    '  "summary": "지원자에 대한 2문장 요약 (한국어로 작성)"',
    "}"
  ].join("\n");
}

// ─── Applications sheet ────────────────────────────────────────────────────────

function ensureHeader(sheet) {
  if (sheet.getLastRow() === 0) {
    sheet.appendRow([
      "Timestamp", "Name", "Sender Email", "Major",
      "Total Score", "Q1 (20)", "Q2 (15)", "Q3 (20)", "Q4 (25)", "Activities (20)",
      "Recommendation", "Strengths", "Weaknesses",
      "Availability Flag", "Availability Note", "Summary",
      "Q1 이유", "Q2 이유", "Q3 이유", "Q4 이유", "Activities 이유"
    ]);
    sheet.getRange(1, 1, 1, 21).setFontWeight("bold");
    sheet.setFrozenRows(1);

    const widths = [130, 80, 160, 120, 80, 55, 55, 55, 55, 80, 100, 200, 200, 90, 120, 220, 160, 160, 160, 160, 160];
    widths.forEach(function(w, i) { sheet.setColumnWidth(i + 1, w); });

    sheet.getRange(1, 1, 1000, 21).setWrap(false);
    [12, 13, 15, 16, 17, 18, 19, 20, 21].forEach(function(col) {
      sheet.getRange(1, col, 1000, 1).setWrap(true);
    });
  }
}

function appendToSheet(sheet, result, date) {
  const recommendation = result.recommendation || "";
  const row = [
    date,
    result.name || "",
    result.sender_email || "",
    result.major || "",
    result.total_score || 0,
    result.q1_score || 0,
    result.q2_score || 0,
    result.q3_score || 0,
    result.q4_score || 0,
    result.activities_score || 0,
    recommendation,
    result.strengths || "",
    result.weaknesses || "",
    result.availability_flag ? "FLAG" : "OK",
    result.availability_note || "",
    result.summary || "",
    result.q1_reason || "",
    result.q2_reason || "",
    result.q3_reason || "",
    result.q4_reason || "",
    result.activities_reason || "",
  ];

  sheet.appendRow(row);

  const lastRow = sheet.getLastRow();
  // Auto-expand row height to fit wrapped text
  sheet.autoResizeRows(lastRow, 1);

  const colors = {
    "Strong Pass": "#c6efce",
    "Pass": "#ebf1de",
    "Borderline": "#ffeb9c",
    "Reject": "#ffc7ce",
  };
  if (colors[recommendation]) {
    sheet.getRange(lastRow, 1, 1, 21).setBackground(colors[recommendation]);
  }
}

// ─── Interview Schedule sheet ─────────────────────────────────────────────────

function ensureScheduleSheet(spreadsheet) {
  let s = spreadsheet.getSheetByName(CONFIG.SCHEDULE_SHEET_NAME);

  // If old per-applicant format exists, clear it and rebuild as slot grid
  if (s) {
    const header = s.getRange(1, 1).getValue();
    if (header === "슬롯") return s; // already new format
    s.clearContents();
    s.clearFormats();
  } else {
    s = spreadsheet.insertSheet(CONFIG.SCHEDULE_SHEET_NAME);
  }

  // Header row
  s.appendRow(["슬롯", "배정 지원자", "비고"]);
  s.getRange(1, 1, 1, 3).setFontWeight("bold").setBackground("#f3f3f3");
  s.setFrozenRows(1);

  // 3/14 section header
  s.appendRow(["3/14 (토)", "", ""]);
  s.getRange(s.getLastRow(), 1, 1, 3).setBackground("#c9daf8").setFontWeight("bold");

  // 3/14 slots — no color yet (colored when assigned or finalized)
  SLOTS_SAT.forEach(function(slot) { s.appendRow([slot, "", ""]); });

  // 3/15 section header
  s.appendRow(["3/15 (일)", "", ""]);
  s.getRange(s.getLastRow(), 1, 1, 3).setBackground("#c9daf8").setFontWeight("bold");

  // 3/15 slots
  SLOTS_SUN.forEach(function(slot) { s.appendRow([slot, "", ""]); });

  s.setColumnWidth(1, 165);
  s.setColumnWidth(2, 120);
  s.setColumnWidth(3, 220);

  return s;
}

function appendToScheduleSheet(scheduleSheet, result) {
  const available = result.available_slots || [];

  const lastRow = scheduleSheet.getLastRow();
  const data = scheduleSheet.getRange(2, 1, lastRow - 1, 2).getValues();

  // Greedy assignment: find the applicant's first available unoccupied slot
  let assigned = false;
  for (let i = 0; i < available.length; i++) {
    const target = available[i];
    for (let r = 0; r < data.length; r++) {
      if (data[r][0] === target && !data[r][1]) {
        const rowNum = r + 2;
        scheduleSheet.getRange(rowNum, 2).setValue(result.name || "");
        scheduleSheet.getRange(rowNum, 1, 1, 3).setBackground("#c6efce"); // green = assigned
        assigned = true;
        break;
      }
    }
    if (assigned) break;
  }

  // No available slot found — all their slots were already taken or they have none
  if (!assigned) {
    const note = available.length > 0
      ? "가능 슬롯 전부 배정됨: " + available.join(", ")
      : "가능 슬롯 없음";
    scheduleSheet.appendRow(["[미배정]", result.name || "", note]);
    scheduleSheet.getRange(scheduleSheet.getLastRow(), 1, 1, 3).setBackground("#ffc7ce"); // red
  }
}

// Run once after all applicants are processed to color unassigned slots red.
function finalizeSchedule() {
  const props = PropertiesService.getScriptProperties();
  const spreadsheet = SpreadsheetApp.openById(props.getProperty("SHEET_ID"));
  const s = spreadsheet.getSheetByName(CONFIG.SCHEDULE_SHEET_NAME);
  if (!s) { console.error("Interview Schedule sheet not found"); return; }

  const lastRow = s.getLastRow();
  const data = s.getRange(2, 1, lastRow - 1, 3).getValues();
  let unassigned = 0;

  for (let r = 0; r < data.length; r++) {
    const slot   = String(data[r][0]);
    const name   = data[r][1];
    const rowNum = r + 2;

    if (!slot.startsWith("3/")) continue; // skip section headers and overflow rows
    if (!name) {
      s.getRange(rowNum, 1, 1, 3).setBackground("#ffc7ce"); // red = no one available
      unassigned++;
    }
  }

  console.log("Schedule finalized. Unassigned slots marked red: " + unassigned);
}

// ─── Setup & utilities ─────────────────────────────────────────────────────────

function setupTrigger() {
  ScriptApp.getProjectTriggers().forEach(function(t) { ScriptApp.deleteTrigger(t); });

  ScriptApp.newTrigger("processNewApplications")
    .timeBased()
    .everyMinutes(15)
    .create();

  console.log("Trigger installed: processNewApplications runs every 15 minutes");
}

// Deletes all data rows where Name (column B) is blank.
// Run once manually to remove leftover partial rows from old versions.
// Clears ALL applicant data and resets both sheets to a clean state.
// After running this: remove Gmail labels from all threads, then wait for re-processing.
function resetAllData() {
  const props = PropertiesService.getScriptProperties();
  const spreadsheet = SpreadsheetApp.openById(props.getProperty("SHEET_ID"));

  // 1. Clear Applications sheet — delete all rows below header
  const sheet = spreadsheet.getSheetByName(CONFIG.SHEET_NAME);
  if (sheet && sheet.getLastRow() > 1) {
    sheet.deleteRows(2, sheet.getLastRow() - 1);
    console.log("Applications sheet cleared.");
  }

  // 2. Delete and recreate the Interview Schedule sheet as a fresh slot grid
  const existing = spreadsheet.getSheetByName(CONFIG.SCHEDULE_SHEET_NAME);
  if (existing) {
    spreadsheet.deleteSheet(existing);
    console.log("Old Interview Schedule sheet deleted.");
  }
  ensureScheduleSheet(spreadsheet);
  console.log("Interview Schedule sheet rebuilt.");

  console.log("Reset complete. Now remove the SDC-Applications Gmail label from all threads, then wait for the trigger or run processNewApplications manually.");
}

function cleanupSheet() {
  const props = PropertiesService.getScriptProperties();
  const spreadsheet = SpreadsheetApp.openById(props.getProperty("SHEET_ID"));
  const sheet = spreadsheet.getSheetByName(CONFIG.SHEET_NAME);
  if (!sheet) { console.error("Applications sheet not found"); return; }

  const lastRow = sheet.getLastRow();
  const rowsToDelete = [];

  if (lastRow < 2) {
    console.log("No data rows to clean up.");
    return;
  }

  // Read all Name values at once (one API call) instead of one per row
  const nameValues = sheet.getRange(2, 2, lastRow - 1, 1).getValues();
  for (let i = 0; i < nameValues.length; i++) {
    const name = nameValues[i][0];
    if (!name || String(name).trim() === "") {
      rowsToDelete.push(i + 2); // +2: 0-indexed + skipped header
    }
  }

  // Delete bottom-up so row indices stay valid
  for (let i = rowsToDelete.length - 1; i >= 0; i--) {
    sheet.deleteRow(rowsToDelete[i]);
  }

  console.log("Deleted " + rowsToDelete.length + " empty row(s). Sheet now has " + (sheet.getLastRow() - 1) + " applicant(s).");
}

// Sorts the Applications sheet by Total Score (col 5) descending — highest score first.
// Called automatically after processNewApplications(). Also run manually if needed.
function sortByScore(sheetArg) {
  const props = PropertiesService.getScriptProperties();
  const sheet = sheetArg || SpreadsheetApp.openById(props.getProperty("SHEET_ID"))
                                          .getSheetByName(CONFIG.SHEET_NAME);
  if (!sheet) { console.error("Applications sheet not found"); return; }

  const lastRow = sheet.getLastRow();
  if (lastRow < 2) { console.log("Nothing to sort."); return; }

  // Sort data rows only (skip header row 1), by column 5 (Total Score), descending
  sheet.getRange(2, 1, lastRow - 1, 21).sort({ column: 5, ascending: false });
  console.log("Applications sorted by Total Score (high → low).");
}

function debugGmail() {
  const email = Session.getActiveUser().getEmail();
  console.log("Script running as: " + email);

  const threads = GmailApp.search("has:attachment");
  console.log("Total emails with attachments found: " + threads.length);

  const inbox = GmailApp.getInboxThreads(0, 5);
  inbox.forEach(function(t) { console.log("Inbox: " + t.getFirstMessageSubject()); });
}

function fixSheetFormatting() {
  const props = PropertiesService.getScriptProperties();
  const spreadsheet = SpreadsheetApp.openById(props.getProperty("SHEET_ID"));

  // Applications sheet
  const sheet = spreadsheet.getSheetByName(CONFIG.SHEET_NAME);
  if (sheet) {
    // Always overwrite row 1 — handles upgrades from older versions
    sheet.getRange(1, 1, 1, 21).setValues([[
      "Timestamp", "Name", "Sender Email", "Major",
      "Total Score", "Q1 (20)", "Q2 (15)", "Q3 (20)", "Q4 (25)", "Activities (20)",
      "Recommendation", "Strengths", "Weaknesses",
      "Availability Flag", "Availability Note", "Summary",
      "Q1 이유", "Q2 이유", "Q3 이유", "Q4 이유", "Activities 이유"
    ]]);
    sheet.getRange(1, 1, 1, 21).setFontWeight("bold").setBackground("#f3f3f3");
    sheet.setFrozenRows(1);
    sheet.setFrozenColumns(2); // Name stays visible when scrolling right

    const widths = [130, 100, 160, 120, 80, 55, 55, 55, 55, 80, 100, 200, 200, 90, 120, 220, 160, 160, 160, 160, 160];
    widths.forEach(function(w, i) { sheet.setColumnWidth(i + 1, w); });

    sheet.getRange(1, 1, 1000, 21).setWrap(false);
    [12, 13, 15, 16, 17, 18, 19, 20, 21].forEach(function(col) {
      sheet.getRange(1, col, 1000, 1).setWrap(true);
    });
    console.log("Applications sheet header and formatting applied (21 columns)");
  }

  // Schedule sheet
  ensureScheduleSheet(spreadsheet);
  console.log("Interview Schedule sheet ensured");
}
