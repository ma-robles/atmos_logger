# Procedimiento de almacenamiento

Los archivos serán de tipo CSV.
Se creará un archivo nuevo al iniciar
muestreo de cada X segundos
Almacenamiento de datos cada minuto (una línea de archivo)
Envío de datos cada 10 minutos
Se generarán archivos para cada envío.
los datos contaran con un ID contador para saber su secuencia de muestreo.
nombre de archivo: ID\_fecha.csv con los datos del primer renglón
Sistema de carpetas
Se creará una carpeta cada 250 archivos, el nombre de cada carpeta corresponderá con el nombre del primer archivo almacenado en ella. Es decir: 000, 250, 500, ...
Se creará un archivo send.txt con el ID(nombre) del ultimo archivo enviado.
## Inicialización
Creación de carpeta de datos (data)
Creación de carpeta de datos temporal (tmp)
Creación de archivo de datos nuevo
