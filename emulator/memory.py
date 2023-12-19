import datetime

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

    def print_bytes(self, f: int, t: int):
        for i in range(f, t):
            print(f"{self.data[i]:0>2x}|", end="")
        print()

    def save_snapshot(self, file: str = "mem.snap"):
        with open(file, "wb") as f:
            f.write(str(datetime.datetime.now()).encode())
            f.write(b"\0")
            curr = self.data[0]
            count = 0
            for v in self.data:
                if v == curr:
                    count += 1
                else:
                    f.write(curr.to_bytes())
                    f.write(count.to_bytes())
                    count = 1
                    curr = v
            f.write(curr.to_bytes())
            f.write(count.to_bytes())

    def load_snapshot(self, file: str):
        with open(file, "rb") as f:
            while f.read(1)[0] != 0:
                continue
            ind = 0
            while len(b := f.read(2)) == 2:
                v = b[0]
                for i in range(ind, ind + b[1]):
                    self.data[i] = v
                ind += b[1]
