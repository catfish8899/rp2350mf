# ==========================================
# 用户配置区域
# ==========================================
IMAGE_1_PATH = 'target1.png'      # 第一步要找的图片 (双击)
IMAGE_2_PATH = 'target2.png'      # 第二步要找的图片 (单击并输入)

MATCH_THRESHOLD = 0.8             # 图像识别的严谨度
TIMEOUT_SECONDS = 30              # 每一步寻找目标的耐心值（秒）
COM_PORT = 'COM4'                 # RP2350 的实际端口号
BAUD_RATE = 115200                # 串口通信速率
INPUT_STRING = "1#Aa甘蓝"         # 第二步要输入的内容
