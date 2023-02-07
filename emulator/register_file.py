Byte = int
Long = int


class RegisterFile:
    def __init__(self, reg_count: int, ireg_count: int):
        self.reg_count = reg_count
        self.ireg_count = ireg_count
        self.total_count = reg_count + 2 * ireg_count
        self.registers = [0 for _ in range(self.total_count)]

    def check_r_index(self, index: int) -> bool:
        if index >= self.total_count:
            print(f"Index out of range! {index} >= {self.total_count}")
            return False
        return True

    def check_i_index(self, index: int) -> bool:
        if index >= self.ireg_count:
            print(f"Index out of range! {index} >= {self.ireg_count}")
            return False
        return True

    def get_register(self, index: int) -> Byte:
        if not self.check_r_index(index):
            return 0
        return self.registers[index]

    def get_iregister(self, index: int) -> Long:
        if not self.check_i_index(index):
            return 0
        p1 = self.registers[self.reg_count + index * 2] << 8
        p2 = self.registers[self.reg_count + index * 2 + 1]
        return p1 | p2

    def set_register(self, index: int, byte: Byte):
        if self.check_r_index(index):
            self.registers[index] = byte & 0xFF

    def set_iregister(self, index: int, value: Long):
        if self.check_i_index(index):
            self.registers[self.reg_count + index * 2] = (value >> 8) & 0xFF
            self.registers[self.reg_count + index * 2 + 1] = value & 0xFF
