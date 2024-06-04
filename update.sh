#!/bin/bash
if [ -d "./new_editor" ]
then
    rm -Rf new_editor
fi
if [ -d "./OpenPLC-Editor-KauriIOT-Edition-" ]
then
    rm -Rf OpenPLC-Editor-KauriIOT-Edition-
fi
git clone https://github.com/thiagoralves/OpenPLC-Editor-KauriIOT-Edition-
if [ -d "./OpenPLC-Editor-KauriIOT-Edition-/editor" ]
then
    mv "./OpenPLC-Editor-KauriIOT-Edition-/editor" ./new_editor
    mv "./OpenPLC-Editor-KauriIOT-Edition-/matiec/lib" ./new_lib
    cp ./OpenPLC-Editor-KauriIOT-Edition-/revision ./
    rm -Rf OpenPLC-Editor-KauriIOT-Edition-
    echo "Update applied successfully"
else
    echo "Error cloning from repository!"
fi
