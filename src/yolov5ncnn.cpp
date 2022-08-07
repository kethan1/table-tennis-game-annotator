// Copyright (C) 2022 THL A29 Limited, a Tencent company. All rights reserved.
// Changes copyright (C) 2022 Kethan Vegunta. All rights reserved.
//
// This file is licensed under the BSD 3-Clause License (the "License"); you may not use this file except
// in compliance with the License. You may obtain a copy of the License at
//
// https://opensource.org/licenses/BSD-3-Clause
//
// Unless required by applicable law or agreed to in writing, software distributed
// under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.

#include <simpleocv.h>

#include "globals.hpp"
#include "stdint.h"
#include "yolov5.hpp"

static YOLOv5 *g_yolov5 = 0;

static void load_YOLOv5() {
    if (!g_yolov5) {
        g_yolov5 = new YOLOv5;
        g_yolov5->load();
    }
}

static void run_inference(cv::Mat &rgba, std::vector<Detection> &objects) {
    load_YOLOv5();
    g_yolov5->detect(rgba, objects);
}

static void on_image_render(cv::Mat &rgba) {
    load_YOLOv5();

    std::vector<Detection> objects;
    run_inference(rgba, objects);

    g_yolov5->draw(rgba, objects);
}

#ifdef __EMSCRIPTEN_PTHREADS__

static const unsigned char *rgba_data = 0;
static int w = 0;
static int h = 0;
static const unsigned char *rgba_data2 = 0;
static int w2 = 0;
static int h2 = 0;
float *output_arr;
int output_arr_length;
static uint16_t *return_value;

static ncnn::Mutex lock;
static ncnn::ConditionVariable condition;
static ncnn::Mutex lock2;
static ncnn::ConditionVariable condition2;

static ncnn::Mutex finish_lock;
static ncnn::ConditionVariable finish_condition;
static ncnn::Mutex finish_lock2;
static ncnn::ConditionVariable finish_condition2;

static void worker() {
    while (true) {
        lock.lock();
        while (rgba_data == 0) {
            condition.wait(lock);
        }

        cv::Mat rgba(h, w, CV_8UC4, (void *)rgba_data);

        on_image_render(rgba);

        rgba_data = 0;

        lock.unlock();

        finish_lock.lock();
        finish_condition.signal();
        finish_lock.unlock();
    }
}

static void worker2() {
    while (true) {
        lock2.lock();
        while (rgba_data2 == 0) {
            condition.wait(lock2);
        }
        rgba_data2 = 0;

        lock2.unlock();

        cv::Mat rgba(h, w, CV_8UC4, (void *)rgba_data2);
        std::vector<Detection> objects;
        run_inference(rgba, objects);

        Detection max = *std::max_element(objects.begin(),
                                          objects.end(),
                                          [](const Detection &a, const Detection &b) { return a.prob < b.prob; });

        finish_lock2.lock();
        finish_condition2.signal();
        finish_lock2.unlock();

        return_value[0] = max.rect.x;
        return_value[1] = max.rect.y;
        return_value[2] = max.rect.width;
        return_value[3] = max.rect.height;
        return_value[4] = max.label;
        return_value[5] = max.prob;
    }
}

#include <thread>
static std::thread t(worker);

extern "C" {

    void yolov5_ncnn(unsigned char *_rgba_data, int _w, int _h, float *_output_arr, int _output_arr_length) {
        lock.lock();
        while (rgba_data != 0) {
            condition.wait(lock);
        }

        rgba_data = _rgba_data;
        w = _w;
        h = _h;
        output_arr = _output_arr;
        output_arr_length = _output_arr_length;

        lock.unlock();

        condition.signal();

        // wait for finished
        finish_lock.lock();
        while (rgba_data != 0) {
            finish_condition.wait(finish_lock);
        }
        finish_lock.unlock();
    }

    uint16_t *yolov5_ncnn_inference(unsigned char *_rgba_data, int _w, int _h) {
        lock2.lock();
        while (rgba_data != 0) {
            condition2.wait(lock);
        }

        rgba_data2 = _rgba_data;
        w2 = _w;
        h2 = _h;

        lock2.unlock();

        condition2.signal();

        // wait for finished
        finish_lock2.lock();
        while (rgba_data != 0) {
            finish_condition2.wait(finish_lock);
        }
        finish_lock2.unlock();

        return return_value;
    }
}

#else  // __EMSCRIPTEN_PTHREADS__

extern "C" {
    void yolov5_ncnn(unsigned char *rgba_data, int w, int h) {
        cv::Mat rgba(h, w, CV_8UC4, (void *)rgba_data);

        on_image_render(rgba);
    }

    void yolov5_ncnn_inference(unsigned char *rgba_data, int w, int h, float *output_arr, int output_arr_length) {
        cv::Mat rgba(h, w, CV_8UC4, (void *)rgba_data);
        std::vector<Detection> objects;
        run_inference(rgba, objects);

        if (objects.size() > 0) {
            Detection max = *std::max_element(objects.begin(),
                                              objects.end(),
                                              [](const Detection &a, const Detection &b) { return a.prob < b.prob; });

            output_arr[0] = max.rect.x;
            output_arr[1] = max.rect.y;
            output_arr[2] = max.rect.width;
            output_arr[3] = max.rect.height;
            output_arr[4] = max.label;
            output_arr[5] = max.prob;
        } else {
            for (int i = 0; i < output_arr_length; i++) {
                output_arr[i] = 0;
            }
        }
    }
}

#endif  // __EMSCRIPTEN_PTHREADS__
