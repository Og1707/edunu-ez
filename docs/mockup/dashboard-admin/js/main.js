/* =========================================================
   EDUPANEL - CONTROLADOR PRINCIPAL Y GESTIÓN DE DATOS
   ========================================================= */

// ============ BASE DE DATOS LOCAL / MOCK DATA ============
const database = {
  periods: ["2026-1", "2025-2", "2025-1"],
  activePeriod: "2026-1",
  
  courses: [
    { id: "10° A", grade: "Secundaria", teacher: "Prof. Roberto Gómez", totalStudents: 48, promedio: 85.4, passRate: "93.7%", bestSubject: "Lenguaje (92%)" },
    { id: "10° B", grade: "Secundaria", teacher: "Prof. Clara Domínguez", totalStudents: 45, promedio: 83.1, passRate: "88.8%", bestSubject: "Matemáticas (89%)" },
    { id: "11° A", grade: "Secundaria", teacher: "Prof. Andrés Morales", totalStudents: 32, promedio: 86.0, passRate: "94.0%", bestSubject: "Ciencias (90%)" }
  ],

  students: [
    {
      id: 1, initials: "AR", name: "Ana Ramírez", course: "10° A", grade: "Secundaria",
      promedio: 85, attendance: "98%", actividades: "46/48", aciertos: 250, fallos: 41,
      trendColor: "#22c55e", trendType: "up", status: "Excelente", statusClass: "excelente",
      dotClass: "green", dotIcon: "check", aciertosPct: "85%", fallosPct: "15%",
      parent: "Claudia Morales (Madre)", phone: "+57 312 456 7890", email: "ana.ramirez@estudiante.edu",
      evolution: [40, 55, 62, 70, 78, 80, 85],
      subjects: { Lenguaje: 88, Matemáticas: 90, Ciencias: 80, Inglés: 70 },
      aiStrengths: "Matemáticas y Razonamiento Lógico",
      aiWeaknesses: "Vocabulario específico en Inglés",
      aiPriority: "Media",
      aiSummary: "La estudiante presenta un rendimiento sobresaliente en ciencias exactas y lógica matemática (85%). Mantiene un ritmo constante de estudio y alta participación en clase.",
      activities: [
        { name: "Álgebra básica", course: "10° A", result: "Excelente", badge: "excelente", aciertos: 38, fallos: 2, pct: "95%" },
        { name: "Lectura Crítica", course: "10° A", result: "Bueno", badge: "bueno", aciertos: 28, fallos: 5, pct: "84%" }
      ]
    },
    {
      id: 2, initials: "MG", name: "María González", course: "10° A", grade: "Secundaria",
      promedio: 87, attendance: "96%", actividades: "42/48", aciertos: 89, fallos: 11,
      trendColor: "#22c55e", trendType: "up", status: "Bueno", statusClass: "bueno",
      dotClass: "green", dotIcon: "check", aciertosPct: "89%", fallosPct: "11%",
      parent: "Jorge González (Padre)", phone: "+57 310 987 6543", email: "maria.gonzalez@estudiante.edu",
      evolution: [35, 58, 60, 68, 84, 73, 91],
      subjects: { Lenguaje: 92, Matemáticas: 91, Ciencias: 84, Inglés: 76 },
      aiStrengths: "Lenguaje, Redacción y Matemáticas",
      aiWeaknesses: "Comprensión lectora en textos avanzados en Inglés",
      aiPriority: "Media",
      aiSummary: "La estudiante presenta un buen rendimiento general (87%). Sus principales fortalezas se encuentran en Matemáticas e Historia. Sin embargo, presenta dificultades recurrentes en comprensión lectora en idioma extranjero.",
      activities: [
        { name: "Álgebra básica", course: "10° A", result: "Excelente", badge: "excelente", aciertos: 35, fallos: 4, pct: "89%" },
        { name: "Comprensión T.", course: "10° A", result: "Bueno", badge: "bueno", aciertos: 29, fallos: 7, pct: "76%" }
      ]
    },
    {
      id: 3, initials: "MC", name: "María Ciencias", course: "10° A", grade: "Secundaria",
      promedio: 84, attendance: "94%", actividades: "40/48", aciertos: 44, fallos: 5,
      trendColor: "#3b82f6", trendType: "flat", status: "Bueno", statusClass: "bueno",
      dotClass: "blue", dotIcon: "check", aciertosPct: "84%", fallosPct: "16%",
      parent: "Patricia Casas (Madre)", phone: "+57 315 222 3344", email: "maria.ciencias@estudiante.edu",
      evolution: [50, 52, 60, 63, 70, 75, 84],
      subjects: { Lenguaje: 80, Matemáticas: 78, Ciencias: 91, Inglés: 74 },
      aiStrengths: "Biología, Química y Método Científico",
      aiWeaknesses: "Cálculo algebraico y trigonometría",
      aiPriority: "Baja",
      aiSummary: "Destacado interés por experimentos de ciencias naturales (91%). Requiere apoyo puntual en ejercicios de álgebra práctica.",
      activities: [
        { name: "Biología Celular", course: "10° A", result: "Excelente", badge: "excelente", aciertos: 40, fallos: 2, pct: "95%" },
        { name: "Física Básica", course: "10° A", result: "Bueno", badge: "bueno", aciertos: 26, fallos: 6, pct: "81%" }
      ]
    },
    {
      id: 4, initials: "MI", name: "María Inglés", course: "10° A", grade: "Secundaria",
      promedio: 76, attendance: "88%", actividades: "34/48", aciertos: 33, fallos: 10,
      trendColor: "#f59e0b", trendType: "flatdown", status: "En Riesgo", statusClass: "riesgo",
      dotClass: "orange", dotIcon: "check", aciertosPct: "76%", fallosPct: "24%",
      parent: "Ricardo Ibarra (Padre)", phone: "+57 318 444 5566", email: "maria.ingles@estudiante.edu",
      evolution: [60, 58, 55, 52, 50, 60, 76],
      subjects: { Lenguaje: 70, Matemáticas: 68, Ciencias: 72, Inglés: 85 },
      aiStrengths: "Idiomas y Conversación en Inglés",
      aiWeaknesses: "Matemáticas y Ciencias Exactas",
      aiPriority: "Alta",
      aiSummary: "Excelente desenvolvimiento lingüístico, pero sus calificaciones en matemáticas (68%) la ubican en riesgo académico. Requiere tutoría de nivelación.",
      activities: [
        { name: "Grammar Quiz", course: "10° A", result: "Excelente", badge: "excelente", aciertos: 32, fallos: 3, pct: "91%" },
        { name: "Álgebra básica", course: "10° A", result: "Atención", badge: "atencion", aciertos: 18, fallos: 14, pct: "56%" }
      ]
    },
    {
      id: 5, initials: "MR", name: "María Ramírez", course: "10° A", grade: "Secundaria",
      promedio: 62, attendance: "78%", actividades: "22/48", aciertos: 20, fallos: 18,
      trendColor: "#ef4444", trendType: "down", status: "Requiere Atención", statusClass: "atencion",
      dotClass: "red", dotIcon: "check", aciertosPct: "62%", fallosPct: "38%",
      parent: "Luisa Rincón (Madre)", phone: "+57 320 888 9900", email: "maria.ramirez@estudiante.edu",
      evolution: [70, 65, 60, 55, 50, 45, 62],
      subjects: { Lenguaje: 60, Matemáticas: 58, Ciencias: 65, Inglés: 55 },
      aiStrengths: "Expresión Artística",
      aiWeaknesses: "Entregas tardías y bajo rendimiento general",
      aiPriority: "Urgente",
      aiSummary: "La estudiante presenta rezago académico significativo (62%) con bajo índice de asistencia (78%). Se aconseja citación a acudientes y plan de seguimiento intensivo.",
      activities: [
        { name: "Taller General", course: "10° A", result: "Atención", badge: "atencion", aciertos: 15, fallos: 15, pct: "50%" },
        { name: "Ecuaciones", course: "10° A", result: "Atención", badge: "atencion", aciertos: 12, fallos: 16, pct: "42%" }
      ]
    }
  ]
};

