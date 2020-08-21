"""CPU functionality."""

import sys

# Instruction definitions
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
ADD = 0b10100000
ADDI = 0b10100101
SUB = 0b10100001
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ST = 0b10000100
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

# Determine Stack Pointer position
SP = 7


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = 0xf4
        self.pc = 0
        self.fl = 0b00000000

        # Initiate branchtable
        self.branchtable = {}
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop
        self.branchtable[CALL] = self.handle_call
        self.branchtable[RET] = self.handle_ret
        self.branchtable[ST] = self.handle_st
        self.branchtable[JMP] = self.handle_jmp
        self.branchtable[JEQ] = self.handle_jeq
        self.branchtable[JNE] = self.handle_jne

        # Initiate ALU branchtable
        self.alu_branchtable = {}
        self.alu_branchtable[ADD] = self.handle_add
        self.alu_branchtable[SUB] = self.handle_sub
        self.alu_branchtable[MUL] = self.handle_mul
        self.alu_branchtable[CMP] = self.handle_cmp
        self.alu_branchtable[ADDI] = self.handle_addi

    def load(self):
        """Load a program into memory."""

        address = 0

        # Provide usage message for invalid command line args
        if len(sys.argv) != 2:
            print("usage: cpu.py progname")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    line = line.strip()
                    temp = line.split()

                    # Skip blank lines
                    if len(temp) == 0:
                        continue

                    # Skip commented lines
                    if temp[0][0] == '#':
                        continue

                    try:
                        # Write instruction to ram
                        self.ram_write(int(temp[0], 2), address)

                    except ValueError:
                        print(f"Invalid Instruction: {temp[0]}")
                        sys.exit(1)

                    address += 1

        except FileNotFoundError:
            print(f"Couldn't open {sys.argv[1]}")
            sys.exit(1)

        # Exit program if program empty
        if address == 0:
            print("Provided program was empty.")
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        try:
            self.alu_branchtable[op](reg_a, reg_b)

        except KeyError:
            print("Unsupported ALU operation")
            sys.exit(1)

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while True:
            ir = self.ram_read(self.pc)

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # Send ALU instructions to ALU
            if ir >> 5 & 1 == 1:
                self.alu(ir, operand_a, operand_b)

            # Else, call branchtable function
            else:
                self.branchtable[ir](operand_a, operand_b)

            # Increment PC if not set in function
            if ir >> 4 & 1 == 0:
                num_args = ir >> 6
                self.pc += (num_args + 1)

    def ram_read(self, address):
        """
        Read into the RAM at the given address and return what is stored.
        """
        return self.ram[address]

    def ram_write(self, value, address):
        """
        Write given value into RAM at given address.
        """
        self.ram[address] = value

    def handle_ldi(self, reg_num, immediate):
        """Load an immediate into a given register."""
        self.reg[reg_num] = immediate

    def handle_prn(self, reg_num, operand_b):
        """Print value at a given register."""
        print(self.reg[reg_num])

    def handle_hlt(self, operand_a, operand_b):
        """Stop program and exit simulator."""
        sys.exit(0)

    def handle_push(self, reg_num, operand_b):
        """Push value in register onto stack."""
        self.reg[SP] -= 1

        # Get value from register
        value = self.reg[reg_num]

        # Store it on stack
        top_of_stack_addr = self.reg[SP]
        self.ram[top_of_stack_addr] = value

    def handle_pop(self, reg_num, operand_b):
        """ Pop value at top of stack to given register."""
        # Get value from top of stack
        top_of_stack_addr = self.reg[SP]
        value = self.ram[top_of_stack_addr]

        # Get reg number and store value
        self.reg[reg_num] = value

        self.reg[SP] += 1

    def handle_call(self, subroutine, operand_b):
        """Call subroutine at given register."""
        # Push return address
        ret_addr = self.pc + 2
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = ret_addr

        # Call subroutine
        self.pc = self.reg[subroutine]

    def handle_ret(self, operand_a, operand_b):
        """Return from subroutine."""
        # Pop return addr off the stack
        ret_addr = self.ram[self.reg[SP]]
        self.reg[SP] += 1

        # Set PC
        self.pc = ret_addr

    def handle_st(self, reg_a, reg_b):
        """Store value in reg_b to address stored in reg_a."""
        value = self.reg[reg_b]
        address = self.reg[reg_a]
        self.ram_write(value, address)

    def handle_jmp(self, reg_num, operand_b):
        """Jump to address in given register."""
        self.pc = self.reg[reg_num]
        # self.pc = self.ram_read(address)
        # print("successful jump to", self.pc)

    def handle_jeq(self, reg_num, operand_b):
        """If equal flag is True, jump to address in given register."""
        # Check if equal flag is true
        if self.fl & 1 == 1:
            self.handle_jmp(reg_num, operand_b)
        else:
            self.pc += 2
        # print("successful jeq")

    def handle_jne(self, reg_num, operand_b):
        """If equal flag is clear, jump to address in given register."""
        # Check to see if equal flag is false
        if self.fl & 1 == 0:
            self.handle_jmp(reg_num, operand_b)
        else:
            self.pc += 2

    def handle_add(self, reg_a, reg_b):
        """
        ALU Instruction.
        Adds two registers and stores in reg_a.
        """
        self.reg[reg_a] += self.reg[reg_b]

    def handle_sub(self, reg_a, reg_b):
        """
        ALU Instruction.
        Subtracts two registers and stores in reg_a.
        """
        self.reg[reg_a] -= self.reg[reg_b]

    def handle_mul(self, reg_a, reg_b):
        """
        ALU Instruction.
        Multiplies two registers and stores in reg_a.
        """
        self.reg[reg_a] *= self.reg[reg_b]

    def handle_cmp(self, reg_a, reg_b):
        """
        ALU Instruction.
        Compares two registers and sets self.fl based on outcome.
        """
        valueA = self.reg[reg_a]
        valueB = self.reg[reg_b]

        if valueA == valueB:
            # set equal flag to 1
            self.fl = 0b00000001

        elif valueA < valueB:
            # set less-than flag to 1
            self.fl = 0b00000100

        elif valueA > valueB:
            # set greater-than flag to 1
            self.fl = 0b00000010

        else:
            raise TypeError("Values provided to handle_cmp() not comparable")

    def handle_addi(self, reg_num, immediate):
        """
        ALU Instruction.
        Adds an immediate to value in reg_a.
        """
        self.reg[reg_num] += immediate
