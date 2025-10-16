#!/bin/zsh

pyinstaller -D -w -i ../logo.icns --workpath build/build --distpath build/dist --specpath build --name 浏览器助手 main.py
