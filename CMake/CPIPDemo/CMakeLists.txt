cmake_minimum_required(VERSION 3.24)
project(CPIPDemo C)

set(CMAKE_C_STANDARD 99)

include_directories(
        sys
        usr
)

add_executable(CPIPDemo main.c usr/user.h sys/system.h)
