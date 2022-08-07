let wasmModuleLoaded = new VariableWatcher(false);
let wasmModuleLoadedCallbacks = [];

var Module = {
    locateFile: file => `/static/wasm_modules/${file}`,
    print: text => console.log(text),
    onRuntimeInitialized: () => {
        wasmModuleLoaded.variable = true;
        for (let callback of wasmModuleLoadedCallbacks) {
            callback();
        }
    },
    yolov5_ncnn_inference_wrapper: (dst, w, h, outputArrayPtr, outputArr) => {
        Module._yolov5_ncnn_inference(dst, w, h, outputArrayPtr, outputArr.length);
    
        return Module.HEAPF32.subarray(outputArrayPtr >> 2, (outputArrayPtr >> 2) + 8);
    }
};

let dst = null;

window.addEventListener("load", event => {
    load_wasm_module();
    let fileInput = document.querySelector("input[name='file_upload']");
    let fileDisplayArea = document.getElementById("file_display_area");
    let styledFileInputUI = document.getElementById("styled_file_input_ui");
    let videoElement = document.getElementById("video_element");
    let submitGameplayButton = document.getElementById("submit_gameplay_button");
    let videoAnalyzationDiv = document.getElementById("video_analyzation");
    let canvas = document.getElementById("canvas_element");
    let toasts = document.getElementById("toasts");

    fileInput.addEventListener("change", event => {
        let fileName = fileInput.files[0].name;
        fileDisplayArea.innerText = fileName;
    });
    
    styledFileInputUI.addEventListener("dragover", event => {
        event.preventDefault();
    });

    styledFileInputUI.addEventListener("drop", event => {
        event.preventDefault();
      
        if (event.dataTransfer.items) {
            if (event.dataTransfer.items.length > 1) {
                showToast(toasts, "You can only upload one file at a time.", [], toastType="warning");
                return;
            } else if (event.dataTransfer.items.length === 0) {
                showToast(toasts, "No file selected.", [], toastType="warning");
                return;
            }
            const file = event.dataTransfer.items[0].getAsFile();
            if (!file.type.includes("video/")) {
                showToast(toasts, "You can only upload videos.", toastType="warning");
                return;
            }
            fileInput.files = event.dataTransfer.files;
        }
    });

    submitGameplayButton.addEventListener("click", event => {
        if (fileInput.files.length < 1) {
            showToast(toasts, "No file selected.", [], "warning");
            return;
        }

        videoAnalyzationDiv.classList.remove("hidden");
        videoAnalyzationDiv.classList.add("flex");
        videoElement.setAttribute("src", URL.createObjectURL(fileInput.files[0]));

        drawingLoop();
    });

    async function drawingLoop() {
        if (!wasmModuleLoaded.variable) {
            await wasmModuleLoaded.waitForSet();
        }

        await videoElement.play();

        const {videoWidth, videoHeight} = videoElement;
        videoElement.width = videoWidth;
        videoElement.height = videoHeight;
        let tempCanvas = new OffscreenCanvas(videoWidth, videoHeight);
        let tempCanvasCtx = tempCanvas.getContext("2d");
        let mat = new cv.Mat(videoHeight, videoWidth, cv.CV_8UC4);
        let sameDirBallDetections = [];
        let ball;

        const cap = new cv.VideoCapture(videoElement);

        let dstLength = (new ImageData(videoElement.videoWidth, videoElement.videoHeight)).data.length;
        dst = Module._malloc(dstLength);

        let [outputPtr, outputArray] = transferNumberArrayToHeap([0, 0, 0, 0, 0, 0, 0, 0], TYPES.f32);

        let frameIndex = 0;

        while (!videoElement.ended && !videoElement.paused) {
            frameIndex++;
            if (frameIndex % 2 == 0) {
                cap.read(mat);
                cv.imshow(tempCanvas, mat);
                videoElement.pause();

                let imageData = tempCanvasCtx.getImageData(0, 0, canvas.width, canvas.height);
                let data = imageData.data;

                Module.HEAPU8.set(data, dst);

                let detection = Module.yolov5_ncnn_inference_wrapper(dst, imageData.width, imageData.height, outputPtr, outputArray);

                ball = {};
                if (detection.some(item => item !== 0)) {
                    ball.xmin = detection[0];
                    ball.ymin = detection[1];
                    ball.xmax = detection[0] + detection[2];
                    ball.ymax = detection[1] + detection[3];
                    ball.width = detection[2];
                    ball.height = detection[3];
                    ball.label = detection[4];
                    ball.confidence = detection[5];

                    console.log(ball);

                    let {xmin, xmax, ymin, ymax} = ball;
                    sameDirBallDetections.push(ball);
                    if (sameDirBallDetections.length > 2) {
                        let prevPrevBall = sameDirBallDetections.at(-3);
                        let prevBall = sameDirBallDetections.at(-2);
                        let prevXMoved = prevPrevBall.xmin - prevBall.xmin;
                        let prevYMoved = prevPrevBall.ymin - prevBall.ymin;
                        let currentXMoved = prevBall.xmin - xmin;
                        let currentYMoved = prevBall.ymin - ymin;
                        if (prevXMoved * currentXMoved < 0 || prevYMoved * currentYMoved < 0) {
                            sameDirBallDetections = sameDirBallDetections.slice(-2);
                        } else {
                            let equation = calculateParabolaEquation(
                                avg(prevPrevBall.xmin, prevPrevBall.xmax),
                                avg(prevPrevBall.ymin, prevPrevBall.ymax),
                                avg(prevBall.xmin, prevBall.xmax),
                                avg(prevBall.ymin, prevBall.ymax),
                                avg(xmin, xmax),
                                avg(ymin, ymax),
                            );
                            for (let x=0; x < mat.cols; x+=5) {
                                cv.circle(
                                    mat,
                                    new cv.Point(x, Math.round(equation(x))),
                                    2,
                                    [0, 255, 0, 255],
                                    -1,
                                );
                            }

                            for (let pastBall of sameDirBallDetections) {
                                cv.circle(
                                    mat,
                                    new cv.Point(
                                        Math.round(avg(pastBall.xmin, pastBall.xmax)),
                                        Math.round(avg(pastBall.ymin, pastBall.ymax)),
                                    ),
                                    9,
                                    [255, 0, 0, 255],
                                    -1
                                );
                            }
                        }
                    }
                    cv.circle(
                        mat,
                        new cv.Point(
                            Math.round(avg(xmin, xmax)),
                            Math.round(avg(ymin, ymax)),
                        ),
                        9,
                        [255, 0, 0, 255],
                        -1
                    );             
                }

                cv.imshow(canvas, mat);
                await videoElement.play();
            } else {
                await new Promise(resolve => setTimeout(resolve, 25));
            }
        }
        mat.delete();
        Module._free(dst);
        Module._free(outputPtr);
    };
});
