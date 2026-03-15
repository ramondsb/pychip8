import unittest

from pychip8 import chip8


class TestChip8(unittest.TestCase):
    def setUp(self):
        self.chip = chip8.Chip8()
        self.state = {
            "memory": [0x0000, 0x0001, 0x0001, 0x0000],
            "pc": 0
        }


    def test_fetch_opcode(self):

        opcode = self.chip.fetch_opcode(self.state)

        self.assertEqual(opcode, 1)

        self.state["pc"] = 2
        opcode = self.chip.fetch_opcode(self.state)

        self.assertEqual(opcode, 256)


    # 8XY4 - Add VY to VX, set carry flag
    def test_opcode_8XY4_no_carry(self):
        self.chip.registers[1] = 0x10
        self.chip.registers[2] = 0x20
        self.chip.opcode_0x8XY4(0x8124)
        self.assertEqual(self.chip.registers[1], 0x30)
        self.assertEqual(self.chip.registers[0xF], 0)

    def test_opcode_8XY4_carry(self):
        self.chip.registers[1] = 0xFF
        self.chip.registers[2] = 0x01
        self.chip.opcode_0x8XY4(0x8124)
        self.assertEqual(self.chip.registers[1], 0x00)  # wraps to 0
        self.assertEqual(self.chip.registers[0xF], 1)

    def test_opcode_8XY4_result_masked_to_8bit(self):
        self.chip.registers[1] = 0xFF
        self.chip.registers[2] = 0xFF
        self.chip.opcode_0x8XY4(0x8124)
        self.assertLessEqual(self.chip.registers[1], 0xFF)


    # 8XY5 - Subtract VY from VX, set borrow flag
    def test_opcode_8XY5_no_borrow(self):
        self.chip.registers[1] = 0x30
        self.chip.registers[2] = 0x10
        self.chip.opcode_0x8XY5(0x8125)
        self.assertEqual(self.chip.registers[1], 0x20)
        self.assertEqual(self.chip.registers[0xF], 1)  # no borrow

    def test_opcode_8XY5_borrow(self):
        self.chip.registers[1] = 0x10
        self.chip.registers[2] = 0x30
        self.chip.opcode_0x8XY5(0x8125)
        self.assertEqual(self.chip.registers[1], 0xE0)  # wraps via & 0xFF
        self.assertEqual(self.chip.registers[0xF], 0)   # borrow

    def test_opcode_8XY5_result_masked_to_8bit(self):
        self.chip.registers[1] = 0x00
        self.chip.registers[2] = 0x01
        self.chip.opcode_0x8XY5(0x8125)
        self.assertLessEqual(self.chip.registers[1], 0xFF)


    # 8XY7 - Subtract VX from VY, store in VX
    def test_opcode_8XY7_no_borrow(self):
        self.chip.registers[1] = 0x10
        self.chip.registers[2] = 0x30
        self.chip.opcode_0x8XY7(0x8127)
        self.assertEqual(self.chip.registers[1], 0x20)
        self.assertEqual(self.chip.registers[0xF], 1)  # no borrow

    def test_opcode_8XY7_borrow(self):
        self.chip.registers[1] = 0x30
        self.chip.registers[2] = 0x10
        self.chip.opcode_0x8XY7(0x8127)
        self.assertEqual(self.chip.registers[1], 0xE0)  # wraps via & 0xFF
        self.assertEqual(self.chip.registers[0xF], 0)   # borrow

    def test_opcode_8XY7_result_masked_to_8bit(self):
        self.chip.registers[1] = 0x01
        self.chip.registers[2] = 0x00
        self.chip.opcode_0x8XY7(0x8127)
        self.assertLessEqual(self.chip.registers[1], 0xFF)


    # 8XYE - Shift VX left by 1, store MSB in VF
    def test_opcode_8XYE_msb_set(self):
        self.chip.registers[1] = 0x80  # MSB is set
        self.chip.opcode_0x8XYE(0x811E)
        self.assertEqual(self.chip.registers[0xF], 1)
        self.assertEqual(self.chip.registers[1], 0x00)  # 0x80 << 1 masked to 8-bit

    def test_opcode_8XYE_msb_not_set(self):
        self.chip.registers[1] = 0x01  # MSB is not set
        self.chip.opcode_0x8XYE(0x811E)
        self.assertEqual(self.chip.registers[0xF], 0)
        self.assertEqual(self.chip.registers[1], 0x02)

    def test_opcode_8XYE_result_masked_to_8bit(self):
        self.chip.registers[1] = 0xFF
        self.chip.opcode_0x8XYE(0x811E)
        self.assertLessEqual(self.chip.registers[1], 0xFF)


    # EX9E - Skip next instruction if key in VX is pressed
    def test_opcode_EX9E_key_pressed(self):
        self.chip.registers[1] = 0x5
        self.chip.keypad[0x5] = True
        pc_before = self.chip.pc
        self.chip.opcode_EX9E(0xE19E)
        self.assertEqual(self.chip.pc, pc_before + 4)

    def test_opcode_EX9E_key_not_pressed(self):
        self.chip.registers[1] = 0x5
        self.chip.keypad[0x5] = False
        pc_before = self.chip.pc
        self.chip.opcode_EX9E(0xE19E)
        self.assertEqual(self.chip.pc, pc_before + 2)


    # EXA1 - Skip next instruction if key in VX is not pressed
    def test_opcode_EXA1_key_not_pressed(self):
        self.chip.registers[1] = 0x5
        self.chip.keypad[0x5] = False
        pc_before = self.chip.pc
        self.chip.opcode_EXA1(0xE1A1)
        self.assertEqual(self.chip.pc, pc_before + 4)

    def test_opcode_EXA1_key_pressed(self):
        self.chip.registers[1] = 0x5
        self.chip.keypad[0x5] = True
        pc_before = self.chip.pc
        self.chip.opcode_EXA1(0xE1A1)
        self.assertEqual(self.chip.pc, pc_before + 2)


    # FX1E - Add VX to I, set carry if overflow
    def test_opcode_FX1E_no_carry(self):
        self.chip.registers[1] = 0x10
        self.chip.i = 0x100
        self.chip.opcode_FX1E(0xF11E)
        self.assertEqual(self.chip.i, 0x110)
        self.assertEqual(self.chip.registers[0xF], 0)

    def test_opcode_FX1E_carry(self):
        self.chip.registers[1] = 0x01
        self.chip.i = 0xFFF
        self.chip.opcode_FX1E(0xF11E)
        self.assertEqual(self.chip.registers[0xF], 1)

    def test_opcode_FX1E_no_carry_at_255(self):
        # 255 should NOT trigger carry (I is 12-bit)
        self.chip.registers[1] = 0xFF
        self.chip.i = 0x00
        self.chip.opcode_FX1E(0xF11E)
        self.assertEqual(self.chip.registers[0xF], 0)


    # FX29 - Set I to sprite address for character in VX
    def test_opcode_FX29(self):
        self.chip.registers[1] = 0x0
        self.chip.opcode_FX29(0xF129)
        self.assertEqual(self.chip.i, 0)  # 0 * 5 = 0

    def test_opcode_FX29_character_A(self):
        self.chip.registers[1] = 0xA
        self.chip.opcode_FX29(0xF129)
        self.assertEqual(self.chip.i, 50)  # 10 * 5 = 50

    def test_opcode_FX29_character_F(self):
        self.chip.registers[1] = 0xF
        self.chip.opcode_FX29(0xF129)
        self.assertEqual(self.chip.i, 75)  # 15 * 5 = 75


    # 00E0 - Clear screen
    def test_opcode_00E0(self):
        self.chip.display[0] = 1
        self.chip.display[100] = 1
        self.chip.opcode_00E0(0x00E0)
        self.assertEqual(sum(self.chip.display), 0)

    # 00EE - Return from subroutine
    def test_opcode_00EE(self):
        self.chip.stack[0] = 0x300
        self.chip.sp = 1
        self.chip.opcode_00EE(0x00EE)
        self.assertEqual(self.chip.pc, 0x300)
        self.assertEqual(self.chip.sp, 0)

    # 1NNN - Jump to address NNN
    def test_opcode_1NNN(self):
        self.chip.opcode_0x1NNN(0x1300)
        self.assertEqual(self.chip.pc, 0x300)

    # 2NNN - Call subroutine at NNN
    def test_opcode_2NNN(self):
        self.chip.pc = 0x200
        self.chip.opcode_0x2NNN(0x2400)
        self.assertEqual(self.chip.pc, 0x400)
        self.assertEqual(self.chip.stack[0], 0x200)
        self.assertEqual(self.chip.sp, 1)

    # 3XNN - Skip if VX == NN
    def test_opcode_3XNN_equal(self):
        self.chip.registers[1] = 0x42
        pc_before = self.chip.pc
        self.chip.opcode_0x3XNN(0x3142)
        self.assertEqual(self.chip.pc, pc_before + 4)

    def test_opcode_3XNN_not_equal(self):
        self.chip.registers[1] = 0x10
        pc_before = self.chip.pc
        self.chip.opcode_0x3XNN(0x3142)
        self.assertEqual(self.chip.pc, pc_before + 2)

    # 4XNN - Skip if VX != NN
    def test_opcode_4XNN_not_equal(self):
        self.chip.registers[1] = 0x10
        pc_before = self.chip.pc
        self.chip.opcode_0x4XNN(0x4142)
        self.assertEqual(self.chip.pc, pc_before + 4)

    def test_opcode_4XNN_equal(self):
        self.chip.registers[1] = 0x42
        pc_before = self.chip.pc
        self.chip.opcode_0x4XNN(0x4142)
        self.assertEqual(self.chip.pc, pc_before + 2)

    # 5XY0 - Skip if VX == VY
    def test_opcode_5XY0_equal(self):
        self.chip.registers[1] = 0x10
        self.chip.registers[2] = 0x10
        pc_before = self.chip.pc
        self.chip.opcode_0x5XY0(0x5120)
        self.assertEqual(self.chip.pc, pc_before + 4)

    def test_opcode_5XY0_not_equal(self):
        self.chip.registers[1] = 0x10
        self.chip.registers[2] = 0x20
        pc_before = self.chip.pc
        self.chip.opcode_0x5XY0(0x5120)
        self.assertEqual(self.chip.pc, pc_before + 2)

    # 6XNN - Set VX to NN
    def test_opcode_6XNN(self):
        self.chip.opcode_0x6XNN(0x6142)
        self.assertEqual(self.chip.registers[1], 0x42)

    # 7XNN - Add NN to VX
    def test_opcode_7XNN(self):
        self.chip.registers[1] = 0x10
        self.chip.opcode_0x7XNN(0x7105)
        self.assertEqual(self.chip.registers[1], 0x15)

    # 8XY0 - Set VX to VY
    def test_opcode_8XY0(self):
        self.chip.registers[2] = 0x42
        self.chip.opcode_0x8XY0(0x8120)
        self.assertEqual(self.chip.registers[1], 0x42)

    # 8XY1 - Set VX to VX | VY
    def test_opcode_8XY1(self):
        self.chip.registers[1] = 0b00001111
        self.chip.registers[2] = 0b11110000
        self.chip.opcode_0x8XY1(0x8121)
        self.assertEqual(self.chip.registers[1], 0xFF)

    # 8XY2 - Set VX to VX & VY
    def test_opcode_8XY2(self):
        self.chip.registers[1] = 0b11111111
        self.chip.registers[2] = 0b00001111
        self.chip.opcode_0x8XY2(0x8122)
        self.assertEqual(self.chip.registers[1], 0x0F)

    # 8XY3 - Set VX to VX ^ VY
    def test_opcode_8XY3(self):
        self.chip.registers[1] = 0b11110000
        self.chip.registers[2] = 0b11001100
        self.chip.opcode_0x8XY3(0x8123)
        self.assertEqual(self.chip.registers[1], 0b00111100)

    # 8XY6 - Shift VX right by 1, LSB to VF
    def test_opcode_8XY6_lsb_set(self):
        self.chip.registers[1] = 0b00000101
        self.chip.opcode_0x8XY6(0x8106)
        self.assertEqual(self.chip.registers[1], 0b00000010)
        self.assertEqual(self.chip.registers[0xF], 1)

    def test_opcode_8XY6_lsb_not_set(self):
        self.chip.registers[1] = 0b00000100
        self.chip.opcode_0x8XY6(0x8106)
        self.assertEqual(self.chip.registers[1], 0b00000010)
        self.assertEqual(self.chip.registers[0xF], 0)

    # 9XY0 - Skip if VX != VY
    def test_opcode_9XY0_not_equal(self):
        self.chip.registers[1] = 0x10
        self.chip.registers[2] = 0x20
        pc_before = self.chip.pc
        self.chip.opcode_0x9XY0(0x9120)
        self.assertEqual(self.chip.pc, pc_before + 4)

    def test_opcode_9XY0_equal(self):
        self.chip.registers[1] = 0x10
        self.chip.registers[2] = 0x10
        pc_before = self.chip.pc
        self.chip.opcode_0x9XY0(0x9120)
        self.assertEqual(self.chip.pc, pc_before + 2)

    # AXXX - Set I to address
    def test_opcode_AXXX(self):
        self.chip.opcode_0xAXXX(0xA300)
        self.assertEqual(self.chip.i, 0x300)

    # BXXX - Jump to address + V0
    def test_opcode_BXXX(self):
        self.chip.registers[0] = 0x10
        self.chip.opcode_0xBXXX(0xB300)
        self.assertEqual(self.chip.pc, 0x310)

    # CXNN - Set VX to random & NN
    def test_opcode_CXNN_result_in_range(self):
        self.chip.opcode_0xCXNN(0xC1FF)
        self.assertGreaterEqual(self.chip.registers[1], 0)
        self.assertLessEqual(self.chip.registers[1], 0xFF)

    def test_opcode_CXNN_masked_by_nn(self):
        # With NN=0x00, result must always be 0
        self.chip.opcode_0xCXNN(0xC100)
        self.assertEqual(self.chip.registers[1], 0)

    # FX07 - Set VX to delay timer
    def test_opcode_FX07(self):
        self.chip.delay_timer = 0x42
        self.chip.opcode_FX07(0xF107)
        self.assertEqual(self.chip.registers[1], 0x42)

    # FX15 - Set delay timer to VX
    def test_opcode_FX15(self):
        self.chip.registers[1] = 0x30
        self.chip.opcode_FX15(0xF115)
        self.assertEqual(self.chip.delay_timer, 0x30)

    # FX18 - Set sound timer to VX
    def test_opcode_FX18(self):
        self.chip.registers[1] = 0x20
        self.chip.opcode_FX18(0xF118)
        self.assertEqual(self.chip.sound_timer, 0x20)

    # FX33 - Store BCD of VX in memory at I, I+1, I+2
    def test_opcode_FX33(self):
        self.chip.registers[1] = 234
        self.chip.i = 0x300
        self.chip.opcode_FX33(0xF133)
        self.assertEqual(self.chip.memory[0x300], 2)  # hundreds
        self.assertEqual(self.chip.memory[0x301], 3)  # tens
        self.assertEqual(self.chip.memory[0x302], 4)  # units

    def test_opcode_FX33_zero(self):
        self.chip.registers[1] = 0
        self.chip.i = 0x300
        self.chip.opcode_FX33(0xF133)
        self.assertEqual(self.chip.memory[0x300], 0)
        self.assertEqual(self.chip.memory[0x301], 0)
        self.assertEqual(self.chip.memory[0x302], 0)

    # FX55 - Store V0..VX in memory starting at I
    def test_opcode_FX55(self):
        self.chip.registers[0] = 0x10
        self.chip.registers[1] = 0x20
        self.chip.registers[2] = 0x30
        self.chip.i = 0x300
        self.chip.opcode_FX55(0xF255)  # store V0..V2
        self.assertEqual(self.chip.memory[0x300], 0x10)
        self.assertEqual(self.chip.memory[0x301], 0x20)
        self.assertEqual(self.chip.memory[0x302], 0x30)

    # FX65 - Load V0..VX from memory starting at I
    def test_opcode_FX65(self):
        self.chip.memory[0x300] = 0x10
        self.chip.memory[0x301] = 0x20
        self.chip.memory[0x302] = 0x30
        self.chip.i = 0x300
        self.chip.opcode_FX65(0xF265)  # load into V0..V2
        self.assertEqual(self.chip.registers[0], 0x10)
        self.assertEqual(self.chip.registers[1], 0x20)
        self.assertEqual(self.chip.registers[2], 0x30)


if __name__ ==  "__main__":
    unittest.main()
