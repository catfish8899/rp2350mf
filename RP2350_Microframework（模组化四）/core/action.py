import ctypes
from ctypes import wintypes
import math
import time

def get_current_mouse_pos():
    """获取当前鼠标在屏幕上的物理坐标"""
    point = wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y

def smooth_move_to(controller, target_x, target_y):
    """拟人化平滑移动算法"""
    max_loops = 300 
    loop_count = 0
    while loop_count < max_loops:
        cur_x, cur_y = get_current_mouse_pos()
        diff_x = target_x - cur_x
        diff_y = target_y - cur_y
        
        if abs(diff_x) <= 3 and abs(diff_y) <= 3: break
        
        distance = math.sqrt(diff_x**2 + diff_y**2)
        if distance > 100: speed_factor = 0.15 
        elif distance > 20: speed_factor = 0.3
        else: speed_factor = 0.6
            
        move_x = int(diff_x * speed_factor)
        move_y = int(diff_y * speed_factor)
        
        max_step = 15
        move_x = max(-max_step, min(max_step, move_x))
        move_y = max(-max_step, min(max_step, move_y))
        
        if move_x == 0 and abs(diff_x) > 0: move_x = 1 if diff_x > 0 else -1
        if move_y == 0 and abs(diff_y) > 0: move_y = 1 if diff_y > 0 else -1
        
        controller.send_move(move_x, move_y)
        time.sleep(0.015) 
        loop_count += 1
        
    cur_x, cur_y = get_current_mouse_pos()
    final_dx = target_x - cur_x
    final_dy = target_y - cur_y
    if abs(final_dx) > 0 or abs(final_dy) > 0:
        controller.send_move(final_dx, final_dy)
