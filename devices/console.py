from emulator.device import Device

class Console(Device):
    def on_write(self, data: int):
        print(chr(data))