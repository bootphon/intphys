cmake_minimum_required(VERSION 3.10)
project(intphys_postprocessing CXX)

set(CMAKE_BUILD_TYPE Release)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Boost 1.40 COMPONENTS program_options filesystem iostreams REQUIRED)
find_package(PNG REQUIRED)
find_package(Threads REQUIRED)

include_directories(
  ${Boost_INCLUDE_DIR}
  ${PNG_INCLUDE_DIRS}
  ${PROJECT_SOURCE_DIR}/include)

file(GLOB CXX_SRC ${PROJECT_SOURCE_DIR}/src/*.cc)
add_executable(postprocess ${CXX_SRC})
target_link_libraries(
  postprocess LINK_PUBLIC
  ${Boost_LIBRARIES}
  ${PNG_LIBRARIES}
  ${CMAKE_THREAD_LIBS_INIT})
