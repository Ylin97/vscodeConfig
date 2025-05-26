## 初始化 vscode 项目
function Init-c
    set template_path "$HOME/.config/Code/projectTemplate/c"
    # 复制所有模板文件到当前目录
    cp -r $template_path/. . > /dev/null 2>&1
    if test $status -eq 0
        # 检查 git 命令是否存在，如果存在则初始化一个仓库
        if type -q git
            git init
            git add .
            git commit -m "Initialized a project."
        else
            echo "WARN: 'git' command not found!"
            return 2
        end
        # 尝试用 vscode 打开 main.c 文件
        if type -q code
            code source/main.c
        end
    else
        echo -e "\033[33mError: can't initialize a project here, please check if the path '$template_path' exists.\033[0m"
        return 1
    end
    return 0
end

function Init-cpp
    set template_path "$HOME/.config/Code/projectTemplate/cpp"
    # 复制所有模板文件到当前目录
    cp -r $template_path/. . > /dev/null 2>&1
    if test $status -eq 0
        # 检查 git 命令是否存在，如果存在则初始化一个仓库
        if type -q git
            git init
            git add .
            git commit -m "Initialized a project."
        else
            echo "WARN: 'git' command not found!"
            return 2
        end
        # 尝试用 vscode 打开 main.cpp 文件
        if type -q code
            code source/main.cpp
        end
    else
        echo -e "\033[33mError: can't initialize a project here, please check if the path '$template_path' exists.\033[0m"
        return 1
    end
    return 0
end

function Reset-c
    set template_path "$HOME/.config/Code/projectTemplate/c"
    # 复制所有配置文件到当前目录
    cp -r $template_path/.vscode . > /dev/null 2>&1
    if test $status -eq 0
        echo "Reset workspace's configuration for a C project successfully!"
    else
        echo "Error: can't reset workspace configuration, please try again!"
    end
end

function Reset-cpp
    set template_path "$HOME/.config/Code/projectTemplate/cpp"
    # 复制所有配置文件到当前目录
    cp -r $template_path/.vscode . > /dev/null 2>&1
    if test $status -eq 0
        echo "Reset workspace's configuration for a C++ project successfully!"
    else
        echo "Error: can't reset workspace configuration, please try again!"
    end
end