// ============ VARIABLES DE ESTADO GLOBALES ============
let currentFilteredStudents = [...database.students];
let selectedStudentIndex = 1; // María González por defecto
let mainChart = null;
let evolutionChart = null;
let subjectChart = null;

// Estado del Segmentador de Fechas
let currentDateFilter = {
  from: "2026-01-01",
  to: "2026-07-31",
  label: "01/01/2026 - 31/07/2026",
  preset: "all",
  startMonthIdx: 0,
  endMonthIdx: 6
};

const allMonthLabels = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul"];

// ============ FUNCIONES DE RENDERIZADO ============

// Renderizado de Sparklines SVG
function generateSparkline(data, width = 54, height = 22, color = "#3b82f6") {
  if (!data || data.length < 2) return "";
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = (max - min) || 1;
  const pts = data.map((val, idx) => {
    const x = (idx / (data.length - 1)) * (width - 4) + 2;
    const y = height - ((val - min) / range) * (height - 6) - 3;
    return [x, y];
  });
  const pathD = pts.map((p, i) => (i === 0 ? "M" : "L") + p[0].toFixed(1) + "," + p[1].toFixed(1)).join(" ");
  return `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" fill="none">
    <path d="${pathD}" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
}

// Renderizar tabla principal del Dashboard
function renderDashboardStudentsTable(studentsList) {
  const tbody = document.getElementById("studentsTbody");
  const countLabel = document.getElementById("tableCountLabel");
  if (!tbody) return;

  tbody.innerHTML = "";
  if (countLabel) {
    countLabel.textContent = `${studentsList.length} estudiante${studentsList.length === 1 ? '' : 's'} listado${studentsList.length === 1 ? '' : 's'}`;
  }

  if (studentsList.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;color:var(--text-muted);">No se encontraron estudiantes con los filtros seleccionados.</td></tr>`;
    return;
  }

  studentsList.forEach((s) => {
    const tr = document.createElement("tr");
    tr.dataset.id = s.id;
    if (database.students[selectedStudentIndex] && database.students[selectedStudentIndex].id === s.id) {
      tr.classList.add("selected-row");
    }

    tr.innerHTML = `
      <td>
        <div class="student-cell">
          <div class="student-avatar">${s.initials}</div>
          <span style="font-weight:600;">${s.name}</span>
        </div>
      </td>
      <td>${s.course}</td>
      <td><strong>${s.promedio}%</strong></td>
      <td><span class="status-dot ${s.dotClass}"><i data-lucide="check"></i></span></td>
      <td>${s.aciertos}</td>
      <td>${s.fallos}</td>
      <td><div class="trend-cell">${generateSparkline(s.evolution, 54, 22, s.trendColor)}</div></td>
      <td><span class="badge ${s.statusClass}">${s.status}</span></td>
    `;

    tr.addEventListener("click", () => {
      const realIndex = database.students.findIndex(st => st.id === s.id);
      if (realIndex !== -1) {
        selectStudent(realIndex);
      }
    });

    tbody.appendChild(tr);
  });

  if (window.lucide) lucide.createIcons();
}

