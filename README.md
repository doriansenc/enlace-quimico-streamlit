# Explorador interactivo de enlace químico

Aplicación desarrollada en Streamlit para analizar el tipo de enlace entre dos elementos de la tabla periódica usando:

- electronegatividad de Pauling,
- electronegatividad de Mulliken,
- una visualización conceptual inspirada en el triángulo de Arkel–Ketelaar.

## Estructura del proyecto

```text
enlace_quimico_streamlit/
├── app.py
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── config.toml
└── data/
    └── master_elements_118.csv
```

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Qué muestra la app

1. Introducción del proyecto y metodología.
2. Selección de cualquier par de elementos.
3. Resultado por electronegatividad:
   - Pauling
   - Mulliken
4. Diagrama conceptual inspirado en Arkel–Ketelaar.
5. Conclusión científica y propiedades esperadas.

## Nota metodológica

- La app incluye los 118 elementos.
- No todos tienen datos completos para todos los métodos.
- Cuando falta un dato, la app muestra la ficha del elemento y avisa que el método no puede aplicarse con rigor.

