set gitdir=%CD%\pgit
set path=%gitdir%\cmd;%path%
if exist .\new_editor\ rmdir /s /Q new_editor
if exist .\OpenPLC-Editor-KauriIOT-Edition-\ rmdir /s /Q OpenPLC-Editor-KauriIOT-Edition-
git clone https://github.com/Very1ucky/OpenPLC-Editor-KauriIOT-Edition-
if exist .\OpenPLC-Editor-KauriIOT-Edition-\editor\ (
  move .\OpenPLC-Editor-KauriIOT-Edition-\editor .\new_editor
  move .\OpenPLC-Editor-KauriIOT-Edition-\matiec\lib .\new_lib
  copy /y .\OpenPLC-Editor-KauriIOT-Edition-\revision .\
  rmdir /s /Q OpenPLC-Editor-KauriIOT-Edition-
  echo "Update applied successfully"
) else (
  echo "Error cloning from repository!"
)
