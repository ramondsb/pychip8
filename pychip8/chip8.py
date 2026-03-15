import random
import pygame


class Chip8:

    def __init__(self):
        self.memory = 4096 * [int("0x00", 16)]
        self.pc = int("0x200", 16)
        self.stack = 16 * [int("0x00", 16)]
        self.sp = 0
        self.i = int("0x00", 16)
        self.registers = 16 * [int("0x00", 16)]
        self.delay_timer = int("0x00", 16)
        self.sound_timer = int("0x00", 16)
        self.keypad = 16 * [False]
        self.display = (64 * 32) * [int("0x00", 16)]


    def draw_display(self):
        sout = ""
        for y in range(0, 32):
            sout += "\n"
            for x in range(0, 64):
                address = x + y * 64
                if self.display[address] == 0:
                    sout += "."
                else:
                    sout += "#"




    def cycle(self):
        state = self.get_state()
        opcode = self.fetch_opcode(state)

        self.decode_opcode(opcode)

        # Update timers
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer == 0:
            pass  #TODO: Integrate sound system


    def get_state(self):
        """Returns a dict with the current state data"""
        return {
            "memory": self.memory,
            "pc": self.pc
        }


    def fetch_opcode(self, state):
        memory = state["memory"]
        pc = state["pc"]

        msb = memory[pc]
        lsb = memory[pc + 1]

        return ((msb << 8) | (lsb))


    def decode_opcode(self, opcode):
        opcode = opcode & 0xffff


        def opcode_0x00XX(opcode):
            g2 = {
                0x00e0: self.opcode_00E0,
                0x00ee: self.opcode_00EE
            }
            op = (opcode & int('0x00FF', 16))
            g2[op](opcode)

        def opcode_0x8NNN(opcode):
            g = {
                0x0000: self.opcode_0x8XY0,
                0x0001: self.opcode_0x8XY1,
                0x0002: self.opcode_0x8XY2,
                0x0003: self.opcode_0x8XY3,
                0x0004: self.opcode_0x8XY4,
                0x0005: self.opcode_0x8XY5,
                0x0006: self.opcode_0x8XY6,
                0x0007: self.opcode_0x8XY7,
                0x000E: self.opcode_0x8XYE,
            }
            op = (opcode & int('0x000F', 16))
            g[op](opcode)

        def opcode_0xEXXX(opcode):
            g2 = {
                0x009E: self.opcode_EX9E,
                0x00A1: self.opcode_EXA1
            }
            op = (opcode & int('0x00FF', 16))
            g2[op](opcode)

        def opcode_0xFXXX(opcode):
            g = {
                0x0007: self.opcode_FX07,
                0x000A: self.opcode_FX0A,
                0x0015: self.opcode_FX15,
                0x0018: self.opcode_FX18,
                0x001E: self.opcode_FX1E,
                0x0029: self.opcode_FX29,
                0x0033: self.opcode_FX33,
                0x0055: self.opcode_FX55,
                0x0065: self.opcode_FX65,
            }
            op = (opcode & int('0x00FF', 16))
            g[op](opcode)

        g1 = {
                0x1000: self.opcode_0x1NNN,
                0x2000: self.opcode_0x2NNN,
                0x3000: self.opcode_0x3XNN,
                0x4000: self.opcode_0x4XNN,
                0x5000: self.opcode_0x5XY0,
                0x6000: self.opcode_0x6XNN,
                0x7000: self.opcode_0x7XNN,
                0x8000: opcode_0x8NNN,
                0x9000: self.opcode_0x9XY0,
                0xa000: self.opcode_0xAXXX,
                0xb000: self.opcode_0xBXXX,
                0xc000: self.opcode_0xCXNN,
                0xd000: self.opcode_0xDXYN,
                0xe000: opcode_0xEXXX,
                0xf000: opcode_0xFXXX,
                0x0000: opcode_0x00XX
        }

        op = (opcode & int('0xF000', 16))
        #print("op: {}".format(hex(op)))

        g1[op](opcode)


    def initialize(self):
        # Load font set
        fonts = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]

        for i in range(0, len(fonts)):
            self.memory[i] = fonts[i]


    def load_rom(self, bytes):
        bytes = list(bytes)
        for i in range(len(bytes)):
            self.memory[i + 512] = bytes[i]


    def run(self):
        self.cycle()


    def opcode_0x1NNN(self, opcode):

        """Jumps to address NNN"""
        address = opcode & 0x0FFF
        self.pc = address


    def opcode_0x2NNN(self, opcode):

        """Calls subroutine at NNN"""
        address = opcode & 0x0FFF
        self.stack[self.sp] = self.pc + 2  # return address is instruction after the call
        self.sp += 1
        self.pc = address


    def opcode_0x3XNN(self, opcode):

        """Skips the next instruction if VX equals NN"""
        x = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF

        vx = self.registers[x]
        if vx == nn:
            self.pc += 4
        else:
            self.pc += 2


    def opcode_0x4XNN(self, opcode):

        """Skips the next instruction if VX doesn't equal NN"""
        x = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF

        vx = self.registers[x]
        if vx != nn:
            self.pc += 4
        else:
            self.pc += 2


    def opcode_0x5XY0(self, opcode):

        """Skips the next instruction if VX equals VY"""
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4



        vx = self.registers[x]
        vy = self.registers[y]
        if vx == vy:
            self.pc += 4
        else:
            self.pc += 2


    def opcode_0x6XNN(self, opcode):

        """Sets VX to NN"""
        x = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF

        self.registers[x] = nn
        self.pc += 2


    def opcode_0x7XNN(self, opcode):

        """Adds NN to VX"""
        x = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF

        self.registers[x] += nn
        self.pc += 2


    def opcode_0x8XY0(self, opcode):

        """Sets VX to the value of VY"""
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4



        vy = self.registers[y]
        self.registers[x] = vy
        self.pc += 2


    def opcode_0x8XY1(self, opcode):

        """Sets VX to VX or VY"""
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4



        vx = self.registers[x]
        vy = self.registers[y]
        self.registers[x] = vx | vy
        self.pc += 2


    def opcode_0x8XY2(self, opcode):

        """Sets VX to VX and VY"""
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4



        vx = self.registers[x]
        vy = self.registers[y]
        self.registers[x] = vx & vy
        self.pc += 2


    def opcode_0x8XY3(self, opcode):

        """Sets VX to VX xor VY"""
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4



        vx = self.registers[x]
        vy = self.registers[y]
        self.registers[x] = vx ^ vy
        self.pc += 2


    def opcode_0x8XY4(self, opcode):

        """Adds VY to VX and set carry flag"""
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4



        vx = self.registers[x]
        vy = self.registers[y]

        sum = vx + vy

        self.registers[x] = (sum & 0xFF)

        if (vx + vy) > 255:
            self.registers[15] = 0x0001 # VF = 1
        else:
            self.registers[15] = 0x0000 # VF = 0
        self.pc += 2


    def opcode_0x8XY5(self, opcode):

        """VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there isn't. """
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4



        vx = self.registers[x]
        vy = self.registers[y]

        sub = vx - vy

        self.registers[x] = (sub & 0xFF)

        if vx > vy:
            self.registers[15] = 0x0001 # VF = 1
        else:
            self.registers[15] = 0x0000 # VF = 0
        self.pc += 2


    def opcode_0x8XY6(self, opcode):

        """Stores the least significant bit of VX in VF and then shifts VX to the right by 1(Vx is divided by 2)"""
        x = (opcode & 0x0F00) >> 8

        vx = self.registers[x]

        least_significant_bit = vx & 0x0001

        self.registers[x] = vx >> 1

        # Set VF to the least significant bit
        self.registers[15] = least_significant_bit

        self.pc += 2


    def opcode_0x8XY7(self, opcode):

        """VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there isn't. """
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4



        vx = self.registers[x]
        vy = self.registers[y]

        sub = vy - vx

        self.registers[x] = (sub & 0xFF)

        if vy > vx:
            self.registers[15] = 0x0001 # VF = 1
        else:
            self.registers[15] = 0x0000 # VF = 0
        self.pc += 2


    def opcode_0x8XYE(self, opcode):

        """Stores the most significant bit of VX in VF and then shifts VX to the left by 1 (Vx is multiplied by 2)"""
        x = (opcode & 0x0F00) >> 8

        vx = self.registers[x]

        msb = 1 << 7

        most_significant_bit = vx & msb

        self.registers[x] = (vx << 1) & 0xFF

        # Set VF to the most significant bit
        self.registers[15] = 1 if most_significant_bit else 0

        self.pc += 2


    def opcode_0x9XY0(self, opcode):

        """Skips the next instruction if VX doesn't equal VY"""
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4



        vx = self.registers[x]
        vy = self.registers[y]

        if vx != vy:
            self.pc += 4
        else:
            self.pc += 2


    def sys_address2(self, opcode):
        pass


    def opcode_00E0(self, opcode):
        """Clear screen"""

        self.display = (64 * 32) * [int("0x00", 16)]
        self.pc += 2
        # TODO: Set draw flag


    def opcode_0xAXXX(self, opcode):

        address = opcode & 0x0FFF
        self.i = address 
        self.pc += 2


    def opcode_0xBXXX(self, opcode):

        """Jumps to the address XXX plus V0"""
        address = opcode & 0x0FFF
        v0 = self.registers[0]
        self.pc = address + v0


    def opcode_0xCXNN(self, opcode):

        """Sets VX to the result of a bitwise AND operation on a random number"""
        x = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF
        random_number = random.randrange(0, 256)

        self.registers[x] = random_number & nn

        self.pc += 2


    def opcode_0xDXYN(self, opcode):

        """Display N-byte pattern from coordinate (VX,VY)"""

        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        n = opcode & 0x000F



        vx = self.registers[x]
        vy = self.registers[y]

        self.update_screen_state(vx, vy, n)

        self.pc += 2


    def opcode_EX9E(self, opcode):

        x = (opcode & 0x0F00) >> 8
        vx = self.registers[x]


        if self.keypad[vx] == True:
            self.pc += 4
        else:
            self.pc += 2


    def opcode_EXA1(self, opcode):

        """Skips the next instruction if the key stored in VX isn't pressed"""
        x = (opcode & 0x0F00) >> 8
        vx = self.registers[x]


        if self.keypad[vx] == False:
            self.pc += 4
        else:
            self.pc += 2


    def opcode_FX07(self, opcode):

        """Sets VX to the value of the delay timer"""
        x = (opcode & 0x0F00) >> 8

        self.registers[x] = self.delay_timer 

        self.pc += 2


    def opcode_FX0A(self, opcode):

        """Wait key press and then store in VX"""

        def wait_keypress():
            key_pressed = None
            while True:
                event = pygame.event.wait()
                if event.type == pygame.KEYDOWN:
                    keys = {
                        pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
                        pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
                        pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
                        pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF,
                    }

                    if event.key in keys.keys():
                        key_pressed = keys[event.key]
                        break
                    else:
                        continue

            return key_pressed

        x = (opcode & 0x0F00) >> 8

        self.registers[x] = wait_keypress()

        self.pc += 2


    def opcode_FX15(self, opcode):

        """Sets the delay timer to VX"""

        x = (opcode & 0x0F00) >> 8
        vx = self.registers[x]

        self.delay_timer = vx

        self.pc += 2


    def opcode_FX18(self, opcode):

        """Sets the sound timer to VX"""

        x = (opcode & 0x0F00) >> 8
        vx = self.registers[x]

        self.sound_timer = vx

        self.pc += 2


    def opcode_FX1E(self, opcode):

        """Adds VX to I"""

        x = (opcode & 0x0F00) >> 8
        vx = self.registers[x]

        sum = vx + self.i

        self.i = (sum & 0xFFFF)

        if sum > 0xFFF:  # I register is 12-bit, max value is 0xFFF (4095)
            self.registers[15] = 0x0001 # VF = 1
        else:
            self.registers[15] = 0x0000 # VF = 0

        self.pc += 2


    def opcode_FX29(self, opcode):

        """Sets I to the location of the sprite for the character in VX"""

        x = (opcode & 0x0F00) >> 8
        vx = self.registers[x]

        self.i = vx * 5

        self.pc += 2


    def opcode_FX33(self, opcode):

        """Stores the binary-coded decimal representation of VX"""

        x = (opcode & 0x0F00) >> 8
        vx = self.registers[x]

        c = int(vx / 100)
        d = int(vx % 100 / 10)
        u = int(vx % 10)

        self.memory[self.i] = c
        self.memory[self.i + 1] = d
        self.memory[self.i + 2] = u

        self.pc += 2


    def opcode_FX55(self, opcode):

        """Stores V0 to VX in memory starting at address I"""

        x = (opcode & 0x0F00) >> 8

        for offset in range(0, x + 1):
            self.memory[self.i + offset] = self.registers[offset]

        self.pc += 2


    def opcode_FX65(self, opcode):

        """Fills V0 to VX with values from memory starting at address I"""

        x = (opcode & 0x0F00) >> 8

        for offset in range(0, x + 1):
            self.registers[offset] = self.memory[self.i + offset]

        self.pc += 2


    def opcode_00EE(self, opcode):

        """Return from a subroutine"""

        self.pc = self.stack[self.sp - 1]
        self.sp -= 1


    def update_screen_state(self, x, y, n):
        # TODO: read n bytes starting at I from memory


        sprites = []
        for i in range(0, n):
            sprites.append(self.memory[i])

        # TODO: XOR bytes with screen
        for h in range(0, n):
            mem = self.memory[self.i + h]
            for v in range(0, 8):
                if (mem & (0x80 >> v)) != 0:
                    # TODO: Use size definitions
                    address = v + x + (h + y) * 64
                    if address > 64 * 32: continue
                    old_pixel = self.display[address]
                    new_pixel = old_pixel ^ 1
                    self.display[address] = new_pixel
                    if old_pixel == 1:
                        self.registers[0xf] = 1

