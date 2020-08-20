"""CPU functionality."""

import sys

# Instruction definitions
HLT = 0b00000001  # Stops program and exits simulator
LDI = 0b10000010  # Loads immediate (cp+2) into a given register (cp+1)
PRN = 0b01000111  # Prints the value at a given register (cp+1)
MUL = 0b10100010  # ALU - multiplies two registers
ADD = 0b10100000  # ALU - adds two registers
PUSH = 0b01000101  # push value in given reg (cp+1) to stack
POP = 0b01000110  # pop value at top of stack to given reg (cp+1)
CALL = 0b01010000  # calls a subroutine at given reg (cp+1)
RET = 0b00010001  # return from subroutine

# Determine Stack Pointer position
SP = 7

# Qs: Is this what the instructions are supposed to look like?


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = 0xf4
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

        # branch = BranchTable()

        while self.running:
            ir = self.ram_read(self.pc)

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if ir == LDI:
                self.reg[operand_a] = operand_b
                self.pc += 3

            elif ir == PRN:
                print(self.reg[operand_a])
                self.pc += 2

            elif ir == HLT:
                self.running = False
                sys.exit(0)

            elif ir == MUL:
                self.alu('MUL', operand_a, operand_b)
                self.pc += 3

            elif ir == ADD:
                self.alu('ADD', operand_a, operand_b)
                self.pc += 3

            elif ir == PUSH:
                self.reg[SP] -= 1

                # Get value from register
                value = self.reg[operand_a]

                # Store it on the stack
                top_of_stack_addr = self.reg[SP]
                self.ram[top_of_stack_addr] = value

                self.pc += 2

                # print(f"stack: {self.ram[0xE4:0xF4]}")

            elif ir == POP:
                # Get value from top of stack
                top_of_stack_addr = self.reg[SP]
                value = self.ram[top_of_stack_addr]

                # Get reg number and store value
                self.reg[operand_a] = value

                self.reg[SP] += 1

                self.pc += 2

            elif ir == CALL:
                # Push return address
                ret_addr = self.pc + 2
                self.reg[SP] -= 1
                self.ram[self.reg[SP]] = ret_addr

                # Call subroutine
                self.pc = self.reg[operand_a]

            elif ir == RET:
                # Pop return addr off the stack
                ret_addr = self.ram[self.reg[SP]]
                self.reg[SP] += 1

                # Set PC
                self.pc = ret_addr

            else:
                print('Instruction not found:', self.pc)
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


# class BranchTable:

#     def __init__(self):
#         self.branchtable = {}
#         self.branchtable[HLT] = self.handle_hlt
#         self.branchtable[LDI] = self.handle_ldi
#         self.branchtable[PRN] = self.handle_prn
#         self.branchtable[MUL] = self.handle_mul

#     def handle_hlt(self):
#         print("Halted")
#         self.running = False
#         sys.exit(0)

#     def handle_ldi(self):
#         self.reg

#     def handle_prn(self):
#         pass

#     def handle_mul(self):
#         self.alu('MUL', operand_a, operand_b)

#     def run(self):
#         ir = self.ram_read(self.pc)

    # Find a way to make more DRY?
    # figure out what arguments to include
    # how to incorporate with operands ? / rest of comment?
    # include a standardized something for cpu incrementing?
