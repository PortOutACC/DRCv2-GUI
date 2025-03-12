""" doc """
from time import sleep
import sys
from PyQt5.QtWidgets import *
from libcpu import DRCv2System
from PyQt5.QtCore import QTimer


class App(QMainWindow):
    """ ewda """

    def __init__(self):
        super().__init__()

        self.run = False
        self.program = []
        self.total_clk = 0
        self.filename = "programs/mod_calc.a"
        self.old_mem_map = []

        ######################
        # Creation of window elements
        ######################
        # global
        title = 'DRC v.2 computer system emulator'
        window = QWidget()

        layout0 = QHBoxLayout()

        # devices column = QVBoxLayout()
        dev_layout = QVBoxLayout()
        # central column = QVBoxLayout()
        c_layout = QVBoxLayout()
        # controls area = QGridLayout()

        # Bar
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('File')

        # actions
        load_rom = QAction('Load program to ROM', self)
        reset_system = QAction('Reset system', self)
        exit_program = QAction('Exit', self)

        # Clock controls.
        step_btn = QPushButton('Step', self)
        self.start_btn = QPushButton('Start', self)
        self.stop_btn = QPushButton('Stop', self)
        self.freq_box = QDoubleSpinBox(self)
        self.clk_count = QLineEdit(self)

        # Console.
        self.console_out = QLineEdit(self)
        self.console_in = QLineEdit(self)
        enter_btn = QPushButton('Enter', self)

        # Core memory cell table.
        self.core_table = QTableWidget(self)
        self.core_table.setColumnCount(1)
        self.core_table.setRowCount(192)

        # Registers table.
        self.reg_table = QTableWidget(self)
        self.reg_table.setRowCount(10)  # 8 gpr-s, pc and status reg.
        self.reg_table.setColumnCount(1)

        # ROM table.
        self.rom_table = QTableWidget(self)
        self.rom_table.setRowCount(256)
        self.rom_table.setColumnCount(1)

        # Clock
        self.clock = QTimer()
        self.clock.timeout.connect(self.step)

        ######################
        # stacking them together
        ######################
        # Global
        self.setCentralWidget(window)
        self.setWindowTitle(title)

        layout0.addLayout(dev_layout)
        layout0.addLayout(c_layout)
        layout0.addWidget(self.rom_table)

        window.setLayout(layout0)

        # Devices layout.
        dev_layout.addWidget(self.console_out)
        dev_layout.addWidget(self.console_in)
        dev_layout.addWidget(enter_btn)
        dev_layout.addWidget(self.core_table)

        # Central layout.
        c_layout.addWidget(self.freq_box)
        c_layout.addWidget(self.start_btn)
        c_layout.addWidget(self.stop_btn)
        c_layout.addWidget(step_btn)
        c_layout.addWidget(self.clk_count)
        c_layout.addWidget(self.reg_table)

        # Bar
        fileMenu.addAction(load_rom)
        fileMenu.addAction(reset_system)
        fileMenu.addAction(exit_program)

        ######################
        # initial setup
        ######################
        self.setGeometry(100, 100, 600, 600)

        # set max value for spinbox.
        self.freq_box.setMaximum(50)

        # initialize spinbox with some reasonable value.
        self.freq_box.setValue(50)

        # Properly label memory table.
        tab = []
        for i in range(192):
            tab.append("cell " + str(i))
        self.core_table.setVerticalHeaderLabels(tab)
        self.core_table.setHorizontalHeaderLabels(["Core memory"])

        # Properly ROM table.
        tab = []
        for i in range(256):
            tab.append(str(i))
        self.rom_table.setVerticalHeaderLabels(tab)
        self.rom_table.setHorizontalHeaderLabels(["Program memory"])

        # Properly label register table.
        tab = ["R0", "R1", "R2", "R3", "R4", "R5", "R6", "SP", "PC", "ST"]
        self.reg_table.setVerticalHeaderLabels(tab)
        self.reg_table.setHorizontalHeaderLabels(["Registers"])

        # Resize register table.
        self.core_table.setColumnWidth(0, 117)
        self.reg_table.setColumnWidth(0, 166)
        self.rom_table.setColumnWidth(0, 145)


        # Set stop button as pushed down,
        # because initially there is nothing to stop.
        self.stop_btn.setEnabled(False)

        ######################
        # user input handling
        ######################
        exit_program.triggered.connect(self.exit_program)
        reset_system.triggered.connect(self.reset)
        load_rom.triggered.connect(self.load)

        step_btn.clicked.connect(self.step)
        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)

        enter_btn.clicked.connect(self.cons_enter)

        ######################

        self.initialize_core()
        self.show()

    ######################
    # methods
    ######################

    # Write user input into console buffer.
    def cons_enter(self):
        val = self.console_in.text()
        if val:
            val = int(val)
        #  if val != "":
            self.sys0.devices[2].write(val)
        self.sys0.status_reg["wait_bit"] = False

    # Load program.
    def load(self):
        options = QFileDialog.Options()
        self.filename, _ = QFileDialog.getOpenFileName(self,
                                "Select file...", "", options=options)
        self.reset()
        self.update_contents()

    # Start clock
    def start(self):
        period = (1/self.freq_box.value())*1000
        period = int(period)
        self.clock.start(period)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    # Stop clock.
    def stop(self):
        self.clock.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def step(self):
        self.sys0.get_next_state()
        #  if self.sys0.program_counter
        self.update_contents()
        if self.sys0.status_reg["halt_bit"] == True:
            self.stop()

    def reset(self):
        del self.sys0
        self.total_clk = 0
        self.initialize_core()
        self.update_contents()

    # initialize back-end
    def initialize_core(self):
        """ Start application back-end. """
        self.sys0 = DRCv2System()
        self.sys0.load_rom(self.filename)

        with open(self.filename, "r") as f:
            self.program = []
            for line in f:
                self.program.append(line.strip())

    # update contents
    def update_contents(self):
        """ Update back-end state with new parameters. """

        # Fill core memory table.
        mem_tab = []
        for i in range(64, 256):
            if self.sys0.registers[7] == i:
                mem_tab.append(str(self.sys0.devices[i].val) + "   <-- SP")
            else:
                mem_tab.append(str(self.sys0.devices[i].val))

        for i in range(len(mem_tab)):
            self.core_table.setItem(i, 0, QTableWidgetItem(mem_tab[i]))

        if self.sys0.last_written:
            last_written = self.sys0.last_written - 64
            self.core_table.selectRow(last_written)


        # Fill ROM display table.
        # Display an arrow pointing on the next instruction.
        tab = []
        for i in range(len(self.program)):
            #  if i == self.sys0.program_counter:
                #  tab.append(self.program[i] + "    <--")
            #  else:
            tab.append(self.program[i])

        for i in range(len(tab)):
            self.rom_table.setItem(i, 0, QTableWidgetItem(tab[i]))

        self.rom_table.selectRow(self.sys0.program_counter)

        # Print out registers.
        for i in range(len(self.sys0.registers)):
            self.reg_table.setItem(i, 0, QTableWidgetItem(str(self.sys0.registers[i])))
        self.reg_table.setItem(8, 0, QTableWidgetItem(str(self.sys0.program_counter)))

        status_str = "h: "
        status_str += str(self.sys0.status_reg["halt_bit"])
        status_str += " c: "
        status_str += str(self.sys0.status_reg["carry_flag"])
        status_str += " z: "
        status_str += str(self.sys0.status_reg["zero_flag"])
        self.reg_table.setItem(9, 0, QTableWidgetItem(status_str))

        # Resize register table.
        #  self.reg_table.resizeColumnsToContents()

        # Display console buffer contents.
        self.console_out.setText(str(self.sys0.devices[2].buffer[0]))

        # Display total clock cycles.
        self.clk_count.setText(f"Clock ticks: {self.total_clk}")
        self.total_clk += 1

    # exit
    def exit_program(self):
        """ Gracefully terminate app. """
        sys.exit(0)

    # Prompt user for console input.
    def prompt(self):
        val, ok = QInputDialog().getInt(self, "Console",
                                "Integer input:", QLineEdit.Normal)
        if ok and val:
            return(val)
        return(-1)  # if smth gone wrong


app = QApplication(sys.argv)
ex = App()
app.exec_()
