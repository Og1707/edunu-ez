import React from 'react';

/**
 * HeroIllustration
 * Ilustración SVG responsiva para la página de Login.
 * viewBox="0 0 700 600" — 5 capas organizadas jerárquicamente:
 *   1. Fondo y elementos ambientales (arcos + nubes 3D)
 *   2. Flora / árboles laterales
 *   3. Monitor central con pantalla dividida
 *   4. Personaje sentado sobre el monitor
 *   5. Tarjetas flotantes en primer plano
 *
 * Paleta de colores: paleta oficial EduNúñez (Home.css)
 *   Principal:  #4f46e5 (indigo), #6366f1 (indigo medio), #3730a3 (indigo oscuro)
 *   Pálido:     #eef2ff, #c7d2fe, #818cf8
 *   Fondo:      #f4f5ff (gris-azulado muy claro)
 *   Accents:    #f59e0b (ámbar), #f87171 (rojo), #10b981 (verde)
 *   Texto:      #172554, #0f172a
 */
const HeroIllustration = () => (
  <svg
    xmlns="https://www.w3.org/TR/SVG/"
    viewBox="0 0 700 600"
    aria-label="Ilustración educativa: persona trabajando frente a un monitor"
    role="img"
    style={{ width: '100%', height: '100%', display: 'block' }}
  >
    <defs>
      {/* Degradados radiales para nubes 3D */}
      <radialGradient id="cloudGrad1" cx="50%" cy="40%" r="55%">
        <stop offset="0%" stopColor="#FFFFFF" />
        <stop offset="100%" stopColor="#CBD5E1" />
      </radialGradient>
      <radialGradient id="cloudGrad2" cx="50%" cy="40%" r="55%">
        <stop offset="0%" stopColor="#FFFFFF" />
        <stop offset="100%" stopColor="#B8C9D9" />
      </radialGradient>

      {/* Degradado indigo para árboles */}
      <radialGradient id="treeGrad" cx="40%" cy="35%" r="60%">
        <stop offset="0%" stopColor="#818cf8" />
        <stop offset="100%" stopColor="#4f46e5" />
      </radialGradient>

      {/* Sombra suave para tarjetas flotantes */}
      <filter id="cardShadow" x="-10%" y="-10%" width="120%" height="130%">
        <feDropShadow dx="0" dy="4" stdDeviation="6" floodColor="rgba(0,0,0,0.12)" />
      </filter>

      {/* Sombra para el monitor */}
      <filter id="monitorShadow" x="-8%" y="-8%" width="116%" height="120%">
        <feDropShadow dx="0" dy="8" stdDeviation="10" floodColor="rgba(79,70,229,0.18)" />
      </filter>

      {/* Clip del monitor — pantalla interior */}
      <clipPath id="screenClip">
        <rect x="200" y="170" width="300" height="200" rx="6" />
      </clipPath>
    </defs>

    {/* ═══════════════════════════════════════════════
        CAPA 1 — Fondo y elementos ambientales
    ═══════════════════════════════════════════════ */}
    <g id="layer-background">
      {/* Fondo: gris-azulado muy claro — igual al hero del Home */}
      <rect width="700" height="600" fill="#f4f5ff" />

      {/* Radial indigo sutil — esquina superior derecha (igual que el Home) */}
      <circle cx="595" cy="270" r="200" fill="rgba(99,102,241,0.08)" />

      {/* Arcos geométricos concéntricos — esquina superior izquierda */}
      {[60, 110, 160, 210, 260, 310].map((r, i) => (
        <circle
          key={`arc-${i}`}
          cx="0"
          cy="0"
          r={r}
          fill="none"
          stroke="rgba(79,70,229,0.07)"
          strokeWidth="1"
        />
      ))}

      {/* Arcos — esquina inferior derecha (decoración sutil) */}
      {[50, 100, 150, 200].map((r, i) => (
        <circle
          key={`arc-br-${i}`}
          cx="700"
          cy="600"
          r={r}
          fill="none"
          stroke="rgba(79,70,229,0.05)"
          strokeWidth="1"
        />
      ))}

      {/* Nube 3D — Izquierda */}
      <g id="cloud-left" transform="translate(42, 80)">
        <ellipse cx="38" cy="28" rx="22" ry="16" fill="url(#cloudGrad2)" opacity="0.82" />
        <ellipse cx="58" cy="22" rx="26" ry="18" fill="url(#cloudGrad1)" opacity="0.9" />
        <ellipse cx="80" cy="26" rx="22" ry="15" fill="url(#cloudGrad2)" opacity="0.82" />
        <ellipse cx="96" cy="32" rx="16" ry="12" fill="url(#cloudGrad1)" opacity="0.75" />
        {/* Base plana de la nube */}
        <rect x="28" y="32" width="84" height="10" rx="5" fill="url(#cloudGrad2)" opacity="0.7" />
      </g>

      {/* Nube 3D — Derecha */}
      <g id="cloud-right" transform="translate(530, 55)">
        <ellipse cx="30" cy="24" rx="18" ry="13" fill="url(#cloudGrad2)" opacity="0.78" />
        <ellipse cx="52" cy="18" rx="24" ry="17" fill="url(#cloudGrad1)" opacity="0.88" />
        <ellipse cx="76" cy="22" rx="20" ry="14" fill="url(#cloudGrad2)" opacity="0.78" />
        <ellipse cx="90" cy="28" rx="14" ry="11" fill="url(#cloudGrad1)" opacity="0.72" />
        <rect x="22" y="28" width="78" height="9" rx="4.5" fill="url(#cloudGrad2)" opacity="0.65" />
      </g>
    </g>

    {/* ═══════════════════════════════════════════════
        CAPA 2 — Flora / Árboles laterales
    ═══════════════════════════════════════════════ */}
    <g id="layer-flora">

      {/* ── Árboles izquierda ── */}
      {/* Árbol pequeño/oscuro detrás */}
      <g id="tree-left-back" transform="translate(52, 200)">
        {/* Tronco */}
        <rect x="18" y="62" width="8" height="30" rx="4" fill="#1e1b4b" />
        {/* Copa */}
        <circle cx="22" cy="52" r="32" fill="#312e81" />
        {/* Ramas internas sutiles */}
        <line x1="22" y1="30" x2="22" y2="60" stroke="rgba(255,255,255,0.10)" strokeWidth="1.5" />
        <line x1="6"  y1="50" x2="38" y2="50" stroke="rgba(255,255,255,0.10)" strokeWidth="1.5" />
        <line x1="10" y1="38" x2="34" y2="62" stroke="rgba(255,255,255,0.07)" strokeWidth="1" />
        <line x1="34" y1="38" x2="10" y2="62" stroke="rgba(255,255,255,0.07)" strokeWidth="1" />
      </g>

      {/* Árbol grande/indigo delante */}
      <g id="tree-left-front" transform="translate(20, 155)">
        {/* Tronco */}
        <rect x="26" y="82" width="10" height="40" rx="5" fill="#4f46e5" />
        {/* Copa principal */}
        <circle cx="31" cy="68" r="44" fill="url(#treeGrad)" />
        {/* Iluminación interna */}
        <circle cx="22" cy="55" r="14" fill="rgba(255,255,255,0.14)" />
        {/* Ramas internas */}
        <line x1="31" y1="38" x2="31" y2="78" stroke="rgba(49,46,129,0.35)" strokeWidth="2" />
        <line x1="8"  y1="65" x2="54" y2="65" stroke="rgba(49,46,129,0.35)" strokeWidth="2" />
        <line x1="14" y1="48" x2="48" y2="80" stroke="rgba(49,46,129,0.22)" strokeWidth="1.5" />
        <line x1="48" y1="48" x2="14" y2="80" stroke="rgba(49,46,129,0.22)" strokeWidth="1.5" />
        {/* Pequeños círculos decorativos */}
        <circle cx="18" cy="60" r="5" fill="rgba(49,46,129,0.28)" />
        <circle cx="44" cy="72" r="4" fill="rgba(49,46,129,0.22)" />
      </g>

      {/* ── Árbol derecha ── */}
      <g id="tree-right" transform="translate(578, 165)">
        {/* Copa */}
        <circle cx="42" cy="56" r="40" fill="url(#treeGrad)" />
        <circle cx="30" cy="44" r="12" fill="rgba(255,255,255,0.14)" />
        {/* Tronco */}
        <rect x="34" y="94" width="10" height="36" rx="5" fill="#4f46e5" />
        {/* Ramas */}
        <line x1="42" y1="28" x2="42" y2="72" stroke="rgba(49,46,129,0.30)" strokeWidth="2" />
        <line x1="18" y1="54" x2="66" y2="54" stroke="rgba(49,46,129,0.30)" strokeWidth="2" />
        <line x1="22" y1="36" x2="60" y2="74" stroke="rgba(49,46,129,0.18)" strokeWidth="1.5" />
        <line x1="60" y1="36" x2="22" y2="74" stroke="rgba(49,46,129,0.18)" strokeWidth="1.5" />
      </g>

      {/* Maceta trapezoidal — esquina inferior derecha */}
      <g id="pot-right" transform="translate(600, 430)">
        {/* Maceta */}
        <polygon points="10,50 0,80 64,80 54,50" fill="#6366f1" />
        {/* Borde superior de la maceta */}
        <rect x="4" y="44" width="56" height="10" rx="5" fill="#4f46e5" />
        {/* Tierra */}
        <ellipse cx="32" cy="54" rx="24" ry="5" fill="#312e81" />
        {/* Tallo central */}
        <line x1="32" y1="54" x2="32" y2="14" stroke="#4f46e5" strokeWidth="3" strokeLinecap="round" />
        {/* Hojas alargadas */}
        <ellipse cx="32" cy="22" rx="6" ry="18" fill="#818cf8" transform="rotate(-25, 32, 22)" />
        <ellipse cx="32" cy="22" rx="6" ry="18" fill="#6366f1" transform="rotate(25, 32, 22)" />
        <ellipse cx="32" cy="18" rx="5" ry="14" fill="#818cf8" transform="rotate(0, 32, 18)" />
        {/* Brillo hoja */}
        <ellipse cx="34" cy="16" rx="2" ry="8" fill="rgba(255,255,255,0.22)" transform="rotate(-5, 34, 16)" />
      </g>
    </g>

    {/* ═══════════════════════════════════════════════
        CAPA 3 — Monitor central
    ═══════════════════════════════════════════════ */}
    <g id="layer-monitor" filter="url(#monitorShadow)">

      {/* Marco del monitor — indigo pálido con borde indigo */}
      <rect
        x="172" y="155"
        width="356" height="260"
        rx="16" ry="16"
        fill="#eef2ff"
        stroke="#6366f1"
        strokeWidth="3"
      />

      {/* Pantalla interior (fondo blanco) */}
      <rect x="200" y="170" width="300" height="200" rx="6" fill="#FFFFFF" />

      {/* ── Panel izquierdo de la pantalla ── */}
      <g clipPath="url(#screenClip)">
        {/* Divisor central */}
        <line x1="350" y1="170" x2="350" y2="370" stroke="#E2E8F0" strokeWidth="1.5" />

        {/* Flowchart — bloque superior */}
        <rect x="212" y="182" width="58" height="22" rx="6" fill="#6366f1" opacity="0.85" />
        <rect x="278" y="182" width="42" height="22" rx="6" fill="#818cf8" opacity="0.65" />
        {/* Conector */}
        <line x1="270" y1="193" x2="278" y2="193" stroke="#6366f1" strokeWidth="1.5" />

        {/* Flowchart — bloque medio */}
        <rect x="224" y="214" width="80" height="18" rx="5" fill="#818cf8" opacity="0.70" />
        <line x1="241" y1="204" x2="241" y2="214" stroke="#6366f1" strokeWidth="1.5" />

        {/* Líneas de texto simulado */}
        <rect x="212" y="242" width="110" height="5" rx="2.5" fill="#c7d2fe" opacity="0.85" />
        <rect x="212" y="254" width="90"  height="5" rx="2.5" fill="#c7d2fe" opacity="0.65" />
        <rect x="212" y="266" width="100" height="5" rx="2.5" fill="#c7d2fe" opacity="0.75" />
        <rect x="212" y="278" width="75"  height="5" rx="2.5" fill="#c7d2fe" opacity="0.55" />

        {/* Onda ámbar en la base del panel izquierdo */}
        <path
          d="M208,340 Q222,320 236,340 Q250,360 264,340 Q278,320 292,340 Q306,360 320,340 Q334,320 348,340"
          fill="none"
          stroke="#f59e0b"
          strokeWidth="2.5"
          strokeLinecap="round"
        />

        {/* ── Panel derecho de la pantalla ── */}
        {/* Barras del gráfico — indigo decorativo */}
        {[
          { x: 362, h: 40, y: 310 },
          { x: 384, h: 60, y: 290 },
          { x: 406, h: 85, y: 265 },
          { x: 428, h: 55, y: 295 },
          { x: 450, h: 100, y: 250 },
        ].map((bar, i) => (
          <rect
            key={`bar-${i}`}
            x={bar.x}
            y={bar.y}
            width="18"
            height={bar.h}
            rx="4"
            fill="#818cf8"
            opacity="0.88"
          />
        ))}

        {/* Línea base del gráfico de barras */}
        <line x1="358" y1="350" x2="478" y2="350" stroke="#CBD5E1" strokeWidth="1.5" />

        {/* Líneas de datos indigo — panel derecho */}
        <rect x="362" y="180" width="108" height="4" rx="2" fill="#6366f1" opacity="0.65" />
        <rect x="362" y="192" width="88"  height="4" rx="2" fill="#6366f1" opacity="0.50" />
        <rect x="362" y="204" width="98"  height="4" rx="2" fill="#6366f1" opacity="0.60" />
        <rect x="362" y="216" width="70"  height="4" rx="2" fill="#6366f1" opacity="0.45" />
        <rect x="362" y="228" width="94"  height="4" rx="2" fill="#6366f1" opacity="0.55" />
      </g>

      {/* Base del monitor — cuello y pie, indigo */}
      <rect x="324" y="415" width="52" height="16" rx="6" fill="#6366f1" />
      <rect x="290" y="428" width="120" height="14" rx="7" fill="#eef2ff" stroke="#c7d2fe" strokeWidth="1.5" />
    </g>

    {/* ═══════════════════════════════════════════════
        CAPA 4 — Personaje
    ═══════════════════════════════════════════════ */}
    <g id="layer-character">

      {/* Piernas / Pantalones ámbar — paleta oficial */}
      {/* Pierna izquierda */}
      <rect x="298" y="155" width="28" height="75" rx="10" fill="#f59e0b" />
      {/* Pierna derecha */}
      <rect x="378" y="155" width="28" height="75" rx="10" fill="#f59e0b" />

      {/* Zapatos indigo */}
      <ellipse cx="312" cy="232" rx="18" ry="10" fill="#4f46e5" />
      <ellipse cx="392" cy="232" rx="18" ry="10" fill="#4f46e5" />

      {/* Torso — suéter indigo */}
      <rect x="305" y="85" width="90" height="78" rx="18" fill="#6366f1" />

      {/* Portátil blanco sobre las piernas */}
      <rect x="292" y="130" width="116" height="70" rx="8" fill="#F0F4F8" stroke="#CBD5E1" strokeWidth="2" />
      {/* Tapa del portátil (ligeramente abierta) */}
      <rect x="296" y="82" width="108" height="55" rx="6" fill="#FFFFFF" stroke="#CBD5E1" strokeWidth="1.5" />
      {/* Pantalla del portátil */}
      <rect x="302" y="87" width="96" height="44" rx="4" fill="#eef2ff" />
      {/* Líneas en pantalla del portátil */}
      <rect x="308" y="97"  width="60" height="4" rx="2" fill="#6366f1" opacity="0.7" />
      <rect x="308" y="107" width="46" height="4" rx="2" fill="#818cf8" opacity="0.5" />
      <rect x="308" y="117" width="54" height="4" rx="2" fill="#6366f1" opacity="0.6" />
      {/* Cursor parpadeante en portátil — ámbar */}
      <rect x="308" y="127" width="8" height="4" rx="1" fill="#f59e0b" opacity="0.9" />

      {/* Brazos — indigo */}
      {/* Brazo izquierdo */}
      <path d="M306,100 Q282,115 288,135" stroke="#6366f1" strokeWidth="22" strokeLinecap="round" fill="none" />
      {/* Mano izquierda */}
      <circle cx="290" cy="137" r="10" fill="#FFD5C2" />
      {/* Brazo derecho */}
      <path d="M394,100 Q418,115 412,135" stroke="#6366f1" strokeWidth="22" strokeLinecap="round" fill="none" />
      {/* Mano derecha */}
      <circle cx="410" cy="137" r="10" fill="#FFD5C2" />

      {/* Cabeza — tono de piel (sin cambios) */}
      <ellipse cx="350" cy="55" rx="38" ry="38" fill="#FFD5C2" />

      {/* Cabello — moño alto (sin cambios, es neutro) */}
      <ellipse cx="350" cy="38" rx="36" ry="28" fill="#5A3825" />
      <ellipse cx="350" cy="14" rx="16" ry="12" fill="#5A3825" />
      <ellipse cx="350" cy="12" rx="10" ry="8"  fill="#7A4F35" />
      {/* Flequillo lateral */}
      <path d="M316,42 Q318,28 330,32" fill="#5A3825" />
      <path d="M384,42 Q382,28 370,32" fill="#5A3825" />

      {/* Ojos */}
      <ellipse cx="337" cy="55" rx="5" ry="5.5" fill="#2D1B0E" />
      <ellipse cx="363" cy="55" rx="5" ry="5.5" fill="#2D1B0E" />
      {/* Brillo en ojos */}
      <circle cx="339" cy="52" r="1.8" fill="white" />
      <circle cx="365" cy="52" r="1.8" fill="white" />

      {/* Sonrisa */}
      <path
        d="M338,67 Q350,78 362,67"
        fill="none"
        stroke="#C07060"
        strokeWidth="2.5"
        strokeLinecap="round"
      />

      {/* Mejillas ruborizadas */}
      <ellipse cx="326" cy="65" rx="8" ry="5" fill="#FFAAA0" opacity="0.40" />
      <ellipse cx="374" cy="65" rx="8" ry="5" fill="#FFAAA0" opacity="0.40" />
    </g>

    {/* ═══════════════════════════════════════════════
        CAPA 5 — Tarjetas flotantes en primer plano
    ═══════════════════════════════════════════════ */}
    <g id="layer-cards">

      {/* ── Widget inferior izquierdo — Gráfico de Dona ── */}
      <g id="card-donut" transform="translate(48, 385)" filter="url(#cardShadow)">
        {/* Tarjeta */}
        <rect width="162" height="130" rx="14" fill="white" stroke="#c7d2fe" strokeWidth="1.8" />

        {/* Título */}
        <text x="12" y="22" fontSize="10" fontWeight="700" fill="#172554" fontFamily="sans-serif">
          Progress
        </text>

        {/* ── Gráfico de dona ── */}
        {/* Sector 1 — indigo (40%) */}
        <path
          d="M74,75 L74,48 A27,27 0 0,1 98,89 Z"
          fill="#6366f1"
        />
        {/* Sector 2 — ámbar (25%) */}
        <path
          d="M74,75 L98,89 A27,27 0 0,1 60,100 Z"
          fill="#f59e0b"
        />
        {/* Sector 3 — rojo coral (20%) */}
        <path
          d="M74,75 L60,100 A27,27 0 0,1 47,58 Z"
          fill="#f87171"
        />
        {/* Sector 4 — indigo pálido (15%) */}
        <path
          d="M74,75 L47,58 A27,27 0 0,1 74,48 Z"
          fill="#c7d2fe"
        />
        {/* Hueco central de la dona */}
        <circle cx="74" cy="75" r="14" fill="white" />
        {/* Texto central */}
        <text x="74" y="79" fontSize="9" fontWeight="700" fill="#172554"
          textAnchor="middle" fontFamily="sans-serif">75%</text>

        {/* Leyenda */}
        <circle cx="110" cy="55" r="4" fill="#6366f1" />
        <text x="118" y="59" fontSize="8" fill="#64748B" fontFamily="sans-serif">Math</text>
        <circle cx="110" cy="70" r="4" fill="#f59e0b" />
        <text x="118" y="74" fontSize="8" fill="#64748B" fontFamily="sans-serif">Science</text>
        <circle cx="110" cy="85" r="4" fill="#f87171" />
        <text x="118" y="89" fontSize="8" fill="#64748B" fontFamily="sans-serif">Arts</text>
        <circle cx="110" cy="100" r="4" fill="#c7d2fe" />
        <text x="118" y="104" fontSize="8" fill="#64748B" fontFamily="sans-serif">Lang</text>

        {/* Líneas de estado indigo */}
        <rect x="12" y="112" width="72" height="5" rx="2.5" fill="#6366f1" opacity="0.70" />
        <rect x="90" y="112" width="40" height="5" rx="2.5" fill="#eef2ff" stroke="#c7d2fe" strokeWidth="1" />
        <rect x="12" y="121" width="52" height="4" rx="2" fill="#c7d2fe" opacity="0.75" />
      </g>

      {/* ── Widget inferior derecho — Panel Móvil/Tablet ── */}
      <g id="card-mobile" transform="translate(496, 370)" filter="url(#cardShadow)">
        {/* Tarjeta vertical */}
        <rect width="110" height="155" rx="14" fill="white" stroke="#E2E8F0" strokeWidth="1.5" />

        {/* Pantalla interna indigo pálido */}
        <rect x="12" y="24" width="86" height="88" rx="8" fill="#eef2ff" stroke="#c7d2fe" strokeWidth="1.2" />

        {/* Gráfico de línea ascendente — ámbar */}
        <polyline
          points="18,102  34,88  50,78  66,62  82,50  94,38"
          fill="none"
          stroke="#f59e0b"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Nodos del gráfico */}
        {[
          [18, 102], [34, 88], [50, 78], [66, 62], [82, 50], [94, 38]
        ].map(([cx, cy], i) => (
          <circle key={`node-${i}`} cx={cx} cy={cy} r="4" fill="#f59e0b" stroke="white" strokeWidth="1.5" />
        ))}

        {/* Etiquetas eje X simplificadas */}
        <text x="14"  y="118" fontSize="7" fill="#94A3B8" fontFamily="sans-serif">Jan</text>
        <text x="46"  y="118" fontSize="7" fill="#94A3B8" fontFamily="sans-serif">Mar</text>
        <text x="78"  y="118" fontSize="7" fill="#94A3B8" fontFamily="sans-serif">Jun</text>

        {/* Título */}
        <text x="12" y="18" fontSize="9" fontWeight="700" fill="#172554" fontFamily="sans-serif">
          Scores
        </text>

        {/* Líneas de metadatos debajo de la pantalla */}
        <rect x="12" y="120" width="86" height="5"  rx="2.5" fill="#E2E8F0" />
        <rect x="12" y="130" width="60" height="4"  rx="2"   fill="#F1F5F9" />

        {/* Barra inferior — botón home del dispositivo */}
        <circle cx="55" cy="148" r="5" fill="#E2E8F0" />
      </g>
    </g>
  </svg>
);

export default HeroIllustration;
