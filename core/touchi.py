import os
import random
from PIL import Image, ImageDraw
from datetime import datetime
import glob
import math
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
items_dir = os.path.join(script_dir, "items")
expressions_dir = os.path.join(script_dir, "expressions")
output_dir = os.path.join(script_dir, "output")

os.makedirs(items_dir, exist_ok=True)
os.makedirs(expressions_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Define border color
ITEM_BORDER_COLOR = (100, 100, 110)
BORDER_WIDTH = 1

def get_size(size_str):
    if 'x' in size_str:
        parts = size_str.split('x')
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            return int(parts[0]), int(parts[1])
    return 1, 1

# 物品价值映射表
ITEM_VALUES = {
    # Blue items (蓝色物品)
    "blue_1x1_cha": 10030, "blue_1x1_jidianqi": 10459, "blue_1x1_kele": 12654,
    "blue_1x1_paotengpian": 9908, "blue_1x1_sanjiao": 11984, "blue_1x1_shangyewenjian": 7812,
    "blue_1x1_yinbi": 8661, "blue_1x2_kafeihu": 16604, "blue_1x2_nvlang": 15242,
    "blue_1x2_wangyuanjing": 11389, "blue_1x2_yandou": 15504, "blue_1x2_zidanlingjian": 20405,
    "blue_1x3_luyin": 28296, "blue_2x1_qiangxieliangjian": 17558, "blue_2x1_xianwei": 25325,
    "blue_2x2_meiqiguan": 21715, "blue_2x2_wenduji": 17403, "blue_2x2_wurenji": 98589,
    "blue_2x2_youqi": 21361, "blue_2x2_zazhi": 16694, "blue_2x3_shuini": 50545,
    "blue_3x1_guju": 19900, "blue_4x2_tainengban": 24434,
    
    # Gold items (金色物品)
    "gold_1x1_1": 1936842, "gold_1x1_2": 1576462, "gold_1x1_chuliqi": 105766,
    "gold_1x1_cpu": 64177, "gold_1x1_duanzi": 58182, "gold_1x1_huoji": 61611,
    "gold_1x1_jinbi": 57741, "gold_1x1_jingtou": 105244, "gold_1x1_jiubei": 62760,
    "gold_1x1_kafei": 68304, "gold_1x1_mofang": 94669, "gold_1x1_ranliao": 68336,
    "gold_1x1_shouji": 61319, "gold_1x1_tuzhi": 67208, "gold_1x2_longshelan": 80863,
    "gold_1x2_maixiaodan": 0, "gold_1x2_taoyong": 90669, "gold_2x2_danfan": 129910,
    "gold_2x2_dianlan": 447649, "gold_2x2_tongxunyi": 501153, "gold_2x2_wangyuanjing": 93442,
    "gold_2x2_zhayao": 131427, "gold_2x2_zhong": 58000, "gold_2x3_ranliaodianchi": 378482,
    "gold_3x1_touguan": 143697, "gold_3x2_": 394788, "gold_3x2_bendishoushi": 424032,
    "gold_4x3_fuwuqi": 593475,
    
    # Purple items (紫色物品)
    "purple_1x1_1": 338091, "purple_1x1_2": 824218, "purple_1x1_3": 335980, "purple_1x1_4": 1056413,
    "purple_1x1_erhuan": 13172, "purple_1x1_ganraoqi": 12079, "purple_1x1_jiandiebi": 21086,
    "purple_1x1_junshiqingbao": 12554, "purple_1x1_neicun": 26305, "purple_1x1_rexiangyi": 55993,
    "purple_1x1_shoubing": 34616, "purple_1x1_shoudian": 19861, "purple_1x1_wandao": 24128,
    "purple_1x2_dangan": 22530, "purple_1x2_fuliaobao": 18685, "purple_1x2_jiuhu": 24732,
    "purple_1x2_shizhang": 20464, "purple_1x2_shuihu": 32154, "purple_1x2_tezhonggang": 44260,
    "purple_1x2_tideng": 36019, "purple_2x1_niuniu": 17145, "purple_2x2_lixinji": 60559,
    "purple_2x2_shouju": 51703, "purple_2x2_xueyayi": 37439, "purple_2x2_zhuban": 47223,
    "purple_2x3_dentai": 112592, "purple_3x2_bishou": 114755, "purple_3x2_diandongche": 66852,
    
    # Red items (红色物品)
    "red_1x1_1": 4085603, "red_1x1_2": 6775951, "red_1x1_3": 4603790,
    "red_1x1_huaibiao": 214532, "red_1x1_jixiebiao": 210234, "red_1x1_xin": 13581911,
    "red_1x1_yuzijiang": 174537, "red_1x2_jintiao": 330271, "red_1x2_maixiaodan": 0,
    "red_1x2_xiangbin": 337113, "red_2x1_huashi": 346382, "red_2x1_xianka": 332793,
    "red_2x2_jingui": 440000, "red_2x2_junyongji": 534661, "red_2x2_lu": 434781,
    "red_2x2_tianyuandifang": 537003, "red_2x2_weixing": 245000, "red_2x3_liushengji": 1264435,
    "red_2x3_rentou": 1300362, "red_2x3_yiliaobot": 1253570, "red_3x2_buzhanche": 1333684,
    "red_3x2_dainnao": 3786322, "red_3x2_paodan": 1440722, "red_3x2_zhuangjiadianchi": 1339889,
    "red_3x3_banzi": 2111841, "red_3x3_chaosuan": 2003197, "red_3x3_fanyinglu": 2147262,
    "red_3x3_huxiji": 10962096, "red_3x3_tanke": 2113480, "red_3x3_wanjinleiguan": 3646401,
    "red_3x3_zongheng": 3337324, "red_3x4_daopian": 1427562, "red_3x4_ranliao": 1400000,
    "red_4x1_huatang": 676493, "red_4x3_cipanzhenlie": 1662799, "red_4x3_dongdidianchi": 1409728
}

# 稀有物品列表 - 概率为原来的三分之一
RARE_ITEMS = {
    "gold_1x1_1", "gold_1x1_2", "red_1x1_1", "red_1x1_2", "red_1x1_3", 
    "red_3x3_huxiji", "gold_3x2_bendishoushi", "purple_1x1_2", "purple_1x1_4","purple_1x1_3", "purple_1x1_1","red_4x3_cipanzhenlie","red_4x3_dongdidianchi","red_3x4_daopian","red_3x3_wanjinleiguan","red_3x3_tanke"
}

# 超稀有物品列表 - 概率为0.0009%
ULTRA_RARE_ITEMS = {
    "red_1x1_xin"
}

def get_item_value(item_name):
    """获取物品价值"""
    return ITEM_VALUES.get(item_name, 1000)

# 缓存物品列表以提高性能
_items_cache = None
_items_cache_time = 0
CACHE_DURATION = 300  # 5分钟缓存

def load_items():
    global _items_cache, _items_cache_time
    import time
    
    current_time = time.time()
    # 检查缓存是否有效
    if _items_cache is not None and (current_time - _items_cache_time) < CACHE_DURATION:
        return _items_cache
    
    items = []
    valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')  # 使用元组提高性能
    
    try:
        for filename in os.listdir(items_dir):
            if not filename.lower().endswith(valid_extensions):
                continue
                
            file_path = os.path.join(items_dir, filename)
            if not os.path.isfile(file_path):
                continue
                
            parts = os.path.splitext(filename)[0].split('_')
            level = parts[0].lower() if len(parts) >= 2 else "purple"
            size = parts[1] if len(parts) >= 2 else "1x1"
            width, height = get_size(size)
            
            # 获取物品基础名称（不含扩展名）
            item_base_name = os.path.splitext(filename)[0]
            item_value = get_item_value(item_base_name)
            
            items.append({
                "path": file_path, "level": level, "size": size,
                "grid_width": width, "grid_height": height,
                "base_name": item_base_name, "value": item_value,
                "name": f"{item_base_name} (价值: {item_value:,})"
            })
    except Exception as e:
        print(f"Error loading items: {e}")
        return []
    
    # 更新缓存
    _items_cache = items
    _items_cache_time = current_time
    return items

def load_expressions():
    expressions = {}
    valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    for filename in os.listdir(expressions_dir):
        file_path = os.path.join(expressions_dir, filename)
        if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in valid_extensions):
            expressions[os.path.splitext(filename)[0]] = file_path
    return expressions

