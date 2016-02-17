# Marvin Dynamic Analyzer #

Analizador dinámico de vulnerabilidades de aplicaciones Android utilzando OpenNebula y emuladores Android-x86.

Version: 0.01

## Arquitectura general ##

![architecture.jpg](https://raw.githubusercontent.com/programa-stic/Marvin-dynamic-Analyzer/master/images/architecture.jpg)

Las vulnerabilidades analizadas dinámicamente son:

* JAVASCRIPT_INTERFACE
* PHONEGAP_JS_INJECTION
* PHONEGAP_CVE_3500_URL
* SSL_CUSTOM_TRUSTMANAGER
* SSL_CUSTOM_HOSTNAMEVERIFIER
* SSL_ALLOWALL_HOSTNAMEVERIFIER
* SSL_INSECURE_SOCKET_FACTORY
* SSL_WEBVIEW_ERROR
* WEBVIEW_FILE_SCHEME

Además, intenta analizar por otro tipo de vulnerabilidades mientras analizando las anteriores:

* ZIP_PATH_TRAVERSAL
* INSECURE_TRANSMISSION
* INSECURE_STORAGE

El VMManager esta encargado de buscar nuevas vulnerabilidades en la base de datos de Marvin para analizar dinámicamente.

Los VMClient reciben las aplicaciones y los tipos de vulnerabilidades a analizar del VMManager. Luego, usa ADB para conectarse al emulador y comenzar el análisis. Además configura al emulador para que él pueda actuar de router para interceptar los pedidos HTTP/HTTPS. Utilizan un fuzzer personalizado [MarvinToqueton](https://github.com/programastic/Marvin-toqueton/) cuyo objetivo es interactuar con la aplicación para disparar las vulnerabilidades. 

Los emuladores corren Android 4.3 x86 para soportar Cydia Substrate. Las próximas versiones soportaran Xposed.
El proyecto está utilizando las imágenes de [Android-x86](www.android-x86.org).

Hay 3 tipos de emuladores:
* Emuladores sin ningún tipo de verificación SSL
* Emuladores con verificación SSL normal (utilizados para ver si las aplicaciones realizan verificaciones SSL)
* Emuladores corriendo ICS 4.0 (usados para explotar la vulnerabilidad de interfaces Javascript/Java )

## Configuraciones ##

Las configuraciones de VMManager se encuentran en el archivo settings.py:

```
NET_ID = 1 #ID used de la red Virtual OpenNebula
# IP RPC OpenNebula
ONE_IP = "http://IP:2633/RPC2"
ONE_CREDS = "" #Credenciales OpenNebula xml RPC
ELASTIC_SEARCH_SERVER = "ELASTIC_SEARCH_IP_ADDRESS"
DOWNLOAD_APK_SITE = "http://FRONTEND_IP_ADDRESS/frontpage/"
ANDROID_VM_POOL = {"NONSSL":{"NON_SSL_EMULATOR_IP"},"SSL":{"EMULATOR_IP"},"JAVASCRIPTINTERFACE":{"ICS_EMULATOR_IP"}}
```

**IMPORTANTE:** Bajo el directorio django_support, configurar el archivo settings.py con los SECRET_KEY, contraseñas de la base de datos y URL de BungieSearch correspondientes a la configuración de Marvin-frontend.

El cliente de VMClient también incluye configuraciones en settings.py:

```
VM_MANAGER_IP = 'VMMANAGER_IP_ADDRESS:8082'
REPORTER_IP = 'localhost:8081'
DEBUG_MODE = False

#Algunas configuraciones del Fuzzer que pueden ser modificadas en el proyecto Marvin-toqueton.
```

## Para correrlo ##

Comenzar el servidor con:

```
	python VMManager.py
```

Y los clientes con:

```
	./client.sh
```

## Análisis de una aplicación ##

El analizador dinámico obtiene la siguiente aplicación a analizar del conjunto de vulnerabilidades no verificadas en la base de datos de Marvin. Para hacer análisis de una sola aplicación, cambiar DEBUG_MODE a True en settings.py del cliente. Y luego correr el cliente de la siguiente forma:

```
	python VMClient.py [VULNERABILITY_ID] [NOMBRE-PAQUETE/NOMBRE ARCHIVO APK] '''{"emulator":"IP_DEL_EMULADOR_A_USAR","count":0}'''
```

En el caso de la vulnerabilidad PHONEGAP_CVE_3500_URL se debe además agregar como parámetro el campo "activity" que referencia a la Activity inicial de la aplicación. Si sólo querés corroborar vulnerabilidades no encontradas estáticamente como ZIP Path Traversal o transmisión y almacenamiento inseguro, utiliza "dummy" como ID de la vulnerabilidad.

**IMPORTANTE:** El nombre del archivo APK debe coincidir con el nombre del paquete de la aplicación.

## Deployment ##

VMManager y VMClient pueden utilizar cualquier VM hosteada en OpenNebula. Los autores utilizaron ttylinux - kvm del Marketstore de OpenNebula como template.

### Dependencias de VMManager ### 

Correr los siguientes comandos para instalar las dependencias:

```
	pip install bungiesearch

	sudo apt-get install python-mysqldb

	apt-get install default-jre

	apt-get install python-django
```

### Dependencias de VMClient ###

Correr los siguientes comandos para instalar las dependencias:

```
	apt-get install mitmproxy
```
### Crear un emulador ###

Descargar desde el sitio de Android-x86 el ISO para el release 4.3 o 4.0. Instalar en un disco con una herramienta de virtualización. Los autores utilizamos VirtualBox para ello.

Convierte la imagen instalada del disco a formato qemu de KVM para soportar snapshots en OpenNebula. Puedes utilizar el siguiente comando: 

```
	qemu-img convert -O qcow2 original-image image-converted.qcow
```
Sube la imagen a OpenNebula y create un nuevo template para el emulador.

Ejemplo de template:

```
	CONTEXT=[NETWORK="YES",SSH_PUBLIC_KEY="$USER[SSH_PUBLIC_KEY]"]

	CPU="2"

	DISK=[DRIVER="qcow2",IMAGE="Image Name",IMAGE_UNAME="Your user"]

	GRAPHICS=[LISTEN="0.0.0.0",TYPE="VNC"]

	HYPERVISOR="kvm"

	MEMORY="512"

	NIC=[MODEL="pcnet",NETWORK="Your Virtual Network Name",NETWORK_UNAME="Your user"]

	SUNSTONE_CAPACITY_SELECT="YES"

	SUNSTONE_NETWORK_SELECT="YES"
```

**IMPORTANTE:** COnfigurar QCOW2 como el driver de disco para soportar snapshots.

**IMPORTANTE:** Al crear un dispositivo Android ICS, configurar el driver de red a pcnet.

Crear una VM utilizando el template creado anteriormente y prende el dispositivo.

**IMPORTANT:** Iniciar la primera vez en modo Debug y editar el archivo /mnt/grub/menu.lst. Agregar "quiet nomodeset vga=788" antes de video=-16 a los argumentos del kernel.

Por ahora no hay soporte de contextualización para las VMs de Android corriendo en OpenNebula así que las interfaces de red deben ser configuradas manualmente para poder conectarse remotamente desde ADB. Para correr comandos como root desde la aplicación Terminal utilizar:

```
	adb root

	adb kill-server

	adb start-server

	adb shell
```

Los siguientes comandos deberían funcionar para configurar la red corriendo en la aplicación de Terminal como root:

```
	ifconfig eth0 [IP] netmask [NETMASK]

	busybox route add default gw [GATEWAY] dev eth0
```


Una vez terminada la configuración de la red, **salir de la terminal en modo root** e utilizar ADB para permitir depuración remota con:

```
	adb tcpip 5556
```

Manualmente configurar:
* Deshabilitar el sonido en el Emulador (Settings->Sound)
* Destildar la verificación de las aplicaciones en Settings->Security->Uncheck Verify Apps

Correr android_setup_client.sh en un host con los siguientes parámetros:

```
	emulator_setup.sh {SSL/NOSSL} {IP-EMULADOR} {ROUTER-PARA-EMULADOR}
```

Seleccionar {SSL/NOSSL} para desplegar un emulador de tipo 1 o 2.

El script:
* Rootea el emulador
* Agrega una configuración de red estática
* Instala SuperUser y CydiaSubstrate, linkea Substrate y le permite correr como root.
* Si es de tipo NOSSL, instala Android-SSL-TrustKiller para dejar de validar la verificación SSL.
* Instala el fuzzer Marvin-toqueton.
* Deshabilita el bloqueo de pantalla y la suspensión.


Por último, crear un snapshot de la VM corriendo con el nombre que prefieras.

### Requerimientos ###

* Marvin-frontend instalado en alguna VM de OpenNebula.
* Python 2.7.x (No usar Python 3.X) 

### Créditos ###
* Joaquín Rinaudo ([@xeroxnir](https://www.twitter.com/xeroxnir))
* Juan Heguiabehere ([@jheguia](https://www.twitter.com/jheguia))

### Contacto ###
* Mandar un correo a stic en el dominio fundacionsadosky.org.ar
