@echo off

pyinstaller -D -w -i ..\logo.ico --workpath .\build\build --distpath .\build\dist --specpath .\build --name 浏览器助手 .\main.py
