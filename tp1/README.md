## Ejecución

### Configuración

Para correr el sistema primero se deberá generar un `docker-compose.yaml` con los parámetros
de escalamiento.
Dicho archivo se genera con el comando:

```
sh dfile_gen.sh <REPLICAS_CLIENT> <REPLICAS_JOINER> <REPLICAS_DROPPER> <REPLICAS_TRENDING> <REPLICAS_THUMBNAIL> <REPLICAS_LIKES_FILTER> <REPLICAS_WATCHER> <TRENDING_ROUTER_ENABLED> <THUMBNAIL_ROUTER_ENABLED> <DOWNLOADER_ENABLED> <TAG_UNIQUE_ENABLED> <TRENDING_TOP_ENABLED> <ACCEPTOR_ENABLED>
```

Existen scripts de ayuda para poder probar cada uno de los 3 pipelines por separado. Estos scripts son:

```
sh dfile_pipeline1.sh
sh dfile_pipeline2.sh
sh dfile_pipeline3.sh
```

O bien un script para probar todo junto con una configuración de ejemplo:

```
sh dfile_all.sh
```

Se recomienda probar con 1 para cada valor e ir ajustando de acuerdo al flujo de mensajes que se puede visualizar directamente desde la consola de RabbitMQ.

Se deja un ejemplo de la estructura de archivos en la carpeta `/data` que actúa como set de prueba.

### Inicio

Para correr el programa se deben inicializar todos los servicios, esto se puede hacer con el comando:

```
make up
```
Esto levantará todos los servicios de procesamiento.

Verificar si la versión de docker instalada implica el uso del plugin compose de la siguiente manera `docker compose` o su forma legacy `docker-compose`.

En caso de requerir correr con el plugin, para levantar el sistema usar:

```
make nup
```

### Corrida

Finalmente para iniciar el programa se deberá correr en otra terminal:

```
sh run_client.sh
```

Esto comenzará a enviar la información provista en la carpeta `data` para cada uno de los clientes. Ver la carpeta de ejemplo para saber cómo estructurar los datos.

### Resultados

Al finalizar el procesamiento, dentro de la carpeta `.tmp` se guardará bajo `client_X` la descarga de los thumbnails más un log con los resultados obtenidos.

### Pruebas

Para pruebas, se deja una carpeta `.results` con una corrida con los set de datos de ejemplo en `data` para conocer cuáles fueron sus resultados originales.

Se puede volver a correr el programa y se podrá comparar los resultados mediante el script:

```
sh check_results.sh
```

Que realizará un diff entre las carpetas `.tmp/client_X` con su respectivo `.result/client_X`.

En caso exitoso, no habrá diferencia entre ambos directorios.

### Chaos

Se proveen una serie de `chaos scripts` para simular la caída de los servicios. Estos scripts se ejecutan de la siguiente manera:

```
sh ./chaos_{SERVICE}.sh <KILL_FRECUENCY>
```

Donde se le indica la frecuencia con la cual bajar el servicio.

También se provee un script para bajar aleatoriamente cualquier servicio, el mismo también recibe la frecuencia de caída:

```
sh ./chaos_all.sh <KILL_FRECUENCY>
```

En los logs se podrá observar tanto la caída del servicio, como la recuperación mediante los `Watchers` disponibles en el sistema.

### Resumen

Este es un resumen para una ejecución rápida del proyecto

```
sh ./dfile_all.sh
make up

(EN OTRA TERMINAL)
sh ./run_client.sh

(AL TERMINAR)
sh ./check_results.sh
```