def place_items(items, grid_width, grid_height, total_grid_size=2):
    # 优化：使用一维数组代替二维数组提高性能
    grid = [0] * (grid_width * grid_height)
    placed = []
    
    # 修复大物品放置偏向问题：使用随机顺序而不是按尺寸排序
    # 这样可以给所有物品相等的放置机会，避免大物品优先占用空间
    sorted_items = items.copy()
    random.shuffle(sorted_items)
    
    for item in sorted_items:
        # Generate orientation options (consider rotation)
        orientations = [(item["grid_width"], item["grid_height"], False)]
        if item["grid_width"] != item["grid_height"]:
            orientations.append((item["grid_height"], item["grid_width"], True))
        
        placed_success = False
        
        # Try to place the item - 优化循环
        for y in range(grid_height):
            if placed_success:
                break
            for x in range(grid_width):
                if placed_success:
                    break
                for width, height, rotated in orientations:
                    # 新的边界检查：物品左上角必须在放置格子内，但物品整体必须在总格子内
                    # 左上角在放置格子内的检查（x, y必须在grid_width, grid_height范围内）
                    if x >= grid_width or y >= grid_height:
                        continue
                    
                    # 物品整体在总格子内的检查
                    if x + width > total_grid_size or y + height > total_grid_size:
                        continue
                        
                    # Check if space is available - 只检查在放置格子内的部分
                    can_place = True
                    for i in range(height):
                        if not can_place:
                            break
                        for j in range(width):
                            # 只检查在放置格子范围内的格子是否被占用
                            check_x = x + j
                            check_y = y + i
                            if check_x < grid_width and check_y < grid_height:
                                if grid[check_y * grid_width + check_x] != 0:
                                    can_place = False
                                    break
                    
                    if can_place:
                        # Mark space as occupied - 只标记在放置格子内的部分
                        for i in range(height):
                            for j in range(width):
                                mark_x = x + j
                                mark_y = y + i
                                if mark_x < grid_width and mark_y < grid_height:
                                    grid[mark_y * grid_width + mark_x] = 1
                        
                        placed.append({
                            "item": item, 
                            "x": x, 
                            "y": y, 
                            "width": width, 
                            "height": height, 
                            "rotated": rotated
                        })
                        placed_success = True
                        break
    
    return placed

