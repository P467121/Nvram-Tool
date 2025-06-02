import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import os
import subprocess
import sys, ctypes
import uuid
COLORS = {
    "bg": "#242424",
    "fg": "#f0f0f0",
    "inputbg": "#2e2e2e",
    "inputfg": "#ffffff",
    "selectbg": "#3a3a3a",
    "selectfg": "#ffffff",
    "buttonbg": "#333333",
    "buttonfg": "#f0f0f0",
    "framebg": "#2a2a2a",
    "textbg": "#2e2e2e",
    "textfg": "#f0f0f0"
}
def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
def run_as_admin():
    """Relaunch the script with administrator privileges."""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()  
class BIOSSetting:
    def __init__(self, setup_question, options=None, content=None):
        self.setup_question = setup_question
        self.help_string = None
        self.token = None
        self.offset = None
        self.width = None
        self.bios_default = None
        self.value = None
        self.options = options if options is not None else []  
        self.option_values = []  
        self.option_lines = []  
        self.active_option = None  
        self.content = content if content is not None else []  
        self.unique_id = str(uuid.uuid4())  
class SettingsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BIOS Settings Manager")
        self.changed_settings = []
        window_width = 1000
        window_height = 630
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(fg_color=COLORS["bg"])
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background=COLORS["textbg"],
            foreground=COLORS["textfg"],
            fieldbackground=COLORS["textbg"],
            rowheight=20
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["buttonbg"],
            foreground=COLORS["buttonfg"],
            font=("Hervetica", 9)
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["selectbg"])],
            foreground=[("selected", COLORS["selectfg"])]
        )
        style.configure(
            "TNotebook",
            background=COLORS["framebg"],
            tabmargins=0
        )
        style.configure(
            "TNotebook.Tab",
            background=COLORS["buttonbg"],
            foreground=COLORS["buttonfg"],
            padding=[10, 5],
            font=("Arial", 9)
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLORS["selectbg"]), ("active", COLORS["selectbg"])],
            foreground=[("selected", COLORS["selectfg"]), ("active", COLORS["selectfg"])]
        )
        self.settings = []
        self.filtered_settings = []
        self.filtered_predefined_settings = []
        self.original_lines = []
        self.current_file = None
        self.cpu = "unknown"
        self.selected_setting = None
        self.current_setting = None  
        self.current_unique_options = None  
        self.predefined_settings = {}
        self.predefined_settings_wifi = {
            "WAN Radio": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wi-Fi 6E for Japan": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "WWAN Participant": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "WWAN": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wifi Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wifi Core": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wi-Fi Core": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wireless CNV Config Device": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "WWAN Reset Workaround": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Onboard WAN Device": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wi-Fi Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_LTR_MECHANISM = {
            "LTR Mechanism Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_LTR = {
            "LTR": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_non_snoop_value = {
            "Non Snoop Latency Value": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_snoop_value = {
            "Snoop Latency Value": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_non_snoop_option = {
            "Non Snoop Latency Override": ['Manual', 'Enabled', 'Enable'],
        }
        self.predefined_settings_snoop_option = {
            "Snoop Latency Override": ['Manual', 'Enabled', 'Enable'],
        }
        self.predefined_settings_non_snoop_multiplier = {
            "Non Snoop Latency Multiplier": '1 ns',
        }
        self.predefined_settings_snoop_multiplier = {
            "Snoop Latency Multiplier": '1 ns',
        }
        self.predefined_settings_wifi_bluetooth = {
            "WAN Radio": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wi-Fi 6E for Japan": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Onboard CNVi Module Control": ['Disable Integrated', 'Disable', 'Disabled'],
            "CNVi mode": ['Disable Integrated', 'Disable', 'Disabled'],
            "WWAN Participant": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "WWAN": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wifi Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wifi Core": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wi-Fi Core": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wireless CNV Config Device": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "WWAN Reset Workaround": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Connectivity mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Onboard WAN Device": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BT Core": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Blue Tooth Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Bluetooth PLDR support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BT core": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Bluetooth": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Bluetooth Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Discrete Bluetooth Interface": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Bluetooth Sideband": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BT Intel HFP": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BT Intel A2DP": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BT Intel LE Audio": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Onboard CNVi Module Control": ['Disable Integrated', 'Disable', 'Disabled'],
            "CNVi Mode": ['Disable Integrated', 'Disable', 'Disabled'],
            "Connectivity mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_VMX = {
            "IGD VTD Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IPU VTD Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IOP VTD Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "VT-d": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Control IOMMU": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Intel (VMX) Virtualization Technology": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Intel Virtualization Technology": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_MonitorMWAIT = {
            "MonitorMWait": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_Speed_Shift = {
            "Intel Speed Shift Technology": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Intel(R) Speed Shift Technology": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_espi = {
            "ESPI Enable": ['Disabled', 'Disable', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_Thunderbolt= {
            "Windows 10 Thunderbolt support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Thunderbolt Add-in Card": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Thunderbolt Security Level": ["No Security",'0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'No Security'],
            "Thunderbolt Force PWR": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Thunderbolt Boot From TB": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Thunderbolt Boot From USB": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Thunderbolt Assign Resource": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Thunderbolt L1SS Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Thunderbolt Wake Up Command": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DTBT Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DTBT Controller 1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DTBT Controller 2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DTBT Controller 3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DTBT Controller 4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DTBT Controller 5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DTBT Controller 6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DTBT Controller 7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DTBT Controller 8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ITBT Root Port": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ITBT Root Port 1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ITBT Root Port 2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ITBT Root Port 3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ITBT Root Port 4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ITBT Root Port 5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ITBT Root Port 6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ITBT Root Port 7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ITBT Root Port 8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_TPM = {
            "Security Device Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_Memory_Scrambler = {
            "Memory Scrambler": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_Self_Refresh = {
            "SelfRefresh Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_UART= {
            "UART Test Device": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C Devices Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "GP_0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "GP_1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "GP_2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "GP_3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "GP_4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "GP_5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "GP_6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "GP_7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SPI0 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SPI1 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SPI2 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SPI3 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SPI4 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SPI5 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SPI6 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SPI7 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART0 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART1 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART2 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART3 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART4 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART5 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART6 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART7 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C0 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C1 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C2 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C3 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C4 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C5 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C6 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C7 Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_Turbo_boost= {
            "Intel Turbo Boost.": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Intel(R) Adaptive Boost Technology": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_IGPU= {
            "Internal Graphics": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_USBC= {
            "UCSI Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "USBC connector manager selection": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Disable UCSI Device'],
        }
        self.predefined_settings_D_Enhanced_Interleaving= {
            "Enhanced Interleave": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_E_Enhanced_Interleaving= {
            "Enhanced Interleave": ['Standard', 'Enabled', 'Enable'],
        }
        self.predefined_settings_PBR= {
            "Per Bank Refresh": ['Standard', 'Enabled', 'Enable'],
        }
        self.predefined_settings_VR_CONFIG= {
        }
        self.predefined_settings_Full_Screen_Logo= {
            "Full Screen LOGO Show": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Boot Logo Display": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_Speedstep= {
            "speedstep": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_VGA_Detection= {
            "VGA Detection": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
        }
        self.predefined_settings_HT= {
            "Hyper-Threading": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "Hyper Threading": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "Hyper-Threading of Core 0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "Hyper-Threading of Core 1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "Hyper-Threading of Core 2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "Hyper-Threading of Core 3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "Hyper-Threading of Core 4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "Hyper-Threading of Core 5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "Hyper-Threading of Core 6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "Hyper-Threading of Core 7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "Hyper-Threading of Core 8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "Hyper-Threading of Core 9": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "Per P-Core Hyper-Threading Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "P-Core 0 Hyper-Threading": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "P-Core 1 Hyper-Threading": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "P-Core 2 Hyper-Threading": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "P-Core 3 Hyper-Threading": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "P-Core 4 Hyper-Threading": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "P-Core 5 Hyper-Threading": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "P-Core 6 Hyper-Threading": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "P-Core 7 Hyper-Threading": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
            "SMT Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
        }
        self.predefined_settings_Optane= {
            "Intel(R) Optane(TM) Memory": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
        }
        self.predefined_settings_CLKASIG= {
            "Clock0 assignment": ['Disable', 'Disabled'],
            "Clock1 assignment": ['Disable', 'Disabled'],
            "Clock2 assignment": ['Disable', 'Disabled'],
            "Clock3 assignment": ['Disable', 'Disabled'],
            "Clock4 assignment": ['Disable', 'Disabled'],
            "Clock5 assignment": ['Disable', 'Disabled'],
            "Clock6 assignment": ['Disable', 'Disabled'],
            "Clock7 assignment": ['Disable', 'Disabled'],
            "Clock8 assignment": ['Disable', 'Disabled'],
            "Clock9 assignment": ['Disable', 'Disabled'],
            "Clock10 assignment": ['Disable', 'Disabled'],
            "Clock11 assignment": ['Disable', 'Disabled'],
            "Clock12 assignment": ['Disable', 'Disabled'],
            "Clock13 assignment": ['Disable', 'Disabled'],
            "Clock14 assignment": ['Disable', 'Disabled'],
            "Clock15 assignment": ['Disable', 'Disabled'],
            "Clock16 assignment": ['Disable', 'Disabled'],
            "Clock17 assignment": ['Disable', 'Disabled'],
        }
        self.predefined_settings_bluetooth = {
            "BT Core": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Blue Tooth Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Bluetooth PLDR support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BT core": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Bluetooth": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Bluetooth Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Discrete Bluetooth Interface": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Bluetooth Sideband": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BT Intel HFP": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BT Intel A2DP": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BT Intel LE Audio": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_sata = {
            "Sata0 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata1 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata2 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata3 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata4 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata5 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata6 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata7 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata8 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata0 eSATA Port0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata0 eSATA Port1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata0 eSATA Port2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata0 eSATA Port3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata0 eSATA Port4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata0 eSATA Port5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata0 eSATA Port6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata0 eSATA Port7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata0 eSATA Port8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata1 eSATA Port0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata1 eSATA Port1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata1 eSATA Port2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata1 eSATA Port3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata1 eSATA Port4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata1 eSATA Port5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata1 eSATA Port6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata1 eSATA Port7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata1 eSATA Port8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata2 eSATA Port0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata2 eSATA Port1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata2 eSATA Port2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata2 eSATA Port3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata2 eSATA Port4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata2 eSATA Port5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata2 eSATA Port6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata2 eSATA Port7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata2 eSATA Port8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata3 eSATA Port0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata3 eSATA Port1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata3 eSATA Port2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata3 eSATA Port3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata3 eSATA Port4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata3 eSATA Port5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata3 eSATA Port6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata3 eSATA Port7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata3 eSATA Port8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata4 eSATA Port0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata4 eSATA Port1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata4 eSATA Port2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata4 eSATA Port3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata4 eSATA Port4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata4 eSATA Port5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata4 eSATA Port6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata4 eSATA Port7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata4 eSATA Port8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata5 eSATA Port0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata5 eSATA Port1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata5 eSATA Port2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata5 eSATA Port3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata5 eSATA Port4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata5 eSATA Port5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata5 eSATA Port6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata5 eSATA Port7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata5 eSATA Port8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata6 eSATA Port0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata6 eSATA Port1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata6 eSATA Port2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata6 eSATA Port3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata6 eSATA Port4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata6 eSATA Port5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata6 eSATA Port6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata6 eSATA Port7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata6 eSATA Port8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata7 eSATA Port0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata7 eSATA Port1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata7 eSATA Port2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata7 eSATA Port3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata7 eSATA Port4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata7 eSATA Port5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata7 eSATA Port6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata7 eSATA Port7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata7 eSATA Port8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata8 eSATA Port0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata8 eSATA Port1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata8 eSATA Port2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata8 eSATA Port3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata8 eSATA Port4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata8 eSATA Port5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata8 eSATA Port6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata8 eSATA Port7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata8 eSATA Port8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata9 eSATA Port0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata9 eSATA Port1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata9 eSATA Port2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata9 eSATA Port3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata9 eSATA Port4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata9 eSATA Port5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata9 eSATA Port6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata9 eSATA Port7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata9 eSATA Port8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata0 (Socket1) Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata1 (Socket1) Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata2 (Socket1) Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata3 (Socket1) Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata4 (Socket1) Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata5 (Socket1) Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata6 (Socket1) Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata7 (Socket1) Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata8 (Socket1) Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "External SATA 6GB/s Controller Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Controller(s)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA0 port0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA0 port1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA0 port2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA0 port3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA0 port4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA0 port5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA0 port6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA0 port7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA0 port0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA1 port1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA1 port2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA1 port3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA1 port4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA1 port5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA1 port6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA1 port7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ESATA Port On Port 0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ESATA Port On Port 1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ESATA Port On Port 2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ESATA Port On Port 3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ESATA Port On Port 4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ESATA Port On Port 5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ESATA Port On Port 6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ESATA Port On Port 7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA SGPIO 0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA SGPIO 1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata0 SGPIO": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata1 SGPIO": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata2 SGPIO": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata3 SGPIO": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata4 SGPIO": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata5 SGPIO": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata6 SGPIO": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata7 SGPIO": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA PORT 0 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA PORT 1 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA PORT 2 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA PORT 3 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA PORT 4 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA PORT 5 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA PORT 6 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA PORT 7 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA PORT 8 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Port 0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Port 1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Port 2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Port 3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Port 4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Port 5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Port 6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Port 7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Port 8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PORT 0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PORT 1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PORT 2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PORT 3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PORT 4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PORT 5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PORT 6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PORT 7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PORT 8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA0 Hot Plug": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA1 Hot Plug": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA2 Hot Plug": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA3 Hot Plug": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA4 Hot Plug": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA5 Hot Plug": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA6 Hot Plug": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA7 Hot Plug": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA8 Hot Plug": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata Port 0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata Port 1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata Port 2": ['Disable', 'Disabled'],
            "Sata Port 3": ['Disable', 'Disabled'],
            "Sata Port 4": ['Disable', 'Disabled'],
            "Sata Port 5": ['Disable', 'Disabled'],
            "Sata Port 6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata Port 7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Port 8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Port 0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Port 1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Port 2": ['Disable', 'Disabled'],
            "SATA Port 3": ['Disable', 'Disabled'],
            "SATA Port 4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Port 5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Port 6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Port 7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Port 8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "T1 Multipler": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "T2 Multipler": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "T3 Multipler": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "T3 Multipler": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Chipset SATA Port Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Chipset SATA Port Hot Plug": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Thermal Setting": ['Manual', 'Disable', 'Disabled'],
        }
        self.predefined_settings_security = {
            "NX Mode": ['Standard', 'Enabled', 'Enable'],
            "Secure Boot Mode": ['Standard', 'Enabled', 'Enable'],
            "Execute Disable Bit": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Secure Boot": ['Enabled', 'Enable'],
            "SECURE BOOT": ['Enabled', 'Enable'],
            "Total Memory Encryption": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "AES": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ASF Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "TPM State": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "TCM State": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PTID Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BME DMA Mitigation": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Intel Trusted Execution Technology": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Intel Platform Trust Technology (PTT)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Intel Platform Trust Technology": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ACS": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PAVP Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Lock PCH Sideband Access": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Disable TBT PCIE Tree BME": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_clkreq = {
            "ClkReq for Clock0": ['Disable', 'Disabled'],
            "ClkReq for Clock1": ['Disable', 'Disabled'],
            "ClkReq for Clock2": ['Disable', 'Disabled'],
            "ClkReq for Clock3": ['Disable', 'Disabled'],
            "ClkReq for Clock4": ['Disable', 'Disabled'],
            "ClkReq for Clock5": ['Disable', 'Disabled'],
            "ClkReq for Clock6": ['Disable', 'Disabled'],
            "ClkReq for Clock7": ['Disable', 'Disabled'],
            "ClkReq for Clock8": ['Disable', 'Disabled'],
            "ClkReq for Clock9": ['Disable', 'Disabled'],
            "ClkReq for Clock10": ['Disable', 'Disabled'],
            "ClkReq for Clock11": ['Disable', 'Disabled'],
            "ClkReq for Clock12": ['Disable', 'Disabled'],
            "ClkReq for Clock13": ['Disable', 'Disabled'],
            "ClkReq for Clock14": ['Disable', 'Disabled'],
            "ClkReq for Clock15": ['Disable', 'Disabled'],
            "ClkReq for Clock16": ['Disable', 'Disabled'],
            "ClkReq for Clock17": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ0": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ1": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ2": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ3": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ4": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ5": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ6": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ7": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ8": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ9": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ10": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ11": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ12": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ13": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ14": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ15": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ16": ['Disable', 'Disabled'],
            "Clock PM: CLK_REQ17": ['Disable', 'Disabled']
        }
        self.predefined_settings_audio_intel = {
            "HD Audio Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "NB Azalia": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Audio Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "HDA Link": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "USB Audio Offload": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "HD Audio Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Onboard HDMI HD Audio": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Onboard HD Audio": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "HD Audio": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_audio_amd = {
            "HD Audio Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "NB Azalia": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Audio Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "HDA Link": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "USB Audio Offload": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "HD Audio Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Onboard HDMI HD Audio": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Onboard HD Audio": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "HD Audio": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_amd = {
            "Platform First Error Handling": ['0', 'False', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCIe ASPM Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "USB BT Remote Wakeup": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Thunderbolt Wake Up Command": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wake on LAN": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Power Loading": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PME Turn Off Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "USB Phy Power Down": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Platform Hierarchy": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "RGB Fusion": ['0', 'Off', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "LEDs in System Power On State": ['0', 'Off', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "LEDs in Sleep, Hibernation, and Soft Off States": ['0', 'Off', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Storage Hierarchy": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Endorsement Hierarchy": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wake on PME": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wake Up Event By": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "XHCI Hand-off": ['Enabled', 'Enable'],
            "Prochot VRM Throttling": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "AIM-T Support": ['AIM-T Disabled', 'Enabled', 'Enable'],
            "USB4 Non-Prefetch Memory Reserved": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Primary Video Adaptor": ['0', 'Ext Graphics (PEG)', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SB C1E Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PBO Limits": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "S3 PCIe Save Restore Mode": ['0', 'Both Disabled', 'Disable', 'Disabled'],
            "Integrated Graphics": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Power Slow Slew Rate": ['10 mV', 'Disable', 'Disabled'],
            "SMT Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SMT Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "iGPU Configuration": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Pluton Security Processor": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Device Sleep for AHCI Port 0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Device Sleep for AHCI Port 1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Device Sleep for AHCI Port 2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Device Sleep for AHCI Port 3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "NPU Deep Sleep Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SMT": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ECC": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UECC": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PX Dynamic Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IPv4 PXE Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IPv4 HTTP Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IPv6 PXE Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IPv6 HTTP Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Discrete GPU's Audio": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Adaptive S4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "LAN Power Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PM L1 SS": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Unused GPP Clocks Off": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Clock Power Management(CLKREQ#)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Clock Power Management": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Power Supply Idle Control": ['Typical Current Idle'],
            "Win7 USB Wake Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ACP Power Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ACP Clock Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ACP CLock Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DRAM Latency Enhance": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Power Down Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ECO Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "LN2 Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SoC/Uncore OC Mode": ['Enabled', 'Enable'],
            "LCLK DPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "LCLK DPM Enhanced PCIe Detection": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SMEE": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Global C-state Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ACPI _CST C1 Declaration": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Indirect Branch Prediction Speculation": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Fast Short REP MOVSB": ['Enabled', 'Enable'],
            "Memory interleaving": ['Auto', 'Enabled', 'Enable'],
            "Chipselect Interleaving": ['Auto', 'Enabled', 'Enable'],
            "Channel Interleaving": ['Auto', 'Enabled', 'Enable'],
            "Rank Interleaving": ['Auto', 'Enabled', 'Enable'],
            "MONITOR and MWAIT disable": ['Enabled', 'Enable'],
            "AVX512": ['Enabled', 'Enable'],
            "Enhanced REP MOVSB/STOSB": ['Enabled', 'Enable'],
            "REP-MOV/STOS Streaming": ['Enabled', 'Enable'],
            "Disable DF to external downstream IP SyncFloodPropagation": ['Sync flood disabled'],
            "Disable DF to external downstream IP Sync Flood Propagation": ['Sync flood disabled'],
            "Disable DF sync flood propagation": ['Sync flood disabled'],
            "Freeze DF module queues on error": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CC6 memory region encryption": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "AMD Cool&Quiet function": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'False'],
            "PSP error injection support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'False'],
            "MCA error thresh enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'False'],
            "Memory interleaving": ['Enabled', 'Enable'],
            "DRAM scrub time": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Data Scramble": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Poison scrubber control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Redirect scrubber control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "GMI encryption control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Memory Context Restore": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Pre-boot DMA Protection": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Kernel DMA Protection Indicator": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "xGMI encryption control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Data Poisoning": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "RCD Parity": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DRAM Address Command Parity Retry": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Write CRC Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DRAM Write CRC Enable and Retry Limit": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DRAM ECC Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Advanced Error Reporting (AER)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Advanced Error Reporting": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PSPP Policy": ['Disabled', 'Disable'],
            "D3Cold Support": ['Disabled', 'Disable'],
            "Discrete GPU D3Cold HPD Support": ['Disabled', 'Disable'],
            "Discrete GPU's Audio": ['Disabled', 'Disable'],
            "Discrete GPU's USB Port": ['Disabled', 'Disable'],
            "Discrete GPU D3Cold HPD Support": ['Disabled', 'Disable'],
            "Discrete GPU D3Cold HPD Support": ['Disabled', 'Disable'],
            "Discrete GPU D3Cold HPD Support": ['Disabled', 'Disable'],
            "Discrete GPU D3Cold HPD Support": ['Disabled', 'Disable'],
            "Discrete GPU D3Cold HPD Support": ['Disabled', 'Disable'],
            "Discrete GPU D3Cold HPD Support": ['Disabled', 'Disable'],
            "Bootup NumLock State": ['Off', 'Disabled', 'Disable'],
            "DRAM UECC Retry": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Above 4G Decoding": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BankGroupSwap": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BankSwapMode": ['Swap APU', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BankGroupSwapAlt": ['Enabled', 'Enable'],
            "Address Hash Bank": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Address Hash CS": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Address Hash Rm": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Address Hash Subchannel": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IOMMU": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DMA Protection": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DMAr Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ACS Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enable AER Cap": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ErP": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SRIS": ['Enabled', 'Enable'],
            "Determinism Control": ['Manual'],
            "Determinism Slider": ['Power'],
            "APBDIS": ['1'],
            "SmartShift Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCIe Power Management Features": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DF Cstates": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Fixed SOC Pstate": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPPC": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPPC Preferred Cores": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "NBIO SyncFlood Generation": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "NBIO SyncFlood Reporting": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Log Poison Data from SLINK": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Edpc Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ALink RAS Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BIOS Mode": ['OC Genie Mode'],
            "CPU temperature Warning Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "System Power Fault Protection": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Resume By RTC Alarm": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Resume By PCI-E Device": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Resume By Onboard Intel LAN": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Resume By USB Device": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Resume From S3/S4/S5 By PS/2 Mouse": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Resume From S3/S4/S5 By PS/2 keyboard": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Re-Size BAR Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ASPM Control for CPU": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "S3/Modern Standby Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "HPET": ['Enabled', 'Enable'],
            "DRAM map inversion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SVM Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SVM Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Latency Under Load (LUL)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Latency Under Load": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "FCH Spread Spectrum": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SB Clock Spread Spectrum": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Spread Spectrum": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Spread Spectrum Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Opcache Control": ['Enabled', 'Enable'],
            "TSME": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ACPI Standby State": ['Disabled', 'Suspend Disabled'],
            "ASPM Mode Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PPC Adjustment": ['PState 0'],
            "SR-IOV Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ASPM Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCIB Clock Run": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Int. Clk Differential Spread": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Slumber State Capability": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SB Clock Spread Spectrum": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ACPI SLIT remote relative distance": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SPD Read Optimization": ['Near'],
            "PCIe Ten Bit Tag Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "NBIO DPM Control": ['Manual'],
            "NBIO Poison Consumption": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "NBIO RAS Global Control": ['Manual'],
            "NBIO RAS Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sata RAS Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Aggressive SATA Device Sleep Port 0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Aggressive SATA Device Sleep Port 1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Socket1 DevSlp0 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Socket1 DevSlp1 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Chipset Power Saving Features": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SecureBio Camera Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SecureBio Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ACPI SRAT L3 Cache As NUMA Domain": ['Enabled', 'Enable'],
            "Periodic Directory Rinse": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PSS Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "AB Clock Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enable Hibernation": ['0', 'Disabled'],
            "4-link xGMI max speed": ['25Gbps'],
            "3-link xGMI max speed": ['25Gbps'],
            "xGMI Link Width Control": ['Manual'],
            "xGMI Force Link Width": ['2'],
            "xGMI Force Link Width Control": ['Force'],
            "xGMI Max Link Width Control": ['Manual'],
            "xGMI Max Link Width": ['1'],
            "Option ROM Messages": ['Keep Current'],
            "Socket 0 NBIO 0 Target DPM Level": ['2'],
            "Socket 0 NBIO 1 Target DPM Level": ['2'],
            "Socket 0 NBIO 2 Target DPM Level": ['2'],
            "Aggresive SATA Device Sleep Port 0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Aggresive SATA Device Sleep Port 1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Aggresive SATA Device Sleep Port 2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Aggresive SATA Device Sleep Port 3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Aggresive SATA Device Sleep Port 4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Aggresive SATA Device Sleep Port 5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Aggresive SATA Device Sleep Port 6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Aggresive SATA Device Sleep Port 7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Socket 0 NBIO 3 Target DPM Level": ['2'],
            "Socket 1 NBIO 0 Target DPM Level": ['2'],
            "Socket 1 NBIO 1 Target DPM Level": ['2'],
            "Socket 1 NBIO 2 Target DPM Level": ['2'],
            "Socket 1 NBIO 3 Target DPM Level": ['2'],
            "Core Watchdog Timer Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Maximum Payload": ['Auto'],
            "Maximum Read Request": ['Auto'],
            "Streaming Stores Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "D3 Cold Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C 0 D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C 1 D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C 2 D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C 3 D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C 4 D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I2C 5 D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART 0 D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART 1 D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART 2 D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UART 3 D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPPC CTRL": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Mode": ['AHCI'],
            "Sata Mode": ['AHCI Mode', 'AHCI'],
            "SATA Auto Shutdown": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "EHCI D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "XHCI D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SD D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Internal PCIe GPP 0 D3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SOC GPU D3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SOC HD Audio D3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SOC USB3.1 D3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SOC ACP D3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SOC Azalia D3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Internal PCIe GPP 2 D3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SOC USB2.0 D3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SOC USB3.1 for USB4 D3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SOC USB4 D3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Internal USB4 PCIe Tunneling D3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SOC USB4 PCIe Endpoint D3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ACPI D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ACPI Sleep State": ['Disabled', 'Suspend Disabled'],
        }
        self.predefined_settings_intel = {
            "ACPI Debug": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ALS Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ARI Forwarding": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "AVX2": ['Enabled', 'Enable'],
            "Above 4G Decoding": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Active LFP": "No eDP",
            "Active Trip Point 0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Active Trip Point 1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Aggressive LPM Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "AtomicOp Egress Blocking": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "AtomicOp Requester Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Audio DSP": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BCLK Amplitude": "900mV",
            "BCLK Slew Rate": "Fast",
            "BCLK Spread Spectrum": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BIOS Hot-Plug Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BIOS Lock": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BT Audio Offload": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Boot from Network Devices": "Ignore",
            "Boot from Storage Devices": "Ignore",
            "C-State Un-demotion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "C-state Pre-Wake": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "C6DRAM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CDR Relock for CPU DMI": ['Enabled', 'Enable'],
            "CPU C-states": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPU Graphics Current Capability": "140%",
            "CPU Power Duty Control": "Extreme",
            "CPU Power Phase Control": "Extreme",
            "CPU Temp Read": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPU Temperature LED Switch": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CTO": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Cache Dynamic OC Switcher": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Camera1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Camera2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Camera3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Camera4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Camera5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Camera6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Configure GT for use": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Connectivity mode (Wi-Fi & Bluetooth)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Control Iommu Pre-boot Behavior": "Disable IOMMU",
            "Cooler Efficiency Customize": "Stop Training",
            "Core Bios Done Message": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Core Ratio Extension Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Core VR Fast Vmode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CrashLog GPRs": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "D3 Setting for Storage": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DMA Control Guarantee": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DMI Thermal Sensor Autonomous Width": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DMIC #0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DMIC #1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DTBT Controller 0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DTBT RTD3 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DeepSx Wake on WLAN and BT Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Disable PROCHOT# Output": ['Enabled', 'Enable'],
            "Discrete Thunderbolt(TM) Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Display Enter Setup Hotkey String": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Dynamic Memory Boost": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enable ClockReq Messaging": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enable Display Audio Link in Pre-OS": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enable Hibernation": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enable Tools Interface": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enable VMD controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Energy Efficient P-state": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enhance Port 80h LPC Decoding": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enhanced C-states": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Erase All": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "FLL OC mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Fine Granularity Refresh mode": ['Enabled', 'Enable'],
            "Finger Print Sensor": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Flash Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Foxville I225 Wake on LAN Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "GT VR Fast Vmode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "HECI Message check Disable": ['Enabled', 'Enable'],
            "Hot Plug": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "I/O Resources Padding": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IDO Completion Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IDO Request Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IPU Device (B0:D5:F0)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IPv4 HTTP Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IPv4 PXE Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IPv6 HTTP Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IPv6 PXE Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ISH Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ITBT Root Port 0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Intel Rapid Recovery Technology": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Intel(R) SpeedStep(tm)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Intel(R) Turbo Boost Max Technology 3.0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Launch Video OPROM policy": "Ignore",
            "Legacy USB Support": "Auto",
            "Link Training Retry": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "MMIO 32 bit Resources Padding": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "MRC Fast Boot": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "MRC Memory Scrubbing": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Machine Check": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Max Power Saving": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Mechanical Presence Switch": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "New Features 1 - MRC": ['Enabled', 'Enable'],
            "New Features 2 - MRC": ['Enabled', 'Enable'],
            "Next Boot after AC Power Loss": "Normal Boot",
            "PCH FIVR Participant": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCI Buses Padding": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCI Express Native Power Management": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCIE Resizable BAR Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCIE/DMI Amplitude": "900mV",
            "PCIE/DMI Slew Rate": "Fast",
            "PCIE/DMI Spread Spectrum": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PET Progress": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PFMMIO 32 bit Resources Padding": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PFMMIO 64 bit Resources Padding": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PMAX Audio codec": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PMAX Object": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "POST Delay Time": "0 sec",
            "PROCHOT Lock": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PROCHOT Response": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PTID Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Package C-State Un-demotion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Panel Scaling": ['0',"Off", 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Passive Trip Point": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Per Core P State OS control mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Port8xh Decode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Processor trace": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Pseudo G3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "RAID0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "RAID1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "RAID10": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "RAID5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "RP08 D3 cold Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "RRT volumes can span internal and eSATA drives": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "RTC Memory Lock": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Race To Halt (RTH)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Realtime Memory Frequency": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Realtime Memory Timing": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Regulate Frequency by above Threshold": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Repair Type": "Do Not Repair",
            "Resize BAR Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Retrain on Fast Fail": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Runtime BCLK OC": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SA VR Fast Vmode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Port 0 DevSlp": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Port 1 DevSlp": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Port 2 DevSlp": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Port 3 DevSlp": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Port 4 DevSlp": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Port 5 DevSlp": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Port 6 DevSlp": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA Port 7 DevSlp": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA6G_1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA6G_1 Hot Plug": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA6G_1(Gray)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA6G_2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA6G_2 Hot Plug": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA6G_2(Gray)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA6G_3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA6G_3 Hot Plug": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA6G_3(Gray)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA6G_4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SATA6G_4 Hot Plug": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SECE": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SEFE": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SENFE": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SLP_LAN# Low on DC Power": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SMART Self Test": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SNDW #1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SNDW #2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SNDW #3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SNDW #4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SPD Write Disable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', "True"],
            "SPI_0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SSP #0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SSP #1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SSP #2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SSP #3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SSP #4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SSP #5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Scan Matrix Keyboard Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sensor Device 2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sensor Device 3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sensor Device 4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Sensor Device 5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "TVB Ratio Clipping": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Tcc Offset Clamp Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Thermal Device (B0:D4:F0)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Thermal Sensor 0 Width": "x16",
            "Thermal Sensor 1 Width": "x16",
            "Thermal Sensor 2 Width": "x16",
            "Thermal Sensor 3 Width": "x16",
            "Three Strike Counter": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Thunderbolt Boot Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Touch Panel": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UFS Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "USB Audio": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "USB Sensor Hub": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "USB power delivery in Soft Off state (S5)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "USB4/TBT Boot Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Unlimited ICCMAX": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Unpopulated Links": "Keep Link ON",
            "VRM Initialization Check": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Intel(R) Speed Shift Technology Interrupt Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ACPI Standby State": 'Suspend Disabled',
            "Power Down Mode": ['Disabled', 'No Power Down'],
            "VRM Spread Spectrum": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ACPI T-States": ['0', 'Disabled', 'Disable'],
            "ACPI D3Cold Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ACPI D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ACPI Sleep State": ['Disabled', 'Suspend Disabled'],
            "Active Trip Points": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Acoustic Noise Mitigation": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "AP Threads Idle Manner": ['RUN Loop'],
            "ARTG Object": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Bi-Directional PROCHOT": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Bi-directional PROCHOT#": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BCLK Aware Adaptive Voltage": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPU Enhanced Halt(C1E)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPU Enhanced Halt": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPU Run Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Above 4G Decoding": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPU Run Control Lock": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPU C6 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPU C7 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "C0 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "C1 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "C2 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "C3 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "C States": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Clock Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Command Tristate": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "C-State Auto Demotion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "C-State Un-Demotion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CState Pre-Wake": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPU C-States": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "C10 Dynamic threshold adjustment": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPU VRM Thermal Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPU Current Capability": ['140%'],
            "CPU Current Reporting": ['100%'],
            "CPU Thermal Throttling": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Clock Power Management": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Critical Trip Points": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "C6Dram": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "AVX512": ['Enabled', 'Enable'],
            "Core CEP Enabled": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Core Voltage Suspension": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Deep Sleep": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Disable DSX ACPRESENT PullDown": ['Enabled', 'Enable'],
            "D3 Setting for storage": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DMI ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DMI Thermal Setting": ['0', 'Disable', 'Disabled', 'No Constraint', 'Manual'],
            "DMI Gen3 ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Dual Tau Boost": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Disable Fast PKG C State Ramp for IA Domain": ['TRUE', 'Enabled', 'Enable'],
            "Disable Fast PKG C State Ramp for GT Domain": ['TRUE', 'Enabled', 'Enable'],
            "Disable Fast PKG C State Ramp for SA Domain": ['TRUE', 'Enabled', 'Enable'],
            "Disable VR Thermal Alert": ['Enabled', 'Enable'],
            "DTBT Go2Sx Command": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "D0I3 Setting for HECI Disable": ['Enabled', 'Enable'],
            "EC Low Power Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "EC Notification": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "EC CS Debug Light": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "EPG DIMM Idd3N": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "EPG DIMM Idd3P": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Energy Efficient Turbo": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enhanced C-States": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Energy Performance Gain": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Energy Efficient P-State": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "EIST": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enable 8254 Clock Gate": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enable All Thermal Functions": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enable ClockReq Messeging": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enhanced Halt State(C1E)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "LPM S0i2.0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "LPM S0i2.1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "LPM S0i3.0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "LPM S0i2.2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "LPM S0i3.2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "LPM S0i3.3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "LPM S0i3.4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "EDPC": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "GT CEP Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "GT CEP Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "GT CEP Support                   En": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "GT CEP Support For 14th": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "GT CEP Support For 14th          En": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "GT CEP": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "HDC Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "HwP Lock": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCI Delay Optimization": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "HwP Autonomous Per Core P State": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "HwP Autonomous EPP Grouping": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Intel C-State": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Intel Speed-Shift Technology": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "vC1 Read Metering": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "INT3400 Device": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ITBT RTD3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IA CEP Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IA CEP Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IA CEP Support                   En": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IA CEP Support                   Dis": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IA CEP Support For 14th": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IA CEP Support For 14th          En": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IA CEP": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IA SoC Iccmax Reactive Protector": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Inverse Temperature Dependency Throttle": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "JTAG C10 Power Gate": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "L1 Substates": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "L1 Low": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "LPMode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Low Power S0 Idle Capability": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "LPM S0i2.0USB2PHY Sus Well Power Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Legacy IO Low Latency": ['Enabled', 'Enable'],
            "Native PCIE Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Native ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Max Power Savings Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Memory Thermal Management": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "OS IDLE Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "S0i": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "S0ix Auto Demotion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "USB2PHY Sus Well Power Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Number of Stop Grant Cycles": ['1'],
            "Package C State Limit": ['C0/C1'],
            "Package C State limit": ['C0/C1'],
            "DDR PowerDown and idle counter": ['PCODE'],
            "For LPDDR Only: DDR PowerDown and idle counter": ['PCODE'],
            "PCIE Native Power Management": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCIE Express Native Power Management": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Processor Thermal Device": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Package Power Limit MSR Lock": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PS3 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PS4 Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PMAX object": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PMAX Device": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PMAX audio codec": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PMAX WF Camera": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PMAX UF Camera": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PMAX Flash device": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Package C-State Demotion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Package C-State Un-Demotion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Passive Trip Points": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCH ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCH Energy Reporting": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCIE Clock Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCH Cross Throttling": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEG ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP CPU": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP Graphics": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP IPU": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP GNA": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP SATA": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP enumerated SATA ports": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP PCIe Storage": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP PCIe LAN": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP PCIe WLAN": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP PCIe GFX": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP PCIe Other": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP UART": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP I2C0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP I2C1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP I2C2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP I2C3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP I2C4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP I2C5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP I2C6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP I2C7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP SPI": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP XHCI": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP Audio": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP CSME": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP HECI3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP LAN(GBE)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP THC0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP THC1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP TCSS": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP VMD": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PEP EMMC": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCI Express Power Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCI Express Clock Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PUIS Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PECI": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PS_ON Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Pcie Pll SSC": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Power Down Unused Lanes": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Power Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Platform Power Management": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Power Loading": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PSMI": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PPCC Object": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Per Core P state os control mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Prochot Response": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Prochot Lock": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Race to Halt": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "RC6(Render Standby)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "RSR": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Regulate Freaquency by above threshold": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Suspend to RAM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SA CEP": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "VC1 Read Metering": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Tcc Offset Lock Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Tcc OFfset Clamp Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "TDC Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Thermal Throttling Level": ['Manual'],
            "ZPODD": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Touch Pad": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Fine Granularity Refresh": ['Enabled', 'Enable'],
            "MWAIT Redirection": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "RFI Spread Spectrum": ['0.5%'],
            "SA GV": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "MC Refresh Rate": '4x Refresh',
            "Row Hammer Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Row Hammer Prevention": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Throttler CKEMin Defeature": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "For LPDDR Only: Throttler CKEMin Defeature": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SelfRefresh Idletimer": '65535',
            "RFI Mitigation": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DLVR RFI Mitigation": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SelfRefresh Idletimer": '65535',
            "ECC Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Password Protection of Runtime Variables": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Publish HLL Resources": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Advanced Error Reporting": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Auto Driver Installer": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BCLK Spread Spectrum Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BCLK TSC HW Fixup": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "BCLK Trimmer": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Boot Performance Mode": ['Turbo Performance'],
            "CER": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPU Energy Read": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DPC": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "EDPC": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "NFER": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "RGB Light": ['0', 'Off', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "OBFF": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PME SCI": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "FER": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "URR": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ACS": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPU Thermal Monitor": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CrashLog Feature": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CrashLog PMC Rearm": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CrashLog PMC Clear": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CrashLog Cdie Rearm": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CrashLog On All Reset": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CRB Test": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CFG Lock": ['Enabled', 'Enable'],
            "CSE Data Resilience Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Completion Timeout": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPU CrashLog": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Cpu CrashLog (Device 10)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PowerDown Energy Ch0Dimm0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PowerDown Energy Ch1Dimm0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PowerDown Energy Ch0Dimm1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PowerDown Energy Ch1Dimm1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Core BIOS Done Message": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Passive TC1 Value": ['1'],
            "Bootup NumLock State": ['Off', 'Disabled', 'Disable'],
            "Passive TC2 Value": ['1'],
            "Passive TSP Value": ['32'],
            "Stop Grant Configuration": ['Manual'],
            "Tcc Activation Offset": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPU Replace Polling Disable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Deep Sx Wake on WLAN and BT Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DPC": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "DMA Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Dma Control Guarantee": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enhanced Thermal Velocity Boost": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enhanced TVB": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "End Of Post Message": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enhanced Turbo": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enable xdpclock": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enable VMD Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Enable VMD Global Mapping": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Fast Boot": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "MSI Fast Boot": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "FER": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "FIVR Spread Spectrum": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "FCLK Frequency for Early Power On": ['1GHz'],
            "GNA Device": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "CPU Replaced Polling Disable": ['Enabled', 'Enable'],
            "EC Polling Period": ['255'],
            "HECI Message Check Disable": ['Enabled', 'Enable'],
            "Hardware Autonomous Width": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Hardware Autonomous Speed": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Hardware Flow Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Intel Thermal Velocity Boost Voltage Optimizations": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Interrupt Redirection Mode Selection": ['Round robin'],
            "IPU Device": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "ISH Controler": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "HECI Timeouts": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "IOAPIC 24-119 Entries": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "LAN Wake From DeepSx": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Legacy Game Compatibility Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Maximum Payload": ['Auto'],
            "Legacy UART": ['0', 'Disabled'],
            "Maximum Read Request": ['Auto'],
            "MBP HOB Skip": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Network Stack": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "KT Device": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Network Stack Driver Support": ['Disabled', 'Disable Link'],
            "NFER": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "OBFF": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCH Trace Hub Enable Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PCI-X Latency Timer": ['32 PCI Bus Clocks'],
            "PCIE Tunneling over USB4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PMC Debug Message Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Port 60/64 Emulation": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Port 61h Bit-4 emulation": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Processor Trace": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PS2 Devices Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "PS2 Keyboard and mouse": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Power Loss Notification Feature": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Pet Progress": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Ring Down Bin": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Ring Down Bin                    En": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SLP_LAN# Low On DC Power": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Serial Debug Messages": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SA PLL Frequency": ['3200MHz', '3200 MHz'],
            "SA PLL Frequency Override": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', '3200 MHz'],
            "PCH Temp Read": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SMM MSR Save State Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SMM Processor Trace": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SMM Use Block Indication": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SMM Use Delay Indication": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SMM Use SMM en-US Indication": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "SPD Write Disabled": ['TRUE'],
            "Spread Spectrum": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "USB Overcurrent": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "USB Overcurrent Lock": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Show Memory Prompt Message": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "TVB Ratio Clipping      En": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "TVB Ratio Clipping Enhanced      En": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "TVB Ratio Clipping Enhanced": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "TVB Voltage Optimizations": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "TVB Voltage Optimizations        En": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Option ROM Messages": ['Keep Current'],
            "WDT Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "WRC Feature": ['Enabled', 'Enable'],
            "Wake On Touch": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wake on LAN Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wake on WLAN and BT Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Wake From Thunderbolt(TM) Devices": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Overclocking TVB": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Thermal Velocity Boost": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Thermal Monitor": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "UnderVolt Protection": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "URR": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "USB DbC Enable Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "USB Power Delivery in Soft Off state": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "USB S5 Wakeup Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "USB3 Type-C UFP2DFP Kernel/Platform Debug Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "VMD": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "WoV (Wake On Voice)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "VMD Peripherals": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "VMD Mapped to CPU": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "VTd Mapped to CPU": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Voltage Adjust": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "Voltage Response": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "WWAN Wakeup": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "WWAN": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "WWAN": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "P-state Capping": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
            "XHCI Hand-off": ['Enabled', 'Enable'],
            "[*]Power Down Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        }
        self.predefined_settings_time_unit = {
            "Time Unit": '1 ns',
        }
        self.predefined_settings_active_ltr = {
            "Active LTR": '80008000',
        }
        self.predefined_settings_idle_ltr = {
            "Idle LTR": '80008000',
        }
        self.predefined_settings_force_ltr_override = {
            "Force LTR Override": ['Enabled', 'Enable'],
        }
        self.checkbox_vars = {}
        self.intel_checkbox_to_settings = {
            "Intel Settings": self.predefined_settings_intel,
            "Wi-Fi Settings": self.predefined_settings_wifi,
            "Bluetooth Settings": self.predefined_settings_bluetooth,
            "SATA Settings": self.predefined_settings_sata,
            "Security Settings": self.predefined_settings_security,
            "CLKREQ Settings": self.predefined_settings_clkreq,
            "Audio Settings": self.predefined_settings_audio_intel,
            "Wi-Fi Bluetooth Settings": self.predefined_settings_wifi_bluetooth,
            "VMX Settings": self.predefined_settings_VMX,
            "Monitor MWAIT Settings": self.predefined_settings_MonitorMWAIT,
            "Speed Shift Settings": self.predefined_settings_Speed_Shift,
            "Thunderbolt Settings": self.predefined_settings_Thunderbolt,
            "TPM Settings": self.predefined_settings_TPM,
            "Memory Scrambler Settings": self.predefined_settings_Memory_Scrambler,
            "Self Refresh Settings": self.predefined_settings_Self_Refresh,
            "UART Settings": self.predefined_settings_UART,
            "Turbo Boost Settings": self.predefined_settings_Turbo_boost,
            "IGPU Settings": self.predefined_settings_IGPU,
            "USBC Settings": self.predefined_settings_USBC,
            "D Enhanced Interleaving Settings": self.predefined_settings_D_Enhanced_Interleaving,
            "E Enhanced Interleaving Settings": self.predefined_settings_E_Enhanced_Interleaving,
            "PBR Settings": self.predefined_settings_PBR,
            "VR CONFIG Settings": self.predefined_settings_VR_CONFIG,
            "Full Screen Logo Settings": self.predefined_settings_Full_Screen_Logo,
            "Speedstep Settings": self.predefined_settings_Speedstep,
            "VGA Detection Settings": self.predefined_settings_VGA_Detection,
            "HT Settings": self.predefined_settings_HT,
            "Optane Settings": self.predefined_settings_Optane,
            "CLKASIG Settings": self.predefined_settings_CLKASIG,
            "LTR Settings": self.predefined_settings_LTR,
            "LTR Mechanism": self.predefined_settings_LTR_MECHANISM,
            "Time Unit Settings": self.predefined_settings_time_unit,
            "Force LTR Settings": self.predefined_settings_force_ltr_override,
            "Snoop Latency Value": self.predefined_settings_snoop_value,
            "Non Snoop Latency Value": self.predefined_settings_non_snoop_value,
            "Snoop Latency Multiplier": self.predefined_settings_snoop_multiplier,
            "Non Snoop Latency Multiplier": self.predefined_settings_non_snoop_multiplier,
            "Snoop Latency Option": self.predefined_settings_snoop_option,
            "Non Snoop Latency Option": self.predefined_settings_non_snoop_option,
            "Idle LTR Settings": self.predefined_settings_idle_ltr,
            "Active LTR Settings": self.predefined_settings_active_ltr,
        }
        self.amd_checkbox_to_settings = {
            "AMD Settings": self.predefined_settings_amd,
            "ESPI Settings": self.predefined_settings_espi,
            "Audio Settings": self.predefined_settings_audio_amd,
        }
        self.priority_values = {
            "Memory Interleaving": "enable"  
        }
        self.re_comment = re.compile(r'//.*$')
        self.re_setup_question = re.compile(r'^Setup Question\s*=\s*(.*)')
        self.re_help_string = re.compile(r'^Help String\s*=\s*(.*)')
        self.re_token = re.compile(r'^Token\s*=\s*(.*)')
        self.re_offset = re.compile(r'^Offset\s*=\s*(.*)')
        self.re_width = re.compile(r'^Width\s*=\s*(.*)')
        self.re_bios_default = re.compile(r'^BIOS Default\s*=\s*(.*)')
        self.re_value = re.compile(r'^Value\s*=\s*(.*)')
        self.re_options = re.compile(r'^Options\s*=\s*(.*)')
        self.create_widgets()
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS["framebg"], corner_radius=10)
        main_frame.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)
        self.title_label = ctk.CTkLabel(
            main_frame,
            text="BIOSTool",
            font=("Arial", 16, "bold"),
            text_color=COLORS["fg"],
            fg_color=COLORS["framebg"]
        )
        self.title_label.pack(pady=(10, 10))
        search_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["framebg"], corner_radius=0)
        search_frame.pack(fill=ctk.X, padx=5, pady=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._filter_settings)
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            fg_color=COLORS["inputbg"],
            text_color=COLORS["inputfg"],
            font=("Arial", 12),
            corner_radius=5,
            border_width=0
        )
        search_entry.pack(fill=ctk.X, padx=5, pady=5)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=ctk.BOTH, expand=True, padx=5, pady=(5, 5))
        tab1_frame = ctk.CTkFrame(notebook, fg_color=COLORS["framebg"])
        notebook.add(tab1_frame, text="List Editor")
        listbox_frame = ctk.CTkFrame(tab1_frame, fg_color=COLORS["textbg"])
        listbox_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=False, padx=(0, 5), ipadx=5, ipady=5)
        scrollbar1 = tk.Scrollbar(listbox_frame)
        scrollbar1.pack(side=tk.RIGHT, fill=tk.Y)
        self.settings_list = ttk.Treeview(
            listbox_frame,
            columns=("Setting", "Value"),
            show="",  
            yscrollcommand=scrollbar1.set,
            selectmode="browse",
            height=20
        )
        self.settings_list.column("Setting", width=300, stretch=True)  
        self.settings_list.column("Value", width=100, anchor="w", stretch=False)  
        self.settings_list.pack(fill=tk.BOTH, expand=True)
        scrollbar1.config(command=self.settings_list.yview)
        style = ttk.Style()
        style.configure("Treeview", 
                        background=COLORS["textbg"],
                        foreground=COLORS["textfg"],
                        fieldbackground=COLORS["textbg"],
                        font=("Arial", 12))
        style.map("Treeview",
                  background=[("selected", COLORS["selectbg"])],
                  foreground=[("selected", COLORS["selectfg"])])
        style.configure("Treeview", highlightthickness=0, bd=0)
        self.settings_list.bind('<<TreeviewSelect>>', self._on_setting_select)
        right_frame = ctk.CTkFrame(tab1_frame, fg_color=COLORS["framebg"])
        right_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=(5, 0))
        self.details_frame = ctk.CTkFrame(right_frame, fg_color=COLORS["textbg"], corner_radius=5)
        self.details_frame.pack(fill=ctk.BOTH, expand=True, padx=5, pady=(0, 5))
        self.details_label = ctk.CTkLabel(
            self.details_frame,
            text="Details",
            font=("Arial", 12, "bold"),
            text_color=COLORS["fg"]
        )
        self.details_label.pack(anchor="w", padx=5, pady=(5, 0))
        self.details_text = tk.Text(
            self.details_frame,
            bg=COLORS["textbg"],
            fg=COLORS["textfg"],
            font=("Arial", 12),
            relief=tk.FLAT,
            height=10,
            wrap=tk.WORD
        )
        self.details_text.pack(fill=ctk.BOTH, expand=True, padx=5, pady=(0, 5))
        self.details_text.config(state="disabled")
        self.options_frame = ctk.CTkFrame(right_frame, fg_color=COLORS["textbg"], corner_radius=5)
        self.options_frame.pack(fill=ctk.X, padx=5, pady=(5, 0))
        self.options_label = ctk.CTkLabel(
            self.options_frame,
            text="Options",
            font=("Arial", 12, "bold"),
            text_color=COLORS["fg"]
        )
        self.options_label.pack(anchor="w", padx=5, pady=(5, 0))
        self.option_var = tk.StringVar(value="No options available")
        self.option_button = tk.Menubutton(
            self.options_frame,
            textvariable=self.option_var,
            relief=tk.FLAT,
            bg=COLORS["inputbg"],
            fg=COLORS["inputfg"],
            activebackground=COLORS["selectbg"],
            activeforeground=COLORS["selectfg"],
            font=("Arial", 12),
            anchor="w"
        )
        self.option_button.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.option_button.bind("<Button-1>", self._on_option_button_click)
        tab2_frame = ctk.CTkFrame(notebook, fg_color=COLORS["framebg"])
        notebook.add(tab2_frame, text="BIOS Config")
        listbox_frame = ctk.CTkFrame(tab2_frame, fg_color=COLORS["textbg"])
        listbox_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=False, padx=(0, 5), ipadx=5, ipady=5)
        scrollbar2 = tk.Scrollbar(listbox_frame)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        self.predefined_settings_list = ttk.Treeview(
            listbox_frame,
            columns=("Setting", "ValueDOCKER"),
            show="",  
            yscrollcommand=scrollbar2.set,
            selectmode="browse",
            height=20
        )
        self.predefined_settings_list.column("Setting", width=300, stretch=True)
        self.predefined_settings_list.column("ValueDOCKER", width=100, anchor="w", stretch=False)
        self.predefined_settings_list.pack(fill=tk.BOTH, expand=True)
        scrollbar2.config(command=self.predefined_settings_list.yview)
        self.predefined_settings_list.bind('<<TreeviewSelect>>', self._on_predefined_setting_select)
        right_frame = ctk.CTkFrame(tab2_frame, fg_color=COLORS["framebg"])
        right_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=(5, 0))
        tabs_frame = ctk.CTkFrame(right_frame, fg_color=COLORS["framebg"])
        tabs_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        buttons_frame = ctk.CTkFrame(right_frame, fg_color=COLORS["framebg"], width=120)
        buttons_frame.pack(side=ctk.RIGHT, fill=ctk.Y, padx=(5, 0))
        self.nested_notebook = ttk.Notebook(tabs_frame)  
        self.nested_notebook.pack(fill=ctk.BOTH, expand=True)
        intel_frame = ctk.CTkFrame(self.nested_notebook, fg_color=COLORS["framebg"])
        self.nested_notebook.add(intel_frame, text="Intel")
        amd_frame = ctk.CTkFrame(self.nested_notebook, fg_color=COLORS["framebg"])
        self.nested_notebook.add(amd_frame, text="AMD")
        select_all_button = ctk.CTkButton(
            buttons_frame,
            text="Select All",
            command=self._select_all,
            fg_color=COLORS["buttonbg"],
            text_color=COLORS["buttonfg"],
            hover_color=COLORS["selectbg"],
            font=("Arial", 11)
        )
        select_all_button.pack(fill=ctk.X, padx=5, pady=5)
        deselect_button = ctk.CTkButton(
            buttons_frame,
            text="Deselect",
            command=self._deselect,
            fg_color=COLORS["buttonbg"],
            text_color=COLORS["buttonfg"],
            hover_color=COLORS["selectbg"],
            font=("Arial", 11)
        )
        deselect_button.pack(fill=ctk.X, padx=5, pady=5)
        invert_button = ctk.CTkButton(
            buttons_frame,
            text="Invert Select",
            command=self._invert_select,
            fg_color=COLORS["buttonbg"],
            text_color=COLORS["buttonfg"],
            hover_color=COLORS["selectbg"],
            font=("Arial", 11)
        )
        invert_button.pack(fill=ctk.X, padx=5, pady=5)
        safe_config_button = ctk.CTkButton(
            buttons_frame,
            text="Safe Config",
            command=self._safe_config,
            fg_color=COLORS["buttonbg"],
            text_color=COLORS["buttonfg"],
            hover_color=COLORS["selectbg"],
            font=("Arial", 11)
        )
        safe_config_button.pack(fill=ctk.X, padx=5, pady=5)
        def create_scrollable_checkboxes(parent_frame, checkbox_dict, tab_prefix):
            canvas = tk.Canvas(parent_frame, bg=COLORS["framebg"], highlightthickness=0)
            scrollbar = tk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=canvas.yview,
                                    bg=COLORS["framebg"], troughcolor=COLORS["bg"])
            checkbox_frame = ctk.CTkFrame(canvas, fg_color=COLORS["framebg"])
            canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            canvas.create_window((0, 0), window=checkbox_frame, anchor="nw")
            def update_scroll_region(event=None):
                canvas.configure(scrollregion=canvas.bbox("all"))
            checkbox_frame.bind("<Configure>", update_scroll_region)
            checkboxes = list(checkbox_dict.keys())
            num_rows = (len(checkboxes) + 1) // 2  
            for i in range(num_rows):
                if i < len(checkboxes):
                    label = checkboxes[i]
                    var = tk.BooleanVar(value=False)
                    self.checkbox_vars[f"{tab_prefix}_{label}"] = var  
                    checkbox = ctk.CTkCheckBox(
                        checkbox_frame,
                        text=label,
                        variable=var,
                        command=self._update_predefined_settings,
                        fg_color=COLORS["buttonbg"],
                        text_color=COLORS["buttonfg"],
                        font=("Arial", 11),
                        hover_color=COLORS["selectbg"],
                        width=180,
                        height=20,
                        checkbox_width=18,
                        checkbox_height=18
                    )
                    checkbox.grid(row=i, column=0, sticky="w", padx=5, pady=2)
                second_idx = i + num_rows
                if second_idx < len(checkboxes):
                    label = checkboxes[second_idx]
                    var = tk.BooleanVar(value=False)
                    self.checkbox_vars[f"{tab_prefix}_{label}"] = var  
                    checkbox = ctk.CTkCheckBox(
                        checkbox_frame,
                        text=label,
                        variable=var,
                        command=self._update_predefined_settings,
                        fg_color=COLORS["buttonbg"],
                        text_color=COLORS["buttonfg"],
                        font=("Arial", 11),
                        hover_color=COLORS["selectbg"],
                        width=180,
                        height=20,
                        checkbox_width=18,
                        checkbox_height=18
                    )
                    checkbox.grid(row=i, column=1, sticky="w", padx=5, pady=2)
            checkbox_frame.grid_columnconfigure(0, weight=1)
            checkbox_frame.grid_columnconfigure(1, weight=1)
            def on_mouse_wheel(event):
                if canvas.winfo_containing(event.x_root, event.y_root) == canvas:
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            parent_frame.bind("<MouseWheel>", on_mouse_wheel)
        create_scrollable_checkboxes(intel_frame, self.intel_checkbox_to_settings, "intel")
        create_scrollable_checkboxes(amd_frame, self.amd_checkbox_to_settings, "amd")
        button_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["framebg"], corner_radius=0)
        button_frame.pack(fill=ctk.X, padx=5, pady=(5, 0))
        scewin_button = ctk.CTkButton(
            button_frame,
            text="SCEWIN Export",
            command=self._scewin_export,
            fg_color=COLORS["buttonbg"],
            text_color=COLORS["buttonfg"],
            font=("Arial", 12),
            corner_radius=5,
            hover_color=COLORS["selectbg"]
        )
        scewin_button.pack(side=ctk.LEFT, padx=5)
        load_button = ctk.CTkButton(
            button_frame,
            text="Load File",
            command=self._load_file,
            fg_color=COLORS["buttonbg"],
            text_color=COLORS["buttonfg"],
            font=("Arial", 12),
            corner_radius=5,
            hover_color=COLORS["selectbg"]
        )
        load_button.pack(side=ctk.LEFT, padx=5)
        save_button = ctk.CTkButton(
            button_frame,
            text="Save File",
            command=self._save_file,
            fg_color=COLORS["buttonbg"],
            text_color=COLORS["buttonfg"],
            font=("Arial", 12),
            corner_radius=5,
            hover_color=COLORS["selectbg"]
        )
        save_button.pack(side=ctk.LEFT, padx=5)
        apply_button = ctk.CTkButton(
            button_frame,
            text="Apply Config",
            command=self._apply_config,
            fg_color=COLORS["buttonbg"],
            text_color=COLORS["buttonfg"],
            font=("Arial", 12),
            corner_radius=5,
            hover_color=COLORS["selectbg"]
        )
        apply_button.pack(side=ctk.LEFT, padx=50)
        self.count_label = ctk.CTkLabel(
            button_frame,
            text="0 settings",
            font=("Arial", 12),
            text_color=COLORS["textfg"],
            fg_color=COLORS["framebg"]
        )
        self.count_label.pack(side=ctk.RIGHT, padx=10)
    def _update_predefined_settings(self):
        self.predefined_settings.clear()
        for label, var in self.checkbox_vars.items():
            if var.get():  
                clean_label = label.split('_', 1)[1] if '_' in label else label
                settings_list = None
                if clean_label in self.intel_checkbox_to_settings:
                    settings_list = self.intel_checkbox_to_settings[clean_label]
                elif clean_label in self.amd_checkbox_to_settings:
                    settings_list = self.amd_checkbox_to_settings[clean_label]
                if settings_list:
                    self.predefined_settings.update(settings_list)
        self._populate_settings_list(self.search_var.get())
    def _get_current_tab_prefix(self):
        """Get the prefix ('intel' or 'amd') of the currently active tab."""
        current_tab = self.nested_notebook.select()
        tab_name = self.nested_notebook.tab(current_tab, "text").lower()
        return tab_name  
    def _get_current_checkbox_dict(self):
        """Get the checkbox dictionary for the currently active tab."""
        tab_prefix = self._get_current_tab_prefix()
        return self.intel_checkbox_to_settings if tab_prefix == "intel" else self.amd_checkbox_to_settings
    def _invert_select(self):
        """Invert the selection state of all checkboxes in the current tab."""
        tab_prefix = self._get_current_tab_prefix()
        checkbox_dict = self._get_current_checkbox_dict()
        for label in checkbox_dict.keys():
            var = self.checkbox_vars.get(f"{tab_prefix}_{label}")
            if var:
                var.set(not var.get())
        self._update_predefined_settings()
    def _select_all(self):
        """Select all checkboxes in the current tab."""
        tab_prefix = self._get_current_tab_prefix()
        checkbox_dict = self._get_current_checkbox_dict()
        for label in checkbox_dict.keys():
            var = self.checkbox_vars.get(f"{tab_prefix}_{label}")
            if var:
                var.set(True)
        self._update_predefined_settings()
    def _deselect(self):
        """Deselect all checkboxes in the current tab."""
        tab_prefix = self._get_current_tab_prefix()
        checkbox_dict = self._get_current_checkbox_dict()
        for label in checkbox_dict.keys():
            var = self.checkbox_vars.get(f"{tab_prefix}_{label}")
            if var:
                var.set(False)
        self._update_predefined_settings()
    def _safe_config(self):
        """Apply a safe configuration by selecting a subset of checkboxes."""
        tab_prefix = self._get_current_tab_prefix()
        checkbox_dict = self._get_current_checkbox_dict()
        safe_intel_settings = [
            "Wi-Fi Settings",
            "Audio Settings",
            "TPM Settings",
            "Memory Scrambler Settings",
            "Speedstep Settings"
        ]
        safe_amd_settings = [
            "Wi-Fi Settings",
            "Speedstep Settings",
            "HT Settings"
        ]
        safe_settings = safe_intel_settings if tab_prefix == "intel" else safe_amd_settings
        for label in checkbox_dict.keys():
            var = self.checkbox_vars.get(f"{tab_prefix}_{label}")
            if var:
                var.set(label in safe_settings)
        self._update_predefined_settings()
    def _on_option_button_click(self, event):
        if self.current_setting and self.current_unique_options:
            self._show_scrollable_menu(self.current_setting, self.current_unique_options)
    def _show_scrollable_menu(self, setting, unique_options):
        menu_window = tk.Toplevel(self.root)
        menu_window.overrideredirect(True)
        menu_window.configure(bg=COLORS["inputbg"])
        button_x = self.option_button.winfo_rootx()
        button_y = self.option_button.winfo_rooty() + self.option_button.winfo_height()
        menu_width = self.options_frame.winfo_width()
        menu_height = min(len(unique_options) * 25, 200)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        if button_x + menu_width > screen_width:
            button_x = screen_width - menu_width
        if button_y + menu_height > screen_height:
            menu_height = screen_height - button_y - 10
        menu_window.geometry(f"{menu_width}x{menu_height}+{button_x}+{button_y}")
        menu_frame = tk.Frame(menu_window, bg=COLORS["inputbg"])
        menu_frame.pack(fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(menu_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox = tk.Listbox(
            menu_frame,
            yscrollcommand=scrollbar.set,
            bg=COLORS["inputbg"],
            fg=COLORS["inputfg"],
            selectbackground=COLORS["selectbg"],
            selectforeground=COLORS["selectfg"],
            font=("Arial", 12),
            relief=tk.FLAT,
            highlightthickness=0
        )
        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        for opt in unique_options:
            listbox.insert(tk.END, opt)
        if setting.active_option is not None and 0 <= setting.active_option < len(setting.options):
            active_opt = setting.options[setting.active_option]
            match = re.match(r'^\[([^\]]+)\](.*)$', active_opt)
            display_text = match.group(2).strip() if match else active_opt
            try:
                active_index = unique_options.index(display_text)
                listbox.selection_set(active_index)
                listbox.see(active_index)
            except ValueError:
                pass
        def on_select(event):
            if listbox.curselection():
                selected = listbox.get(listbox.curselection()[0])
                self.option_var.set(selected)
                idx = setting.options.index(next(opt for opt in setting.options if selected in opt))
                self._update_option(setting, idx)
                menu_window.destroy()
        listbox.bind("<<ListboxSelect>>", on_select)
        def close_menu(event):
            if event.widget not in [listbox, menu_window]:
                menu_window.destroy()
        menu_window.bind("<Button-1>", close_menu)
        listbox.focus_set()
    def _apply_config(self):
        update_count = 0
        disable_variants = {'disabled', 'disable', 'no constraint', 'suspend disabled'}
        
        for setting in self.filtered_predefined_settings:
            if setting.setup_question not in self.predefined_settings:
                continue
            target_values = self.predefined_settings[setting.setup_question]
            current_value = ""
            if setting.options and setting.active_option is not None:
                active_opt = setting.options[setting.active_option]
                match = re.match(r'^\[([^\]]+)\](.*)$', active_opt)
                current_value = match.group(2).strip() if match else active_opt
            elif setting.value is not None:
                current_value = setting.value
            current_value_normalized = current_value.strip().lower() if current_value else ""
            if isinstance(target_values, list):
                if setting.options:
                    matching_options = []
                    for target in target_values:
                        target_normalized = target.strip().lower()
                        if target_normalized.endswith('d'):
                            target_normalized_alt = target_normalized[:-1]
                        else:
                            target_normalized_alt = target_normalized + 'd'
                        for idx, opt in enumerate(setting.options):
                            match = re.match(r'^\[([^\]]+)\](.*)$', opt)
                            display_text = match.group(2).strip() if match else opt
                            display_text_normalized = display_text.lower()
                            if (display_text_normalized == target_normalized or
                                    display_text_normalized == target_normalized_alt):
                                matching_options.append((target, idx))
                                break
                    
                    if not matching_options:
                        continue
                    
                    priority_value = self.priority_values.get(setting.setup_question)
                    if priority_value:
                        priority_value_normalized = priority_value.lower()
                        if priority_value_normalized.endswith('d'):
                            priority_value_normalized_alt = priority_value_normalized[:-1]
                        else:
                            priority_value_normalized_alt = priority_value_normalized + 'd'
                        
                        current_is_priority = (
                            current_value_normalized == priority_value_normalized or
                            current_value_normalized == priority_value_normalized_alt
                        )
                        
                        priority_option_idx = None
                        for target, opt_idx in matching_options:
                            target_normalized = target.lower()
                            if (target_normalized == priority_value_normalized or
                                    target_normalized == priority_value_normalized_alt):
                                priority_option_idx = opt_idx
                                break
                        
                        if priority_option_idx is not None:
                            if not current_is_priority:
                                setting.active_option = priority_option_idx
                                update_count += 1
                                if setting not in self.changed_settings:
                                    self.changed_settings.append(setting)
                        else:
                            _, first_opt_idx = matching_options[0]
                            if setting.active_option != first_opt_idx:
                                setting.active_option = first_opt_idx
                                update_count += 1
                                if setting not in self.changed_settings:
                                    self.changed_settings.append(setting)
                    else:
                        current_target_idx = -1
                        for idx, (target, opt_idx) in enumerate(matching_options):
                            target_normalized = target.strip().lower()
                            if target_normalized.endswith('d'):
                                target_normalized_alt = target_normalized[:-1]
                            else:
                                target_normalized_alt = target_normalized + 'd'
                            if (current_value_normalized == target_normalized or
                                    current_value_normalized == target_normalized_alt):
                                current_target_idx = idx
                                break
                        
                        if current_target_idx >= 0:
                            next_target_idx = (current_target_idx + 1) % len(matching_options)
                            _, next_opt_idx = matching_options[next_target_idx]
                        else:
                            _, next_opt_idx = matching_options[0]
                        
                        if setting.active_option != next_opt_idx:
                            setting.active_option = next_opt_idx
                            update_count += 1
                            if setting not in self.changed_settings:
                                self.changed_settings.append(setting)
                
                else:
                    use_brackets = False
                    if setting.value and re.match(r'^<.*>$', setting.value.strip()):
                        use_brackets = True

                    for target in target_values:
                        target_clean = target.strip()
                        target_normalized = target_clean.lower()
                        try:
                            if target_clean.startswith("0x"):
                                new_value_int = int(target_clean, 16)
                            else:
                                new_value_int = int(target_clean)
                            new_value = f"<{new_value_int}>" if use_brackets else str(new_value_int)
                        except ValueError:
                            is_target_disable = target_normalized in disable_variants
                            new_value_int = 0 if is_target_disable else 1
                            new_value = f"<{new_value_int}>" if use_brackets else str(new_value_int)

                        if setting.value != new_value:
                            setting.value = new_value
                            update_count += 1
                            if setting not in self.changed_settings:
                                self.changed_settings.append(setting)
                            break
            else:
                target_value_normalized = target_values.strip().lower()
                if current_value_normalized != target_value_normalized:
                    if setting.options:
                        for idx, opt in enumerate(setting.options):
                            match = re.match(r'^\[([^\]]+)\](.*)$', opt)
                            display_text = match.group(2).strip() if match else opt
                            if display_text.lower() == target_value_normalized:
                                if setting.active_option != idx:
                                    setting.active_option = idx
                                    update_count += 1
                                    if setting not in self.changed_settings:
                                        self.changed_settings.append(setting)
                                break
                    else:
                        if setting.setup_question in ["Active LTR", "Idle LTR"]:
                            new_value = target_values
                            if setting.value != new_value:
                                setting.value = new_value
                                update_count += 1
                                if setting not in self.changed_settings:
                                    self.changed_settings.append(setting)
                        else:
                            use_brackets = False
                            if setting.value and re.match(r'^<.*>$', setting.value.strip()):
                                use_brackets = True
                            
                            try:
                                next_numeric_value = int(target_values, 16)
                                new_value = f"<{next_numeric_value}>" if use_brackets else str(next_numeric_value)
                            except ValueError:
                                is_target_disable = target_value_normalized in disable_variants
                                next_numeric_value = 0 if is_target_disable else 1
                                new_value = f"<{next_numeric_value}>" if use_brackets else str(next_numeric_value)
                            
                            if setting.value != new_value:
                                setting.value = new_value
                                update_count += 1
                                if setting not in self.changed_settings:
                                    self.changed_settings.append(setting)
        
        self._populate_settings_list(self.search_var.get())
        
        if update_count > 0:
            messagebox.showinfo("Success", f"Updated {update_count} setting(s).")
        else:
            messagebox.showinfo("Info", "No predefined settings needed updating or no matching values were found.")
    def _scewin_export(self):
        try:
            current_dir = os.path.dirname(resource_path(__file__))
            os.chdir(current_dir)
            for driver in ["amifldrv64.sys", "amigendrv64.sys"]:
                driver_path = resource_path(driver)
                if not os.path.exists(driver_path):
                    messagebox.showerror("Error", f"{driver} not found in the application directory")
                    return
            scewin_path = resource_path("SCEWIN_64.exe")
            result = subprocess.run(
                [scewin_path, "/o", "/s", "nvram.txt"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            nvram_file = os.path.join(current_dir, "nvram.txt")
            if not os.path.exists(nvram_file):
                error_msg = result.stderr.decode('utf-8') if result.stderr else "Unknown error"
                messagebox.showerror("Error", f"nvram.txt not generated: {error_msg}")
                return
            self.current_file = nvram_file
            self.is_exported = True
            self.settings.clear()
            self.settings_list.delete(*self.settings_list.get_children())
            self.predefined_settings_list.delete(*self.predefined_settings_list.get_children())
            self.option_var.set("No options available")
            self.current_setting = None
            self.current_unique_options = None
            self.details_text.config(state="normal")
            self.details_text.delete(1.0, tk.END)
            self.details_text.config(state="disabled")
            self.selected_setting = None
            with open(nvram_file, 'r', encoding='ansi') as f:
                self.original_lines = f.readlines()
            current_setting = None
            def finalize_setting(s: BIOSSetting):
                if s is not None:
                    if s.options is None:
                        s.options = []
                    if len(s.options) == 1 and s.active_option is None:
                        s.value = s.options[0]
                        s.options = []
                    self.settings.append(s)
            re_bracket_option = re.compile(r'^\**\[(.*?)\](.*)')
            for raw_line in self.original_lines:
                line = self.re_comment.sub('', raw_line).strip()
                if not line:
                    continue
                match_setup = self.re_setup_question.match(line)
                if match_setup:
                    finalize_setting(current_setting)
                    current_setting = BIOSSetting(
                        setup_question=match_setup.group(1).strip(),
                        options=[],
                        content=[]
                    )
                    continue
                if not current_setting:
                    continue
                if (match := self.re_help_string.match(line)):
                    current_setting.help_string = match.group(1).strip()
                    continue
                if (match := self.re_token.match(line)):
                    current_setting.token = match.group(1).strip()
                    continue
                if (match := self.re_offset.match(line)):
                    current_setting.offset = match.group(1).strip()
                    continue
                if (match := self.re_width.match(line)):
                    current_setting.width = match.group(1).strip()
                    continue
                if (match := self.re_bios_default.match(line)):
                    current_setting.bios_default = match.group(1).strip()
                    continue
                if (match := self.re_options.match(line)):
                    remainder = match.group(1).strip()
                    self._parse_options_line(remainder, current_setting, re_bracket_option)
                    continue
                if (match := self.re_value.match(line)):
                    current_setting.value = match.group(1).strip()
                    continue
                if re_bracket_option.match(line):
                    self._parse_options_line(line, current_setting, re_bracket_option)
                    continue
                current_setting.content.append(line)
            finalize_setting(current_setting)
            self._populate_settings_list()
            for setting in self.settings:
                if 'intel' in setting.setup_question.lower():
                    self.title_label.configure(text="BIOSTool [Intel]")
                    self.cpu = "intel"
                    break
                elif 'amd' in setting.setup_question.lower():
                    self.title_label.configure(text="BIOSTool [AMD]")
                    self.cpu = "amd"
                    break
            else:
                self.title_label.configure(text="BIOSTool")
                self.cpu = "unknown"
        except Exception as e:
            messagebox.showerror("Error", f"SCEWIN export failed: {str(e)}")
    def _load_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filename:
            return
        self.current_file = filename
        self.is_exported = False
        self.settings.clear()
        self.changed_settings.clear()  
        self.settings_list.delete(*self.settings_list.get_children())
        self.predefined_settings_list.delete(*self.predefined_settings_list.get_children())
        try:
            with open(filename, 'r', encoding='ansi') as f:
                self.original_lines = f.readlines()
            current_setting = None
            def finalize_setting(s: BIOSSetting):
                if s is not None:
                    if s.options is None:
                        s.options = []
                    if len(s.options) == 1 and s.active_option is None:
                        s.value = s.options[0]
                        s.options = []
                    self.settings.append(s)
            re_bracket_option = re.compile(r'^\**\[(.*?)\](.*)')
            for raw_line in self.original_lines:
                line = self.re_comment.sub('', raw_line).strip()
                if not line:
                    continue
                match_setup = self.re_setup_question.match(line)
                if match_setup:
                    finalize_setting(current_setting)
                    current_setting = BIOSSetting(
                        setup_question=match_setup.group(1).strip(),
                        options=[],
                        content=[]
                    )
                    continue
                if not current_setting:
                    continue
                match_help = self.re_help_string.match(line)
                if match_help:
                    current_setting.help_string = match_help.group(1).strip()
                    continue
                match_token = self.re_token.match(line)
                if match_token:
                    current_setting.token = match_token.group(1).strip()
                    continue
                match_off = self.re_offset.match(line)
                if match_off:
                    current_setting.offset = match_off.group(1).strip()
                    continue
                match_wid = self.re_width.match(line)
                if match_wid:
                    current_setting.width = match_wid.group(1).strip()
                    continue
                match_def = self.re_bios_default.match(line)
                if match_def:
                    current_setting.bios_default = match_def.group(1).strip()
                    continue
                match_opt = self.re_options.match(line)
                if match_opt:
                    remainder = match_opt.group(1).strip()
                    self._parse_options_line(remainder, current_setting, re_bracket_option)
                    continue
                match_val = self.re_value.match(line)
                if match_val:
                    val = match_val.group(1).strip()
                    current_setting.value = val
                    continue
                bracket_line = re_bracket_option.match(line)
                if bracket_line:
                    self._parse_options_line(line, current_setting, re_bracket_option)
                    continue
                current_setting.content.append(line)
            finalize_setting(current_setting)
            self._populate_settings_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    def _get_unique_filename(self, base_path, filename="nvmod.txt"):
            """Generate a unique filename by appending (n) if the file exists."""
            filepath = os.path.join(base_path, filename)
            if not os.path.exists(filepath):
                return filepath
            base, ext = os.path.splitext(filename)
            counter = 1
            while True:
                new_filename = f"{base} ({counter}){ext}"
                new_filepath = os.path.join(base_path, new_filename)
                if not os.path.exists(new_filepath):
                    return new_filepath
                counter += 1
    def _parse_options_line(self, line: str, setting: BIOSSetting, re_bracket_option):
        match = re_bracket_option.match(line)
        if not match:
            return
        option_value = f"[{match.group(1)}]{match.group(2).strip()}"
        clean_option = option_value.lstrip('*')
        if clean_option not in setting.options:
            setting.options.append(clean_option)
            setting.option_values.append(match.group(1))
            setting.option_lines.append(line)
            if line.startswith('*') and setting.active_option is None:
                setting.active_option = len(setting.options) - 1
    def _populate_settings_list(self, filter_text: str = ''):
        self.settings_list.delete(*self.settings_list.get_children())
        self.filtered_settings = []
        for setting in self.settings:
            if filter_text.lower() in setting.setup_question.lower():
                self.filtered_settings.append(setting)
                display_value = ""
                if setting.options and setting.active_option is not None and 0 <= setting.active_option < len(setting.options):
                    active_opt = setting.options[setting.active_option]
                    match = re.match(r'^\[([^\]]+)\](.*)$', active_opt)
                    display_value = match.group(2).strip() if match else active_opt
                elif setting.value is not None:
                    display_value = setting.value
                self.settings_list.insert("", tk.END, values=(setting.setup_question, display_value))
        self.predefined_settings_list.delete(*self.predefined_settings_list.get_children())
        self.filtered_predefined_settings = []
        for setting in self.settings:
            if setting.setup_question in self.predefined_settings and filter_text.lower() in setting.setup_question.lower():
                self.filtered_predefined_settings.append(setting)
                display_value = ""
                if setting.options and setting.active_option is not None and 0 <= setting.active_option < len(setting.options):
                    active_opt = setting.options[setting.active_option]
                    match = re.match(r'^\[([^\]]+)\](.*)$', active_opt)
                    display_value = match.group(2).strip() if match else active_opt
                elif setting.value is not None:
                    display_value = setting.value
                self.predefined_settings_list.insert("", tk.END, values=(setting.setup_question, display_value))
        if self.cpu == "unknown":
            self.count_label.configure(text=f"{len(self.filtered_settings)} settings")
        else:
            self.count_label.configure(text=f"in {self.cpu} BIOS found {len(self.filtered_settings)} settings")
    def _filter_settings(self, *args):
        self._populate_settings_list(self.search_var.get())
    def _on_setting_select(self, event):
        selection = self.settings_list.selection()
        if not selection:
            return
        selected_item = selection[0]
        index = self.settings_list.index(selected_item)
        if index >= len(self.filtered_settings):
            return
        setting = self.filtered_settings[index]
        self.selected_setting = setting
        for widget in self.options_frame.winfo_children():
            if widget != self.options_label:
                widget.pack_forget()
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete('1.0', tk.END)
        details_lines = [
            f"Setup Question: {setting.setup_question}",
            f"Help String: {setting.help_string}",
            f"Token: {setting.token}",
            f"Offset: {setting.offset}",
            f"Width: {setting.width}"
        ]
        if setting.bios_default is not None:
            details_lines.append(f"BIOS Default: {setting.bios_default}")
        if setting.value:
            details_lines.append(f"Value: {setting.value}")
        final_details = "\n".join(details_lines) + "\n"
        self.details_text.insert('1.0', final_details)
        self.details_text.config(state=tk.DISABLED)
        if setting.options:
            display_options = []
            for opt in setting.options:
                match = re.match(r'^\[([^\]]+)\](.*)$', opt)
                if match:
                    display_text = match.group(2).strip()
                    display_options.append(display_text)
                else:
                    display_options.append(opt)
            unique_options = []
            seen = set()
            for opt in display_options:
                if opt not in seen:
                    unique_options.append(opt)
                    seen.add(opt)
            self.current_setting = setting
            self.current_unique_options = unique_options
            if setting.active_option is not None and 0 <= setting.active_option < len(setting.options):
                active_opt = setting.options[setting.active_option]
                match = re.match(r'^\[([^\]]+)\](.*)$', active_opt)
                display_text = match.group(2).strip() if match else active_opt
                self.option_var.set(display_text)
            else:
                self.option_var.set(unique_options[0] if unique_options else "No options available")
            self.option_button.pack(fill=tk.X, padx=5, pady=(0, 5))
        else:
            self.current_setting = None
            self.current_unique_options = None
            if setting.value is not None:
                var = tk.StringVar(value=setting.value)
                entry = ctk.CTkEntry(self.options_frame, textvariable=var, font=("Arial", 12))
                entry.pack(fill=tk.X, padx=5, pady=(0, 5))
                update_btn = ctk.CTkButton(
                    self.options_frame,
                    text="Update Value",
                    command=lambda s=setting, v=var: self._update_value(s, v),
                    fg_color=COLORS["buttonbg"],
                    text_color=COLORS["buttonfg"],
                    font=("Arial", 12),
                    corner_radius=5,
                    hover_color=COLORS["selectbg"]
                )
                update_btn.pack()
    def _on_predefined_setting_select(self, event):
        selection = self.predefined_settings_list.selection()
        if not selection:
            return
        selected_item = selection[0]
        index = self.predefined_settings_list.index(selected_item)
        if index >= len(self.filtered_predefined_settings):
            return
        setting = self.filtered_predefined_settings[index]
        self.selected_setting = setting

        for widget in self.options_frame.winfo_children():
            if widget != self.options_label:
                widget.pack_forget()

        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete('1.0', tk.END)
        details_lines = [
            f"Setup Question: {setting.setup_question}",
            f"Help String: {setting.help_string}",
            f"Token: {setting.token}",
            f"Offset: {setting.offset}",
            f"Width: {setting.width}"
        ]
        if setting.bios_default is not None:
            details_lines.append(f"BIOS Default: {setting.bios_default}")
        if setting.value:
            details_lines.append(f"Value: {setting.value}")
        final_details = "\n".join(details_lines) + "\n"
        self.details_text.insert('1.0', final_details)
        self.details_text.config(state=tk.DISABLED)

        if setting.options:
            display_options = []
            for opt in setting.options:
                match = re.match(r'^\[([^\]]+)\](.*)$', opt)
                if match:
                    display_text = match.group(2).strip()
                    display_options.append(display_text)
                else:
                    display_options.append(opt)
            unique_options = []
            seen = set()
            for opt in display_options:
                if opt not in seen:
                    unique_options.append(opt)
                    seen.add(opt)
            
            self.current_setting = setting
            self.current_unique_options = unique_options
            
            if setting.active_option is not None and 0 <= setting.active_option < len(setting.options):
                active_opt = setting.options[setting.active_option]
                match = re.match(r'^\[([^\]]+)\](.*)$', active_opt)
                display_text = match.group(2).strip() if match else active_opt
                self.option_var.set(display_text)
            else:
                self.option_var.set(unique_options[0] if unique_options else "No options available")
            
            self.option_button.pack(fill=tk.X, padx=5, pady=(0, 5))
        else:
            self.current_setting = None
            self.current_unique_options = None
            if setting.value is not None:
                var = tk.StringVar(value=setting.value)
                entry = ctk.CTkEntry(self.options_frame, textvariable=var, font=("Arial", 12))
                entry.pack(fill=tk.X, padx=5, pady=(0, 5))
                update_btn = ctk.CTkButton(
                    self.options_frame,
                    text="Update Value",
                    command=lambda s=setting, v=var: self._update_value(s, v),
                    fg_color=COLORS["buttonbg"],
                    text_color=COLORS["buttonfg"],
                    font=("Arial", 12),
                    corner_radius=5,
                    hover_color=COLORS["selectbg"]
                )
                update_btn.pack()
    def _update_option(self, setting: BIOSSetting, new_active: int):
        if setting.active_option != new_active:
            setting.active_option = new_active
            if setting not in self.changed_settings:
                self.changed_settings.append(setting)
        self._populate_settings_list(self.search_var.get())
    def _update_value(self, setting: BIOSSetting, value_var: tk.StringVar):
        new_value = value_var.get()
        if setting.value != new_value:
            setting.value = new_value
            if setting not in self.changed_settings:
                self.changed_settings.append(setting)
        self._populate_settings_list(self.search_var.get())
    def _save_file(self):
        if not self.current_file or not self.original_lines:
            return
        if self.is_exported:
            base_path = os.path.join(os.path.expanduser("~"), "Desktop")
        else:
            base_path = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = self._get_unique_filename(base_path)
        try:
            setting_blocks = {}
            current_block = []
            current_setting_key = None
            re_setup = re.compile(r'^Setup\s+Question\s*=\s*(.*)', re.IGNORECASE)
            re_token = re.compile(r'^Token\s*=\s*(.*)', re.IGNORECASE)
            re_offset = re.compile(r'^Offset\s*=\s*(.*)', re.IGNORECASE)
            sq, token, offset = None, None, None
            for raw_line in self.original_lines:
                line_stripped = self.re_comment.sub('', raw_line).strip()
                match_sq = re_setup.match(line_stripped) if line_stripped else None
                if match_sq:
                    if current_setting_key and current_block:
                        setting_blocks[current_setting_key] = current_block[:]
                    current_block = []
                    sq = match_sq.group(1).strip()
                    token, offset = None, None
                    current_setting_key = None
                current_block.append(raw_line)
                if not line_stripped:
                    continue
                match_tk = re_token.match(line_stripped)
                if match_tk:
                    token = match_tk.group(1).strip()
                    continue
                match_off = re_offset.match(line_stripped)
                if match_off:
                    offset = match_off.group(1).strip()
                    if sq and token and offset:
                        current_setting_key = (sq, token, offset)
                    continue
            if current_setting_key and current_block:
                setting_blocks[current_setting_key] = current_block[:]
            with open(filename, 'w', encoding='ansi') as f:
                for line in self.original_lines[:6]:
                    f.write(line)
                f.write('\n')
                for setting in self.changed_settings:
                    key = (setting.setup_question.strip(), setting.token.strip(), setting.offset.strip())
                    block = setting_blocks.get(key, [])
                    if not block:
                        continue
                    updated_block = []
                    in_options = False
                    wrote_setup = False
                    for line in block:
                        stripped = self.re_comment.sub('', line).strip()
                        if re_setup.match(stripped):
                            continue
                        if self.re_options.match(stripped) and setting.options:
                            in_options = True
                            if not wrote_setup:
                                updated_block.append(f"Setup Question\t= {setting.setup_question}\n")
                                if setting.help_string:
                                    updated_block.append(f"Help String\t= {setting.help_string}\n")
                                wrote_setup = True
                            for idx, opt in enumerate(setting.options):
                                prefix = "Options\t=" if idx == 0 else "         "
                                is_active = (setting.active_option == idx)
                                updated_block.append(f"{prefix}{'*' if is_active else ''}{opt}\n")
                        elif in_options and re.match(r'^\s*\*?\[.*?\]', stripped):
                            continue
                        elif self.re_value.match(stripped) and setting.value is not None:
                            if not wrote_setup:
                                updated_block.append(f"Setup Question\t= {setting.setup_question}\n")
                                if setting.help_string:
                                    updated_block.append(f"Help String\t= {setting.help_string}\n")
                                wrote_setup = True
                            comment_match = re.search(r'(//.*)$', line)
                            comment = f"\t{comment_match.group(1)}" if comment_match else ""
                            leading_whitespace = re.match(r'^\s*', line).group(0)
                            updated_block.append(f"{leading_whitespace}Value\t={setting.value}{comment}\n")
                            in_options = False
                        elif re.match(r'^Token\s*=\s*', stripped, re.IGNORECASE):
                            if not wrote_setup:
                                updated_block.append(f"Setup Question\t= {setting.setup_question}\n")
                                if setting.help_string:
                                    updated_block.append(f"Help String\t= {setting.help_string}\n")
                                wrote_setup = True
                            updated_block.append(f"Token\t={setting.token}\n")
                            in_options = False
                        elif not in_options and not re.match(r'^Help\s+String\s*=', stripped, re.IGNORECASE):
                            if not wrote_setup:
                                updated_block.append(f"Setup Question\t= {setting.setup_question}\n")
                                if setting.help_string:
                                    updated_block.append(f"Help String\t= {setting.help_string}\n")
                                wrote_setup = True
                            updated_block.append(line)
                            in_options = False
                    f.writelines(updated_block)
                    f.write('\n')
            messagebox.showinfo("Success", f"Saved {len(self.changed_settings)} changed setting(s) to {filename}!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    def run(self):
        self.root.mainloop()
def main():
    run_as_admin()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    root.configure(fg_color=COLORS["bg"])
    app = SettingsGUI(root)
    app.run()
if __name__ == "__main__":
    main()