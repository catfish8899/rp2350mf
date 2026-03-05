import cv2
import numpy as np
import mss

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
