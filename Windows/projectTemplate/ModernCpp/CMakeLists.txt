cmake_minimum_required(VERSION 3.15)
project(example LANGUAGES C CXX)

# Set UTF-8 as default encoding (source and execution character sets)
if (MSVC)
    add_compile_options(/utf-8)
endif()

# C++20 as default
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ── Output directories ────────────────────────────────────────────
set(BASE_OUTPUT_DIR "${CMAKE_SOURCE_DIR}/target")

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY            "${BASE_OUTPUT_DIR}/bin")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG      "${BASE_OUTPUT_DIR}/bin/Debug")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE    "${BASE_OUTPUT_DIR}/bin/Release")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${BASE_OUTPUT_DIR}/bin/MinSizeRel")

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY            "${BASE_OUTPUT_DIR}/lib")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_DEBUG      "${BASE_OUTPUT_DIR}/lib/Debug")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE    "${BASE_OUTPUT_DIR}/lib/Release")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_MINSIZEREL "${BASE_OUTPUT_DIR}/lib/MinSizeRel")

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY            "${BASE_OUTPUT_DIR}/lib")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_DEBUG      "${BASE_OUTPUT_DIR}/lib/Debug")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_RELEASE    "${BASE_OUTPUT_DIR}/lib/Release")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_MINSIZEREL "${BASE_OUTPUT_DIR}/lib/MinSizeRel")

# ── Targets ───────────────────────────────────────────────────────
add_executable(${PROJECT_NAME}
    src/source/main.cpp
)

target_include_directories(${PROJECT_NAME}
    PRIVATE ${CMAKE_SOURCE_DIR}/src/include
)

# Pull & link fmt via vcpkg
#find_package(fmt CONFIG REQUIRED)

#target_link_libraries(${PROJECT_NAME} PRIVATE fmt::fmt)