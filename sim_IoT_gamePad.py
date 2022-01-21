from pynput.keyboard import Key, Listener
import asyncio
import json
import os
import keyboard
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message

async def send_telemetry(device_client, telemetry_msg, component_name=None):
    msg = Message(json.dumps(telemetry_msg))
    msg.content_encoding = "utf-8"
    msg.content_type = "application/json"
    await device_client.send_message(msg)
    print("Sent message")
    print(msg)

async def main(): 
    doQuit = False
    arrows = {
        "buttonA": 0,   # left
        "buttonB": 0,   # right
    }
    

    switch = os.getenv("IOTHUB_DEVICE_SECURITY_TYPE")
    if switch == "connectionString":
        conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
        print("Connecting using Connection String " + conn_str,flush=True)
    else:
        raise RuntimeError(
            "At least one choice needs to be made for complete functioning of this sample."
        )

    #control = ControlKeyboard()
    device_client = IoTHubDeviceClient.create_from_connection_string(
            conn_str
        )

    await device_client.connect()
    #control.start(device_client)

    # # Wait for user to indicate they are done listening for method calls
    while not doQuit:

        if keyboard.is_pressed('left'):
            if not arrows["buttonA"]:
                arrows["buttonA"] = 1
                await send_telemetry(device_client, arrows)
                print("Left pressed",flush=True)
        else:
            if arrows["buttonA"]:
                arrows["buttonA"] = 0
                await send_telemetry(device_client, arrows)
                print("Left released",flush=True)
        
        if keyboard.is_pressed('right'):
            if not arrows["buttonB"]:
                arrows["buttonB"] = 1
                await send_telemetry(device_client, arrows)
                print("Right pressed",flush=True)
        else:
            if arrows["buttonB"]:
                arrows["buttonB"] = 0
                await send_telemetry(device_client, arrows)
                print("Right released",flush=True)

        if keyboard.is_pressed('esc'):
            doQuit = True

        await asyncio.sleep(0.05)

    # Finally, shut down the client
    await device_client.shutdown()



if __name__ == "__main__":
    asyncio.run(main())
