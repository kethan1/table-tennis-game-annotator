window.addEventListener("load", (event) => {
    let fileInput = document.querySelector("input[name='file_upload']");
    let fileDisplayArea = document.getElementById("file_display_area");
    let styledFileInputUI = document.getElementById("styled_file_input_ui");
    let videoElement = document.getElementById("video_element");
    let submitGameplayButton = document.getElementById("submit_gameplay_button");
    let videoAnalyzationDiv = document.getElementById("video_analyzation");
    let canvas = document.getElementById("canvas_element");
    // let fakeCanvasHeightDiv = document.getElementById("fake_canvas_height_div");
    // let skipToFrame = document.getElementById("skip_to_frame");
    // let frameInput = document.getElementById("frame_input");
    let toasts = document.getElementById("toasts");

    function showToast(message="", positionClasses=[], toastType="info", timeout=3000) {
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
        toasts.appendChild(toastWrapper);
        setTimeout(() => {
            toast.classList.add("animate-fade");
            setTimeout(() => {
                toastWrapper.remove();
            }, 500)
        }, timeout);
    }

    globalThis.showToast = showToast;

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
                showToast("You can only upload one file at a time.", [], toastType="warning");
                return;
            } else if (event.dataTransfer.items.length === 0) {
                showToast("No file selected.", [], toastType="warning");
                return;
            }
            const file = event.dataTransfer.items[0].getAsFile();
            if (!file.type.includes("video/")) {
                showToast("You can only upload videos.", toastType="warning");
                return;
            }
            fileInput.files = event.dataTransfer.files;
        }
    });

    submitGameplayButton.addEventListener("click", event => {
        if (fileInput.files.length < 1) {
            var toastType;
            showToast("No file selected.", [], toastType="warning");
            return;
        }

        videoAnalyzationDiv.classList.remove("hidden");
        videoAnalyzationDiv.classList.add("flex");
        videoElement.setAttribute("src", URL.createObjectURL(fileInput.files[0]));

        drawingLoop();
    });

    // skipToFrame.addEventListener("click", event => {
    //     videoElement.pause();
    //     videoElement.play();
    //     skipFrames(frameInput.value);
    // });

    let frameIndex = 0;

    async function drawingLoop() {
        await videoElement.play();

        const {videoWidth, videoHeight} = videoElement;
        videoElement.width = videoWidth;
        videoElement.height = videoHeight;
        let tempCanvas = new OffscreenCanvas(videoWidth, videoHeight);
        let mat = new cv.Mat(videoHeight, videoWidth, cv.CV_8UC4);
        let sameDirBallDetections = [];

        const cap = new cv.VideoCapture(videoElement);

        while (true) {
            frameIndex++;
            cap.read(mat);
            videoElement.pause();
            cv.imshow(tempCanvas, mat);
            const blob = await tempCanvas.convertToBlob();

            let formData = new FormData();
            formData.append("file", blob);

            let response = await fetch("/api/v1/detect-ball", {
                method: "POST",
                body: formData,
            });
            let ball = await response.json();

            if (Object.keys(ball).length) {
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
                            avg(prevPrevBall.ymim, prevPrevBall.ymax),
                            avg(prevBall.xmin, prevBall.xmax),
                            avg(prevBall.ymin, prevBall.ymax),
                            avg(xmin, xmax),
                            avg(ymin, ymax),
                        );
                        for (let x=0; x < mat.shape[1]; x+=5) {
                            cv.circle(
                                mat,
                                new cv.Point(x, equation(x)),
                                2,
                                [0, 255, 0, 255],
                                -1,
                            );
                        }
                    }
                }
                for (let pastBall of sameDirBallDetections) {
                    cv.circle(mat, new cv.Point(avg(pastBall.xmin, pastBall.xmax), avg(pastBall.ymin, pastBall.ymax)), 9, [255, 0, 0, 255], -1);
                }
            }

            cv.imshow(canvas, mat);
            await videoElement.play();
            if (videoElement.ended || frameIndex === 30) {
                break;
            }
        }
        mat.delete();
        
        // if (frameIndex % 5 === 0) {
        //     const bitmap = await createImageBitmap(videoElement);
        //     videoElement.pause();
            
        //     if (!heightsSet) {
        //         canvas.height = canvasDrawing.height = fakeCanvasHeightDiv.height = bitmap.height * canvas.width / bitmap.width;
        //         heightsSet = true;
        //     }
        //     const bitmap_ctx = canvas.getContext("bitmaprenderer");
        //     bitmap_ctx.transferFromImageBitmap(bitmap);
        //     const blob = await new Promise((res) => canvas.toBlob(res));
            
        //     let formData = new FormData();
        //     formData.append("file", blob);

        //     let response = await fetch("/api/v1/detect-ball", {
        //         method: "POST",
        //         body: formData,
        //     })
        //     let data = await response.json();
        //     console.log(data);
        //     if (Object.keys(data).length) {
        //         ctx.beginPath();
        //         let widthRatio = canvas.width / videoElement.videoWidth;
        //         let heightRatio = canvas.height / videoElement.videoHeight;
        //         console.log(Math.round(avg(data.xmin, data.xmax) * widthRatio), Math.round(avg(data.ymin, data.ymax) * heightRatio), widthRatio, heightRatio);
        //         ctx.arc(Math.round(avg(data.xmin, data.xmax) * widthRatio), Math.round(avg(data.ymin, data.ymax) * heightRatio), 4, 0, 2 * Math.PI);
        //         ctx.fillStyle = "red";
        //         ctx.fill();
        //         ctx.lineWidth = 2;
        //         ctx.stroke();
        //     }
        // }

        // if (!videoElement.ended) {
        //     // TODO: send to server and ask for ball detection stuff and draw
        //     await videoElement.play();
        //     frameIndex += 1;
        //     videoElement.requestVideoFrameCallback(drawingLoop);
        // }
    };

    function avg(a, b) {
        return (a + b) / 2;
    }

    // function skipFrames(frames, callback=drawingLoop) {
    //     console.log(1, frames);
    //     if (frames > 0) {
    //         videoElement.requestVideoFrameCallback((timestamp, frame) => skipFrames(frames - 1, callback));
    //     } else {
    //         console.log(2)
    //         videoElement.requestVideoFrameCallback(callback);
    //     }
    // }
});