def create_safe_layout(items, menggong_mode=False, grid_size=2, auto_mode=False, time_multiplier=1.0):
    selected_items = []
    
    # 根据模式调整概率
    if auto_mode:
        # 自动模式：金红概率降低
        if menggong_mode:
            level_chances = {"purple": 0.55, "blue": 0.0, "gold": 0.15, "red": 0.033}
        else:
            level_chances = {"purple": 0.52, "blue": 0.35, "gold": 0.093, "red": 0.017}
    elif menggong_mode:
        level_chances = {"purple": 0.45, "blue": 0.0, "gold": 0.45, "red": 0.10}
    else:
        level_chances = {"purple": 0.42, "blue": 0.25, "gold": 0.28, "red": 0.05}
    
    # 根据时间倍率调整爆率
    # time_multiplier范围0.6-1.4，1.0为基准
    # 时间倍率越大（>1.0）略微提高red和gold爆率
    # 时间倍率越小（<1.0）下调red和gold爆率
    if not auto_mode:  # 只在非自动模式下应用时间倍率影响
        rate_adjustment = (time_multiplier - 1.0) * 0.05  # 调整幅度为±10%
        
        # 调整red和gold概率
        original_red = level_chances["red"]
        original_gold = level_chances["gold"]
        
        level_chances["red"] = max(0.01, original_red + original_red * rate_adjustment)
        level_chances["gold"] = max(0.05, original_gold + original_gold * rate_adjustment)
        
        # 为了保持总概率平衡，相应调整purple概率
        red_diff = level_chances["red"] - original_red
        gold_diff = level_chances["gold"] - original_gold
        level_chances["purple"] = max(0.1, level_chances["purple"] - red_diff - gold_diff)
    
    # Probabilistic item selection with rare item handling
    for item in items:
        base_chance = level_chances.get(item["level"], 0)
        item_name = item["base_name"]
        
        # 调整稀有物品概率
        if item_name in ULTRA_RARE_ITEMS:
            # 超稀有物品：0.0009%概率
            final_chance = 0.000009
        elif item_name in RARE_ITEMS:
            # 稀有物品：原概率的三分之一
            final_chance = base_chance / 3
        else:
            final_chance = base_chance
            
        if random.random() <= final_chance:
            selected_items.append(item)
    
    # Limit number of items
    num_items = random.randint(2, 6)
    if len(selected_items) > num_items:
        selected_items = random.sample(selected_items, num_items)
    elif len(selected_items) < num_items:
        # Supplement with purple items (excluding rare ones)
        purple_items = [item for item in items if item["level"] == "purple" and item["base_name"] not in RARE_ITEMS]
        if purple_items:
            needed = min(num_items - len(selected_items), len(purple_items))
            selected_items.extend(random.sample(purple_items, needed))
    
    random.shuffle(selected_items)
    
    # Region selection (with weights) - 根据特勤处等级调整
    base_options = [(2, 1), (3, 1), (4, 1), (4, 2), (4, 3), (4, 4)]
    
    # 根据grid_size扩展region_options
    if grid_size == 3:  # 特勤处1级
        region_options = [(w+1, h+1) for w, h in base_options] + base_options
    elif grid_size == 4:  # 特勤处2级
        region_options = [(w+2, h+2) for w, h in base_options] + [(w+1, h+1) for w, h in base_options] + base_options
    elif grid_size == 5:  # 特勤处3级
        region_options = [(w+3, h+3) for w, h in base_options] + [(w+2, h+2) for w, h in base_options] + [(w+1, h+1) for w, h in base_options] + base_options
    elif grid_size == 6:  # 特勤处4级
        region_options = [(w+4, h+4) for w, h in base_options] + [(w+3, h+3) for w, h in base_options] + [(w+2, h+2) for w, h in base_options] + [(w+1, h+1) for w, h in base_options] + base_options
    elif grid_size == 7:  # 特勤处5级
        region_options = [(w+5, h+5) for w, h in base_options] + [(w+4, h+4) for w, h in base_options] + [(w+3, h+3) for w, h in base_options] + [(w+2, h+2) for w, h in base_options] + [(w+1, h+1) for w, h in base_options] + base_options
    else:
        region_options = base_options
    
    # 确保region不超过grid_size
    region_options = [(w, h) for w, h in region_options if w <= grid_size and h <= grid_size]
    
    weights = [1] * len(region_options)
    region_width, region_height = random.choices(region_options, weights=weights, k=1)[0]
    
    # Fixed placement in top-left corner
    placed_items = place_items(selected_items, region_width, region_height, grid_size)
    return placed_items, 0, 0, region_width, region_height

