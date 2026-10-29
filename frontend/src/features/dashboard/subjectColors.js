/**
 * Utilidad para asignación de colores pastel de intensidad media a las asignaturas.
 *
 * Reglas de negocio visuales:
 * 1. Matemáticas siempre utiliza azul pastel de forma fija.
 * 2. Las demás asignaturas reciben un color pastel de intensidad media sin repetición
 *    dentro del conjunto de materias visibles.
 * 3. La asignación es determinista y estable: no cambia en cada renderizado de React.
 * 4. Completamente desacoplado del backend y de la base de datos.
 */

export const BLUE_MATEMATICAS = 'linear-gradient(135deg, #74a6f7, #538ee8)';

export const PASTEL_PALETTE = [
  'linear-gradient(135deg, #6bcba1, #4ea882)', // Verde salvia / Menta pastel suave
  'linear-gradient(135deg, #f5be72, #dda34e)', // Ámbar / Miel pastel suave
  'linear-gradient(135deg, #f2968e, #db786f)', // Coral / Melocotón pastel suave
  'linear-gradient(135deg, #b09cf5, #937ce8)', // Lavanda / Violeta pastel suave
  'linear-gradient(135deg, #64c8ce, #46a9af)', // Turquesa / Aguamarina pastel suave
  'linear-gradient(135deg, #ee98be, #d476a0)', // Rosa empolvado pastel suave
  'linear-gradient(135deg, #6dc2eb, #50a6d4)', // Celeste pastel suave
  'linear-gradient(135deg, #9ca9f0, #7c8be0)', // Índigo / Pervinca pastel suave
];

/**
 * Normaliza el nombre de la materia eliminando tildes y pasando a minúsculas.
 */
export function normalizeSubjectName(name = '') {
  return String(name)
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim();
}

/**
 * Determina si una materia corresponde a Matemáticas.
 */
export function isMathematics(name = '') {
  return normalizeSubjectName(name).includes('matematica');
}

/**
 * Genera un hash numérico entero y estable a partir de una cadena.
 */
function hashString(str = '') {
  let hash = 0;
  for (let i = 0; i < str.length; i += 1) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

/**
 * Obtiene el color para una materia individual dada su posición opcional.
 * Matemáticas siempre retorna BLUE_MATEMATICAS.
 */
export function getSubjectColor(subjectName = '', index = 0) {
  if (isMathematics(subjectName)) {
    return BLUE_MATEMATICAS;
  }
  const clean = normalizeSubjectName(subjectName);
  const paletteIndex = (index + hashString(clean)) % PASTEL_PALETTE.length;
  return PASTEL_PALETTE[paletteIndex];
}

/**
 * Asigna colores únicos y sin repetición al conjunto de materias visibles de un estudiante.
 *
 * @param {Array<{ id: number, nombre: string } | string>} subjects
 * @returns {Map<string|number, string>} Mapa de ID o nombre a color de gradiente.
 */
export function assignSubjectColors(subjects = []) {
  const colorMap = new Map();
  const nonMathSubjects = [];

  subjects.forEach((subj) => {
    const name = typeof subj === 'string' ? subj : subj?.nombre || '';
    const key = typeof subj === 'object' && subj?.id !== undefined ? subj.id : name;

    if (isMathematics(name)) {
      colorMap.set(key, BLUE_MATEMATICAS);
    } else {
      nonMathSubjects.push({ key, name });
    }
  });

  // Repartir la paleta sin repetir colores para las materias no matemáticas
  nonMathSubjects.forEach(({ key }, index) => {
    const color = PASTEL_PALETTE[index % PASTEL_PALETTE.length];
    colorMap.set(key, color);
  });

  return colorMap;
}
