import os
import sys
import json
import msvcrt
from shutil import copytree, rmtree

c_cpp_properties_data = {
    "configurations": [
        {
            "name": "Win32",
            "includePath": [
                "${workspaceFolder}",
                "${workspaceFolder}/include"
            ],
            "defines": [
                "_DEBUG",
                "UNICODE",
                "_UNICODE"
            ],
            "compilerPath": "D:\\Tools\\mingw64\\bin\\gcc.exe",
            "cStandard": "gnu11",
            "cppStandard": "gnu++11",
            "intelliSenseMode": "windows-gcc-x64"
        }
    ],
    "version": 4
}

launch_data = {
    "version": "0.2.0",
    "configurations": [
        {
            "name": "gcc.exe - 生成和调试活动文件",
            "type": "cppdbg",
            "request": "launch",
            "program": "${workspaceFolder}\\debug\\main.exe",
            "args": [],
            "stopAtEntry": False,
            "cwd": "${workspaceFolder}",
            "environment": [],
            "externalConsole": False,
            "MIMode": "gdb",
            "miDebuggerPath": "D:\\Tools\\mingw64\\bin\\gdb.exe",
            "setupCommands": [
                {
                    "description": "为 gdb 启用整齐打印",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": True
                }
            ],
            "preLaunchTask": "C/C++: g++.exe 生成活动文件"
        }
    ]
}

tasks_data = {
    "tasks": [
        {
            "type": "cppbuild",
            "label": "C/C++: g++.exe 生成活动文件",
            "command": "D:\\Tools\\mingw64\\bin\\gcc.exe",
            "args": [
                "-fdiagnostics-color=always",
                "-g",
                "-I",
                "${workspaceFolder}\\include",
                "${fileDirname}\\*.c",
                "-o",
                "${workspaceFolder}\\debug\\main.exe"
            ],
            "options": {
                "cwd": "${fileDirname}"
            },
            "problemMatcher": [
                "$gcc"
            ],
            "group": {
                "kind": "build",
                "isDefault": True
            },
            "detail": "调试器生成的任务。"
        }
    ],
    "version": "2.0.0"
}


def read_file(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as fr:
        config = json.loads(fr.read().replace("\'", "\""))
    return config


def write_file(path: str, content: dict) -> None:
    with open(path, 'w', encoding='utf-8') as fw:
        json.dump(content, fw, ensure_ascii=False, indent=4)


def generate_config_file():
    Path = os.getenv('Path').split(';')
    compiler_path = None
    for p in Path:
        try:
            if 'gcc.exe' in os.listdir(p):
                compiler_path = p
                break
        except Exception:
            continue
    c_path = 'projectTemplate\\c\\.vscode'
    cpp_path = 'projectTemplate\\cpp\\.vscode'
    config_files = ('c_cpp_properties.json', 'launch.json', 'tasks.json')

    # set c config files
    for f in config_files:
        if f == 'c_cpp_properties.json':
            config = c_cpp_properties_data
            config['configurations'][0]['compilerPath'] = os.path.join(compiler_path, "gcc.exe")
            write_file(os.path.join(c_path, f), config)
        elif f == 'launch.json':
            config = launch_data
            config['configurations'][0]['name'] = "gcc.exe - 生成和调试活动文件"
            config['configurations'][0]['miDebuggerPath'] = os.path.join(compiler_path, "gdb.exe")
            write_file(os.path.join(c_path, f), config)
        elif f == 'tasks.json':
            config = tasks_data
            config['tasks'][0]['label'] = "C/C++: gcc.exe 生成活动文件"
            config['tasks'][0]['command'] = os.path.join(compiler_path, "gcc.exe")
            config['tasks'][0]['args'] = [
                "-fdiagnostics-color=always",
                "-g",
                "-I",
                "${workspaceFolder}\\include",
                "${fileDirname}\\*.c",
                "-o",
                "${workspaceFolder}\\debug\\main.exe"
            ]
            write_file(os.path.join(c_path, f), config)

    # set cpp config files
    for f in config_files:
        if f == 'c_cpp_properties.json':
            config = c_cpp_properties_data
            config['configurations'][0]['compilerPath'] = os.path.join(compiler_path, "g++.exe")
            write_file(os.path.join(cpp_path, f), config)
        elif f == 'launch.json':
            config = launch_data
            config['configurations'][0]['name'] = "g++.exe - 生成和调试活动文件"
            config['configurations'][0]['miDebuggerPath'] = os.path.join(compiler_path, "gdb.exe")
            write_file(os.path.join(cpp_path, f), config)
        elif f == 'tasks.json':
            config = tasks_data
            config['tasks'][0]['label'] = "C/C++: g++.exe 生成活动文件"
            config['tasks'][0]['command'] = os.path.join(compiler_path, "g++.exe")
            config['tasks'][0]['args'] = [
                "-fdiagnostics-color=always",
                "-g",
                "-I",
                "${workspaceFolder}\\include",
                "${fileDirname}\\*.cpp",
                "-o",
                "${workspaceFolder}\\debug\\main.exe"
            ]
            write_file(os.path.join(cpp_path, f), config)


def set_profile():
    """ 设置 profile.ps1 文件"""
    HOME = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
    profile_path = os.path.join(HOME, 'Documents', 'WindowsPowerShell')
    
    with open('vscode_profile.ps1', 'r', encoding='utf-8') as fr:
        content = fr.read()
    destination = os.path.join(profile_path, 'profile.ps1')
    # destination = 'profile.ps1'
    if os.path.exists(destination):
        with open(destination, 'r', encoding='utf-8') as fr:
            origin_content = fr.readlines()
            start, end = 0, 0
            for cnt, line in enumerate(origin_content):
                if line.strip() == '#region project initialize':
                    start = cnt
                if start != 0 and line.strip() == '#endregion':
                    end = cnt + 1
                    break
    else:
        origin_content = None
    with open(destination, 'w', encoding='utf-8') as fw:
        if not origin_content:
            fw.write(content)
        elif start != 0:
            fw.writelines(origin_content[0:start])
            if len(origin_content[start - 1].strip()) != 0:
                if origin_content[start - 1][-1] != '\n': 
                    fw.write('\n\n')
                else:
                    fw.write('\n')
            fw.write(content)
            if end > start and end < len(origin_content):
                if len(origin_content[end].strip()) != 0:
                    fw.write('\n\n')
                else:
                    fw.write('\n')
                fw.writelines(origin_content[end:])
        else:
            fw.writelines(origin_content)
            fw.write('\n')
            if origin_content[-1][-1] != '\n':
                fw.write('\n')
            fw.write(content)


def move_template():
    """移动项目模板到默认模板放置位置"""
    HOME = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
    vscode_config_path = os.path.join(HOME, '.vscode')
    destination = os.path.join(vscode_config_path, 'projectTemplate')
    if not os.path.exists(vscode_config_path):
        os.makedirs(vscode_config_path)
    if os.path.exists(destination):
        rmtree(destination)
    copytree('projectTemplate', destination)


def main():
    generate_config_file();
    move_template();
    set_profile();
    print("配置已完成，请按任意键退出...")
    ord(msvcrt.getch())


if __name__ == '__main__':
    sys.exit(main())