#region project initialize
function Init-project
{
    param (
        $ProjectType = 'Unknown'
    )
    $TemplatePathRoot = $HOME + "\.vscode\projectTemplate"
    $ResourcePath = switch ( $ProjectType ) 
    {
        'c' {
            $TemplatePathRoot + "\c\*"
        }
        'cpp' {
            $TemplatePathRoot + "\cpp\*"
        }
        default {
            "Unknown"
        }
    }
    Copy-Item -Path $ResourcePath -Destination "." -Recurse 
    if ( $? ) {
        if ( Get-Command "git" -errorAction SilentlyContinue ) {
            git init
            git add .
            git commit -m "Initialized a project."
        } else {
            Write-Host "WARN: 'git' command not found."
        }
        # open main file in vscode
        $MainFile = ".\source\main." + $ProjectType
        Code $MainFile
    }
}

function Reset-Vscode-Config
{
    param (
        $ProjectType = "Unknown"
    )
    
    $CurrentConfigPath = ".\.vscode"
    $TemplatePathRoot = $HOME + "\.vscode\projectTemplate"
    
    # remove the old configuration files
    $TRUE_FALSE = ( Test-Path $CurrentConfigPath )
    if ( $TRUE_FALSE -eq "True" ) {
        remove-Item -Recurse -Force $CurrentConfigPath
    }
    
    $ResourcePath = switch ( $ProjectType ) 
    {
        'c' {
            $TemplatePathRoot + "\c\.vscode"
        }
        'cpp' {
            $TemplatePathRoot + "\cpp\.vscode"
        }
        default {
            "Unknown"
        }
    }
    # reset configuration
    if ( $ResourcePath -ne 'Unknown') {
        Copy-Item -Path $ResourcePath -Destination "." -Recurse
        if ( $? ) {
            $msg = "Reset workspace's configuration for a " + $ProjectType +  " project seccussfully!"
            Write-Host $msg
        } else {
            Write-Host "Error: can't reset workspace configuration, please try again!"
        }
    }
}

function Init-c
{
    Init-project 'c'
}

function Init-cpp
{
    Init-project 'cpp'
}

function Reset-c
{
    Reset-Vscode-Config 'c'
}

function Reset-cpp
{
    Reset-Vscode-Config 'cpp'
}
 
