import traitlets
import pika

class RabbitMQClient(traitlets.HasTraits):
    host = traitlets.Unicode("localhost", help="RabbitMQ server host").tag(config=True)
    port = traitlets.Int(5672, help="RabbitMQ server port").tag(config=True)
    username = traitlets.Unicode("guest", help="RabbitMQ username").tag(config=True)
    password = traitlets.Unicode("guest", help="RabbitMQ password").tag(config=True)
    exchange = traitlets.Unicode("", help="RabbitMQ exchange name").tag(config=True)
    task_queue = traitlets.Unicode("EE-Task-Queue").tag(config=True)
    control_queue = traitlets.Unicode("EE-Control-Queue").tag(config=True)
    result_queue = traitlets.Unicode("EE-Result-Queue").tag(config=True)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._connection = None
        self._channel = None

    def connect(self):
        credentials = pika.PlainCredentials(username=self.username, password=self.password)
        parameters = pika.ConnectionParameters(
            host=self.host, port=self.port, credentials=credentials
        )
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()

    def close_connection(self):
        if self._connection and self._connection.is_open:
            self._connection.close()

    def declare_exchange(self):
        if self.exchange:
            self._channel.exchange_declare(exchange=self.exchange, exchange_type="direct")

    def declare_queues(self):
        for queue in self.queues:
            self._channel.queue_declare(queue=queue)
            self._channel.queue_bind(exchange=self.exchange, queue=queue)

    def on_start(self):
        self.connect()
        self.declare_exchange()
        self.declare_queues()

    def on_stop(self):
        self.close_connection()

# Example usage:
# config = {
#     "RabbitMQClient": {
#         "host": "localhost",
#         "port": 5672,
#         "username": "guest",
#         "password": "guest",
#         "exchange": "e1",
#         "task_queue": "EE-Task-Queue"
#         "control_queue": "EE-Control-Queue"
#         "result_queue": "EE-Result-Queue"
#     }
# }
# client = RabbitMQClient(config=config)
# client.on_start()
# # Do your RabbitMQ operations here
# client.on_stop()
