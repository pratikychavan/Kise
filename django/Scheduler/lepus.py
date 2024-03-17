import traitlets
import pika
from Scheduler.models import Queues
from Scheduler.serializers import get_my_serializer
from Scheduler.constants import QUEUE_CONFIG_PATH


class RabbitMQClient(traitlets.config.Configurable):
    host = traitlets.Unicode("localhost", help="RabbitMQ server host").tag(config=True)
    port = traitlets.Int(5672, help="RabbitMQ server port").tag(config=True)
    username = traitlets.Unicode("guest", help="RabbitMQ username").tag(config=True)
    password = traitlets.Unicode("guest", help="RabbitMQ password").tag(config=True)
    exchange = traitlets.Unicode("nimbus", help="RabbitMQ exchange name").tag(config=True)


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

    def setup_queue(self, queue_name, username):
        self.connect()
        exchange = username if username else self.exchange
        self._channel.exchange_declare(exchange=exchange, exchange_type="direct")
        self._channel.queue_declare(queue=queue_name)
        self._channel.queue_bind(exchange=exchange, queue=queue_name)
    
    def send_message(self, message, queue_name):
        self.connect()
        self._channel.basic_publish(exchange=self.exchange, routing_key=queue_name, body=message)
    
    def receive_message(self, queue_name):
        self.connect()
        method, properties, body = self._channel.basic_get(queue=queue_name)
        self._channel.basic_ack(method.delivery_tag)
        return body.decode('utf-8')
    
    def close_connection(self):
        if self._connection and self._connection.is_open:
            self._connection.close()


class QueueManager:
    def __init__(self, user_obj, execution_mode="Cloud"):
        
        self.user_obj = user_obj
        self.execution_mode = execution_mode
        
        self.task_queue = "EE-Task-Queue"
        self.control_queue = "EE-Control-Queue"
        self.result_queue = "EE-Result-Queue"
        
        self.c = traitlets.config.JSONFileConfigLoader(QUEUE_CONFIG_PATH).load_config()
        self.rmq = RabbitMQClient(config=self.c)
        if execution_mode == "Remote":
        
            self.task_queue += f"-{self.user_obj.username}-{Queues.objects.filter(user_id=self.user_obj.id, queue_type='Task').count()}"
            Queues.objects.create(
                user=self.user_obj,
                queue_name=self.task_queue,
                queue_type="Task"
            )
        
            self.control_queue += f"-{self.user_obj.username}-{Queues.objects.filter(user_id=self.user_obj.id, queue_type='Control').count()}"
            Queues.objects.create(
                user=self.user_obj,
                queue_name=self.control_queue,
                queue_type="Control"
            )
        
            self.result_queue += f"-{self.user_obj.username}-{Queues.objects.filter(user_id=self.user_obj.id, queue_type='Result').count()}"
            Queues.objects.create(
                user=self.user_obj,
                queue_name=self.result_queue,
                queue_type="Result"
            )
        pass
        
        def get_all_queues(self):
            queues = Queues.objects.filter(user=self.user_obj)
            serializer = get_my_serializer(
                model=Queues,
                fields="__all__"
                )(queues)
            return serializer.data
        
        def create_queues(self):
            pass


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
