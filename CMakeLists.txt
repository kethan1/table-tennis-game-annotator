project(ncnn-webassembly-yolov5)

cmake_minimum_required(VERSION 3.10)

set(CMAKE_BUILD_TYPE release)

if(NOT WASM_FEATURE)
    message(FATAL_ERROR "You must pass cmake option -DWASM_FEATURE and possible values are basic, simd, threads and simd-threads")
endif()

set(ncnn_DIR "${CMAKE_CURRENT_SOURCE_DIR}/ncnn-20220701-webassembly/${WASM_FEATURE}/lib/cmake/ncnn")
find_package(ncnn REQUIRED)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -sFORCE_FILESYSTEM=1 -sINITIAL_MEMORY=512MB")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -sFORCE_FILESYSTEM=1 -sINITIAL_MEMORY=512MB")
set(CMAKE_EXECUTBLE_LINKER_FLAGS "${CMAKE_EXECUTBLE_LINKER_FLAGS} -sFORCE_FILESYSTEM=1 -sINITIAL_MEMORY=512MB")

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -sEXPORTED_FUNCTIONS='[\"_yolov5_ncnn\",\"_yolov5_ncnn_inference\"]' -sEXPORTED_RUNTIME_METHODS='[\"ccall\",\"cwrap\",\"getValue\",\"setValue\"]' --preload-file '${CMAKE_CURRENT_SOURCE_DIR}/models@.' -sLLD_REPORT_UNDEFINED -sERROR_ON_UNDEFINED_SYMBOLS=0 -sASSERTIONS")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -sEXPORTED_FUNCTIONS='[\"_yolov5_ncnn\",\"_yolov5_ncnn_inference\"]' -sEXPORTED_RUNTIME_METHODS='[\"ccall\",\"cwrap\",\"getValue\",\"setValue\"]' --preload-file '${CMAKE_CURRENT_SOURCE_DIR}/models@.' -sLLD_REPORT_UNDEFINED -sERROR_ON_UNDEFINED_SYMBOLS=0 -sASSERTIONS")
set(CMAKE_EXECUTBLE_LINKER_FLAGS "${CMAKE_EXECUTBLE_LINKER_FLAGS} -sEXPORTED_FUNCTIONS='[\"_yolov5_ncnn\",\"_yolov5_ncnn_inference\"]' -sEXPORTED_RUNTIME_METHODS='[\"ccall\",\"cwrap\",\"getValue\",\"setValue\"]' --preload-file '${CMAKE_CURRENT_SOURCE_DIR}/models@.' -sLLD_REPORT_UNDEFINED -sERROR_ON_UNDEFINED_SYMBOLS=0 -sASSERTIONS")

if(${WASM_FEATURE} MATCHES "threads")
    MESSAGE(STATUS "running threads")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fopenmp -pthread -s USE_PTHREADS=1 -s PTHREAD_POOL_SIZE=4")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fopenmp -pthread -s USE_PTHREADS=1 -s PTHREAD_POOL_SIZE=4")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fopenmp -pthread -s USE_PTHREADS=1 -s PTHREAD_POOL_SIZE=4")
endif()

MESSAGE(STATUS "building")

add_executable(yolov5-${WASM_FEATURE} src/yolov5.cpp src/yolov5ncnn.cpp src/globals.cpp)
MESSAGE(STATUS "linking")
target_link_libraries(yolov5-${WASM_FEATURE} ncnn)
MESSAGE(STATUS "copying files to output directory")
