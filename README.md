# redis-pubsub-chat

## Introducción

Este ejemplo muestra las capacidades y limitaciones de un sistema mensajería usando la estructura de datos de Redis de
PubSub.

## Funcionamiento

La aplicación permite la creación de N usuarios simultáneos, que pueden chatear en cuatro tópicos preexistentes.

Al elegir un tópico, el usuario se subscribe a un canal Pub/Sub, e inicia un thread escuchando por nuevos mensajes.

```python
# app/users.py

def set_topic(self, topic: str) -> None:
    self.topic = topic
    self.clean_messages()
    self.pubsub = self.redis_client.pubsub(ignore_subscribe_messages=True)
    self.pubsub.subscribe(**{self.topic: self.on_new_message})
    self.pubsub.run_in_thread(sleep_time=0.5)
```

Cada vez que escribe un mensaje, el mensaje es publicado en el canal y todos los otros usuarios suscritos al canal
reciben la publicación.

```python
# app/users.py

def on_new_message(self, message):
    if message['type'] == 'message':
        chat_item = ChatMessage(**json.loads(message['data'].decode()))
        print(f"Received: chat_item: ", chat_item)
        if chat_item['user'] != self.username:
            self.messages.append(chat_item)
```

## Limitaciones

La solución de Redis para Pub/Sub presenta varias limitaciones:

* Los clientes que se suscriben a un canal no pueden ver la historia de los mensajes pasados.
* Cualquier error en el procesamiento de un cliente, no tiene forma de volver a ser re ejecutado, ya que no hay
  visibilidad del lado de Redis sobre si se procesó correctamente el mensaje.

## Alternativas

Redis ofrece otro recurso, los streams, que llevan un timestamp por cada mensaje publicado, permitiendo armar una
secuencia ordenada de eventos (mensajes en nuestro caso). El suscriptor consulta a partir de qué timestamp desde el cual
desea recibir los mensajes, controlando de esta manera cuánta historia desea.

Al leer los mensajes, y procesarlos correctamente, puede incrementar localmente el registro del último timestamp
procesado y continuar leyendo a partir de ese valor. De fallar en el procesamiento, no se actualiza el valor del
timestamp procesado y vuelve a leer desde el punto anterior.

## Instalación

Clonar el repositorio y ejecutar el docker-compose.

```bash 
docker compose --build up
```

La aplicación puede ser accesedida en el url http://localhost:8501

Se puede monitorear los mensajes en redis ejecutando en el contenedor de redis el CLI `redis-cli`

```bash 
docker exec -ti redis /bin/redis-cli
```