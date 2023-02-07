Address = int
Byte = int


class Memory:
    def __init__(self, size: int):
        self.data = [0 for _ in range(size)]
        self.size = size

    def check_index(self, index: Address):
        if index < 0 and index >= self.size:
            print(f"Index out of range! {index} >= {self.size}")
            return False
        return True

    def load_byte(self, index: Address) -> Byte:
        if self.check_index(index):
            return self.data[index]
        return 0

    def store_byte(self, index: Address, byte: Byte):
        if self.check_index(index):
            self.data[index] = byte & 0xFF

    def load_from_file(self, path: str):
        with open(path, "rb") as f:
            buffer = f.read()
        for i, byte in enumerate(buffer):
            self.data[i] = byte

    def print_bytes(self, f: int, t: int):
        for i in range(f, t):
            print(f"{self.data[i]:0>2x}|", end="")
        print()
