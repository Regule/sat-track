cmake_minimum_required(VERSION 3.0)
project(MWL-sattrack)

# Set the source and header directories
set(SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)
set(HEADER_DIR ${CMAKE_CURRENT_SOURCE_DIR}/include)

# Collect all source files
file(GLOB_RECURSE SOURCE_FILES ${SOURCE_DIR}/*.cpp)

# Collect all header files
file(GLOB_RECURSE HEADER_FILES ${HEADER_DIR}/*.h)

# Add the source and header directories to the include paths
include_directories(${HEADER_DIR})

# Create an executable target from the collected source files
add_executable(YourExecutable ${SOURCE_FILES} ${HEADER_FILES})

