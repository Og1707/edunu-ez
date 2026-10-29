import {
  BLUE_MATEMATICAS,
  PASTEL_PALETTE,
  assignSubjectColors,
  getSubjectColor,
  isMathematics,
} from './subjectColors';

describe('subjectColors utility', () => {
  describe('isMathematics', () => {
    it('detecta correctamente variaciones de Matemáticas con y sin tilde o mayúsculas', () => {
      expect(isMathematics('Matemáticas')).toBe(true);
      expect(isMathematics('matematica')).toBe(true);
      expect(isMathematics('MATEMÁTICAS APLICADAS')).toBe(true);
      expect(isMathematics('Lenguaje')).toBe(false);
      expect(isMathematics('Ciencias Naturales')).toBe(false);
      expect(isMathematics('')).toBe(false);
      expect(isMathematics(null)).toBe(false);
    });
  });

  describe('getSubjectColor', () => {
    it('asigna siempre azul pastel a Matemáticas independientemente del índice', () => {
      expect(getSubjectColor('Matemáticas', 0)).toBe(BLUE_MATEMATICAS);
      expect(getSubjectColor('Matemáticas', 5)).toBe(BLUE_MATEMATICAS);
      expect(getSubjectColor('matematica', 99)).toBe(BLUE_MATEMATICAS);
    });

    it('devuelve colores válidos de la paleta para otras materias', () => {
      const color = getSubjectColor('Lenguaje', 0);
      expect(PASTEL_PALETTE).toContain(color);
      expect(color).not.toBe(BLUE_MATEMATICAS);
    });

    it('es determinista y estable en llamadas repetidas', () => {
      const first = getSubjectColor('Lenguaje', 1);
      const second = getSubjectColor('Lenguaje', 1);
      expect(first).toBe(second);
    });
  });

  describe('assignSubjectColors', () => {
    it('asigna colores sin repetición a las materias visibles y respeta Matemáticas en azul', () => {
      const subjects = [
        { id: 1, nombre: 'Lenguaje' },
        { id: 2, nombre: 'Matemáticas' },
        { id: 3, nombre: 'Ciencias Naturales' },
        { id: 4, nombre: 'Inglés' },
      ];

      const colorMap = assignSubjectColors(subjects);

      expect(colorMap.get(2)).toBe(BLUE_MATEMATICAS);

      const nonMathColors = [colorMap.get(1), colorMap.get(3), colorMap.get(4)];
      // Ninguno es el azul exclusivo de Matemáticas
      nonMathColors.forEach((color) => expect(color).not.toBe(BLUE_MATEMATICAS));
      // No hay colores repetidos entre las 3 materias no matemáticas
      const uniqueColors = new Set(nonMathColors);
      expect(uniqueColors.size).toBe(3);
    });

    it('se mantiene estable durante múltiples evaluaciones simulando renders de React', () => {
      const subjects = [
        { id: 10, nombre: 'Historia' },
        { id: 20, nombre: 'Matemáticas' },
        { id: 30, nombre: 'Física' },
      ];

      const render1 = assignSubjectColors(subjects);
      const render2 = assignSubjectColors(subjects);

      expect(render1.get(10)).toBe(render2.get(10));
      expect(render1.get(20)).toBe(render2.get(20));
      expect(render1.get(30)).toBe(render2.get(30));
    });

    it('soporta lista de strings y lista vacía sin fallar', () => {
      expect(assignSubjectColors([]).size).toBe(0);

      const stringMap = assignSubjectColors(['Lenguaje', 'Matemáticas']);
      expect(stringMap.get('Matemáticas')).toBe(BLUE_MATEMATICAS);
      expect(stringMap.get('Lenguaje')).not.toBe(BLUE_MATEMATICAS);
    });
  });
});
