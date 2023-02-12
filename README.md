## 描述  

一些 vscode 的编译和调试配置文件。通过这些配置文件可以进行多文件编译，而不依赖于`Cmake`等工具。

## 用法 

### Step 1:  配置命令

首先应该通过插件商店安装`C/C++`和`Code Runner`这两个插件。

#### Windows 系统  

运行 `Windows`文件夹中的`setup.py`或者`setup.exe`即可完成配置。

#### Linux 系统

在终端打开`Linux`目录，然后执行`python ./setup.py`即可完成配置。

### Step 2: 使用命令  

用 vscode 打开一个新文件夹，然后在终端使用如下命令来初始化或重置一个项目 (下面命令前面的`$`是命令提示符)：

```shell
$ Init-c     # 初始化一个 C 项目
$ Init-cpp   # 初始化一个 C++ 项目
$ Reset-c    # 重置一个 C 项目
$ Reset-cpp  # 重置一个 C++ 项目
```

项目的结构为：  

- build : 这里存放编译得到的可执行文件（不带调试信息）
- debug : 这里存放编译得到的可调试的可执行文件（带有调试信息）
- include : 这里是自定义的头文件的存放位置
- source : 这里是`.c`文件或者`.cpp`文件的存放位置
- .gitignore : 这是 Git 的配置文件

当我们对一个文件夹初始化 (`Init-c`或`Init-cpp`)后，之后就可以像编译和调试单文件一样点击 vscode 右上角的运行或调试按钮对多文件进行运行或调试了。此外，诸如`F5 调试`等快捷键也是支持的。

> **注意！**Windows 由于是通过 Powershell 脚本来实现命令的，所以首次运行时可能出现“脚本权限不允许”的报错。这时候需要更改一下系统的脚本执行控制权限：
>
> 以管理员身份打开 Powershell，然后执行如下命令:
>
> ```Power
> Set-ExecutionPolicy RemoteSigned
> ```
>
> 然后在出现的确认信息中输入 `y` 以确定修改。更多信息请查阅 [Set-ExecutionPolicy](https://learn.microsoft.com/zh-cn/powershell/module/microsoft.powershell.security/set-executionpolicy?view=powershell-7.3)。

