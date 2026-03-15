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


if __name__ ==  "__main__":
    unittest.main()
