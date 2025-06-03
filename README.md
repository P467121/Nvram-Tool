
# Auto-Scewin BIOS Settings Tool 🔧💻

This is a tool designed to help automate the process of configuring BIOS settings. It allows users to modify settings, export only the changed configurations, and import them into another system. However, please note that some changes may cause issues such as failure to boot. If this happens, a **CMOS reset** is typically the fix.

## Features ✨

- Automatically configures BIOS settings.
- Exports only the settings that have been changed. 
- Easy to import the exported configuration to another PC.
- Configurations can be easily modified or extended by changing the source code.

## Requirements 📦

To run the source code version of this project, you'll need to install the following dependencies:

1. **CustomTkinter** – For the graphical user interface.
2. **PyInstaller** – To package the tool as a standalone executable (optional).

You can install them via pip:

pip install customtkinter pyinstaller


## Usage 🛠️

### Running from Source Code

Clone or download the repository.

Install the required dependencies using pip:

Run the script using Python:

```bash
python NvramView.py
```

### Building an Executable

If you prefer to create a standalone executable, you can use PyInstaller. Run the following command in your terminal:

```bash
pyinstaller .spec file
```

This will generate an executable file in the `dist` directory.

## Custom Configurations ⚙️

The auto configuration settings can be changed or added directly in the source code. Simply modify the `config.py` (or relevant file) to add or adjust the BIOS settings you wish to automate.

## Important Notes ⚠️

**PC Boot Issue:** After applying certain BIOS configurations, your PC may fail to boot. If this occurs, performing a CMOS reset will usually resolve the issue.

You can reset the CMOS either by using the reset jumper on your motherboard or by removing and reinserting the CMOS battery. 🔋

**Exported Configuration:** Only the settings that have been changed will be exported. These can be imported as regular BIOS configuration files on another machine.
