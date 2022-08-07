1. Install emscripten
```shell
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install latest
./emsdk activate latest

source emsdk/emsdk_env.sh
```

2. Download and extract ncnn webassembly package
```shell
wget https://github.com/Tencent/ncnn/releases/download/20220721/ncnn-20220701-webassembly.zip
unzip ncnn-20220721-webassembly.zip
```

3. Build four WASM feature variants (this doesn't seem to work in Powershell, so on Windows, use Linux with WSL)
```shell
mkdir build
cd build
cmake -DCMAKE_TOOLCHAIN_FILE=$EMSDK/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake -DWASM_FEATURE=basic ..
make -j4
cmake -DCMAKE_TOOLCHAIN_FILE=$EMSDK/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake -DWASM_FEATURE=simd ..
make -j4
cmake -DCMAKE_TOOLCHAIN_FILE=$EMSDK/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake -DWASM_FEATURE=threads ..
make -j4
cmake -DCMAKE_TOOLCHAIN_FILE=$EMSDK/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake -DWASM_FEATURE=simd-threads ..
make -j4
```

4. Deploy the *.data *.js *.wasm and *.html files to your web server
```
# deploy files
static/wasm_module/
├── yolov5-basic.data
├── yolov5-basic.js
├── yolov5-basic.wasm
├── yolov5-simd.data
├── yolov5-simd.js
├── yolov5-simd-threads.data
├── yolov5-simd-threads.js
├── yolov5-simd-threads.wasm
├── yolov5-simd-threads.worker.js
├── yolov5-simd.wasm
├── yolov5-threads.data
├── yolov5-threads.js
├── yolov5-threads.wasm
└── yolov5-threads.worker.js
```
