# CHIP-8 Opcode Reference

## Notation

| Symbol | Meaning |
|--------|---------|
| `NNN` | 12-bit memory address |
| `NN` | 8-bit constant |
| `N` | 4-bit constant |
| `X` | 4-bit register index (V0–VF) |
| `Y` | 4-bit register index (V0–VF) |
| `VX` | Register X (8-bit value) |
| `VY` | Register Y (8-bit value) |
| `VF` | Register 15, used as a flag by several opcodes |
| `I` | Index register (12-bit, points to memory) |
| `PC` | Program counter |
| `SP` | Stack pointer |

---

## Flow Control

### `1NNN` — Jump
Sets PC to `NNN`. Execution continues from that address.

### `2NNN` — Call subroutine
Pushes `PC + 2` onto the stack (return address), increments SP, then sets PC to `NNN`.

### `00EE` — Return from subroutine
Pops the return address from the stack, decrements SP, and sets PC to that address.

### `BNNN` — Jump with offset
Sets PC to `NNN + V0`. Useful for jump tables.

---

## Conditionals (skip next instruction)

### `3XNN` — Skip if VX == NN
Skips the next instruction (PC += 4) if `VX == NN`, otherwise advances normally (PC += 2).

### `4XNN` — Skip if VX != NN
Skips the next instruction if `VX != NN`.

### `5XY0` — Skip if VX == VY
Skips the next instruction if `VX == VY`.

### `9XY0` — Skip if VX != VY
Skips the next instruction if `VX != VY`.

### `EX9E` — Skip if key pressed
Skips the next instruction if the key with value `VX` is currently pressed.

### `EXA1` — Skip if key not pressed
Skips the next instruction if the key with value `VX` is not currently pressed.

---

## Register Operations

### `6XNN` — Set register
Sets `VX = NN`.

### `7XNN` — Add constant
Adds `NN` to `VX`. No carry flag is set.

### `8XY0` — Copy register
Sets `VX = VY`.

### `8XY1` — Bitwise OR
Sets `VX = VX | VY`.

### `8XY2` — Bitwise AND
Sets `VX = VX & VY`.

### `8XY3` — Bitwise XOR
Sets `VX = VX ^ VY`.

### `8XY4` — Add with carry
Sets `VX = (VX + VY) & 0xFF`. Sets `VF = 1` if the result overflows 8 bits, `VF = 0` otherwise.

### `8XY5` — Subtract VY from VX
Sets `VX = (VX - VY) & 0xFF`. Sets `VF = 1` if `VX > VY` (no borrow), `VF = 0` if there is a borrow.

### `8XY7` — Subtract VX from VY
Sets `VX = (VY - VX) & 0xFF`. Sets `VF = 1` if `VY > VX` (no borrow), `VF = 0` if there is a borrow.

### `8XY6` — Shift right
Stores the least significant bit of `VX` in `VF`, then shifts `VX` right by 1 (divides by 2).

### `8XYE` — Shift left
Stores the most significant bit of `VX` in `VF` (1 or 0), then shifts `VX` left by 1 (multiplies by 2), masked to 8 bits.

### `CXNN` — Random
Sets `VX = random_byte & NN`, where `random_byte` is a random number between 0 and 255.

---

## Memory Operations

### `ANNN` — Set index register
Sets `I = NNN`.

### `FX1E` — Add to index register
Sets `I = I + VX`. Sets `VF = 1` if result overflows 12 bits (exceeds `0xFFF`), `VF = 0` otherwise.

### `FX55` — Store registers to memory
Stores registers `V0` through `VX` into memory starting at address `I`.

### `FX65` — Load registers from memory
Fills registers `V0` through `VX` with values from memory starting at address `I`.

### `FX33` — BCD conversion
Stores the binary-coded decimal (BCD) representation of `VX` in memory:
- `memory[I]` = hundreds digit
- `memory[I+1]` = tens digit
- `memory[I+2]` = units digit

---

## Display

### `00E0` — Clear screen
Clears the entire 64×32 display buffer to zero.

### `DXYN` — Draw sprite
Draws an N-byte sprite from memory at address `I` to screen coordinates `(VX, VY)`.
Each byte represents one row of 8 pixels. Pixels are XOR'd onto the display — drawing
the same sprite twice erases it. Sets `VF = 1` if any pixel is turned off (collision),
`VF = 0` otherwise. Coordinates wrap around the screen edges.

### `FX29` — Set I to font sprite
Sets `I` to the memory address of the built-in font sprite for the hex digit in `VX` (0–F).
Each font character is 5 bytes tall.

---

## Timers

Both timers count down at 60 Hz when non-zero.

### `FX15` — Set delay timer
Sets the delay timer to `VX`.

### `FX07` — Read delay timer
Sets `VX` to the current value of the delay timer.

### `FX18` — Set sound timer
Sets the sound timer to `VX`. A beep plays while the sound timer is non-zero.

---

## Input

### `FX0A` — Wait for key press
Halts execution until any key is pressed, then stores the key value in `VX`.

### Key Layout

The CHIP-8 has a 16-key hexadecimal keypad. The standard keyboard mapping used in this emulator:

```
CHIP-8 key   Keyboard
----------   --------
1 2 3 C      1 2 3 4
4 5 6 D  →   Q W E R
7 8 9 E      A S D F
A 0 B F      Z X C V
```
