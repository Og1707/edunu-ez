import React from 'react';
import {
  ArrowRight,
  BookOpen,
  Gamepad2,
  House,
  Settings,
  BarChart3,
  Check,
  Play,
  Star,
  Atom
} from 'lucide-react';

import './Home.css';
import studentIllustration from '../assets/student-tablet.svg';

const Home = () => {
  return (
    <div className="home-container">

      {/* ================= HERO ================= */}
      <section className="hero-section">

        {/* Decorative elements */}
        <div className="hero-decoration decoration-purple"></div>
        <div className="hero-decoration decoration-blue"></div>
        <div className="hero-dot dot-1"></div>
        <div className="hero-dot dot-2"></div>
        <div className="hero-dot dot-3"></div>
        <div className="hero-star">✦</div>

        <div className="hero-inner">

          {/* ================= LEFT ================= */}
          <div className="hero-content">

            <div className="hero-eyebrow">
              Plataforma educativa
            </div>

            <h1>
              Plataforma Educativa
              <br />
              e Interactiva
              <br />
              <span>EduNúñez</span>
            </h1>

            <p>
              Potenciando el aprendizaje mediante
              actividades multimedia y gamificación.
            </p>

            <div className="hero-buttons">

              <a href="/register" className="btn-primary">
                Explorar Plataforma
                <ArrowRight size={19} />
              </a>

              <a href="/login" className="btn-secondary">
                Ingresar como Estudiante
              </a>

            </div>

          </div>


          {/* ================= RIGHT ================= */}
          <div className="hero-visual">

            <div className="dashboard-window">

              {/* Browser top */}
              <div className="browser-bar">
                <div className="browser-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>

                <div className="dashboard-brand">
                  <span className="brand-icon">🎓</span>
                  EduNúñez
                </div>

                <div className="avatar">
                  V
                </div>
              </div>


              <div className="dashboard-body">

                {/* Sidebar */}
                <aside className="dashboard-sidebar">

                  <div className="sidebar-item active">
                    <House size={19} />
                  </div>

                  <div className="sidebar-item">
                    <BookOpen size={19} />
                  </div>

                  <div className="sidebar-item">
                    <Gamepad2 size={19} />
                  </div>

                  <div className="sidebar-item">
                    <BarChart3 size={19} />
                  </div>

                  <div className="sidebar-item">
                    <Settings size={19} />
                  </div>

                </aside>


                {/* Main dashboard */}
                <main className="dashboard-main">

                  <div className="dashboard-greeting">
                    <h2>¡Hola, Valentina!</h2>
                    <p>
                      Sigue aprendiendo y alcanza tus metas 🚀
                    </p>
                  </div>


                  {/* Stats */}
                  <div className="dashboard-stats">

                    <div className="progress-card">

                      <div className="stat-icon purple">
                        <BookOpen size={20} />
                      </div>

                      <div className="progress-info">

                        <span>Tu progreso general</span>

                        <div className="progress-bar">
                          <div className="progress-value"></div>
                        </div>

                      </div>

                      <strong>68%</strong>

                    </div>


                    <div className="points-card">

                      <div className="points-header">
                        <Star size={19} fill="currentColor" />
                        <span>Puntos</span>
                      </div>

                      <strong>520</strong>

                      <small>
                        ¡Vas muy bien! 🎉
                      </small>

                    </div>

                  </div>


                  {/* Activities */}
                  <div className="activities-section">

                    <h3>Tus actividades</h3>

                    <div className="activity-grid">

                      <div className="activity-card activity-purple">

                        <div className="activity-top">
                          <div className="activity-icon">
                            <Play size={17} fill="currentColor" />
                          </div>
                        </div>

                        <div className="activity-image">
                          🌄
                        </div>

                        <h4>Explora el mundo</h4>
                        <p>Video interactivo</p>

                        <div className="activity-check">
                          <Check size={14} />
                        </div>

                      </div>


                      <div className="activity-card activity-red">

                        <div className="activity-top">
                          <Gamepad2 size={18} />
                        </div>

                        <div className="math-card">
                          <strong>2 + 2</strong>
                          <span>● ● ●</span>
                        </div>

                        <h4>Reto de matemáticas</h4>
                        <p>Juego educativo</p>

                        <div className="activity-arrow">
                          <ArrowRight size={14} />
                        </div>

                      </div>


                      <div className="activity-card activity-green">

                        <div className="activity-top">
                          <BookOpen size={18} />
                        </div>

                        <div className="plant-card">
                          🌱
                        </div>

                        <h4>Ciencia y naturaleza</h4>
                        <p>Actividad multimedia</p>

                        <div className="activity-arrow">
                          <ArrowRight size={14} />
                        </div>

                      </div>

                    </div>

                  </div>

                </main>


                {/* Quiz floating card */}
                <div className="quiz-card">

                  <div className="quiz-title">
                    <Atom size={25} />
                    <div>
                      <strong>Quiz de Ciencias</strong>
                      <span>¿Qué sabes sobre el universo?</span>
                    </div>
                  </div>

                  <div className="quiz-option selected">
                    <span>A</span>
                    Los planetas
                    <Check size={14} />
                  </div>

                  <div className="quiz-option">
                    <span>B</span>
                    Las estrellas
                  </div>

                  <div className="quiz-option">
                    <span>C</span>
                    Los satélites
                  </div>

                  <button className="quiz-button">
                    Continuar
                    <ArrowRight size={14} />
                  </button>

                </div>

              </div>

            </div>


            {/* Student illustration */}
            <img
              src={studentIllustration}
              alt="Estudiante utilizando una tablet"
              className="student-illustration"
            />
          </div>
        </div>
      </section>

    </div>
  );
};

export default Home;
