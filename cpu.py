"""CPU functionality."""
import sys
from dispatch import *


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.halt = False

        # R7 is reserved as the stack pointer (SP)
        self.reg[7] = 255

    def load(self, filename):
        """Load a program into memory."""
        # print("DEBUG: CPU Load")
        address = 0

        # For now, we've just hardcoded a program:

        with open(filename) as file:
            for line in file:
                # print(f"DEBUG: line = {line}")
                if line == '':
                    continue

                first_bit = line[0]
                # print(f"DEBUG: First bit: {line[0]}")

                if first_bit == "0" or first_bit == "1":
                    self.ram[address] = int(line[:8], 2)
                    # print(f"DEBUG: self.ram[{address}] = {line} = {int(line[:8], 2)}")
                    address += 1


    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def dispatch(self, IR):
        self.dispatchtable = {}
        self.dispatchtable[LDI] = self.handle_ldi
        self.dispatchtable[PRN] = self.handle_prn
        self.dispatchtable[HLT] = self.handle_hlt
        self.dispatchtable[PUSH] = self.handle_push
        self.dispatchtable[POP] = self.handle_pop

        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)

        # print(self.dispatchtable[IR])
        self.dispatchtable[IR](operand_a, operand_b)

    def alu(self, IR):
        """ALU operations."""
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alutable = {}
        self.alutable[MUL] = self.reg[operand_a] = self.reg[operand_a] * self.reg[operand_b]

        # if IR == "ADD":
        #     self.reg[reg_a] += self.reg[reg_b]
        # #elif op == "SUB": etc
        try:
            self.alutable[IR]
        except:
            raise Exception("Unsupported ALU operation")

    def handle_ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def handle_prn(self, operand_a, operand_b):
        print(self.reg[operand_a])

    def handle_hlt(self, operand_a, operand_b):
        self.halt = True

    def handle_push(self, operand_a, operand_b):
        self.reg[7] = (pointer - 1) % 255
        pointer = self.reg[7]
        

        self.ram[pointer] = operand_a

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        # Perform the actions
        while not self.halt:
            IR = self.ram_read(self.pc)
            # operand_a = self.ram_read(self.pc + 1)
            # operand_b = self.ram_read(self.pc + 2)
            
            #ir_str = str(bin(IR))[2:]
            ir_str = format(IR, '08b')
            print(f"DEBUG: ir_str = {ir_str}")

            # AAxxxxxx = operation size
            op_size = int(ir_str[:2], 2)
            print(f"DEBUG: op_size = {op_size}")

            # xxBxxxxx = alu operation
            alu_set = (int(ir_str[2:3], 2) == 1)
            print(f"DEBUG: alu_set = {alu_set}")

            # xxxCxxxx = ins_set
            ins_set = (int(ir_str[3:4], 2) == 1)
            # ins_set = ((IR >> 4) == 1)
            print(f"DEBUG: ins_set = {ins_set}")

            if alu_set:
                self.alu(IR)
            else:
                self.dispatch(IR)
            # if IR == LDI:
            #     self.reg[operand_a] = operand_b
            # elif IR == PRN:
            #     print(self.reg[operand_a])
            # elif IR == HLT:
            #     self.halt = True

            if not ins_set:
                self.pc += op_size + 1