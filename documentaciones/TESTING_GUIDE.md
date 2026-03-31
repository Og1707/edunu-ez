# 📋 Guía de Prueba - Juego de Reconocimiento de Colores

## ¿Cómo probar el juego?

### Paso 1: Asegúrate que el servidor esté corriendo
```bash
# En la carpeta del proyecto Django
python manage.py runserver
```

### Paso 2: Asegúrate que React está en ejecución
```bash
# En la carpeta visual_edu
npm start
```

### Paso 3: Crea una actividad de tipo quiz

Para que el juego se active automáticamente, necesitas crear una actividad con:
- **Tipo**: `quiz_ciencias`
- **Título**: Puede incluir "juego" (ej: "Juego de Colores")
- **Descripción**: Descripción de la actividad

#### Opción A: Via API (POSTMAN)

```bash
POST http://127.0.0.1:8000/api/actividades/

Body (JSON):
{
  "user_id": 1,                    # Tu usuario_id
  "titulo": "Juego de Reconocimiento de Colores",
  "descripcion": "Identifica correctamente los colores mostrados. Completa 10 rondas para obtener tu puntuación final.",
  "tipo": "quiz_ciencias",
  "curso": 1                       # Tu curso_id
}
```

#### Opción B: Via Admin de Django

1. Inicia sesión en http://127.0.0.1:8000/admin
2. Ve a "Actividades"
3. Crea una nueva actividad
4. Establece el tipo como "quiz_ciencias"

### Paso 4: Asigna la actividad a un curso

```bash
POST http://127.0.0.1:8000/api/asignar-actividad-curso/

Body (JSON):
{
  "user_id": 1,                    # Tu usuario_id (profesor)
  "curso_id": 1,
  "actividad_ids": [1]             # ID de la actividad creada
}
```

### Paso 5: Accede como estudiante

1. Abre la aplicación React en http://localhost:3000
2. Inicia sesión como estudiante
3. Ve a "Mis Actividades"
4. Deberías ver la actividad del juego

### Paso 6: Prueba el juego

1. Haz clic en "Iniciar Actividad"
2. Se abrirá el modal con el juego
3. Haz clic en "▶️ Jugar Reconocimiento de Colores"
4. El juego debería iniciarse

## Datos de prueba sugeridos

### Estudiante de prueba
```
Email: estudiante@test.com
Contraseña: test123456
```

### Profesor de prueba
```
Email: profesor@test.com
Contraseña: test123456
```

## Archivo de base de datos con datos de prueba

Si quieres usar datos preexistentes, busca: `user_n8n_pogres_aprendizaje.sql`

Restaura la base de datos:
```bash
mysql -u usuario -p nombre_base_datos < user_n8n_pogres_aprendizaje.sql
```

## Casos de prueba

### Caso 1: Prueba básica del juego
- [ ] Inicia el juego
- [ ] El cronómetro comienza a correr
- [ ] Se muestran 10 rondas
- [ ] Puedes seleccionar opciones de color
- [ ] Recibes retroalimentación inmediata
- [ ] Al finalizar, ves el resumen de resultados

### Caso 2: Guardar resultados
- [ ] Completa el juego
- [ ] Haz clic en "✅ Guardar Resultados"
- [ ] El modal se cierra
- [ ] Ves un mensaje de éxito
- [ ] La actividad aparece como completada

### Caso 3: Reintentar
- [ ] Completa el juego
- [ ] Haz clic en "🔄 Jugar de Nuevo"
- [ ] El juego se reinicia
- [ ] El cronómetro se resetea
- [ ] La puntuación anterior se olvida

### Caso 4: Verificar datos guardados
- [ ] Completa el juego con una puntuación específica
- [ ] Guarda los resultados
- [ ] En la API GET de actividades, verifica:
  ```bash
  GET http://127.0.0.1:8000/api/estudiante/actividades/?user_id=1
  ```
- [ ] Debes ver la puntuación guardada en `progreso.puntuacion`

### Caso 5: Cierre del juego
- [ ] Abre el juego
- [ ] Haz clic en "✕ Cerrar" 
- [ ] El juego se cierra sin guardar
- [ ] La actividad sigue pendiente

## Verificaciones de consola

Abre las herramientas de desarrollador (F12) y verifica los logs:

### Logs esperados al iniciar
```
Usuario estudiante cargado: {usuario_id: 1, ...}
Cargando datos para estudiante: 1
Datos cargados exitosamente: {...}
```

### Logs esperados al completar el juego
```
POST http://127.0.0.1:8000/api/estudiante/actividades/completar/
Request: {user_id: 1, actividad_id: 1, puntuacion: 80, tiempo_empleado: 3}
Response: {mensaje: "Actividad completada exitosamente", ...}
```

## Pruebas de rendimiento

### Tiempo de carga
- [ ] El componente ColorGame carga en < 1 segundo
- [ ] Las animaciones son suaves (60fps)

### Consumo de recursos
- [ ] El cronómetro no consume CPU excesiva
- [ ] La aplicación responde sin lag

### Compatibilidad de navegadores
- [ ] Chrome ✓
- [ ] Firefox ✓
- [ ] Safari ✓
- [ ] Edge ✓

## Resolución de problemas

### El juego no aparece
1. Verifica que `actividad.tipo === 'quiz_ciencias'`
2. Recarga la página (F5)
3. Abre la consola de desarrollador para ver errores

### El tiempo no se guarda correctamente
1. Verifica que el endpoint reciba los datos:
   - Ve a Django admin → Actividades → Busca la actividad
   - Revisa la asignación del estudiante
   - Verifica `fecha_entrega` y `calificacion`

### No puedo ver la actividad
1. Verifica que estés inscrito en el curso
2. Verifica que la actividad esté asignada a tu curso
3. Recarga la página

### El botón "Guardar Resultados" no funciona
1. Abre la consola (F12)
2. Busca errores de red
3. Verifica que el servidor Django esté corriendo
4. Verifica que la dirección sea `http://127.0.0.1:8000`

## Archivos modificados

Los siguientes archivos fueron creados/modificados:

### Archivos Nuevos
- ✅ `src/components/ColorGame.js` - Componente principal del juego
- ✅ `src/components/ColorGame.css` - Estilos del juego
- ✅ `COLOR_GAME_DOCUMENTATION.md` - Documentación del juego

### Archivos Modificados
- ✅ `src/components/StudentActivities.js` - Integración del juego
- ✅ `src/components/StudentActivities.css` - Estilos adicionales

## Próximas mejoras sugeridas

1. **Agregar niveles de dificultad**
   - Fácil: 6 colores, 5 opciones
   - Medio: 8 colores, 4 opciones
   - Difícil: 10 colores, 3 opciones

2. **Agregar más tipos de juegos**
   - Juego de formas
   - Juego de números
   - Juego de memoria

3. **Agregar tabla de puntuaciones**
   - Top 10 estudiantes por puntuación
   - Comparar tiempos

4. **Agregar sonidos**
   - Sonido al acertar
   - Sonido al fallar
   - Sonido de victoria

5. **Agregar leaderboard en tiempo real**
   - Mostrar puntuación global
   - Mostrar estadísticas personales

---

¡Listo para probar! 🎮✨
