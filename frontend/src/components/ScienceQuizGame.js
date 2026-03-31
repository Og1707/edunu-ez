import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ScienceQuizGame.css';

const ScienceQuizGame = ({ tema, onGameComplete, onClose }) => {
  const [gameState, setGameState] = useState('loading'); // loading, playing, completed
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [score, setScore] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [wikiContent, setWikiContent] = useState(null);
  const [timeLeft, setTimeLeft] = useState(30);
  const [gameStats, setGameStats] = useState({
    correctAnswers: 0,
    totalQuestions: 0,
    timeSpent: 0
  });

  // Preguntas predefinidas de ciencias naturales
  const scienceQuestions = {
    biologia: [
      {
        question: "¿Cuál es la función principal de los cloroplastos en las plantas?",
        options: ["Respiración", "Fotosíntesis", "Digestión", "Reproducción"],
        correct: 1,
        explanation: "Los cloroplastos contienen clorofila y son responsables de la fotosíntesis."
      },
      {
        question: "¿Qué tipo de animal es una ballena?",
        options: ["Pez", "Mamífero", "Reptil", "Anfibio"],
        correct: 1,
        explanation: "Las ballenas son mamíferos marinos que respiran aire y amamantan a sus crías."
      },
      {
        question: "¿Cuántas cámaras tiene el corazón humano?",
        options: ["2", "3", "4", "5"],
        correct: 2,
        explanation: "El corazón humano tiene 4 cámaras: 2 aurículas y 2 ventrículos."
      }
    ],
    fisica: [
      {
        question: "¿Cuál es la velocidad de la luz en el vacío?",
        options: ["300,000 km/s", "150,000 km/s", "450,000 km/s", "200,000 km/s"],
        correct: 0,
        explanation: "La velocidad de la luz en el vacío es aproximadamente 300,000 km/s."
      },
      {
        question: "¿Qué fuerza mantiene a los planetas en órbita alrededor del Sol?",
        options: ["Magnetismo", "Gravedad", "Fricción", "Presión"],
        correct: 1,
        explanation: "La gravedad es la fuerza que mantiene a los planetas en órbita."
      }
    ],
    quimica: [
      {
        question: "¿Cuál es el símbolo químico del oro?",
        options: ["Go", "Au", "Ag", "Or"],
        correct: 1,
        explanation: "Au viene del latín 'aurum', que significa oro."
      },
      {
        question: "¿Cuántos protones tiene un átomo de carbono?",
        options: ["4", "6", "8", "12"],
        correct: 1,
        explanation: "El carbono tiene 6 protones, lo que define su número atómico."
      }
    ]
  };

  useEffect(() => {
    initializeGame();
  }, [tema]);

  useEffect(() => {
    let timer;
    if (gameState === 'playing' && timeLeft > 0) {
      timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
    } else if (timeLeft === 0) {
      handleTimeUp();
    }
    return () => clearTimeout(timer);
  }, [gameState, timeLeft]);

  const initializeGame = async () => {
    try {
      // Obtener contenido de Wikipedia para contexto
      if (tema) {
        const response = await axios.get(`http://127.0.0.1:8000/api/wikipedia/contenido/?tema=${tema}`);
        setWikiContent(response.data);
      }

      // Seleccionar preguntas basadas en el tema
      const temaKey = detectarCategoria(tema);
      const selectedQuestions = scienceQuestions[temaKey] || scienceQuestions.biologia;
      
      setQuestions(selectedQuestions);
      setGameStats(prev => ({ ...prev, totalQuestions: selectedQuestions.length }));
      setGameState('playing');
    } catch (error) {
      console.error('Error al inicializar el juego:', error);
      // Usar preguntas de biología por defecto
      setQuestions(scienceQuestions.biologia);
      setGameState('playing');
    }
  };

  const detectarCategoria = (tema) => {
    const temaLower = tema.toLowerCase();
    if (temaLower.includes('fisica') || temaLower.includes('fuerza') || temaLower.includes('energia')) {
      return 'fisica';
    } else if (temaLower.includes('quimica') || temaLower.includes('elemento') || temaLower.includes('atomo')) {
      return 'quimica';
    }
    return 'biologia'; // Por defecto
  };

  const handleAnswerSelect = (answerIndex) => {
    setSelectedAnswer(answerIndex);
  };

  const handleSubmitAnswer = () => {
    const isCorrect = selectedAnswer === questions[currentQuestion].correct;
    
    if (isCorrect) {
      setScore(score + 10);
      setGameStats(prev => ({ ...prev, correctAnswers: prev.correctAnswers + 1 }));
    }

    setShowResult(true);
    
    setTimeout(() => {
      if (currentQuestion + 1 < questions.length) {
        setCurrentQuestion(currentQuestion + 1);
        setSelectedAnswer(null);
        setShowResult(false);
        setTimeLeft(30);
      } else {
        completeGame();
      }
    }, 2000);
  };

  const handleTimeUp = () => {
    setShowResult(true);
    setTimeout(() => {
      if (currentQuestion + 1 < questions.length) {
        setCurrentQuestion(currentQuestion + 1);
        setSelectedAnswer(null);
        setShowResult(false);
        setTimeLeft(30);
      } else {
        completeGame();
      }
    }, 2000);
  };

  const completeGame = () => {
    const finalStats = {
      ...gameStats,
      finalScore: score,
      accuracy: (gameStats.correctAnswers / questions.length) * 100
    };
    
    setGameState('completed');
    if (onGameComplete) {
      onGameComplete(finalStats);
    }
  };

  const restartGame = () => {
    setCurrentQuestion(0);
    setScore(0);
    setSelectedAnswer(null);
    setShowResult(false);
    setTimeLeft(30);
    setGameStats({ correctAnswers: 0, totalQuestions: questions.length, timeSpent: 0 });
    setGameState('playing');
  };

  if (gameState === 'loading') {
    return (
      <div className="science-quiz-game loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Cargando juego de ciencias...</p>
        </div>
      </div>
    );
  }

  if (gameState === 'completed') {
    return (
      <div className="science-quiz-game completed">
        <div className="game-results">
          <h2>¡Juego Completado!</h2>
          <div className="stats">
            <div className="stat-item">
              <span className="stat-label">Puntuación Final:</span>
              <span className="stat-value">{score} puntos</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Respuestas Correctas:</span>
              <span className="stat-value">{gameStats.correctAnswers}/{questions.length}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Precisión:</span>
              <span className="stat-value">{Math.round((gameStats.correctAnswers / questions.length) * 100)}%</span>
            </div>
          </div>
          
          {wikiContent && (
            <div className="wiki-context">
              <h3>Aprende más sobre: {wikiContent.titulo}</h3>
              <p>{wikiContent.resumen.substring(0, 200)}...</p>
              <a href={wikiContent.url_completa} target="_blank" rel="noopener noreferrer">
                Ver artículo completo
              </a>
            </div>
          )}
          
          <div className="game-actions">
            <button className="restart-btn" onClick={restartGame}>
              Jugar de Nuevo
            </button>
            <button className="close-btn" onClick={onClose}>
              Cerrar
            </button>
          </div>
        </div>
      </div>
    );
  }

  const question = questions[currentQuestion];
  
  return (
    <div className="science-quiz-game playing">
      <div className="game-header">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
          ></div>
        </div>
        <div className="game-info">
          <span className="question-counter">
            Pregunta {currentQuestion + 1} de {questions.length}
          </span>
          <span className="score">Puntuación: {score}</span>
          <span className={`timer ${timeLeft <= 10 ? 'warning' : ''}`}>
            Tiempo: {timeLeft}s
          </span>
        </div>
      </div>

      <div className="question-container">
        <h3 className="question-text">{question.question}</h3>
        
        <div className="options-container">
          {question.options.map((option, index) => (
            <button
              key={index}
              className={`option-btn ${selectedAnswer === index ? 'selected' : ''} ${
                showResult ? (index === question.correct ? 'correct' : selectedAnswer === index ? 'incorrect' : '') : ''
              }`}
              onClick={() => handleAnswerSelect(index)}
              disabled={showResult}
            >
              {option}
            </button>
          ))}
        </div>

        {showResult && (
          <div className="result-feedback">
            <p className={selectedAnswer === question.correct ? 'correct-feedback' : 'incorrect-feedback'}>
              {selectedAnswer === question.correct ? '¡Correcto!' : 'Incorrecto'}
            </p>
            <p className="explanation">{question.explanation}</p>
          </div>
        )}

        {!showResult && selectedAnswer !== null && (
          <button className="submit-btn" onClick={handleSubmitAnswer}>
            Confirmar Respuesta
          </button>
        )}
      </div>
    </div>
  );
};

export default ScienceQuizGame;
