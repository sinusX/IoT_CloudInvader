import sys
import os
import msrest
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod


iothub_connection_str = os.getenv("IOTHUB_CONNECTION_STRING")
device_id = "iot-gamepad"
method_name = "setDisplayText"
method_payload = ":-)"


try:
    # Create IoTHubRegistryManager
    registry_manager = IoTHubRegistryManager.from_connection_string(iothub_connection_str)

    deviceMethod = CloudToDeviceMethod(method_name=method_name, payload=method_payload)
    registry_manager.invoke_device_method(device_id, deviceMethod)

except msrest.exceptions.HttpOperationError as ex:
    print("HttpOperationError error {0}".format(ex.response.text))
except Exception as ex:
    print("Unexpected error {0}".format(ex))
except KeyboardInterrupt:
    print("{} stopped".format(__file__))
finally:
    print("{} finished".format(__file__))