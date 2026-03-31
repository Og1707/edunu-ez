import React, { useState, useEffect, useRef } from 'react';
import axios from '../utils/axiosConfig';
import './ColorGame.css';

const ColorGame = ({ user, actividad, onComplete, onClose }) => {
  // Estados del juego
  const [gameStarted, setGameStarted] = useState(false);
  const [gameOver, setGameOver] = useState(false);
  const [score, setScore] = useState(0);
  const [round, setRound] = useState(0);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [respuestas, setRespuestas] = useState([]); // Guardar detalle de cada respuesta
  
  // Color actual y opciones
  const [currentColor, setCurrentColor] = useState(null);
  const [colorOptions, setColorOptions] = useState([]);
  const [selectedColor, setSelectedColor] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const [feedbackType, setFeedbackType] = useState(''); // 'correct' o 'incorrect'
  
  // Configuración del juego
  const MAX_ROUNDS = 10;
  const COLORS = [
    { name: 'Rojo', hex: '#FF6B6B', rgb: 'rgb(255, 107, 107)' },
    { name: 'Azul', hex: '#4ECDC4', rgb: 'rgb(78, 205, 196)' },
    { name: 'Verde', hex: '#95E1D3', rgb: 'rgb(149, 225, 211)' },
    { name: 'Amarillo', hex: '#FFE66D', rgb: 'rgb(255, 230, 109)' },
    { name: 'Morado', hex: '#A29BFE', rgb: 'rgb(162, 155, 254)' },
    { name: 'Rosa', hex: '#FD79A8', rgb: 'rgb(253, 121, 168)' },
    { name: 'Naranja', hex: '#FDCB6E', rgb: 'rgb(253, 203, 110)' },
    { name: 'Cian', hex: '#74B9FF', rgb: 'rgb(116, 185, 255)' },
  ];
  
  const gameTimer = useRef(null);
  const startTime = useRef(null);
  const respuestasRef = useRef([]); // Usar ref para guardar respuestas inmediatamente

  // Iniciar el temporizador
  useEffect(() => {
    if (gameStarted && !gameOver) {
      if (!startTime.current) {
        startTime.current = Date.now() - (timeElapsed * 1000);
      }

      gameTimer.current = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime.current) / 1000);
        setTimeElapsed(elapsed);
      }, 100);

      return () => {
        if (gameTimer.current) clearInterval(gameTimer.current);
      };
    }
  }, [gameStarted, gameOver]);

  // Generar un nuevo round
  const generateRound = () => {
    if (round >= MAX_ROUNDS) {
      finishGame();
      return;
    }

    const randomColor = COLORS[Math.floor(Math.random() * COLORS.length)];
    setCurrentColor(randomColor);

    // Generar opciones (3 colores diferentes incluyendo el correcto)
    const shuffledColors = COLORS.sort(() => Math.random() - 0.5).slice(0, 4);
    if (!shuffledColors.find(c => c.name === randomColor.name)) {
      shuffledColors[Math.floor(Math.random() * 4)] = randomColor;
    }
    setColorOptions(shuffledColors.sort(() => Math.random() - 0.5));

    setSelectedColor(null);
    setShowFeedback(false);
    setRound(round + 1);
  };

  // Iniciar el juego
  const startGame = () => {
    setGameStarted(true);
    setGameOver(false);
    setScore(0);
    setRound(0);
    setTimeElapsed(0);
    respuestasRef.current = []; // Limpiar respuestas anteriores
    setRespuestas([]); // Limpiar estado también
    setSelectedColor(null);
    startTime.current = Date.now();
    generateRound();
  };

  // Manejar selección de color
  const handleColorSelect = (selectedOption) => {
    if (gameOver || showFeedback || selectedColor) return;

    setSelectedColor(selectedOption);

    const isCorrect = selectedOption.name === currentColor.name;
    setFeedbackType(isCorrect ? 'correct' : 'incorrect');
    setFeedbackMessage(
      isCorrect
        ? `¡Correcto! ${selectedOption.name} es la respuesta correcta.`
        : `Incorrecto. El color correcto era ${currentColor.name}.`
    );
    setShowFeedback(true);

    // Guardar detalle de la respuesta inmediatamente en el ref
    const respuestaActual = {
      numero_pregunta: round,
      color_mostrado: currentColor.name,
      hex_color: currentColor.hex,
      respuesta_estudiante: selectedOption.name,
      respuesta_correcta: currentColor.name,
      es_correcta: isCorrect,
      tiempo_respuesta: timeElapsed
    };
    respuestasRef.current.push(respuestaActual);
    setRespuestas([...respuestasRef.current]); // También actualizar state para UI si lo necesitas

    if (isCorrect) {
      setScore(score + 1);
    }

    // Pasar al siguiente round después de 2 segundos
    setTimeout(() => {
      if (round < MAX_ROUNDS) {
        generateRound();
      } else {
        finishGame();
      }
    }, 2000);
  };

  // Finalizar el juego
  const finishGame = () => {
    setGameOver(true);
    setGameStarted(false);
    if (gameTimer.current) {
      clearInterval(gameTimer.current);
    }
  };

  // Guardar resultados
  const saveResults = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/estudiante/actividades/completar/', {
        user_id: user.usuario_id,
        actividad_id: actividad.id,
        puntuacion: Math.round((score / MAX_ROUNDS) * 100),
        tiempo_empleado: Math.round(timeElapsed / 60), // en minutos
        respuestas_detalle: respuestasRef.current, // Usar ref en lugar de state
      });

      // Llamar callback para notificar que se completó
      if (onComplete) {
        onComplete({
          puntuacion: Math.round((score / MAX_ROUNDS) * 100),
          tiempoEmpleado: timeElapsed,
          aciertos: score,
        });
      }
    } catch (error) {
      console.error('Error al guardar resultados:', error);
    }
  };

  // Reintentar el juego
  const retryGame = () => {
    setGameStarted(false);
    setGameOver(false);
    setScore(0);
    setRound(0);
    setTimeElapsed(0);
    setCurrentColor(null);
    setColorOptions([]);
    setSelectedColor(null);
    setShowFeedback(false);
    setRespuestas([]); // Limpiar respuestas anteriores
    respuestasRef.current = []; // Limpiar ref
    startTime.current = null;
  };

  // Formatear tiempo
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (!gameStarted && !gameOver) {
    return (
      <div className="color-game">
        <div className="game-container">
          <div className="game-intro">
            <h2>🎨 Juego de Reconocimiento de Colores</h2>
            <p>Selecciona el nombre correcto del color que se muestra en la pantalla.</p>
            
            <div className="game-instructions">
              <h3>Instrucciones:</h3>
              <ul>
                <li>Se mostrarán 10 colores en secuencia</li>
                <li>Debes seleccionar el nombre correcto del color</li>
                <li>Tienes tiempo ilimitado pero el cronómetro registrará tu velocidad</li>
                <li>La puntuación se basa en el número de aciertos</li>
              </ul>
            </div>

            <div className="game-difficulty">
              <h3>Dificultad: Media</h3>
              <p>4 opciones de colores para elegir</p>
            </div>

            <button className="btn-start-game" onClick={startGame}>
              🚀 Comenzar Juego
            </button>

            {onClose && (
              <button className="btn-close-game" onClick={onClose}>
                ✕ Cerrar
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (gameOver) {
    const accuracy = Math.round((score / MAX_ROUNDS) * 100);
    const timeFormatted = formatTime(timeElapsed);

    return (
      <div className="color-game">
        <div className="game-container">
          <div className="game-results">
            <h2>🎉 ¡Juego Terminado!</h2>

            <div className="results-grid">
              <div className="result-card">
                <div className="result-icon">🎯</div>
                <div className="result-value">{score}/{MAX_ROUNDS}</div>
                <div className="result-label">Aciertos</div>
              </div>

              <div className="result-card">
                <div className="result-icon">📊</div>
                <div className="result-value">{accuracy}%</div>
                <div className="result-label">Precisión</div>
              </div>

              <div className="result-card">
                <div className="result-icon">⏱️</div>
                <div className="result-value">{timeFormatted}</div>
                <div className="result-label">Tiempo Total</div>
              </div>

              <div className="result-card">
                <div className="result-icon">⚡</div>
                <div className="result-value">
                  {score > 0 ? (timeElapsed / score).toFixed(1) : '0'}s
                </div>
                <div className="result-label">Tiempo/Acierto</div>
              </div>
            </div>

            <div className="results-message">
              {accuracy === 100 && (
                <div className="message success">
                  ¡Excelente! ¡Identificaste todos los colores correctamente! 🌟
                </div>
              )}
              {accuracy >= 80 && accuracy < 100 && (
                <div className="message good">
                  ¡Muy bien! Tienes una excelente precisión. 👍
                </div>
              )}
              {accuracy >= 60 && accuracy < 80 && (
                <div className="message okay">
                  Buen trabajo. Puedes mejorar practicando más. 📚
                </div>
              )}
              {accuracy < 60 && (
                <div className="message poor">
                  Necesitas practicar más. ¡Inténtalo de nuevo! 💪
                </div>
              )}
            </div>

            <div className="results-actions">
              <button className="btn-save-results" onClick={saveResults}>
                ✅ Guardar Resultados
              </button>

              <button className="btn-retry-game" onClick={retryGame}>
                🔄 Jugar de Nuevo
              </button>

              {onClose && (
                <button className="btn-close-game" onClick={onClose}>
                  ✕ Cerrar
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Juego en progreso
  return (
    <div className="color-game">
      <div className="game-container">
        <div className="game-header">
          <div className="game-stats">
            <div className="stat">
              <span className="stat-label">Ronda:</span>
              <span className="stat-value">{round}/{MAX_ROUNDS}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Aciertos:</span>
              <span className="stat-value">{score}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Tiempo:</span>
              <span className="stat-value">{formatTime(timeElapsed)}</span>
            </div>
          </div>
        </div>

        <div className="game-playground">
          <h3 className="question">¿Qué color es este?</h3>

          {currentColor && (
            <div 
              className="color-display"
              style={{ backgroundColor: currentColor.hex }}
              title={currentColor.name}
            >
              {/* Patrón de punto para mejor visualización */}
              <div className="color-pattern"></div>
            </div>
          )}

          <div className="color-options">
            {colorOptions.map((color, index) => (
              <button
                key={index}
                className={`color-option ${
                  selectedColor?.name === color.name ? 'selected' : ''
                } ${
                  showFeedback
                    ? color.name === currentColor.name
                      ? 'correct'
                      : 'incorrect'
                    : ''
                }`}
                onClick={() => handleColorSelect(color)}
                disabled={showFeedback || selectedColor}
              >
                <div className="option-color" style={{ backgroundColor: color.hex }}></div>
                <span className="option-name">{color.name}</span>
              </button>
            ))}
          </div>

          {showFeedback && (
            <div className={`feedback ${feedbackType}`}>
              <span className="feedback-icon">
                {feedbackType === 'correct' ? '✅' : '❌'}
              </span>
              <span className="feedback-message">{feedbackMessage}</span>
            </div>
          )}
        </div>

        <div className="game-footer">
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${(round / MAX_ROUNDS) * 100}%` }}
            ></div>
          </div>
          <p className="progress-text">Progreso: {round}/{MAX_ROUNDS} completados</p>
        </div>
      </div>
    </div>
  );
};

export default ColorGame;
