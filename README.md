# AutoTotalPoll

Es una aplicacion de Python creada con fines educativos que vota automáticamente y de forma continua en encuestas creadas con el plugin **TotalPoll** de WordPress.

## ¿Cómo funciona?

1. Recibe la URL de una página que contenga una encuesta TotalPoll (directamente o dentro de un iframe).
2. Extrae las opciones disponibles de la encuesta.
3. Te permite elegir las opciónes a votar de forma interactiva, o pasarlas directamente como argumento.
4. Envía votos en bucle infinito hasta que detengas el script.

## Instalación

### 1. Clona o descarga el proyecto

```bash
git clone https://github.com/igorlpz/AutoTotalPoll.git
cd AutoTotalPoll
```

### 2. Instala las dependencias

```bash
pip install requests beautifulsoup4 colorama
```

## Uso

### Modo interactivo

```bash
python autoVotoTotalPoll.py
```
Te solicitara la url y se mostrarán las opciones disponibles y podrás elegir a cuál(es) votar.

### Modo automático (sin interacción)

Pasa el número de opción directamente como argumento:

```bash
python autoVotoTotalPoll.py -url https://ejemplo.com/pagina-con-encuesta 2
```

También puedes votar a varias opciones separándolas con comas, o a todas con `all`:

```bash
# Votar a las opciones 1 y 3
python autoVotoTotalPoll.py -url https://ejemplo.com/pagina-con-encuesta 1,3

# Votar a todas las opciones
python autoVotoTotalPoll.py -url https://ejemplo.com/pagina-con-encuesta all
```

## Dependencias

| Paquete | Uso |
|---|---|
| `requests` | Hacer peticiones HTTP a la encuesta |
| `beautifulsoup4` | Parsear el HTML y extraer las opciones |
| `colorama` | Colorear los prints en la terminal |
