const TYPES = {
    i8: { array: Int8Array, heap: "HEAP8" },
    i16: { array: Int16Array, heap: "HEAP16" },
    i32: { array: Int32Array, heap: "HEAP32" },
    f32: { array: Float32Array, heap: "HEAPF32" },
    f64: { array: Float64Array, heap: "HEAPF64" },
    u8: { array: Uint8Array, heap: "HEAPU8" },
    u16: { array: Uint16Array, heap: "HEAPU16" },
    u32: { array: Uint32Array, heap: "HEAPU32" }
};


class VariableWatcher {
    constructor(variable) {
        this._variable = variable;
        this.callbacks = [];
    }

    get variable() { return this._variable; }
    set variable(newVar) {
        this._variable = newVar;
        for (let callback of this.callbacks) {
            callback();
        }
        this.callbacks = [];
    }

    waitForSet() {
        return new Promise((fulfilled, rejected) => {
            this.callbacks.push(fulfilled);
        });
    }
}


function avg(a, b) {
    return (a + b) / 2;
}


async function load_wasm_module() {
    let has_simd = await wasmFeatureDetect.simd();
    let has_threads = await wasmFeatureDetect.threads();
    let yolov5_module_name = "/static/wasm_modules/yolov5";
    
    if (has_simd) {
        yolov5_module_name += "-simd";
    }
    if (has_threads) {
        yolov5_module_name += "-threads";
    }
    if (!(has_simd || has_threads)) {
        yolov5_module_name += "-basic";
    }

    console.log(`Loading ${yolov5_module_name}`);

    let yolov5wasm = `${yolov5_module_name}.wasm`;
    let yolov5js = `${yolov5_module_name}.js`;

    let response = await fetch(yolov5wasm);
    let buffer = await response.arrayBuffer();
    Module.wasmBinary = buffer;
    let script = document.createElement("script");
    script.src = yolov5js;
    script.onload = () => {
        console.log("Emscripten boilerplate loaded.");
    }
    document.body.appendChild(script);
}


function showToast(toastContainer, message="", positionClasses=[], toastType="info", timeout=3000) {
    if (!["info", "success", "warning", "danger"].includes(toastType)) {
        toastType = "info";
    }
    let toastWrapper = document.createElement("div");
    toastWrapper.classList.add("toast", "opacity-100", ...positionClasses);
    let toast = document.createElement("div");
    toast.classList.add("alert", `alert-${toastType}`);
    let messageSpan = document.createElement("span");
    messageSpan.innerText = message;
    toast.appendChild(messageSpan);
    toastWrapper.appendChild(toast);
    toastContainer.appendChild(toastWrapper);
    setTimeout(() => {
        toast.classList.add("animate-fade");
        setTimeout(() => {
            toastWrapper.remove();
        }, 500)
    }, timeout);
}

function transferNumberArrayToHeap(array, type) {
    const typedArray = type.array.from(array);
    const heapPointer = Module._malloc(
        typedArray.length * typedArray.BYTES_PER_ELEMENT
    );

    Module[type.heap].set(typedArray, heapPointer >> 2);

    return [heapPointer, typedArray];
}
