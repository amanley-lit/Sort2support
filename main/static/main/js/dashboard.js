console.log("dashboard.js loaded");

let colorModeEnabled = false;
let symbolModeEnabled = false;

// 🔧 Toggle this to choose preview style
const autoPreview = false;  // true = live updates, false = button only
const debounceDelay = 500;  // ms delay before auto-preview fires

// === Grouping thresholds: only Needs Support vs Instructional ===
function getGroupFromPercent(pct) {
  if (pct >= 50) return "Instructional";
  return "Needs Support";
}

// === Enrich parsed data with groups and teacher override ===
function groupStudentsByConcept(parsedData, lesson1Max, lesson2Max) {
  return parsedData.map(student => {
    const pct1 = Math.round((student.score1 / lesson1Max) * 100);
    const pct2 = Math.round((student.score2 / lesson2Max) * 100);

    return {
      ...student,
      pct1,
      pct2,
      group1: getGroupFromPercent(pct1),
      group2: getGroupFromPercent(pct2),     
    };
  });
}

// === Render two grouped tables ===
function renderGroupedTables(groupedData, lesson1, lesson2) {
  const container = document.getElementById("tableContainer");
  container.innerHTML = "";

  // Concept 1
  const table1 = document.createElement("table");
  table1.classList.add("excel-table");
  table1.innerHTML = `
    <thead>
      <tr><th>Student</th><th>${lesson1.concept}</th><th>Group</th></tr>
    </thead>
    <tbody>
      ${groupedData.map(s => `
        <tr>
          <td>${s.name}</td>
          <td>${s.score1}</td>
        </tr>
      `).join("")}
    </tbody>
  `;
  container.appendChild(table1);

  // Concept 2
  const table2 = document.createElement("table");
  table2.classList.add("excel-table");
  table2.innerHTML = `
    <thead>
      <tr><th>Student</th><th>${lesson2.concept}</th><th>Group</th></tr>
    </thead>
    <tbody>
      ${groupedData.map(s => `
        <tr>
          <td>${s.name}</td>
          <td>${s.score2}</td>
        </tr>
      `).join("")}
    </tbody>
  `;
  container.appendChild(table2);
}

// === Render Preview Table (editable) ===
function renderPreviewTable(data, lesson1Name, lesson2Name) {
  const container = document.getElementById("tableContainer");
  const hiddenInputs = document.getElementById("hiddenInputs");

  previewButton?.addEventListener("click", () => {
    const text = pasteArea.value.trim();
    tableContainer.innerHTML = ""; // clear old table
    hiddenInputs.innerHTML = "";   // clear old hidden inputs
    pasteError.textContent = "";

    // 🔑 Look up max scores from selected lessons
    const lesson1Select = document.getElementById("lesson_1");
    const lesson2Select = document.getElementById("lesson_2");
    const lesson1Max = lesson1Select ? parseInt(lesson1Select.selectedOptions[0]?.dataset.max || "0", 10) : 0;
    const lesson2Max = lesson2Select ? parseInt(lesson2Select.selectedOptions[0]?.dataset.max || "0", 10) : 0;

    if (!text) {
      pasteError.textContent = "Please paste some data first.";
      return;
    }

    const rows = text.split(/\n/).map(r => r.trim()).filter(r => r);
    if (rows.length === 0) {
      pasteError.textContent = "No valid rows found.";
      return;
    }

    const table = document.createElement("table");
    table.classList.add("preview-table");

    // Header row
    const headerRow = table.insertRow();
    headerRow.insertCell().innerText = "Name";
    const h1 = headerRow.insertCell(); h1.id = "lesson1Header"; h1.innerText = "Concept 1";
    const h2 = headerRow.insertCell(); h2.id = "lesson2Header"; h2.innerText = "Concept 2";

    let errors = [];

    // Data rows
    rows.forEach((line, i) => {
      const parts = line.split(/[\s,]+/).map(p => p.trim()).filter(p => p);
      const row = table.insertRow();

      const name = parts[0] || "";
      const score1 = parseInt(parts[1], 10) || 0;
      const score2 = parseInt(parts[2], 10) || 0;

      row.insertCell().innerText = name;
      row.insertCell().innerText = score1;
      row.insertCell().innerText = score2;

      // 🚨 validate against max
      if (lesson1Max && score1 > lesson1Max) {
        errors.push(`Row ${i+1}: Score 1 (${score1}) exceeds max (${lesson1Max}).`);
        row.classList.add("error-row");
      }
      if (lesson2Max && score2 > lesson2Max) {
        errors.push(`Row ${i+1}: Score 2 (${score2}) exceeds max (${lesson2Max}).`);
        row.classList.add("error-row");
      }

      // Hidden inputs for Django
      hiddenInputs.insertAdjacentHTML("beforeend", `
        <input type="hidden" name="student_name_${i+1}" value="${name}">
        <input type="hidden" name="ufli_score_1_${i+1}" value="${score1}">
        <input type="hidden" name="ufli_score_2_${i+1}" value="${score2}">
      `);

    }); // closes rows.forEach

    if (errors.length > 0) {
      pasteError.textContent = errors.join(" ");
      return; // 🚫 don’t append the table if invalid scores
    }

    tableContainer.appendChild(table);

    // Update headers with current lesson selections
    updateHeaders();
  }); // closes previewButton click handler
}     // closes renderPreviewTable


