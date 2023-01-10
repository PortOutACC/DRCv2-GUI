""" doc """
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from libcpu import DRCv2System


class App(QMainWindow):
    """ Application GUI setup & functionalities. """

    def __init__(self):
        super().__init__()

        # Initialize class fields.
        self.sys0 = None
        self.program = []
        self.total_clk = 0
        # Default program loaded on a startup.
        self.filename = "programs/mod_calc.a"
        self.old_mem_map = []

        # Run GUI setup.
        self.init_gui()

        # Create clock.
        self.clock = QTimer()
        self.clock.timeout.connect(self.step)

    def init_gui(self):
        """ Create application window """
        ######################
        # Create window elements.
        ######################

        # 1) Global.
        title = 'DRC v.2 computer system emulator'
        window = QWidget()

        # Main layout.
        layout0 = QHBoxLayout()

        dev_layout = QVBoxLayout()  # (devices)
        c_layout = QVBoxLayout()    # (central)
        cc_layout = QGridLayout()   # (clock controls)
        cons_layout = QGridLayout() # (console)

        # 2) Bar.
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')
        help_menu = menu_bar.addMenu('Help')

        # 3) Bar elements actions.
        load_rom = QAction('Load program', self)
        reset_system = QAction('Reset system', self)
        exit_program = QAction('Exit', self)
        help_ = QAction('Help', self)

        # 4) Clock controls.
        step_btn = QPushButton('Step', self)
        step_btn.setToolTip("Increment system clock only by one.")
        self.start_btn = QPushButton('Start', self)
        self.stop_btn = QPushButton('Stop', self)
        self.freq_box = QDoubleSpinBox(self)
        self.clk_count = QLineEdit(self)
        self.clk_count.setReadOnly(True)
        freq_lbl = QLabel(self)
        freq_lbl.setText("Frequency (Hz):")
        cc_lbl = QLabel(self)
        cc_lbl.setText("Clock controls")
        tcp_lbl = QLabel(self)
        tcp_lbl.setText("Clock ticks total:")

        # 5) Console.
        self.console_out = QLineEdit(self)
        self.console_out.setReadOnly(True)
        self.console_in = QLineEdit(self)
        enter_btn = QPushButton('Enter', self)
        enter_btn.setToolTip("Enter your input to console buffer.")
        console_lbl = QLabel(self)
        console_lbl.setText("Peripheral device 0x02 - console")
        console_i_lbl = QLabel(self)
        console_i_lbl.setText("Integer input:")
        console_o_lbl = QLabel(self)
        console_o_lbl.setText("Integer output:")

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

        ######################
        # Stack them together.
        ######################

        # 1) Global
        self.setCentralWidget(window)
        self.setWindowTitle(title)

        layout0.addLayout(dev_layout)
        layout0.addLayout(c_layout)
        layout0.addWidget(self.rom_table)

        window.setLayout(layout0)

        # 2) Devices layout.
        dev_layout.addLayout(cons_layout)
        dev_layout.addWidget(self.core_table)

        # 3) Clock controls layout.
        cc_layout.addWidget(cc_lbl, 0, 0, 1, 2)
        cc_layout.addWidget(freq_lbl, 1, 0)
        cc_layout.addWidget(self.freq_box, 1, 1)
        cc_layout.addWidget(self.start_btn, 2, 0)
        cc_layout.addWidget(self.stop_btn, 2, 1)
        cc_layout.addWidget(step_btn, 3, 0, 1, 2)
        cc_layout.addWidget(tcp_lbl, 4, 0)
        cc_layout.addWidget(self.clk_count, 4, 1)

        # 4) Console layout
        cons_layout.addWidget(console_lbl, 0, 0, 1, 2)
        cons_layout.addWidget(console_o_lbl, 1, 0,)
        cons_layout.addWidget(self.console_out, 1, 1)
        cons_layout.addWidget(console_i_lbl, 2, 0)
        cons_layout.addWidget(self.console_in, 2, 1)
        cons_layout.addWidget(enter_btn, 3, 0, 1, 2)

        # 5) Central layout
        c_layout.addLayout(cc_layout)
        c_layout.addWidget(self.reg_table)

        # 6) Bar
        file_menu.addAction(load_rom)
        file_menu.addAction(reset_system)
        file_menu.addAction(exit_program)
        help_menu.addAction(help_)


        ######################
        # Initial setup
        ######################
        self.setGeometry(100, 100, 600, 600)

        # Set max value for spinbox.
        self.freq_box.setMaximum(50)

        # Initialize spinbox with some reasonable value.
        self.freq_box.setValue(2)

        # Properly label memory table.
        tab = []
        for i in range(192):
            tab.append("cell " + str(i))
        self.core_table.setVerticalHeaderLabels(tab)
        self.core_table.setHorizontalHeaderLabels(["Core memory"])

        # Properly label ROM table.
        tab = []
        for i in range(256):
            tab.append(str(i))
        self.rom_table.setVerticalHeaderLabels(tab)
        self.rom_table.setHorizontalHeaderLabels(["Program memory"])

        # Properly label register table.
        tab = ["Zero", "General purpose 1", "General purpose 2",
               "General purpose 3", "General purpose 4", "General purpose 5",
               "General purpose 6", "Stack Pointer", "Program Counter",
               "Status"]
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
        # User input handling
        ######################

        # Actions.
        exit_program.triggered.connect(self.exit_program)
        reset_system.triggered.connect(self.reset)
        load_rom.triggered.connect(self.load)
        help_.triggered.connect(self.show_help)

        # Buttons.
        step_btn.clicked.connect(self.step)
        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        enter_btn.clicked.connect(self.cons_enter)

        ######################
        self.initialize_core()
        self.show()

    def cons_enter(self):
        """ Write user input into console buffer. """
        val = self.console_in.text()
        if val:
            val = int(val)
            self.sys0.devices[2].write(val)
        self.sys0.status_reg["wait_bit"] = False

    def load(self):
        """ Load program. """
        options = QFileDialog.Options()
        self.filename, _ = \
            QFileDialog.getOpenFileName(self,
                                        "Select file...", "", options=options)
        self.reset()
        self.update_contents()

    def start(self):
        """ Start clock. """
        period = (1/self.freq_box.value())*1000
        self.clock.start(int(period))

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop(self):
        """ Stop clock. """
        self.clock.stop()

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def step(self):
        """ Trigger one clock pulse. """
        self.sys0.get_next_state()
        self.update_contents()

        # But...
        if self.sys0.status_reg["halt_bit"] is True:
            self.stop()
        # Above is written to disable pointless clock ticking after halting.
        # It also lets the user know how long computation took.

    def reset(self):
        """ Reset system state. """
        del self.sys0
        self.total_clk = 0
        self.initialize_core()
        self.update_contents()

    def initialize_core(self):
        """ Start application back-end. """
        self.sys0 = DRCv2System()
        self.sys0.load_rom(self.filename)

        with open(self.filename, "r") as f:
            self.program = []
            for line in f:
                self.program.append(line.strip())

    def update_contents(self):
        """ Update back-end state with new parameters. """

        # Fill core memory table.
        # Display an arrow pointing to the top of the stack.
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
            tab.append(self.program[i])

        for i in range(len(tab)):
            self.rom_table.setItem(i, 0, QTableWidgetItem(tab[i]))

        self.rom_table.selectRow(self.sys0.program_counter)

        # Print out registers.
        for i in range(len(self.sys0.registers)):
            reg = str(self.sys0.registers[i])
            self.reg_table.setItem(i, 0, QTableWidgetItem(reg))
        pc_txt = str(self.sys0.program_counter)
        self.reg_table.setItem(8, 0, QTableWidgetItem(pc_txt))

        status_str = "h: "
        status_str += str(self.sys0.status_reg["halt_bit"])
        status_str += " c: "
        status_str += str(self.sys0.status_reg["carry_flag"])
        status_str += " z: "
        status_str += str(self.sys0.status_reg["zero_flag"])
        self.reg_table.setItem(9, 0, QTableWidgetItem(status_str))

        # Display console buffer contents.
        self.console_out.setText(str(self.sys0.devices[2].buffer[0]))

        # Display total clock cycles.
        self.clk_count.setText(str(self.total_clk))
        self.total_clk += 1

    def exit_program(self):
        """ Gracefully terminate app. """
        sys.exit(0)

    def show_help(self):
        """ Print out help file contents in a message box. """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Help")
        msg.setStandardButtons(QMessageBox.Ok)
        text_edit = QPlainTextEdit()
        text = open('spec.txt').read()
        text_edit.setPlainText(text)
        msg.setText(text)
        msg.exec_()


APP = QApplication(sys.argv)
ex = App()
APP.exec_()
