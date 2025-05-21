# Spotify Pipeline: Análisis de Canciones Más Escuchadas
Este proyecto extrae tus canciones más escuchadas de Spotify, las guarda en una base de datos PostgreSQL (hosteada en AWS RDS), y permite su análisis visual en Power BI.

## 🚀 ¿Qué hace este proyecto?
1. Conecta con la API de Spotify para obtener tus canciones más escuchadas.

2. Transforma los datos en un formato tabular usando pandas.

3. Carga los datos en PostgreSQL, ya sea en local o en una base en la nube (como RDS).

4. Permite visualizar los datos en Power BI para análisis como:

    - Artistas más frecuentes

    - Canciones más populares

    - Distribución por fechas de lanzamiento

    - Evolución de tus gustos musicales

## 🧱 Tech Stack
- Python (con Spotipy, Pandas, SQLAlchemy)

- PostgreSQL (en contenedor Docker o RDS en AWS)

- Power BI (para visualización)

- GitHub Actions (próximamente para automatización del pipeline)

## 📁 Estructura del proyecto
``` bash
spotify-pipeline/
├── main.py               # Ejecuta el pipeline completo
├── spotify_etl.py        # Funciones para extraer y transformar los datos
├── db_utils.py           # Guarda los datos en PostgreSQL
├── .env                  # Variables de entorno (credenciales API y DB)
├── requirements.txt      # Dependencias del proyecto
└── README.md             # Este archivo 🙂
```

## ⚙️ Configuración
1. Clona el repo:

``` bash
git clone https://github.com/tuusuario/spotify-pipeline.git
cd spotify-pipeline
```

2. Crea un archivo .env con tus credenciales:
``` bash
SPOTIPY_CLIENT_ID=tu-client-id
SPOTIPY_CLIENT_SECRET=tu-client-secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback

POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=spotify
```

3. Instala las dependencias:

```bash 
pip install -r requirements.txt
```

4. Ejecuta el pipeline:

``` bash
python main.py
```
5. Abre Power BI y conéctate a tu base PostgreSQL para visualizar los datos.

## 🧠 Ideas de análisis en Power BI

- Gráficas de barras por artista

- Nube de palabras con títulos

- Evolución de popularidad por mes

- Comparativa entre nuevos lanzamientos y clásicos

- Dashboard de géneros (si se añade esa info)

## 🔒 Notas de seguridad
- Nunca subas tu .env al repositorio público.

- Si usas RDS, asegúrate de configurar los grupos de seguridad para permitir solo las IPs necesarias.

## ✨ Próximamente
- Automatización diaria con GitHub Actions

- Dashboard público con Power BI Web

- Incorporar géneros musicales y duración