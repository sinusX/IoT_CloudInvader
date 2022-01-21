from pynput.keyboard import Key, Listener
import asyncio
import json
import os
import keyboard
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message

class ControlKeyboard:

    def __init__(self) -> None:
        self.arrows = {
            "left_arrow": 0,
            "right_arrow": 0,
        }
        self.has_changed = False


    def start(self, device_client):
        self.device_client = device_client
        listener = Listener(
                on_press=self.on_press,
                on_release=self.on_release)
        listener.start()
        
    def on_press(self, key):

        if key == Key.right and not self.arrows["right_arrow"]:
            self.arrows["right_arrow"] = 1
            self.has_changed = True
            print("Right Arrow pressed", flush=True)
        elif key == Key.left and not self.arrows["left_arrow"]:
            self.arrows["left_arrow"] = 1
            self.has_changed = True
            print("Left Arrow pressed", flush=True)

    def on_release(self, key):
        global doQuit
        
        if key == Key.right and self.arrows["right_arrow"]:
            self.arrows["right_arrow"] = 0
            self.has_changed = True
            print("Right Arrow released", flush=True)
        elif key == Key.left and self.arrows["left_arrow"]:
            self.arrows["right_arrow"] = 0
            self.has_changed = True
            print("Left Arrow released", flush=True)

        if key == Key.esc:
            # Stop listener
            doQuit = True
            return False

    def control_has_changed(self):
        return self.has_changed

    def get_arrows(self):
        return self.arrows

    def reset_change_flag(self):
        self.has_changed = False



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
        "left_arrow": 0,
        "right_arrow": 0,
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
            if not arrows["left_arrow"]:
                arrows["left_arrow"] = 1
                await send_telemetry(device_client, arrows)
                print("Left pressed",flush=True)
        else:
            if arrows["left_arrow"]:
                arrows["left_arrow"] = 0
                await send_telemetry(device_client, arrows)
                print("Left released",flush=True)
        
        if keyboard.is_pressed('right'):
            if not arrows["right_arrow"]:
                arrows["right_arrow"] = 1
                await send_telemetry(device_client, arrows)
                print("Right pressed",flush=True)
        else:
            if arrows["right_arrow"]:
                arrows["right_arrow"] = 0
                await send_telemetry(device_client, arrows)
                print("Right released",flush=True)

        if keyboard.is_pressed('esc'):
            doQuit = True

        await asyncio.sleep(0.05)

    # Finally, shut down the client
    await device_client.shutdown()



if __name__ == "__main__":
    asyncio.run(main())
