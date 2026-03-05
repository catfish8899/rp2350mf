import cv2
import numpy as np
import mss
import time
import sys

def find_image_on_screen(template_path, threshold=0.8):
    """使用 OpenCV 进行屏幕找图"""
    try:
        template = cv2.imread(template_path)
        if template is None: return None
        template_h, template_w = template.shape[:2]
        
        with mss.mss() as sct:
            monitor = sct.monitors[1] # 主显示器
            screenshot = np.array(sct.grab(monitor))
            screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
            
            result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                center_x = max_loc[0] + template_w // 2 + monitor["left"]
                center_y = max_loc[1] + template_h // 2 + monitor["top"]
                return center_x, center_y
            else:
                return None
    except: 
        return None

def wait_and_find_image_with_retry(image_path, timeout, threshold=0.8):
    """带重试/跳过/取消机制的找图函数"""
    while True:
        start_time = time.time()
        print(f"正在寻找图片: '{image_path}' ...")
        while (time.time() - start_time) < timeout:
            coords = find_image_on_screen(image_path, threshold)
            if coords:
                return coords
            time.sleep(0.5)
            sys.stdout.write(".")
            sys.stdout.flush()
        
        print(f"\n[失败] 未能在 {timeout} 秒内找到图片 '{image_path}'。")
        print("请选择操作: [1] 重试  [2] 跳过这一步  [3] 取消整体任务")
        choice = input("请输入选项 (1/2/3): ").strip()
        if choice == '1':
            continue
        elif choice == '2':
            return None
        elif choice == '3':
            raise KeyboardInterrupt("用户取消了整体任务")
        else:
            print("无效输入，默认重试。")