// Renderizar tabla completa de gestión de estudiantes (Vista 2)
function renderFullStudentsTable(studentsList) {
  const tbody = document.getElementById("fullStudentsTbody");
  if (!tbody) return;

  tbody.innerHTML = "";
  if (studentsList.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;padding:24px;color:var(--text-muted);">No hay estudiantes que coincidan con la búsqueda.</td></tr>`;
    return;
  }

  studentsList.forEach(s => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>
        <div class="student-cell">
          <div class="student-avatar">${s.initials}</div>
          <div>
            <div style="font-weight:600;">${s.name}</div>
            <div style="font-size:10.5px;color:var(--text-muted);">${s.email}</div>
          </div>
        </div>
      </td>
      <td>${s.course}</td>
      <td><strong>${s.promedio}%</strong></td>
      <td>${s.attendance}</td>
      <td>${s.actividades}</td>
      <td style="color:var(--green-dark);font-weight:600;">${s.aciertos}</td>
      <td style="color:var(--red);font-weight:600;">${s.fallos}</td>
      <td><span class="badge ${s.statusClass}">${s.status}</span></td>
      <td>
        <button class="btn-secondary" style="padding:4px 9px;font-size:11px;" onclick="window.viewStudentDetails(${s.id})">
          <i data-lucide="eye" style="width:12px;height:12px;"></i> Ver Perfil
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  if (window.lucide) lucide.createIcons();
}

// Renderizar tarjetas de cursos (Vista 3)
function renderCoursesView() {
  const container = document.getElementById("coursesGridContainer");
  if (!container) return;

  container.innerHTML = "";
  database.courses.forEach(c => {
    const card = document.createElement("div");
    card.className = "course-card";
    card.innerHTML = `
      <div class="course-card-top">
        <span class="course-badge">${c.grade}</span>
        <span style="font-size:11.5px;color:var(--text-muted);">${c.totalStudents} Estudiantes</span>
      </div>
      <div>
        <h3 style="margin:0 0 4px 0;font-size:17px;font-weight:700;color:var(--text-dark);">${c.id}</h3>
        <div style="font-size:12px;color:var(--text-mid);">${c.teacher}</div>
      </div>
      <div class="course-stats-row">
        <div>
          <div class="slabel">Promedio</div>
          <div class="sval" style="color:var(--blue-dark);">${c.promedio}%</div>
        </div>
        <div>
          <div class="slabel">Aprobación</div>
          <div class="sval" style="color:var(--green-dark);">${c.passRate}</div>
        </div>
        <div>
          <div class="slabel">Destacada</div>
          <div class="sval" style="font-size:11px;overflow:hidden;text-overflow:ellipsis;">${c.bestSubject}</div>
        </div>
      </div>
      <button class="btn-secondary" style="justify-content:center;margin-top:4px;" onclick="window.filterByCourse('${c.id}')">
        <i data-lucide="filter" style="width:13px;height:13px;"></i> Ver Alumnos de este Curso
      </button>
    `;
    container.appendChild(card);
  });

  if (window.lucide) lucide.createIcons();
}

// ============ SELECCIÓN DE ESTUDIANTE Y PANEL 360 ============
function selectStudent(idx) {
  selectedStudentIndex = idx;
  const s = database.students[idx];
  if (!s) return;

  // Actualizar filas activas en tablas
  document.querySelectorAll("#studentsTbody tr").forEach(r => r.classList.remove("selected-row"));
  const activeRow = document.querySelector(`#studentsTbody tr[data-id="${s.id}"]`);
  if (activeRow) activeRow.classList.add("selected-row");

  // Actualizar selector de estudiante en los filtros
  const studentSelect = document.getElementById("fStudentSelect");
  if (studentSelect) {
    studentSelect.value = s.name;
  }

  // Actualizar datos del panel
  const avatar = document.getElementById("profileAvatar");
  const name = document.getElementById("profileName");
  const meta = document.getElementById("profileMeta");
  const statPromedio = document.getElementById("statPromedio");
  const statActividades = document.getElementById("statActividades");
  const statAciertos = document.getElementById("statAciertos");
  const statFallos = document.getElementById("statFallos");
  const aiText = document.getElementById("aiAnalysisText");
  const aiTags = document.getElementById("aiTagsContainer");

  if (avatar) avatar.textContent = s.initials;
  if (name) name.textContent = s.name;
  if (meta) meta.textContent = `${s.course} • Período ${database.activePeriod}`;
  if (statPromedio) statPromedio.textContent = s.promedio + "%";
  if (statActividades) statActividades.textContent = s.actividades;
  if (statAciertos) statAciertos.textContent = s.aciertosPct;
  if (statFallos) statFallos.textContent = s.fallosPct;

  // Asignaturas
  if (document.getElementById("subjLenguaje")) document.getElementById("subjLenguaje").textContent = s.subjects.Lenguaje + "%";
  if (document.getElementById("subjMatematicas")) document.getElementById("subjMatematicas").textContent = s.subjects.Matemáticas + "%";
  if (document.getElementById("subjCiencias")) document.getElementById("subjCiencias").textContent = s.subjects.Ciencias + "%";
  if (document.getElementById("subjIngles")) document.getElementById("subjIngles").textContent = s.subjects.Inglés + "%";

  // Tabla mini actividades
  const miniTbody = document.getElementById("miniActivityTbody");
  if (miniTbody && s.activities) {
    miniTbody.innerHTML = "";
    s.activities.forEach(act => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${act.name}</td>
        <td>${act.course}</td>
        <td><span class="mini-badge ${act.badge}">${act.result}</span></td>
        <td>${act.aciertos}</td>
        <td>${act.fallos}</td>
        <td>${act.pct}</td>
      `;
      miniTbody.appendChild(tr);
    });
  }

  // Tarjeta IA
  if (aiText) aiText.textContent = s.aiSummary;
  if (aiTags) {
    aiTags.innerHTML = `
      <span class="ai-tag">Fortaleza: ${s.aiStrengths}</span>
      <span class="ai-tag">Refuerzo: ${s.aiWeaknesses}</span>
      <span class="ai-tag">Prioridad: ${s.aiPriority}</span>
    `;
  }

  // Gráfico de evolución filtrado por fecha
  updateEvolutionChartData();

  openProfilePanel();
}

function openProfilePanel() {
  const panel = document.getElementById("profilePanel");
  const backdrop = document.getElementById("panelBackdrop");
  if (!panel) return;
  panel.classList.remove("closed");
  if (window.innerWidth <= 1240 && backdrop) {
    backdrop.style.display = "block";
  }
}

function closeProfilePanel() {
  const panel = document.getElementById("profilePanel");
  const backdrop = document.getElementById("panelBackdrop");
  if (!panel) return;
  panel.classList.add("closed");
  if (backdrop) {
    backdrop.style.display = "none";
  }
}

// ============ GRÁFICOS CON CHART.JS Y CANVASES ============
function initMainChart() {
  const canvas = document.getElementById("mainChart");
  if (!canvas) return;

  if (mainChart) {
    mainChart.destroy();
    mainChart = null;
  }

  const ctx = canvas.getContext("2d");
  const gradient = ctx.createLinearGradient(0, 0, 0, 200);
  gradient.addColorStop(0, "rgba(59, 130, 246, 0.25)");
  gradient.addColorStop(1, "rgba(59, 130, 246, 0.01)");

  const dataLabelPlugin = {
    id: "dataLabelPlugin",
    afterDatasetsDraw(chart) {
      const { ctx } = chart;
      chart.data.datasets.forEach((ds, dsIndex) => {
        if (!ds.showValueLabels) return;
        const meta = chart.getDatasetMeta(dsIndex);
        meta.data.forEach((point, i) => {
          const val = ds.data[i];
          ctx.save();
          ctx.font = "700 11px Inter, sans-serif";
          ctx.fillStyle = "#374151";
          ctx.textAlign = "center";
          ctx.fillText(val + "%", point.x, point.y - 10);
          ctx.restore();
        });
      });
    }
  };

  mainChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: ["Matemáticas", "Ciencias", "Lenguaje", "Inglés", "Historia", "Artes"],
      datasets: [{
        data: [91, 83, 87, 76, 89, 94],
        borderColor: "#3b82f6",
        backgroundColor: gradient,
        fill: true,
        tension: 0.38,
        pointBackgroundColor: "#fff",
        pointBorderColor: "#3b82f6",
        pointBorderWidth: 2,
        pointRadius: 4,
        borderWidth: 2.5,
        showValueLabels: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      resizeDelay: 50,
      layout: { padding: { top: 18, left: 4, right: 4, bottom: 0 } },
      plugins: { legend: { display: false }, tooltip: { enabled: true } },
      scales: {
        y: {
          min: 50, max: 100,
          grid: { color: "#f0f1f3", drawTicks: false },
          border: { display: false },
          ticks: { stepSize: 10, color: "#9199a6", font: { size: 10.5 } }
        },
        x: {
          grid: { display: false },
          border: { display: false },
          ticks: { color: "#6b7280", font: { size: 10.5, weight: "600" } }
        }
      }
    },
    plugins: [dataLabelPlugin]
  });
}

function updateEvolutionChartData() {
  if (!evolutionChart) return;
  const s = database.students[selectedStudentIndex];
  const fullEv = s?.evolution || [35, 58, 60, 68, 84, 73, 91];

  const slicedLabels = allMonthLabels.slice(currentDateFilter.startMonthIdx, currentDateFilter.endMonthIdx + 1);
  const slicedData = fullEv.slice(currentDateFilter.startMonthIdx, currentDateFilter.endMonthIdx + 1);

  evolutionChart.data.labels = slicedLabels;
  evolutionChart.data.datasets[0].data = slicedData;
  evolutionChart.update();
}

function initEvolutionChart() {
  const canvas = document.getElementById("evolutionChart");
  if (!canvas) return;

  if (evolutionChart) {
    evolutionChart.destroy();
    evolutionChart = null;
  }

  const ctx = canvas.getContext("2d");
  const gradient = ctx.createLinearGradient(0, 0, 0, 110);
  gradient.addColorStop(0, "rgba(59, 130, 246, 0.25)");
  gradient.addColorStop(1, "rgba(59, 130, 246, 0.01)");

  const s = database.students[selectedStudentIndex];
  const fullEv = s?.evolution || [35, 58, 60, 68, 84, 73, 91];
  const slicedLabels = allMonthLabels.slice(currentDateFilter.startMonthIdx, currentDateFilter.endMonthIdx + 1);
  const slicedData = fullEv.slice(currentDateFilter.startMonthIdx, currentDateFilter.endMonthIdx + 1);

  evolutionChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: slicedLabels,
      datasets: [{
        data: slicedData,
        borderColor: "#3b82f6",
        backgroundColor: gradient,
        fill: true,
        tension: 0.35,
        pointBackgroundColor: "#fff",
        pointBorderColor: "#3b82f6",
        pointBorderWidth: 2,
        pointRadius: 3,
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      resizeDelay: 50,
      plugins: { legend: { display: false }, tooltip: { enabled: true } },
      scales: {
        y: {
          min: 0, max: 100,
          grid: { color: "#f0f1f3", drawTicks: false },
          border: { display: false },
          ticks: { stepSize: 25, color: "#9199a6", font: { size: 9 } }
        },
        x: {
          grid: { display: false },
          border: { display: false },
          ticks: { color: "#9199a6", font: { size: 9 } }
        }
      }
    }
  });
}

function initSubjectComparisonChart() {
  const canvas = document.getElementById("subjectComparisonChart");
  if (!canvas) return;

  if (subjectChart) {
    subjectChart.destroy();
    subjectChart = null;
  }

  const ctx = canvas.getContext("2d");
  subjectChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Lenguaje", "Matemáticas", "Ciencias Naturales", "Inglés Técnico", "Historia y Sociales"],
      datasets: [
        {
          label: "Promedio 10° A",
          data: [92, 91, 84, 76, 88],
          backgroundColor: "#3b82f6",
          borderRadius: 6
        },
        {
          label: "Promedio General Institución",
          data: [86, 88, 81, 79, 84],
          backgroundColor: "#cbd5e1",
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "top", labels: { font: { size: 11, weight: "600" } } }
      },
      scales: {
        y: { min: 40, max: 100, grid: { color: "#f0f1f3" } },
        x: { grid: { display: false } }
      }
    }
  });
}

function drawGauge(canvasId, value) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const w = ctx.canvas.width;
  const h = ctx.canvas.height;
  const cx = w / 2;
  const cy = h - 10;
  const r = Math.min(w / 2, h) - 14;

  ctx.clearRect(0, 0, w, h);

  function colorForSegment(t) {
    if (t < 0.5) return "#ef4444";
    if (t < 0.75) return "#f59e0b";
    return "#22c55e";
  }

  const segments = 36;
  for (let i = 0; i < segments; i++) {
    const t0 = i / segments;
    const t1 = (i + 1) / segments;
    const a0 = Math.PI + t0 * Math.PI;
    const a1 = Math.PI + t1 * Math.PI;
    ctx.beginPath();
    ctx.arc(cx, cy, r, a0, a1);
    ctx.lineWidth = 10;
    ctx.strokeStyle = colorForSegment((t0 + t1) / 2);
    ctx.stroke();
  }

  // Aguja del medidor
  const t = Math.max(0, Math.min(1, value / 100));
  const angle = Math.PI + t * Math.PI;
  const nx = cx + Math.cos(angle) * (r - 6);
  const ny = cy + Math.sin(angle) * (r - 6);

  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(nx, ny);
  ctx.lineWidth = 2.5;
  ctx.strokeStyle = "#1f2430";
  ctx.stroke();

  ctx.beginPath();
  ctx.arc(cx, cy, 4, 0, Math.PI * 2);
  ctx.fillStyle = "#1f2430";
  ctx.fill();

  ctx.font = "700 14px Inter, sans-serif";
  ctx.fillStyle = "#1f2430";
  ctx.textAlign = "center";
  ctx.fillText(value + "%", cx, cy - r / 2);
}

// ============ SISTEMA DE ENRUTAMIENTO DE VISTAS ============
const viewTitles = {
  dashboard: "Rendimiento de Estudiantes",
  estudiantes: "Directorio y Gestión de Estudiantes",
  cursos: "Comparativa y Rendimiento por Cursos",
  rendimiento: "Análisis Detallado de Rendimiento Académico",
  actividades: "Registro de Actividades y Evaluaciones",
  reportes: "Generador de Reportes Académicos",
  configuracion: "Configuración y Parámetros del Sistema"
};

function switchView(viewName) {
  // Ocultar todas las vistas
  document.querySelectorAll(".view-section").forEach(sec => sec.classList.remove("active-view"));
  
  // Activar vista seleccionada
  const targetView = document.getElementById(`view-${viewName}`);
  if (targetView) {
    targetView.classList.add("active-view");
  }

  // Actualizar estado activo en Sidebar
  document.querySelectorAll(".nav-group .nav-item, .nav-bottom .nav-item").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.view === viewName);
  });

  // Actualizar título de la página
  const pageTitle = document.getElementById("pageMainTitle");
  if (pageTitle && viewTitles[viewName]) {
    pageTitle.textContent = viewTitles[viewName];
  }

  // Inicializar gráficos según la vista
  if (viewName === "dashboard") {
    setTimeout(() => {
      initMainChart();
      drawGauge("gauge1", 89);
      drawGauge("gauge2", 76);
    }, 50);
  } else if (viewName === "rendimiento") {
    setTimeout(() => {
      initSubjectComparisonChart();
    }, 50);
  } else if (viewName === "cursos") {
    renderCoursesView();
  } else if (viewName === "estudiantes") {
    renderFullStudentsTable(currentFilteredStudents);
  }

  // En móviles, cerrar sidebar al seleccionar vista
  if (window.innerWidth <= 1024) {
    const sidebar = document.getElementById("sidebar");
    if (sidebar) sidebar.classList.remove("open");
  }

  if (window.lucide) lucide.createIcons();
}

// ============ SEGMENTADOR DE FECHAS (DATE RANGE SLICER) ============
function setDatePreset(presetKey) {
  document.querySelectorAll(".date-preset-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.preset === presetKey);
  });

  if (presetKey === "all") {
    currentDateFilter = {
      from: "2026-01-01",
      to: "2026-07-31",
      label: "01/01/2026 - 31/07/2026",
      preset: "all",
      startMonthIdx: 0,
      endMonthIdx: 6
    };
  } else if (presetKey === "t1") {
    currentDateFilter = {
      from: "2026-01-01",
      to: "2026-03-31",
      label: "01/01/2026 - 31/03/2026",
      preset: "t1",
      startMonthIdx: 0,
      endMonthIdx: 2
    };
  } else if (presetKey === "t2") {
    currentDateFilter = {
      from: "2026-04-01",
      to: "2026-06-30",
      label: "01/04/2026 - 30/06/2026",
      preset: "t2",
      startMonthIdx: 3,
      endMonthIdx: 5
    };
  } else if (presetKey === "last30") {
    currentDateFilter = {
      from: "2026-07-01",
      to: "2026-07-31",
      label: "01/07/2026 - 31/07/2026",
      preset: "last30",
      startMonthIdx: 6,
      endMonthIdx: 6
    };
  }

  // Actualizar inputs del popover
  const fromInput = document.getElementById("dateFromInput");
  const toInput = document.getElementById("dateToInput");
  const textLabel = document.getElementById("fDatesText");

  if (fromInput) fromInput.value = currentDateFilter.from;
  if (toInput) toInput.value = currentDateFilter.to;
  if (textLabel) textLabel.textContent = currentDateFilter.label;

  // Actualizar gráfico de evolución con el nuevo rango
  updateEvolutionChartData();

  // Cerrar popover
  document.getElementById("dateRangeDropdown")?.classList.remove("show");
}

function applyCustomDateRange() {
  const fromInput = document.getElementById("dateFromInput");
  const toInput = document.getElementById("dateToInput");
  const textLabel = document.getElementById("fDatesText");

  if (!fromInput || !toInput) return;
  const fromVal = fromInput.value;
  const toVal = toInput.value;

  if (fromVal > toVal) {
    alert("La fecha inicial debe ser anterior o igual a la fecha final.");
    return;
  }

  // Formato DD/MM/YYYY
  const partsFrom = fromVal.split("-");
  const partsTo = toVal.split("-");
  const formattedLabel = `${partsFrom[2]}/${partsFrom[1]}/${partsFrom[0]} - ${partsTo[2]}/${partsTo[1]}/${partsTo[0]}`;

  // Calcular índice de meses (0 a 6 para Ene - Jul)
  const startM = Math.max(0, Math.min(6, parseInt(partsFrom[1], 10) - 1));
  const endM = Math.max(startM, Math.min(6, parseInt(partsTo[1], 10) - 1));

  currentDateFilter = {
    from: fromVal,
    to: toVal,
    label: formattedLabel,
    preset: "custom",
    startMonthIdx: startM,
    endMonthIdx: endM
  };

  // Quitar active de presets
  document.querySelectorAll(".date-preset-btn").forEach(btn => btn.classList.remove("active"));
  if (textLabel) textLabel.textContent = formattedLabel;

  // Actualizar gráfico de evolución
  updateEvolutionChartData();

  // Cerrar popover
  document.getElementById("dateRangeDropdown")?.classList.remove("show");
}

// ============ FILTRADO REACTIVO ============
function populateStudentSelect() {
  const select = document.getElementById("fStudentSelect");
  if (!select) return;
  select.innerHTML = `<option value="ALL">Todos los Estudiantes</option>`;
  database.students.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s.name;
    opt.textContent = `${s.name} (${s.course})`;
    select.appendChild(opt);
  });
}

function applyFilters() {
  const periodVal = document.getElementById("fPeriodSelect")?.value || "2026-1";
  const courseVal = document.getElementById("fCourseSelect")?.value || "ALL";
  const gradeVal = document.getElementById("fGradeSelect")?.value || "ALL";
  const studentVal = document.getElementById("fStudentSelect")?.value || "ALL";
  const searchVal = document.getElementById("searchInput")?.value.trim().toLowerCase() || "";

  database.activePeriod = periodVal;
  const headerPeriod = document.getElementById("headerPeriodLabel");
  if (headerPeriod) headerPeriod.textContent = periodVal;

  currentFilteredStudents = database.students.filter(s => {
    const matchCourse = (courseVal === "ALL" || s.course === courseVal);
    const matchGrade = (gradeVal === "ALL" || s.grade === gradeVal);
    const matchStudent = (studentVal === "ALL" || s.name === studentVal);
    const matchSearch = (!searchVal || s.name.toLowerCase().includes(searchVal) || s.course.toLowerCase().includes(searchVal));
    return matchCourse && matchGrade && matchStudent && matchSearch;
  });

  // Actualizar KPIs según los datos filtrados
  if (currentFilteredStudents.length > 0) {
    const avg = Math.round(currentFilteredStudents.reduce((acc, curr) => acc + curr.promedio, 0) / currentFilteredStudents.length);
    const kpiProm = document.getElementById("kpiPromedio");
    const kpiEst = document.getElementById("kpiEstudiantes");
    if (kpiProm) kpiProm.textContent = avg + "%";
    if (kpiEst) kpiEst.textContent = (currentFilteredStudents.length * 25).toString();
  }

  renderDashboardStudentsTable(currentFilteredStudents);
  renderFullStudentsTable(currentFilteredStudents);
}

// Reset de Filtros
function resetFilters() {
  if (document.getElementById("fPeriodSelect")) document.getElementById("fPeriodSelect").value = "2026-1";
  if (document.getElementById("fCourseSelect")) document.getElementById("fCourseSelect").value = "10° A";
  if (document.getElementById("fGradeSelect")) document.getElementById("fGradeSelect").value = "Secundaria";
  if (document.getElementById("fStudentSelect")) document.getElementById("fStudentSelect").value = "ALL";
  if (document.getElementById("searchInput")) document.getElementById("searchInput").value = "";

  // Reset del segmentador de fechas
  setDatePreset("all");

  applyFilters();
}

// ============ MODALES Y ACCIONES ============
function openAiModal() {
  const s = database.students[selectedStudentIndex];
  if (!s) return;
  const modal = document.getElementById("aiRecommendationsModal");
  const body = document.getElementById("aiModalBody");
  if (!modal || !body) return;

  body.innerHTML = `
    <div style="background:#f5f3ff;border:1px solid #ddd6fe;padding:14px;border-radius:8px;">
      <div style="font-weight:700;color:var(--purple-dark);font-size:13.5px;">Diagnóstico de ${s.name} (${s.course})</div>
      <p style="margin:6px 0 0 0;font-size:12px;color:var(--text-mid);line-height:1.45;">${s.aiSummary}</p>
    </div>

    <div>
      <h4 style="margin:0 0 6px 0;font-size:12.5px;font-weight:700;">1. Estrategia de Refuerzo Sugerida</h4>
      <ul style="margin:0;padding-left:18px;font-size:12px;color:var(--text-mid);line-height:1.6;">
        <li>Asignar módulo interactivo de vocabulario y lectura contextual en <b>${s.aiWeaknesses}</b>.</li>
        <li>Sesión de tutoría personalizada quincenal de 45 minutos.</li>
        <li>Participación en grupos de estudio guiados con alumnos destacados en la asignatura.</li>
      </ul>
    </div>

    <div>
      <h4 style="margin:0 0 6px 0;font-size:12.5px;font-weight:700;">2. Actividades Complementarias de Nivelación</h4>
      <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <span class="ai-tag" style="background:#e0e7ff;color:#3730a3;border:none;">Taller de Lectura Crítica #3</span>
        <span class="ai-tag" style="background:#e0e7ff;color:#3730a3;border:none;">Quiz de Razonamiento #2</span>
        <span class="ai-tag" style="background:#e0e7ff;color:#3730a3;border:none;">Guía Práctica de Verbos</span>
      </div>
    </div>
  `;

  modal.classList.add("show");
  if (window.lucide) lucide.createIcons();
}

function openDossierModal() {
  const s = database.students[selectedStudentIndex];
  if (!s) return;
  const modal = document.getElementById("studentDossierModal");
  const body = document.getElementById("dossierModalBody");
  if (!modal || !body) return;

  body.innerHTML = `
    <div style="display:flex;align-items:center;gap:14px;padding-bottom:12px;border-bottom:1px solid var(--border);">
      <div class="avatar-lg">${s.initials}</div>
      <div>
        <div style="font-size:16px;font-weight:700;color:var(--text-dark);">${s.name}</div>
        <div style="font-size:12px;color:var(--text-muted);">${s.course} • Grado: ${s.grade} • Matrícula Activa</div>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
      <div>
        <div class="slabel">Acudiente / Contacto</div>
        <div style="font-weight:600;font-size:12.5px;color:var(--text-dark);margin-top:2px;">${s.parent}</div>
        <div style="font-size:11.5px;color:var(--text-muted);">${s.phone}</div>
      </div>
      <div>
        <div class="slabel">Correo Institucional</div>
        <div style="font-weight:600;font-size:12.5px;color:var(--text-dark);margin-top:2px;">${s.email}</div>
      </div>
    </div>

    <div style="background:#f8f9fb;border-radius:8px;padding:12px;">
      <div style="font-weight:700;margin-bottom:6px;">Historial de Asistencia y Participación</div>
      <div style="display:flex;justify-content:space-between;font-size:12px;">
        <span>Porcentaje de Asistencia:</span>
        <b>${s.attendance}</b>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:12px;margin-top:4px;">
        <span>Actividades Entregadas:</span>
        <b>${s.actividades} (${Math.round((parseInt(s.actividades) / 48) * 100)}%)</b>
      </div>
    </div>
  `;

  modal.classList.add("show");
  if (window.lucide) lucide.createIcons();
}

// Funciones globales expuestas para eventos inline seguros
window.viewStudentDetails = function(studentId) {
  const idx = database.students.findIndex(s => s.id === studentId);
  if (idx !== -1) {
    selectStudent(idx);
    openProfilePanel();
  }
};

window.filterByCourse = function(courseName) {
  const courseSelect = document.getElementById("fCourseSelect");
  if (courseSelect) {
    courseSelect.value = courseName;
    applyFilters();
    switchView("dashboard");
  }
};

// ============ INICIALIZACIÓN COMPLETA ============
document.addEventListener("DOMContentLoaded", () => {
  // 1. Inicializar Lucide Icons
  if (window.lucide) lucide.createIcons();

  // 2. Poblar opciones de estudiantes
  populateStudentSelect();

  // 3. Renderizar tablas iniciales
  renderDashboardStudentsTable(currentFilteredStudents);
  renderCoursesView();
  selectStudent(selectedStudentIndex);

  // 4. Inicializar gráficos
  initMainChart();
  initEvolutionChart();
  drawGauge("gauge1", 89);
  drawGauge("gauge2", 76);

  // 5. Navegación del Sidebar
  document.querySelectorAll(".nav-item").forEach(btn => {
    btn.addEventListener("click", () => {
      const view = btn.dataset.view;
      if (view) switchView(view);
    });
  });

  // 6. Toggle Sidebar en móvil
  const toggleBtn = document.getElementById("toggleSidebarBtn");
  const sidebar = document.getElementById("sidebar");
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });
  }

  // 7. Dropdown de Notificaciones, Perfil y Período
  const notifBtn = document.getElementById("notifBtn");
  const mobileNotifBtn = document.getElementById("mobileNotifBtn");
  const notifDropdown = document.getElementById("notifDropdown");
  const userProfileBtn = document.getElementById("userProfileBtn");
  const userDropdown = document.getElementById("userDropdown");
  const dateBtn = document.getElementById("filterDateBtn");
  const dateDropdown = document.getElementById("dateRangeDropdown");
  const headerPeriodBtn = document.getElementById("headerPeriodBtn");
  const headerPeriodDropdown = document.getElementById("headerPeriodDropdown");

  function toggleDropdown(el) {
    if (!el) return;
    const isShowing = el.classList.contains("show");
    document.querySelectorAll(".dropdown-menu").forEach(d => d.classList.remove("show"));
    if (!isShowing) el.classList.add("show");
  }

  if (notifBtn) notifBtn.addEventListener("click", (e) => { e.stopPropagation(); toggleDropdown(notifDropdown); });
  if (mobileNotifBtn) mobileNotifBtn.addEventListener("click", (e) => { e.stopPropagation(); toggleDropdown(notifDropdown); });
  if (userProfileBtn) userProfileBtn.addEventListener("click", (e) => { e.stopPropagation(); toggleDropdown(userDropdown); });
  if (dateBtn) dateBtn.addEventListener("click", (e) => { e.stopPropagation(); toggleDropdown(dateDropdown); });
  if (headerPeriodBtn) headerPeriodBtn.addEventListener("click", (e) => { e.stopPropagation(); toggleDropdown(headerPeriodDropdown); });

  // Selección de período desde el Header Dropdown
  document.querySelectorAll(".period-opt").forEach(opt => {
    opt.addEventListener("click", (e) => {
      e.stopPropagation();
      const period = opt.dataset.period;
      if (period) {
        setAcademicPeriod(period);
        headerPeriodDropdown?.classList.remove("show");
      }
    });
  });

  function setAcademicPeriod(period) {
    database.activePeriod = period;
    const label = document.getElementById("headerPeriodLabel");
    if (label) label.textContent = period;
    const select = document.getElementById("fPeriodSelect");
    if (select) select.value = period;

    document.querySelectorAll(".period-opt").forEach(opt => {
      opt.classList.toggle("active", opt.dataset.period === period);
    });

    applyFilters();
  }

  // Eventos de Presets y Rango de Fechas
  document.querySelectorAll(".date-preset-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const preset = btn.dataset.preset;
      if (preset) setDatePreset(preset);
    });
  });

  document.getElementById("applyCustomDateBtn")?.addEventListener("click", (e) => {
    e.stopPropagation();
    applyCustomDateRange();
  });

  document.getElementById("cancelDateBtn")?.addEventListener("click", (e) => {
    e.stopPropagation();
    dateDropdown?.classList.remove("show");
  });

  document.getElementById("markAllReadBtn")?.addEventListener("click", () => {
    document.querySelectorAll(".dropdown-item.unread").forEach(item => item.classList.remove("unread"));
    const dot = document.querySelector(".bell-dot");
    if (dot) dot.style.display = "none";
  });

  // Cerrar dropdowns al hacer clic fuera
  document.addEventListener("click", () => {
    document.querySelectorAll(".dropdown-menu").forEach(d => d.classList.remove("show"));
  });

  // Evitar que clics dentro del popover de fechas lo cierren accidentalmente
  dateDropdown?.addEventListener("click", (e) => {
    e.stopPropagation();
  });
  headerPeriodDropdown?.addEventListener("click", (e) => {
    e.stopPropagation();
  });

  // 8. Eventos de Filtros
  document.getElementById("fPeriodSelect")?.addEventListener("change", (e) => {
    setAcademicPeriod(e.target.value);
  });
  document.getElementById("fCourseSelect")?.addEventListener("change", applyFilters);
  document.getElementById("fGradeSelect")?.addEventListener("change", applyFilters);
  document.getElementById("fStudentSelect")?.addEventListener("change", applyFilters);
  document.getElementById("clearFiltersBtn")?.addEventListener("click", resetFilters);
  document.getElementById("searchInput")?.addEventListener("input", applyFilters);

  // 9. Eventos de Panel Lateral y Modales
  document.getElementById("closePanelBtn")?.addEventListener("click", closeProfilePanel);
  document.getElementById("panelBackdrop")?.addEventListener("click", () => {
    closeProfilePanel();
    if (sidebar) sidebar.classList.remove("open");
  });

  document.getElementById("viewAiRecommendationsBtn")?.addEventListener("click", openAiModal);
  document.getElementById("closeAiModalBtn")?.addEventListener("click", () => document.getElementById("aiRecommendationsModal")?.classList.remove("show"));
  document.getElementById("closeAiModalFooterBtn")?.addEventListener("click", () => document.getElementById("aiRecommendationsModal")?.classList.remove("show"));
  document.getElementById("applyPedagogyPlanBtn")?.addEventListener("click", () => {
    alert("¡Plan pedagógico de refuerzo asignado exitosamente al estudiante!");
    document.getElementById("aiRecommendationsModal")?.classList.remove("show");
  });

  document.getElementById("panelInfoDossierBtn")?.addEventListener("click", openDossierModal);
  document.getElementById("closeDossierModalBtn")?.addEventListener("click", () => document.getElementById("studentDossierModal")?.classList.remove("show"));
  document.getElementById("closeDossierFooterBtn")?.addEventListener("click", () => document.getElementById("studentDossierModal")?.classList.remove("show"));

  document.getElementById("panelFilterClassmatesBtn")?.addEventListener("click", () => {
    const s = database.students[selectedStudentIndex];
    if (s && document.getElementById("fCourseSelect")) {
      document.getElementById("fCourseSelect").value = s.course;
      applyFilters();
      alert(`Mostrando todos los compañeros de ${s.name} en ${s.course}`);
    }
  });

  document.getElementById("panelPrintStudentBtn")?.addEventListener("click", () => {
    window.print();
  });

  document.getElementById("printReportBtn")?.addEventListener("click", () => {
    window.print();
  });

  document.getElementById("filterOnlyRiskBtn")?.addEventListener("click", () => {
    const riskStudents = database.students.filter(s => s.statusClass === "riesgo" || s.statusClass === "atencion");
    renderFullStudentsTable(riskStudents);
  });

  document.getElementById("exportStudentsBtn")?.addEventListener("click", () => {
    const csvContent = "data:text/csv;charset=utf-8,ID,Nombre,Curso,Promedio,Asistencia,Estado\n" +
      database.students.map(s => `${s.id},${s.name},${s.course},${s.promedio}%,${s.attendance},${s.status}`).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "reporte_estudiantes.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });

  document.getElementById("saveConfigBtn")?.addEventListener("click", () => {
    alert("Configuración académica guardada correctamente.");
  });

  document.getElementById("newActivityBtn")?.addEventListener("click", () => {
    alert("Módulo para crear nueva actividad abierto.");
  });
});
