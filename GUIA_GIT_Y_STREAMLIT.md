# Guía práctica: subir el proyecto a GitHub y conectarlo con Streamlit

## 1. Crear una carpeta del proyecto
Guarda dentro de una misma carpeta estos archivos:

- `app.py`
- `requirements.txt`
- carpeta `data/`
- carpeta `.streamlit/`
- `README.md`

## 2. Probarlo en tu computadora
En la terminal, dentro de la carpeta del proyecto:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Si abre en el navegador y funciona, ya puedes subirlo.

## 3. Subirlo a GitHub usando la web
1. En GitHub, crea un repositorio nuevo.
2. Entra a tu repositorio.
3. Haz clic en **Add file** → **Upload files**.
4. Arrastra todos los archivos y carpetas del proyecto.
5. Escribe un mensaje como `Primer version de la app de enlace quimico`.
6. Haz clic en **Commit changes**.

## 4. Subirlo a GitHub usando Git desde terminal
Dentro de la carpeta del proyecto:

```bash
git init
git add .
git commit -m "Primera version de la app"
```

Luego crea el repositorio en GitHub y conecta el remoto:

```bash
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

## 5. Conectarlo con Streamlit Community Cloud
1. Inicia sesión en Streamlit Community Cloud.
2. Haz clic en **New app**.
3. Selecciona tu repositorio de GitHub.
4. Elige la rama, normalmente `main`.
5. En **Main file path**, escribe:

```text
app.py
```

6. Revisa que `requirements.txt` esté en el repositorio.
7. Despliega la app.

## 6. Si luego haces cambios
Cada vez que cambies algo en el proyecto:

```bash
git add .
git commit -m "Actualizacion"
git push
```

Streamlit normalmente vuelve a construir la app con la nueva versión del repositorio.

## 7. Qué revisar si falla el despliegue
- Que `app.py` exista en la raíz del repositorio.
- Que `requirements.txt` exista.
- Que la carpeta `data/` sí se haya subido.
- Que el nombre del archivo principal en Streamlit sea correcto.
- Que no falten librerías importadas en `requirements.txt`.

## 8. Consejo importante
No subas secretos, contraseñas ni claves privadas al repositorio.
