import pygame

pygame.init()

PIXEL_SIZE = PIXEL_WIDTH, PIXEL_HEIGHT = (10, 10)

class Monitor:
    def __init__(self, w, h) -> None:
        self.res = pygame.math.Vector2(w, h)
        self.window = pygame.display.set_mode((self.res.x * PIXEL_WIDTH, self.res.y * PIXEL_HEIGHT))
        self.running = False
        self.clock = pygame.time.Clock()
        self.counter = 0
    
    def clear(self):
        self.window.fill((0, 0, 0))
    
    def set_at(self, x, y, c):
        pygame.draw.rect(self.window, c, (x * PIXEL_WIDTH, y * PIXEL_HEIGHT, PIXEL_WIDTH, PIXEL_HEIGHT))

    def update(self):
        self.counter = self.counter + 1
        for i in range(self.counter):
            for j in range(min(i, int(self.res.y))):
                x = j
                y = self.res.y - j
                self.set_at(x, y, (255, 255, 255))
        pass

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.clear()
            self.update()
            pygame.display.update()
            self.clock.tick(5)


w = Monitor(80, 40)
w.run()