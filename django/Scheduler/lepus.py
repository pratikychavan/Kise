import traitlets
import pika
from Scheduler.models import Queues
from Scheduler.serializers import get_my_serializer
from Scheduler.constants import QUEUE_CONFIG_PATH, APP_NAME


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

    def create_connection(self):
        credentials = pika.PlainCredentials(
            username=self.username, 
            password=self.password
            )
        parameters = pika.ConnectionParameters(
            host=self.host, 
            port=self.port, 
            credentials=credentials
        )
        self._connection = pika.BlockingConnection(parameters)
    
    def create_channel(self):
        self._channel = self._connection.channel()
    
    def check_channel(self):
        return self._channel.is_open if self._channel else False
    
    def close_channel(self):
        self._channel.close() if self._channel else ""
    
    def requires_channel(self, func):
        def wrapper(*args, **kwargs):
            self.create_channel()
            result = func(*args, **kwargs)
            self.close_channel()
            return result
        return wrapper
    
    # Exchange Operations
    @requires_channel
    def create_exchange(self, username=False):
        exchange = username if username else APP_NAME
        self._channel.exchange_declare(
            exchange=exchange, 
            durable=True, 
            exchange_type="direct"
            )
    
    @requires_channel
    def bind_exchanges(self, **kwargs):
        """
        Bind an exchange to another exchange.

        Parameters:	
            destination (str) - The destination exchange to bind
            source (str) - The source exchange to bind to
            routing_key (str) - The routing key to bind on
            arguments (dict) - Custom key/value pair arguments for the binding
            callback (callable) - callback(pika.frame.Method) for method Exchange.BindOk
        
        Raises:	ValueError 
        """
        self._channel.exchange_bind(**kwargs)
    
    @requires_channel
    def delete_exchanges(self, exchange, force=False):
        self._channel.exchange_delete(exchange=exchange, if_unused=not force)
    
    @requires_channel
    def unbind_exchange(self, **kwargs):
        """
        Unbind an exchange from another exchange.

        Parameters:	
            destination (str) - The destination exchange to unbind
            source (str) - The source exchange to unbind from
            routing_key (str) - The routing key to unbind
            arguments (dict) - Custom key/value pair arguments for the binding
            callback (callable) - callback(pika.frame.Method) for method Exchange.UnbindOk
        Raises: ValueError 
        """
        self._channel.exchange_unbind(**kwargs)
    
    # Queue Operations
    @requires_channel
    def create_queue(self, queue_name, exchange):
        self._channel.queue_declare(queue=queue_name, durable=True)
        self._channel.queue_bind(exchange=exchange, queue=queue_name)
        return queue_name
    
    @requires_channel
    def purge_queue(self, queue_name):
        self._channel.queue_purge(queue=queue_name)
    
    @requires_channel
    def delete_queue(self, queue_name, force=False):
        self._channel.queue_delete(queue=queue_name, if_empty=not force)
    
    @requires_channel
    def send_message(self, message, queue_name):
        self._channel.basic_publish(exchange=self.exchange, routing_key=queue_name, body=message)
    
    @requires_channel
    def receive_message(self, queue_name):
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
        if self.execution_mode == "Remote":
        
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
        pass
        
        def get_all_queues(self):
            queues = Queues.objects.filter(user_id=self.user_obj.id)
            serializer = get_my_serializer(
                model=Queues,
                fields="__all__"
                )(queues)
            return serializer.data
        
        def create_queues(self):
            if self.execution_mode == "Remote":
                self.rmq.create_exchange(self.user_obj.username)
                self.rmq.create_queue(self.task_queue, self.user_obj.username)
                self.rmq.create_queue(self.control_queue, self.user_obj.username)
            else:
                pass
        
        def delete_queues(self, force=False):
            if self.execution_mode == "Remote":
                self.rmq.delete_queue(self.task_queue, force=force)
                self.rmq.delete_queue(self.control_queue, force=force)
                self.rmq.delete_exchange(self.user_obj.username, force=force)
            else:
                pass

