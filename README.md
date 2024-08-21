# OpenPLC Editor - KauriIOT Edition (base)
OpenPLC Editor - IDE capable of creating programs for the OpenPLC Runtime. This edition supports PLC developed in Kauri IOT company.

OpenPLC Editor repository contains modified versions of [Beremiz](https://github.com/beremiz/beremiz) (GPLv2 and LGPLv2) and [MatIEC](https://github.com/beremiz/matiec) (GPLv3) projects.

The codebase has been updated to Python3 and wxPython Phoenix.

It's platform independent base that can can be configured to run on different platforms. Tested on Windows and Ubuntu 22.04.

You can run app from Beremiz.py file.

## Requirements
- `Python 3.9`
- `python packages from requirements.txt`
- `make utils`
- `C/C++ compiler to use matiec`
- `arm-none-eabi-gcc`

## Changes in relation to the OpenPLC Editor
- Changed the app logo and startup banner.
- Matiec was divided into two parts. One part, included here, contains platform-independent PLC libraries and functional blocks logic written in C and ST PLC languages. The second part contains the compiled Matiec code for the platform, which needs to be added to the Matiec folder.
- Removed Arduino library, libraries to work with P1AM, Sequent Microsystems and Jaguar modules from matiec and `editor/plcopen/definitions.py` due to using different platform.
- Added MODBUS, RS485, MQTT libraries.
- Removed unsupported examples from the `editor/examples` folder.
- Removed the `editor/arduino` and `editor/arduino_ext` folders, as well as `editor/dialogs/ArduinoUploadDialog.py`.
- Added the `editor/kauri_parser` folder, which contains scripts and parts of source files to compile the PLC program for devices with a PLC runtime environment. Also it contains matiec modified functional blocks functions realizations which uses platform specific api and libraries (MODBUS library, for example).
- Added `editor/dialogs/KauriUploadDialog.py` for easy setup of PLC device configuration and transferring PLC programs to devices.
- Changed `editor/ProjectController`:
    - Fixed the `_Generate_runtime` function to support working with library functional blocks using byte, bool, or word arrays of size 128.
    - Modified the `findCmd` function to search the Matiec folder within its parent parent folder.
    - Changed the `_generateArduino` method to the `_generateKauri`, which is bound to the `Transfer program to PLC` button and runs `KauriUploadDialog`.
    - Added the `_debugPLCWithoutBuild` function for use after program transfer using `KauriUploadDialog`, allowing for debugging without pressing the `Live debug remote PLC` button if needed.
    - Updated the `_debugPLC` function to utilize the `_debugPLCWithoutBuild` function.
    - Removed the button responsible for generating firmware for OpenPLC Runtime due to the use of our own runtime environment with a different firmware representation.
- Changed `editor/dialogs/DebuggerRemoteConnDialog.py`, `editor/modbus/mb_utils.py` and `editor/modbus/web_settings.py` to support baudrate equal to 256000 bod.

## Adding new functional blocks
Different ways to add new functional blocks described [here](https://autonomylogic.com/docs/3-3-adding-new-blocks-to-openplc-editors-library/). Further comments will be given for Manual Approach:
- To generate .xml, MatIEC lib file and C code files can be used new OpenPLC Editor project with integrated functinal block creation tool. After project building you can extract .xml data from `{build folder}/plc.xml` folder, .st data from `{build folder}/build/plc.st` file and C code data from `{build folder}/build/POUS.h` and `{build folder}/build/POUS.c`.
- The .st files should be put only into `matiec/lib` folder. The .xml files must be put `editor/plcopen` folder to use library blocks in editor window.
- The C sourse files should be put into `matiec/lib/C` folder and `editor/kauri_parser/Sources/Common/MatiecBased`. First source location is used to compile program for simulation and debugging program comparing and visualization. Second source location is used to compile program for PLC device (they can be different from first location's sources and use platform specific libraries).