def render_safe_layout_gif(placed_items, start_x, start_y, region_width, region_height, grid_size=2, cell_size=100):
    """生成GIF动画，物品按顺序逐个显示，带转圈动画效果"""
    img_size = grid_size * cell_size
    frames = []
    
    # 动画参数
    frames_per_item = 8  # 每个物品显示时的帧数
    rotation_frames = 6  # 转圈动画帧数
    
    # 根据物品级别设置转圈时长（与render_safe_layout_gif中的函数保持一致）
    def get_rotation_duration(item_level):
        duration_map = {
            "blue": 6,    # 蓝色最短
            "purple": 8,  # 紫色稍长
            "gold": 20,    # 金色更长
            "red": 32     # 红色最长
        }
        return duration_map.get(item_level, 6)
    
    # 计算总帧数，考虑每个物品的转圈时长
    max_rotation_duration = max([get_rotation_duration(placed["item"]["level"]) for placed in placed_items], default=8)
    # 确保总帧数足够显示所有物品，包括最长的转圈动画
    min_frames_needed = len(placed_items) * frames_per_item + max_rotation_duration
    total_frames = min_frames_needed + 15  # 最后加15帧静止
    
    # Define item background colors (with transparency)
    background_colors = {
        "purple": (50, 43, 97, 90), 
        "blue": (49, 91, 126, 90), 
        "gold": (153, 116, 22, 90), 
        "red": (139, 35, 35, 90)
    }
    
    # 预加载所有物品图片
    item_images = {}
    for i, placed in enumerate(placed_items):
        item = placed["item"]
        try:
            with Image.open(item["path"]).convert("RGBA") as item_img:
                if placed["rotated"]:
                    item_img = item_img.rotate(90, expand=True)
                
                inner_width = placed["width"] * cell_size
                inner_height = placed["height"] * cell_size
                item_img.thumbnail((inner_width, inner_height), Image.LANCZOS)
                item_images[i] = item_img.copy()
        except Exception as e:
            print(f"Error loading item image: {item['path']}, error: {e}")
            item_images[i] = None
    
    # 根据物品级别设置转圈时长
    def get_rotation_duration(item_level):
        duration_map = {
            "blue": 6,    # 蓝色最短
            "purple": 8,  # 紫色稍长
            "gold": 20,    # 金色更长
            "red": 32     # 红色最长
        }
        return duration_map.get(item_level, 6)
    
    for frame_idx in range(total_frames):
        # 创建基础图像
        safe_img = Image.new("RGB", (img_size, img_size), (50, 50, 50))
        draw = ImageDraw.Draw(safe_img)
        
        # 绘制网格线
        for i in range(1, grid_size):
            draw.line([(i * cell_size, 0), (i * cell_size, img_size)], fill=(80, 80, 80), width=1)
            draw.line([(0, i * cell_size), (img_size, i * cell_size)], fill=(80, 80, 80), width=1)
        
        # 创建透明层
        overlay = Image.new("RGBA", safe_img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # 计算当前应该显示的物品数量
        current_item_count = min(len(placed_items), (frame_idx // frames_per_item) + 1)
        if frame_idx >= len(placed_items) * frames_per_item:
            current_item_count = len(placed_items)  # 最后几帧显示所有物品
        
        # 绘制未显示物品的黑色阴影线遮罩
        for i in range(current_item_count, len(placed_items)):
            placed = placed_items[i]
            x0, y0 = placed["x"] * cell_size, placed["y"] * cell_size
            x1, y1 = x0 + placed["width"] * cell_size, y0 + placed["height"] * cell_size
            
            # 绘制黑色半透明遮罩
            overlay_draw.rectangle([x0, y0, x1, y1], fill=(0, 0, 0, 120))
            
            # 绘制网格状阴影线纹理
            for y in range(int(y0), int(y1), 6):
                overlay_draw.line([(int(x0), y), (int(x1), y)], fill=(0, 0, 0, 120), width=1)
            for x in range(int(x0), int(x1), 6):
                overlay_draw.line([(x, int(y0)), (x, int(y1))], fill=(0, 0, 0, 120), width=1)
        
        # 绘制已显示的物品
        for i in range(current_item_count):
            placed = placed_items[i]
            item = placed["item"]
            x0, y0 = placed["x"] * cell_size, placed["y"] * cell_size
            x1, y1 = x0 + placed["width"] * cell_size, y0 + placed["height"] * cell_size
            
            # 获取物品背景色
            bg_color = background_colors.get(item["level"], (128, 128, 128, 200))
            
            # 为每个物品添加转圈动画效果，根据级别调整时长
            item_rotation_duration = get_rotation_duration(item["level"])
            
            # 计算该物品开始显示的帧数
            item_start_frame = i * frames_per_item
            
            # 判断是否在转圈动画期间 - 只有当前正在显示的物品才转圈
            is_rotating = (frame_idx >= item_start_frame and 
                          frame_idx < item_start_frame + item_rotation_duration and
                          i == current_item_count - 1)  # 确保只有当前物品转圈
            
            if is_rotating:
                # 转圈动画期间，先绘制阴影遮罩，再绘制转圈效果
                # 绘制黑色半透明遮罩
                overlay_draw.rectangle([x0, y0, x1, y1], fill=(0, 0, 0, 120))
                
                # 绘制网格状阴影线纹理
                for y in range(int(y0), int(y1), 6):
                    overlay_draw.line([(int(x0), y), (int(x1), y)], fill=(0, 0, 0, 120), width=1)
                for x in range(int(x0), int(x1), 6):
                    overlay_draw.line([(x, int(y0)), (x, int(y1))], fill=(0, 0, 0, 120), width=1)
                
                # 计算转圈动画参数
                rotation_frame = (frame_idx - item_start_frame) % item_rotation_duration
                # 根据转圈时长调整角速度，确保sousuo.png移动速度一致
                # 使用基准时长20帧来标准化角速度，并增加速度倍数
                base_duration = 20
                speed_multiplier = item_rotation_duration / base_duration
                speed_boost = 3.0  # 增加速度倍数，让转圈更快
                rotation_angle = (rotation_frame * 360 * speed_multiplier * speed_boost // item_rotation_duration) % 360
                
                # 创建带旋转效果的背景
                center_x = (x0 + x1) // 2
                center_y = (y0 + y1) // 2
                
                # 计算转圈动画的参数，使用固定半径确保大小格物品轨迹一致
                radius = cell_size // 8  # 缩小圆圈半径，让转圈轨迹更小
                
                # 使用 sousuo.png 图片代替弧线进行转圈动画
                sousuo_path = os.path.join(expressions_dir, "sousuo.png")
                if os.path.exists(sousuo_path):
                    try:
                        with Image.open(sousuo_path).convert("RGBA") as sousuo_img:
                            # 调整 sousuo.png 的大小，使用固定大小确保一致性
                            sousuo_size = 50  # 固定大小，不依赖半径
                            sousuo_img = sousuo_img.resize((sousuo_size, sousuo_size), Image.LANCZOS)
                            
                            # 计算图片中心点的转圈轨迹位置
                            angle_rad = math.radians(rotation_angle)
                            orbit_x = center_x + radius * math.cos(angle_rad)
                            orbit_y = center_y + radius * math.sin(angle_rad)
                            
                            # 计算图片左上角位置（使图片中心在轨迹上）
                            paste_x = int(orbit_x - sousuo_size // 2)
                            paste_y = int(orbit_y - sousuo_size // 2)
                            
                            # 粘贴图片（保持图片方向不变）
                            overlay.paste(sousuo_img, (paste_x, paste_y), sousuo_img)
                    except Exception as e:
                        # 如果加载图片失败，回退到原来的弧线绘制
                        arc_length = 150
                        start_angle = rotation_angle
                        end_angle = rotation_angle + arc_length
                        bbox = [center_x - radius, center_y - radius, 
                               center_x + radius, center_y + radius]
                        overlay_draw.arc(bbox, start_angle, end_angle, 
                                        fill=(255, 255, 255, 220), width=3)
                else:
                    # 如果 sousuo.png 不存在，回退到原来的弧线绘制
                    arc_length = 150
                    start_angle = rotation_angle
                    end_angle = rotation_angle + arc_length
                    bbox = [center_x - radius, center_y - radius, 
                           center_x + radius, center_y + radius]
                    overlay_draw.arc(bbox, start_angle, end_angle, 
                                    fill=(255, 255, 255, 220), width=3)
            else:
                # 转圈动画结束后，显示物品背景色和图片
                # 绘制物品背景
                overlay_draw.rectangle([x0, y0, x1, y1], fill=bg_color)
                
                # 绘制物品图片
                if i in item_images and item_images[i] is not None:
                    item_img = item_images[i]
                    paste_x = x0 + (placed["width"] * cell_size - item_img.width) // 2
                    paste_y = y0 + (placed["height"] * cell_size - item_img.height) // 2
                    overlay.paste(item_img, (int(paste_x), int(paste_y)), item_img)
                
                # 绘制物品边框
                draw.rectangle([x0, y0, x1, y1], outline=ITEM_BORDER_COLOR, width=BORDER_WIDTH)
        
        # 合并图层
        frame_img = Image.alpha_composite(safe_img.convert("RGBA"), overlay).convert("RGB")
        frames.append(frame_img)
    
    return frames

def get_highest_level(placed_items):
    if not placed_items: return "purple"
    levels = {"purple": 2, "blue": 1, "gold": 3, "red": 4}
    return max((p["item"]["level"] for p in placed_items), key=lambda level: levels.get(level, 0), default="purple")

def cleanup_old_images(keep_recent=2):
    try:
        image_files = glob.glob(os.path.join(output_dir, "*.png"))
        image_files.sort(key=os.path.getmtime, reverse=True)
        for old_file in image_files[keep_recent:]:
            os.remove(old_file)
    except Exception as e:
        print(f"Error cleaning up old images: {e}")

def cleanup_old_gifs(keep_recent=2):
    try:
        gif_files = glob.glob(os.path.join(output_dir, "*.gif"))
        gif_files.sort(key=os.path.getmtime, reverse=True)
        for old_file in gif_files[keep_recent:]:
            os.remove(old_file)
    except Exception as e:
        print(f"Error cleaning up old GIFs: {e}")

def generate_safe_image(menggong_mode=False, grid_size=2, time_multiplier=1.0, gif_scale=0.7, optimize_size=False, enable_static_image=False):
    """
    Generate a safe GIF animation and return the image path and list of placed items.
    
    Args:
        menggong_mode (bool): Whether to use menggong mode
        grid_size (int): Size of the grid
        time_multiplier (float): Time multiplier for animation
        gif_scale (float): Scale factor for the final GIF size (1.0 = original size, 0.5 = half size, 2.0 = double size)
        optimize_size (bool): Whether to optimize GIF file size (reduces colors and enables compression, may affect quality)
        enable_static_image (bool): Whether to generate static image (only last frame) instead of GIF animation
    
    Returns:
        tuple: (output_path, placed_items)
    """
    items = load_items()
    expressions = load_expressions()
    
    if not items or not expressions:
        print("Error: Missing image resources in items or expressions folders.")
        return None, []
    
    placed_items, start_x, start_y, region_width, region_height = create_safe_layout(items, menggong_mode, grid_size, auto_mode=False, time_multiplier=time_multiplier)
    safe_frames = render_safe_layout_gif(placed_items, start_x, start_y, region_width, region_height, grid_size)
    highest_level = get_highest_level(placed_items)
    
    # 计算总价值
    total_value = sum(placed["item"]["value"] for placed in placed_items)
    
    # 检查是否有金色物品
    has_gold_items = any(placed["item"]["level"] == "gold" for placed in placed_items)
    
    # 计算动画完成的帧数（所有物品显示完成的时间点）
    frames_per_item = 8  # 与render_safe_layout_gif中的值保持一致
    
    # 使用与render_safe_layout_gif中相同的转圈时长计算逻辑
    duration_map = {
        "blue": 6,    # 蓝色最短
        "purple": 8,  # 紫色稍长
        "gold": 20,    # 金色更长
        "red": 32     # 红色最长
    }
    
    # 计算最长转圈时长
    max_rotation_duration = max([duration_map.get(placed["item"]["level"], 6) for placed in placed_items], default=8)
    min_frames_needed = len(placed_items) * frames_per_item + max_rotation_duration
    animation_complete_frame = min_frames_needed + 5  # 延后5帧显示最终表情
    
    # 加载eating.gif和最终表情图片
    eating_path = expressions.get("eating")
    expression_map = {"gold": "happy", "red": "eat"}
    
    # 表情选择逻辑：优先级为红色>金色>高价值无金色>其他
    if highest_level == "red":
        final_expression = "eat"
    elif highest_level == "gold":
        final_expression = "happy"
    elif total_value > 300000 and not has_gold_items:
        final_expression = "happy"  # 价值大于300000且没有金色物品时使用happy
    else:
        final_expression = "cry"
    
    final_expr_path = expressions.get(final_expression)
    
    if not eating_path or not final_expr_path:
        return None, []
    
    try:
        # 计算表情图片的目标尺寸，使其与保险箱格子边长对齐
        # 使用grid_size * cell_size作为表情图片的尺寸，确保与格子线对齐
        expression_size = grid_size * 100  # cell_size默认为100
        
        # 加载eating.gif的所有帧，强制调整为统一尺寸
        eating_frames = []
        with Image.open(eating_path) as eating_gif:
            for frame_idx in range(eating_gif.n_frames):
                eating_gif.seek(frame_idx)
                eating_frame = eating_gif.convert("RGBA")
                # 强制调整为精确的expression_size尺寸，保持居中
                eating_frame = eating_frame.resize((expression_size, expression_size), Image.LANCZOS)
                eating_frames.append(eating_frame.copy())
        
        # 加载最终表情图片，强制调整为统一尺寸
        with Image.open(final_expr_path).convert("RGBA") as final_expr_img:
            # 强制调整为精确的expression_size尺寸，保持居中
            final_expr_img = final_expr_img.resize((expression_size, expression_size), Image.LANCZOS)
            
            # 为每一帧添加表情图片
            final_frames = []
            for frame_idx, safe_frame in enumerate(safe_frames):
                # 创建最终图像，使用expression_size作为左侧宽度，确保对齐
                final_img = Image.new("RGB", (expression_size + safe_frame.width, safe_frame.height), (50, 50, 50))
                
                # 选择表情图片：第一帧显示最终表情，从第二帧开始显示eating.gif
                if frame_idx == 0:
                    # 第一帧显示最终表情
                    current_expr = final_expr_img
                else:
                    # 从第二帧开始显示eating.gif的循环帧
                    eating_frame_idx = (frame_idx - 1) % len(eating_frames)
                    current_expr = eating_frames[eating_frame_idx]
                
                # 由于表情图片已强制调整为expression_size，直接放置在左上角
                # 处理表情图片的透明通道
                if current_expr.mode == 'RGBA':
                    # 直接粘贴RGBA图片，保持透明效果
                    final_img.paste(current_expr, (0, 0), current_expr)
                else:
                    final_img.paste(current_expr, (0, 0))
                
                # 添加保险箱帧，确保右侧紧贴表情图片
                final_img.paste(safe_frame, (expression_size, 0))
                
                # 应用缩放
                if gif_scale != 1.0:
                    new_width = int(final_img.width * gif_scale)
                    new_height = int(final_img.height * gif_scale)
                    final_img = final_img.resize((new_width, new_height), Image.LANCZOS)
                
                # 如果启用了大小优化，转换为P模式以减少颜色数量
                if optimize_size:
                    # 转换为P模式（调色板模式）以减少文件大小
                    final_img = final_img.convert('P', palette=Image.ADAPTIVE, colors=128)
                
                final_frames.append(final_img)
                
    except Exception as e:
        print(f"Error creating final GIF: {e}")
        return None, []

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 根据静态图片模式选择输出格式和路径
    if enable_static_image:
        # 静态图片模式：生成静态图片（显示最终表情+所有物品显示完毕的状态）
        output_path = os.path.join(output_dir, f"safe_{timestamp}.png")
        if final_frames:
            # 为静态图片创建特殊帧：左侧显示最终表情，右侧显示所有物品完成的保险箱
            static_frame_index = min(animation_complete_frame, len(final_frames) - 1)
            safe_frame = safe_frames[static_frame_index]
            
            # 创建静态图像，使用expression_size确保对齐
            static_img = Image.new("RGB", (expression_size + safe_frame.width, safe_frame.height), (50, 50, 50))
            
            # 由于表情图片已强制调整为expression_size，直接放置在左上角
            # 左侧始终显示最终表情（不是eating.gif）
            if final_expr_img.mode == 'RGBA':
                static_img.paste(final_expr_img, (0, 0), final_expr_img)
            else:
                static_img.paste(final_expr_img, (0, 0))
            
            # 右侧显示所有物品显示完毕的保险箱，确保紧贴表情图片
            static_img.paste(safe_frame, (expression_size, 0))
            
            # 应用缩放
            if gif_scale != 1.0:
                new_width = int(static_img.width * gif_scale)
                new_height = int(static_img.height * gif_scale)
                static_img = static_img.resize((new_width, new_height), Image.LANCZOS)
            
            static_img.save(output_path, 'PNG')
        cleanup_old_images()  # 清理旧的PNG文件
    else:
        # GIF动画模式
        output_path = os.path.join(output_dir, f"safe_{timestamp}.gif")
        
        # 保存GIF动画
        if final_frames:
            # 根据optimize_size参数设置保存选项
            save_kwargs = {
                'save_all': True,
                'append_images': final_frames[1:],
                'duration': 150,  # 每帧150毫秒
                'loop': 0  # 无限循环
            }
            
            if optimize_size:
                # 启用优化选项以减少文件大小
                save_kwargs.update({
                    'optimize': True,  # 启用优化
                    'disposal': 2,     # 恢复到背景色
                    'transparency': 0  # 设置透明色索引
                })
            
            final_frames[0].save(output_path, **save_kwargs)
        
        cleanup_old_gifs()  # 清理旧的GIF文件
    
    return output_path, placed_items