/*  // future: grouping logic for Sort2Support
  const lesson1Max = parseInt(document.getElementById("lesson_1")?.selectedOptions[0]?.dataset.max || "100");
  const lesson2Max = parseInt(document.getElementById("lesson_2")?.selectedOptions[0]?.dataset.max || "100");

  const rows = rawInput.trim().split("\n").filter(line => line.trim() !== "");
  const parsedData = rows.map((line) => {
    const parts = line.trim().split(/[\t, ,]+/); // handles tabs, commas, double spaces
    const name = parts[0] || "";
    const score1 = parseInt(parts[1], 10) || 0;
    const score2 = parseInt(parts[2], 10) || 0;

    const pct1 = Math.round((score1 / lesson1Max) * 100);
    const pct2 = Math.round((score2 / lesson2Max) * 100);

    const group1 = getGroupFromPercent(pct1);
    const group2 = getGroupFromPercent(pct2);

    return { name, score1, score2, group1, group2 };
  });
*/

// === Sample Data (for testing) ===
const currentData = [
  { name: "Amy", score: 85, group: "chips" },
  { name: "Jordan", score: 72, group: "salsa" },
  { name: "Maya", score: 90, group: "guac" },
  { name: "Leo", score: 65, group: "queso" }
];

// === Load UFLI Lesson Table ===
function loadUFLILessonTable() {
  fetch("/static/main/data/ufli_lessons.json")
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById("lessonTableContainer");
      if (!container) return;

      const table = document.createElement("table");
      table.classList.add("preview-table");

      table.innerHTML = `
        <thead>
          <tr><th>Lesson</th><th>Title</th><th>Skills</th></tr>
        </thead>
        <tbody>
          ${data.map(l => `
            <tr>
              <td>${l.lesson}</td>
              <td>${l.title}</td>
              <td>${l.skills.join(", ")}</td>
            </tr>
          `).join("")}
        </tbody>
      `;

      container.innerHTML = "";
      container.appendChild(table);
    });
}
function toggleGroupings() {
  const content = document.getElementById("groupingsContent");
  const button = document.querySelector(".collapsible-toggle");
  content.classList.toggle("open");

  // Update arrow indicator
  if (content.classList.contains("open")) {
    button.textContent = "▼ Reorganized Groupings";
  } else {
    button.textContent = "▶ Reorganized Groupings";
  }
}
function toggleGroupingInfo() {
  const content = document.getElementById("groupingInfoContent");
  const button = document.querySelector(".collapsible-toggle");
  content.classList.toggle("open");

  if (content.classList.contains("open")) {
    button.textContent = "▼ Grouping Info";
  } else {
    button.textContent = "▶ Grouping Info";
  }
}
document.addEventListener("DOMContentLoaded", () => {
  // --- Step 1: Lesson header updates ---
  const lesson1Select = document.getElementById("lesson_1");
  const lesson2Select = document.getElementById("lesson_2");

  function updateHeaders() {
    const lesson1Option = lesson1Select?.selectedOptions[0];
    const lesson2Option = lesson2Select?.selectedOptions[0];

    const lesson1Name = lesson1Option ? lesson1Option.text : "Concept 1";
    const lesson1Max  = lesson1Option?.dataset.max || "";

    const lesson2Name = lesson2Option ? lesson2Option.text : "Concept 2";
    const lesson2Max  = lesson2Option?.dataset.max || "";

    const header1 = document.getElementById("lesson1Header");
    const header2 = document.getElementById("lesson2Header");
    console.log("lesson1:", lesson1Name, "max:", lesson1Max);

    if (header1) {
      header1.textContent = lesson1Max
        ? `${lesson1Name} (Max ${lesson1Max})`
        : lesson1Name;
    }
    if (header2) {
      header2.textContent = lesson2Max
        ? `${lesson2Name} (Max ${lesson2Max})`
        : lesson2Name;
    }
  }

  lesson1Select?.addEventListener("change", updateHeaders);
  lesson2Select?.addEventListener("change", updateHeaders);
  updateHeaders(); // run once on load

  // --- Step 2: Toggle entry blocks ---
  const entryMode = document.getElementById("entryMode");
  const classSizeEntry = document.getElementById("classSizeEntry");
  const pasteEntry = document.getElementById("pasteEntry");
  const manualEntry = document.getElementById("manualEntry");

  function toggleEntryBlocks() {
    classSizeEntry.style.display = "none";
    pasteEntry.style.display = "none";
    manualEntry.style.display = "none";

    if (entryMode.value === "size") {
      console.log("Showing class size entry");
      classSizeEntry.style.display = "block";
    } else if (entryMode.value === "paste") {
      console.log("Showing paste entry");
      pasteEntry.style.display = "block";
      document.getElementById("pasteArea")?.focus();
    } else if (entryMode.value === "manual") {
      console.log("Showing manual entry");
      manualEntry.style.display = "block";
    }

    console.log("entryMode changed to:", entryMode.value);
  }

  entryMode.addEventListener("change", toggleEntryBlocks);
  toggleEntryBlocks(); // run once on load

  // --- Step 3: Hook up preview button ---
  renderPreviewTable();  // ✅ use your function instead of duplicating code
});

console.log("✅ dashboard.js parsed successfully");
