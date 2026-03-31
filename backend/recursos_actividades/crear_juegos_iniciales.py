#!/usr/bin/env python3
"""
Script para crear juegos educativos iniciales para niños
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edunuñez.settings')
django.setup()

from api.models import CategoriaJuego, JuegoEducativo

def crear_categorias_juegos():
    """Crear categorías de juegos educativos"""
    categorias = [
        {
            'nombre': 'Matemáticas Divertidas',
            'tipo': 'matematicas',
            'descripcion': 'Juegos para aprender números, contar y operaciones básicas',
            'edad_minima': 3,
            'edad_maxima': 10,
            'icono': '🔢'
        },
        {
            'nombre': 'Colores y Formas',
            'tipo': 'colores_formas',
            'descripcion': 'Aprende colores, formas geométricas y patrones',
            'edad_minima': 3,
            'edad_maxima': 8,
            'icono': '🎨'
        },
        {
            'nombre': 'Juegos de Memoria',
            'tipo': 'memoria',
            'descripcion': 'Desarrolla la memoria y concentración',
            'edad_minima': 4,
            'edad_maxima': 12,
            'icono': '🧠'
        },
        {
            'nombre': 'Letras y Palabras',
            'tipo': 'lenguaje',
            'descripcion': 'Aprende el alfabeto, palabras y lectura básica',
            'edad_minima': 4,
            'edad_maxima': 10,
            'icono': '📚'
        },
        {
            'nombre': 'Ciencias para Niños',
            'tipo': 'ciencias',
            'descripcion': 'Descubre animales, plantas y el mundo natural',
            'edad_minima': 5,
            'edad_maxima': 12,
            'icono': '🔬'
        }
    ]
    
    for cat_data in categorias:
        categoria, created = CategoriaJuego.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults=cat_data
        )
        if created:
            print(f"✅ Categoría creada: {categoria.icono} {categoria.nombre}")
        else:
            print(f"⚠️  Categoría ya existe: {categoria.icono} {categoria.nombre}")

def crear_juegos_educativos():
    """Crear juegos educativos simples para niños"""
    
    # Obtener categorías
    cat_matematicas = CategoriaJuego.objects.get(tipo='matematicas')
    cat_colores = CategoriaJuego.objects.get(tipo='colores_formas')
    cat_memoria = CategoriaJuego.objects.get(tipo='memoria')
    cat_lenguaje = CategoriaJuego.objects.get(tipo='lenguaje')
    cat_ciencias = CategoriaJuego.objects.get(tipo='ciencias')
    
    juegos = [
        # MATEMÁTICAS
        {
            'titulo': 'Contar Frutas',
            'descripcion': 'Cuenta las frutas que aparecen en pantalla. ¡Muy fácil y divertido!',
            'categoria': cat_matematicas,
            'tipo_juego': 'contar_objetos',
            'nivel_dificultad': 'muy_facil',
            'objetivos_aprendizaje': 'Aprender a contar del 1 al 10',
            'habilidades_desarrolla': ['Conteo básico', 'Reconocimiento de números', 'Atención'],
            'edad_minima': 3,
            'edad_maxima': 6,
            'tiempo_estimado': 3,
            'configuracion': {
                'rango_numeros': [1, 10],
                'objetos': ['🍎', '🍌', '🍊', '🍇', '🍓'],
                'intentos_maximos': 3,
                'mostrar_ayuda': True
            }
        },
        {
            'titulo': 'Números Mágicos',
            'descripcion': 'Encuentra el número que falta en la secuencia',
            'categoria': cat_matematicas,
            'tipo_juego': 'numeros_basicos',
            'nivel_dificultad': 'facil',
            'objetivos_aprendizaje': 'Reconocer secuencias numéricas',
            'habilidades_desarrolla': ['Secuencias', 'Lógica básica', 'Números'],
            'edad_minima': 5,
            'edad_maxima': 8,
            'tiempo_estimado': 5,
            'configuracion': {
                'rango_numeros': [1, 20],
                'longitud_secuencia': 5,
                'numeros_faltantes': 1
            }
        },
        
        # COLORES Y FORMAS
        {
            'titulo': 'Arcoíris de Colores',
            'descripcion': 'Aprende los colores del arcoíris de forma divertida',
            'categoria': cat_colores,
            'tipo_juego': 'colores_primarios',
            'nivel_dificultad': 'muy_facil',
            'objetivos_aprendizaje': 'Reconocer y nombrar colores básicos',
            'habilidades_desarrolla': ['Reconocimiento de colores', 'Vocabulario', 'Memoria visual'],
            'edad_minima': 3,
            'edad_maxima': 6,
            'tiempo_estimado': 4,
            'configuracion': {
                'colores': ['rojo', 'azul', 'amarillo', 'verde', 'naranja', 'morado'],
                'modo_juego': 'identificar_color',
                'sonidos': True
            }
        },
        {
            'titulo': 'Formas Geométricas',
            'descripcion': 'Identifica círculos, cuadrados, triángulos y más formas',
            'categoria': cat_colores,
            'tipo_juego': 'formas_geometricas',
            'nivel_dificultad': 'facil',
            'objetivos_aprendizaje': 'Reconocer formas geométricas básicas',
            'habilidades_desarrolla': ['Geometría básica', 'Reconocimiento visual', 'Clasificación'],
            'edad_minima': 4,
            'edad_maxima': 7,
            'tiempo_estimado': 5,
            'configuracion': {
                'formas': ['círculo', 'cuadrado', 'triángulo', 'rectángulo', 'estrella'],
                'colores_formas': True,
                'tamaños_diferentes': False
            }
        },
        
        # MEMORIA
        {
            'titulo': 'Memoria de Animales',
            'descripcion': 'Encuentra las parejas de animales iguales',
            'categoria': cat_memoria,
            'tipo_juego': 'memoria_colores',
            'nivel_dificultad': 'facil',
            'objetivos_aprendizaje': 'Desarrollar la memoria visual y concentración',
            'habilidades_desarrolla': ['Memoria visual', 'Concentración', 'Animales'],
            'edad_minima': 4,
            'edad_maxima': 10,
            'tiempo_estimado': 6,
            'configuracion': {
                'pares': 6,
                'animales': ['🐶', '🐱', '🐰', '🐸', '🐧', '🦋', '🐝', '🐠'],
                'tiempo_mostrar': 2,
                'intentos_maximos': 20
            }
        },
        
        # LENGUAJE
        {
            'titulo': 'ABC Divertido',
            'descripcion': 'Aprende las letras del alfabeto con sonidos y ejemplos',
            'categoria': cat_lenguaje,
            'tipo_juego': 'letras_palabras',
            'nivel_dificultad': 'muy_facil',
            'objetivos_aprendizaje': 'Reconocer letras del alfabeto',
            'habilidades_desarrolla': ['Alfabeto', 'Fonética', 'Vocabulario básico'],
            'edad_minima': 4,
            'edad_maxima': 7,
            'tiempo_estimado': 5,
            'configuracion': {
                'letras': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                'mostrar_ejemplos': True,
                'sonidos_letras': True,
                'mayusculas_minusculas': False
            }
        },
        
        # CIENCIAS
        {
            'titulo': 'Animales y sus Sonidos',
            'descripcion': 'Escucha el sonido y adivina qué animal es',
            'categoria': cat_ciencias,
            'tipo_juego': 'animales_sonidos',
            'nivel_dificultad': 'facil',
            'objetivos_aprendizaje': 'Conocer animales y sus sonidos característicos',
            'habilidades_desarrolla': ['Conocimiento animal', 'Audición', 'Asociación'],
            'edad_minima': 3,
            'edad_maxima': 8,
            'tiempo_estimado': 4,
            'configuracion': {
                'animales': {
                    'perro': '🐶',
                    'gato': '🐱', 
                    'vaca': '🐄',
                    'pato': '🦆',
                    'león': '🦁',
                    'elefante': '🐘'
                },
                'reproducir_sonido': True,
                'mostrar_imagen': True
            }
        }
    ]
    
    for juego_data in juegos:
        juego, created = JuegoEducativo.objects.get_or_create(
            titulo=juego_data['titulo'],
            defaults=juego_data
        )
        if created:
            print(f"🎮 Juego creado: {juego.titulo} ({juego.categoria.icono})")
        else:
            print(f"⚠️  Juego ya existe: {juego.titulo}")

def main():
    print("🚀 Creando juegos educativos para niños...")
    print("=" * 50)
    
    print("\n📁 Creando categorías...")
    crear_categorias_juegos()
    
    print("\n🎮 Creando juegos...")
    crear_juegos_educativos()
    
    print("\n✅ ¡Proceso completado!")
    print(f"📊 Total categorías: {CategoriaJuego.objects.count()}")
    print(f"🎯 Total juegos: {JuegoEducativo.objects.count()}")

if __name__ == "__main__":
    main()
