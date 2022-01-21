
import asyncio
import time
from azure.eventhub.aio import EventHubConsumerClient

connection_str = "Endpoint=sb://germanywestcentraldedns008.servicebus.windows.net/;SharedAccessKeyName=iothubowner;SharedAccessKey=xbN3jyDH1ipGqleOZeO9EJhwkM/XKBXj01chLGENJLQ=;EntityPath=iothub-ehub-cloudinvap-16967609-6a1ac5c16a"
consumer_group = "$Default"

startup_time = time.time()*1000
print("Time now: {}".format(startup_time),flush=True)

async def on_event(partition_context, event):
    if event.system_properties[b'iothub-enqueuedtime'] > startup_time:
        recv_msg = event.body_as_json(encoding='UTF-8')
        if "left_arrow" in recv_msg:
            if recv_msg["left_arrow"] == 1:
                print("left arrow is pressed",flush=True)
            else: 
                print("left arrow is released",flush=True)
        if "right_arrow" in recv_msg:
            if recv_msg["right_arrow"] == 1:
                print("right arrow is pressed",flush=True)
            else: 
                print("right arrow is released",flush=True)


async def receive():
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group)
    async with client:
        await client.receive(
            on_event=on_event,
            starting_position="-1",  # "-1" is from the beginning of the partition.
        )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(receive())
