"""CPU functionality."""

import sys

# Instruction definitions
HLT = 0b00000001  # Stops program and exits simulator
LDI = 0b10000010  # Loads immediate (cp+2) into a given register (cp+1)
PRN = 0b01000111  # Prints the value at a given register (cp+1)
MUL = 0b10100010  # ALU - multiplies two registers

# Qs: Is this what the instructions are supposed to look like?


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.running = True  # is this necessary?

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

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
            # print(self.reg)
        else:
            raise Exception("Unsupported ALU operation")

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
        while self.running:
            ir = self.ram_read(self.pc)

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if ir == LDI:  # LDI (load immediate)
                self.reg[operand_a] = operand_b
                self.pc += 3

            elif ir == PRN:  # PRN (print)
                print(self.reg[operand_a])
                self.pc += 2

            elif ir == HLT:  # HLT (halt)
                self.running = False
                sys.exit(0)

            elif ir == MUL:  # MUL (multiply)
                self.alu('MUL', operand_a, operand_b)
                self.pc += 3

            else:
                print('Instruction not found')
                sys.exit(1)

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
