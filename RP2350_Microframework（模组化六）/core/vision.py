# ===================================================================================
# 模块名称：视觉识别引擎 (vision.py)
# 模块功能：基于 OpenCV 与 MSS 提供高性能的屏幕截图与模板匹配能力。
#           支持多显示器环境及包含中文字符的复杂文件路径解析。
# ===================================================================================
import cv2
import numpy as np
import mss
import time
import sys
import os

def find_image_on_screen(template_path, threshold=0.8):
    """
    执行单次屏幕模板匹配算法。
    利用 numpy 字节流读取机制，完美兼容 Windows 环境下的中文及特殊字符路径。
    
    参数:
        template_path (str): 视觉模板图像的绝对路径
        threshold (float): 匹配置信度阈值 (0.0 - 1.0)
        
    返回:
        tuple: 匹配成功返回目标中心点绝对坐标 (x, y)，失败返回 None
    """
    try:
        if not os.path.exists(template_path):
            print(f"[视觉引擎异常] 模板文件缺失: {template_path}")
            return None
            
        # 采用 numpy 读取文件流并交由 cv2 解码，规避 cv2.imread 的路径编码缺陷
        template_data = np.fromfile(template_path, dtype=np.uint8)
        template = cv2.imdecode(template_data, cv2.IMREAD_COLOR)
        
        if template is None: 
            return None
            
        template_h, template_w = template.shape[:2]
        
        # 捕获屏幕帧 (支持多显示器架构，此处默认捕获主显示器 monitors[1])
        with mss.mss() as sct:
            monitor = sct.monitors[1] 
            screenshot = np.array(sct.grab(monitor))
            screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
            
            # 执行归一化相关系数匹配算法 (TM_CCOEFF_NORMED)
            result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                # 计算目标中心点并映射至全局物理坐标系
                center_x = max_loc[0] + template_w // 2 + monitor["left"]
                center_y = max_loc[1] + template_h // 2 + monitor["top"]
                return center_x, center_y
            else:
                return None
    except Exception as e: 
        print(f"[视觉引擎异常] 图像处理过程发生错误: {e}")
        return None

def wait_and_find_image_with_retry(image_path, timeout, threshold=0.8):
    """
    带超时控制与异常干预机制的阻塞式视觉定位函数。
    在指定超时时间内持续轮询屏幕帧，超时后提供人工干预选项。
    
    参数:
        image_path (str): 视觉模板图像路径
        timeout (int): 最大轮询超时时间（秒）
        threshold (float): 匹配置信度阈值
        
    返回:
        tuple: 目标坐标 (x, y) 或在用户选择跳过时返回 None
    """
    while True:
        start_time = time.time()
        print(f"[视觉引擎] 正在扫描屏幕特征: '{os.path.basename(image_path)}' ...")
        
        while (time.time() - start_time) < timeout:
            coords = find_image_on_screen(image_path, threshold)
            if coords:
                return coords
            time.sleep(0.5)
            sys.stdout.write(".")
            sys.stdout.flush()
        
        # 超时后的异常处理调度
        print(f"\n[调度警告] 视觉匹配超时 ({timeout}s)，未能锁定目标特征。")
        print("请选择干预策略: [1] 重新扫描  [2] 忽略并跳过当前节点  [3] 终止整个自动化任务")
        choice = input("请输入策略编号 (1/2/3): ").strip()
        
        if choice == '1':
            continue
        elif choice == '2':
            return None
        elif choice == '3':
            raise KeyboardInterrupt("接收到用户手动终止指令")
        else:
            print("[系统提示] 输入无效，默认执行重新扫描策略。")
