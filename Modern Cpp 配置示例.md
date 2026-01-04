[toc]

# Modern Cpp 配置示例

下面的配置只是适配该项目工具的基础配置，更多配置信息可查看微软在线文档：https://code.visualstudio.com/docs/debugtest/debugging-configuration。

## .vscode 文件夹中的配置文件

### launch.json

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      // MSVC 原生调试器，无需配置 GDB/MI
      "name": "Debug with MSVC",
      "type": "cppvsdbg",
      "request": "launch",
      // CMake Tools 会解析为当前 launch target 的输出全路径
      "program": "${command:cmake.launchTargetPath}",
      "args": [],
      "stopAtEntry": false,
      // 把工作目录设置为可执行文件所在目录，方便 DLL 加载等
      "cwd": "${command:cmake.getLaunchTargetDirectory}",
      "environment": [
        {
          "name": "PATH",
          "value": "${command:cmake.getLaunchTargetDirectory};${env:PATH}"
        }
      ],
      // 使用 VSCode 的集成终端
      "console": "integratedTerminal",
      // 若你希望使用外部终端，可以改为:
      // "console": "externalTerminal",
      "preLaunchTask": "build-msvc-debug"
    },
    {
      // GDB (MinGW-w64 / MSYS2 UCRT64) 使用 MI 协议，需要指定调试器
      "name": "Debug with GDB",
      "type": "cppdbg",
      "request": "launch",
      "program": "${command:cmake.launchTargetPath}",
      "args": [],
      "stopAtEntry": false,
      "cwd": "${command:cmake.getLaunchTargetDirectory}",
      "environment": [
        {
          "name": "PATH",
          "value": "D:/msys64/ucrt64/bin;${command:cmake.getLaunchTargetDirectory};${env:PATH}"
        }
      ],
      "externalConsole": false, // 使用系统终端可避免字符集或输入问题
      "MIMode": "gdb", // 指定 MI 模式为 gdb
      "miDebuggerPath": "D:/msys64/ucrt64/bin/gdb.exe", // GDB 可执行路径
      "setupCommands": [ // GDB 启动时的初始化命令
        {
          "description": "Enable pretty-printing for gdb",
          "text": "-enable-pretty-printing",
          "ignoreFailures": true
        }
      ], 
      "preLaunchTask": "build-ucrt64-debug"
    }
  ]
}
```

### tasks.json

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "build-msvc-debug",
      "type": "shell",
      "command": "cmake",
      "args": [
        "--build",
        "${workspaceFolder}/build/msvc-vs-debug",
        "--target",
        "example"
      ],
      "problemMatcher": [],
      "group": {
        "kind": "build",
        "isDefault": true
      }
    },
    {
      "label": "build-ucrt64-debug",
      "type": "shell",
      "command": "cmake",
      "args": [
        "--build",
        "${workspaceFolder}/build/ucrt64-debug",
        "--target",
        "example"
      ],
      "problemMatcher": [],
      "group": "build"
    }
  ]
}
```

### settings.json

```json
{
  "C_Cpp.default.configurationProvider": "ms-vscode.cmake-tools"
}
```

## CMake 预设

### CMakePresets.json

```json
{
    "version": 8,
    "cmakeMinimumRequired": {
        "major": 3,
        "minor": 23,
        "patch": 0
    },
    "configurePresets": [
        {
            "name": "msvc-vs",
            "displayName": "MSVC + VS Ninja (base)",
            "generator": "Ninja",
            "binaryDir": "${sourceDir}/build/${presetName}",
            "installDir": "${sourceDir}/install/${presetName}",
            "environment": {
                "PATH": "D:/msys64/ucrt64/bin;$penv{PATH}"
            },
            "cacheVariables": {
                "CMAKE_MAKE_PROGRAM": "D:/Program Files/Microsoft Visual Studio/2022/Community/Common7/IDE/CommonExtensions/Microsoft/CMake/Ninja/ninja.exe",
                "CMAKE_TOOLCHAIN_FILE": "$env{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake",
                "VCPKG_TARGET_TRIPLET": "x64-windows",
                "VCPKG_MANIFEST_MODE": "ON"
            }
        },
        {
            "name": "ucrt64",
            "displayName": "MinGW-w64 UCRT64 + MSYS2 Ninja (base)",
            "generator": "Ninja",
            "binaryDir": "${sourceDir}/build/${presetName}",
            "installDir": "${sourceDir}/install/${presetName}",
            "environment": {
                "PATH": "D:/msys64/ucrt64/bin;$penv{PATH}"
            },
            "cacheVariables": {
                "CMAKE_MAKE_PROGRAM": "D:/msys64/ucrt64/bin/ninja.exe",
                "CMAKE_C_COMPILER": "D:/msys64/ucrt64/bin/gcc.exe",
                "CMAKE_CXX_COMPILER": "D:/msys64/ucrt64/bin/g++.exe",
                "CMAKE_TOOLCHAIN_FILE": "$env{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake",
                "VCPKG_TARGET_TRIPLET": "x64-mingw-dynamic",
                "VCPKG_MANIFEST_MODE": "ON"
            }
        },
        {
            "name": "msvc-vs-debug",
            "inherits": "msvc-vs",
            "displayName": "MSVC Debug",
            "cacheVariables": {
                "CMAKE_BUILD_TYPE": "Debug"
            }
        },
        {
            "name": "msvc-vs-release",
            "inherits": "msvc-vs",
            "displayName": "MSVC Release",
            "cacheVariables": {
                "CMAKE_BUILD_TYPE": "Release"
            }
        },
        {
            "name": "msvc-vs-minsizerel",
            "inherits": "msvc-vs",
            "displayName": "MSVC MinSizeRel",
            "cacheVariables": {
                "CMAKE_BUILD_TYPE": "MinSizeRel"
            }
        },
        {
            "name": "ucrt64-debug",
            "inherits": "ucrt64",
            "displayName": "UCRT64 Debug",
            "cacheVariables": {
                "CMAKE_BUILD_TYPE": "Debug"
            }
        },
        {
            "name": "ucrt64-release",
            "inherits": "ucrt64",
            "displayName": "UCRT64 Release",
            "cacheVariables": {
                "CMAKE_BUILD_TYPE": "Release"
            }
        },
        {
            "name": "ucrt64-minsizerel",
            "inherits": "ucrt64",
            "displayName": "UCRT64 MinSizeRel",
            "cacheVariables": {
                "CMAKE_BUILD_TYPE": "MinSizeRel"
            }
        }
    ],
    "buildPresets": [
        {
            "name": "build-msvc-debug",
            "configurePreset": "msvc-vs-debug"
        },
        {
            "name": "build-msvc-release",
            "configurePreset": "msvc-vs-release"
        },
        {
            "name": "build-msvc-minsizerel",
            "configurePreset": "msvc-vs-minsizerel"
        },
        {
            "name": "build-ucrt64-debug",
            "configurePreset": "ucrt64-debug"
        },
        {
            "name": "build-ucrt64-release",
            "configurePreset": "ucrt64-release"
        },
        {
            "name": "build-ucrt64-minsizerel",
            "configurePreset": "ucrt64-minsizerel"
        }
    ]
}
```

> **注意**：如果使用 `VCPKG_ROOT` 环境变量，请确保手动将 `vcpkg` 安装目录添加到系统环境变量，否则请直接写绝对路径。