function New-CppProject {
    <#
    .SYNOPSIS
    初始化一个基于 CMake + Ninja + vcpkg + VS Code 的现代 C++ 项目。

    .DESCRIPTION
    本函数用于在当前目录中快速创建一个现代 C++ 项目。它将从指定模板目录复制文件，
    替换 placeholder（如 example），初始化 Git 仓库，并生成 vcpkg 的 manifest 文件。

    默认行为：
    - 项目名默认为当前文件夹名称（规范化后用于 vcpkg）
    - 模板路径默认为 $env:USERPROFILE\.vscode\projectTemplate\ModernCpp

    .PARAMETER name
    指定项目名称。该名称将用于替换模板中的所有 `example` 占位符，并作为 vcpkg 包名称。
    若未指定，则默认使用当前目录名。

    .PARAMETER template
    指定项目模板路径。该路径下应包含一个标准的项目模板结构。
    若未指定，则默认使用 `$env:USERPROFILE\.vscode\projectTemplate\ModernCpp`。

    .EXAMPLE
    PS> New-CppProject

    初始化一个 C++ 项目，使用当前文件夹名作为项目名，使用默认模板路径。

    .EXAMPLE
    PS> New-CppProject -name MyApp

    初始化一个名为 MyApp 的 C++ 项目，使用默认模板路径。

    .EXAMPLE
    PS> New-CppProject -name EngineCore -template "D:\Templates\ModernCpp"

    使用指定模板路径初始化一个名为 EngineCore 的项目。

    .NOTES
    模板文件夹应包含至少以下文件（可通过示例模板生成）：
    - CMakeLists.txt
    - vcpkg.json
    - src/include/example.h
    - src/source/main.cpp 等

    替换逻辑会将所有 `example` 替换为指定项目名，大小写敏感。
    #>

    param(
        [Parameter(Position = 0, HelpMessage = "指定项目名（默认使用当前文件夹名）")]
        [string]$name = $(Split-Path -Leaf (Get-Location)),

        [Parameter(Position = 1, HelpMessage = "指定模板路径（默认：env:USERPROFILE\.vscode\projectTemplate\ModernCpp）")]
        [string]$template = "$env:USERPROFILE\.vscode\projectTemplate\ModernCpp"
    )

    #──────────────── 0. 规范化项目名 ────────────────
    $ProjectNameRaw = $name
    $TemplatePath   = $template
    
    $ProjectName = $ProjectNameRaw.ToLower() -replace '[ _]', '-' -replace '[^a-z0-9\-]', ''
    if ($ProjectName -ne $ProjectNameRaw) {
        Write-Host "⚠️ 项目名 [$ProjectNameRaw] 已规范化为 [$ProjectName] 以符合 vcpkg 要求。" -ForegroundColor DarkYellow
    }

    #──────────────── 1. 可用工具检测 ────────────────
    $tools = @{
        git   = (Get-Command git   -EA SilentlyContinue)
        cmake = (Get-Command cmake -EA SilentlyContinue)
        vcpkg = (Get-Command vcpkg -EA SilentlyContinue)
    }

    foreach ($kvp in $tools.GetEnumerator()) {
        if (-not $kvp.Value) { Write-Warning "未找到 $($kvp.Key)，相关步骤将被跳过。" }
    }

    #──────────────── 2. 复制模板 ───────────────────
    if (-not (Test-Path $TemplatePath)) {
        Write-Error "模板路径 [$TemplatePath] 不存在"; return
    }

    Copy-Item "$TemplatePath\\*" . -Recurse -Force -EA Stop

    #──────────────── 3. 占位符替换 & 文件重命名 ──
    # 1) 替换文件内容中的 example → 项目名
    Get-ChildItem -Recurse -File -Include *.cpp,*.h,*.txt,*.cmake,CMakeLists.txt,vcpkg.json,launch.json,tasks.json |
        ForEach-Object {
            (Get-Content $_.FullName) -replace '\bexample\b', $ProjectName |
                Set-Content $_.FullName
        }

    # 2) 头文件改名
    $oldHeader = "src\include\example.h"
    if (Test-Path $oldHeader) {
        $newLeaf   = "$ProjectName.h"               # 仅文件名
        $newHeader = "src\include\$newLeaf"         # 完整路径备用

        Rename-Item -Path $oldHeader -NewName $newLeaf   # 在同目录重命名

        # 同步 main.cpp 的 #include "…"
        $includeNew = '"' + $newLeaf + '"'
        (Get-Content "src\source\main.cpp") `
            -replace '"example\.h"', $includeNew |
            Set-Content "src\source\main.cpp"
    }

    #──────────────── 4. vcpkg manifest ─────────────
    if ($tools.vcpkg) {
        $vcpkgExe     = $tools.vcpkg.Source
        $haveManifest = Test-Path vcpkg.json

        if ($haveManifest) {
            Write-Host "已存在 vcpkg.json，跳过 vcpkg new。" -ForegroundColor DarkYellow
        }
        else {
            $nameArg = "--name=$ProjectName"
            $versionArg = "--version=0.1.0"

            $vcpkgArgs = @(
                "new",
                $nameArg,
                $versionArg
            )

            Write-Host "▶ 运行: $vcpkgExe $($vcpkgArgs -join ' ')" -ForegroundColor Yellow
            & $vcpkgExe @vcpkgArgs
        }
    }

    #──────────────── 5. Git 初始提交 ───────────────
    if ($tools.git) {
        if (-not (Test-Path '.git')) { git init | Out-Null }
        git add . 2>$null
        git commit -m "Initialized $ProjectName project." 2>$null
    }

    #──────────────── 6. 打开 VS Code ───────────────
    if (Get-Command code -EA SilentlyContinue) {
        $main = "src\\source\\main.cpp"
        & code ($main -as [string])
    }

    Write-Host "✅ [$ProjectName] 初始化完成！" -ForegroundColor Green
}
#endregion