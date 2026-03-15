#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import array
import math
import pygame
import sys

from chip8 import Chip8

# TODO: Move to a file
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Emulator:

    def __init__(self, file):
        print("Loading from \"{}\"".format(file))
        self.chip8 = Chip8()
        self.rom = self.load_from_file(file)

        self.TITLE = "CHIP8 Emulator"
        self.PIXEL_SIZE = 10
        self.WIDTH = 64
        self.HEIGHT = 32
        self.SIZE = [self.WIDTH * self.PIXEL_SIZE, self.HEIGHT * self.PIXEL_SIZE]
        self.MAX_TICKS_PER_SECOND = 60
        self.CPU_CYCLES_PER_FRAME = 10  # ~600 instructions/second

        pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
        pygame.init()
        self.beep_sound = self._generate_beep(frequency=440, duration=0.1)


    def run(self):
        self.chip8.initialize()
        self.chip8.load_rom(self.rom)

        # PyGame initialization
        screen = pygame.display.set_mode(self.SIZE)
        pygame.display.set_caption(self.TITLE)
        clock = pygame.time.Clock()

        # Game loop
        while True:

            # Limit the loop speed
            clock.tick(self.MAX_TICKS_PER_SECOND)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.handle_keypress()

            for _ in range(self.CPU_CYCLES_PER_FRAME):
                self.chip8.run()

            self.handle_sound()

            screen.fill(BLACK)

            self.draw_screen(screen, self.chip8.display)

            pygame.display.update()


    def load_from_file(self, file):
        with open(file, "rb") as file:
            return file.read()


    def _generate_beep(self, frequency, duration):
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * num_samples)
        for i in range(num_samples):
            t = i / sample_rate
            buf[i] = int(32767 * math.sin(2 * math.pi * frequency * t))
        return pygame.mixer.Sound(buffer=buf)

    def handle_sound(self):
        if self.chip8.sound_timer > 0:
            if not pygame.mixer.get_busy():
                self.beep_sound.play(-1)  # loop until stopped
        else:
            self.beep_sound.stop()

    def handle_keypress(self):
        keys = pygame.key.get_pressed()
        mapping = {
            pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
            pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
            pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
            pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF,
        }
        for key, chip8_key in mapping.items():
            self.chip8.keypad[chip8_key] = bool(keys[key])


    def draw_screen(self, screen, display_state):

        def draw_pixel(screen, x, y, color):
            screen.fill(color, [
                x * self.PIXEL_SIZE,
                y * self.PIXEL_SIZE,
                self.PIXEL_SIZE,
                self.PIXEL_SIZE])

        for y in range(0, self.HEIGHT):
            for x in range(0, self.WIDTH):
                address = x + y * self.WIDTH
                pixel = display_state[address]
                if pixel != 0:
                    draw_pixel(screen, x, y, WHITE)
                else:
                    draw_pixel(screen, x, y, BLACK)


def main(filepath):
    emu = Emulator(filepath)
    emu.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    main(args.file)
