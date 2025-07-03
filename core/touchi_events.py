import random
import asyncio
import aiosqlite
import time
from datetime import datetime
import os

class TouchiEvents:
    """偷吃概率事件处理类"""
    
    def __init__(self, db_path, biaoqing_dir):
        self.db_path = db_path
        self.biaoqing_dir = biaoqing_dir
        
        # 事件概率配置（平分概率）
        self.event_probabilities = {
            "broken_liutao": 0.02,      # 2% 概率获得残缺刘涛
            "genius_kick": 0.02,        # 2% 概率遇到天才少年被踢死
            "genius_fine": 0.02,        # 2% 概率排到天才少年被追缴
            "noob_teammate": 0.02,      # 2% 概率遇到菜b队友
            "hunted_escape": 0.02,      # 2% 概率被追杀丢包撤离
            "passerby_mouse": 0.02,     # 2% 概率遇到路人鼠鼠
            "system_compensation": 0.02  # 2% 概率触发系统补偿局
        }
    
    async def check_random_events(self, event, user_id, placed_items, total_value):
        """检查是否触发随机事件
        
        Args:
            event: 消息事件
            user_id: 用户ID
            placed_items: 偷吃获得的物品列表
            total_value: 物品总价值
            
        Returns:
            tuple: (是否触发事件, 事件类型, 修改后的物品列表, 修改后的总价值, 事件消息, 冷却时间倍率)
        """
        
        # 随机检查事件
        rand = random.random()
        cumulative_prob = 0
        
        # 事件1: 获得残缺刘涛 (2%概率)
        cumulative_prob += self.event_probabilities["broken_liutao"]
        if rand < cumulative_prob:
            result = await self._handle_broken_liutao_event(event, user_id, placed_items, total_value)
            return result + (None, None)  # 添加冷却时间倍率和金色物品路径
        
        # 事件2: 遇到天才少年被踢死 (2%概率)
        cumulative_prob += self.event_probabilities["genius_kick"]
        if rand < cumulative_prob:
            result = await self._handle_genius_kick_event(event, user_id, placed_items, total_value)
            return result + (None, None)  # 添加冷却时间倍率和金色物品路径
        
        # 事件3: 排到天才少年被追缴 (2%概率)
        cumulative_prob += self.event_probabilities["genius_fine"]
        if rand < cumulative_prob:
            result = await self._handle_genius_fine_event(event, user_id, placed_items, total_value)
            return result + (None, None)  # 添加冷却时间倍率和金色物品路径
        
        # 事件4: 遇到菜b队友 (2%概率)
        cumulative_prob += self.event_probabilities["noob_teammate"]
        if rand < cumulative_prob:
            result = await self._handle_noob_teammate_event(event, user_id, placed_items, total_value)
            return result + (2.0, None)  # 冷却时间翻倍和金色物品路径
        
        # 事件5: 被追杀丢包撤离 (2%概率)
        cumulative_prob += self.event_probabilities["hunted_escape"]
        if rand < cumulative_prob:
            result = await self._handle_hunted_escape_event(event, user_id, placed_items, total_value)
            return result + (None, None)  # 添加冷却时间倍率和金色物品路径
        
        # 事件6: 遇到路人鼠鼠 (2%概率)
        cumulative_prob += self.event_probabilities["passerby_mouse"]
        if rand < cumulative_prob:
            result = await self._handle_passerby_mouse_event(event, user_id, placed_items, total_value)
            if len(result) == 6:  # 路人鼠鼠事件返回6个值
                return result[0], result[1], result[2], result[3], result[4], None, result[5]  # 事件触发、类型、物品、价值、消息、冷却倍率、金色物品路径
            else:
                return result + (None, None)  # 添加冷却时间倍率和金色物品路径
        
        # 事件7: 系统补偿局 (2%概率)
        cumulative_prob += self.event_probabilities["system_compensation"]
        if rand < cumulative_prob:
            result = await self._handle_system_compensation_event(event, user_id, placed_items, total_value)
            return result + (0.5, None)  # 冷却时间减半和金色物品路径
        
        # 无事件触发
        return False, None, placed_items, total_value, None, None, None
    
    async def _handle_broken_liutao_event(self, event, user_id, placed_items, total_value):
        """处理获得残缺刘涛事件"""
        try:
            # 获取时间倍率
            time_multiplier = await self._get_menggong_time_multiplier()
            
            # 激活六套加成时间（基础1分钟 * 倍率）
            current_time = int(time.time())
            base_duration = 60  # 基础1分钟
            actual_duration = int(base_duration * time_multiplier)
            menggong_end_time = current_time + actual_duration
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "UPDATE user_economy SET menggong_active = 1, menggong_end_time = ? WHERE user_id = ?",
                    (menggong_end_time, user_id)
                )
                await db.commit()
            
            # 创建事件消息
            duration_text = f"{actual_duration//60}分{actual_duration%60}秒" if actual_duration >= 60 else f"{actual_duration}秒"
            event_message = (
                "🎉 特殊事件触发！\n"
                "💎 你额外获得了残缺的刘涛！\n"
                f"⚡ 六套加成时间已激活 {duration_text}！\n"
                "🔥 期间红色和金色物品概率大幅提升！"
            )
            
            return True, "broken_liutao", placed_items, total_value, event_message
            
        except Exception as e:
            print(f"处理残缺刘涛事件时出错: {e}")
            return False, None, placed_items, total_value, None
    
    async def _handle_genius_kick_event(self, event, user_id, placed_items, total_value):
        """处理遇到天才少年被踢死事件"""
        try:
            # 创建事件消息
            event_message = (
                "💀 特殊事件触发！\n"
                "👦 你遇到了天才少年，被一脚踢死了！\n"
                "📦 本次偷吃展示如下，但物品不会计入仓库！\n"
                "💸 本次偷吃的物品全部丢失..."
            )
            
            # 返回原物品用于展示，但总价值设为0（因为不计入数据库）
            # 注意：这里不清空用户现有仓库，只是本次偷吃的物品不计入
            return True, "genius_kick", placed_items, 0, event_message
            
        except Exception as e:
            print(f"处理天才少年踢死事件时出错: {e}")
            return False, None, placed_items, total_value, None
    
    async def _handle_genius_fine_event(self, event, user_id, placed_items, total_value):
        """处理排到天才少年被追缴事件"""
        try:
            fine_amount = 300000  # 追缴金额
            
            async with aiosqlite.connect(self.db_path) as db:
                # 检查当前仓库价值
                cursor = await db.execute(
                    "SELECT warehouse_value FROM user_economy WHERE user_id = ?",
                    (user_id,)
                )
                result = await cursor.fetchone()
                current_value = result[0] if result else 0
                
                # 扣除哈夫币（可以为负数）
                new_value = current_value - fine_amount
                await db.execute(
                    "UPDATE user_economy SET warehouse_value = ? WHERE user_id = ?",
                    (new_value, user_id)
                )
                await db.commit()
            
            # 创建事件消息
            event_message = (
                "⚖️ 特殊事件触发！\n"
                "👦 你排到了天才少年！\n"
                "🍽️ 虽然成功偷吃了，但被追缴了哈夫币！\n"
                f"💸 扣除哈夫币: {fine_amount:,}\n"
                f"💰 当前余额: {new_value:,}"
            )
            
            return True, "genius_fine", placed_items, total_value, event_message
            
        except Exception as e:
            print(f"处理天才少年追缴事件时出错: {e}")
            return False, None, placed_items, total_value, None
    
    async def _handle_noob_teammate_event(self, event, user_id, placed_items, total_value):
        """处理遇到菜b队友事件"""
        try:
            # 创建事件消息
            event_message = (
                "🤦 特殊事件触发！\n"
                "👥 你遇到了菜b队友，撤离时间翻倍！\n"
                "⏰ 下次偷吃冷却时间增加一倍！\n"
                "🍽️ 但偷吃正常进行，物品已获得！"
            )
            
            return True, "noob_teammate", placed_items, total_value, event_message
            
        except Exception as e:
            print(f"处理菜b队友事件时出错: {e}")
            return False, None, placed_items, total_value, None
    
    async def _handle_hunted_escape_event(self, event, user_id, placed_items, total_value):
        """处理被追杀丢包撤离事件"""
        try:
            # 删除用户收藏中的大尺寸物品，只保留小尺寸物品
            allowed_sizes = ['1x1', '1x2', '2x1', '1x3', '3x1']
            
            async with aiosqlite.connect(self.db_path) as db:
                # 获取用户所有物品
                cursor = await db.execute(
                    "SELECT item_name FROM user_touchi_collection WHERE user_id = ?",
                    (user_id,)
                )
                user_items = await cursor.fetchall()
                
                # 删除不符合尺寸要求的物品
                items_removed = 0
                for item_row in user_items:
                    item_name = item_row[0]
                    # 从物品名称中提取尺寸信息
                    item_size = self._extract_size_from_name(item_name)
                    if item_size and item_size not in allowed_sizes:
                        await db.execute(
                            "DELETE FROM user_touchi_collection WHERE user_id = ? AND item_name = ?",
                            (user_id, item_name)
                        )
                        items_removed += 1
                
                # 重新计算仓库价值
                await self._recalculate_warehouse_value(db, user_id)
                await db.commit()
            
            # 创建事件消息
            event_message = (
                "🏃 特殊事件触发！\n"
                "🔫 你被追杀到了丢包撤离点！\n"
                "📦 只能保留小尺寸物品！\n"
                f"💔 丢弃了 {items_removed} 件大尺寸物品！\n"
            )
            
            return True, "hunted_escape", placed_items, total_value, event_message
            
        except Exception as e:
            print(f"处理被追杀丢包撤离事件时出错: {e}")
            return False, None, placed_items, total_value, None
    
    def _extract_size_from_name(self, item_name):
        """从物品名称中提取尺寸信息"""
        # 物品名称格式通常是: 等级_尺寸_物品名
        # 例如: "1_1x1_物品名" 或 "2_2x1_物品名"
        parts = item_name.split('_')
        if len(parts) >= 2:
            potential_size = parts[1]
            if 'x' in potential_size:
                return potential_size
        return None
    
    async def _recalculate_warehouse_value(self, db, user_id):
        """重新计算用户仓库价值"""
        from .touchi import get_item_value
        
        # 获取用户所有剩余物品
        cursor = await db.execute(
            "SELECT item_name, COUNT(*) FROM user_touchi_collection WHERE user_id = ? GROUP BY item_name",
            (user_id,)
        )
        items = await cursor.fetchall()
        
        # 计算总价值
        total_value = 0
        for item_name, count in items:
            item_value = get_item_value(item_name)
            total_value += item_value * count
        
        # 更新仓库价值
        await db.execute(
            "UPDATE user_economy SET warehouse_value = ? WHERE user_id = ?",
            (total_value, user_id)
         )
    
    async def _handle_passerby_mouse_event(self, event, user_id, placed_items, total_value):
        """处理遇到路人鼠鼠事件"""
        try:
            import os
            import glob
            import random
            
            # 获取所有金色物品
            items_dir = os.path.join(os.path.dirname(__file__), "items")
            gold_items = glob.glob(os.path.join(items_dir, "gold_*.png"))
            
            if gold_items:
                # 随机选择一个金色物品
                selected_gold_item = random.choice(gold_items)
                item_name = os.path.splitext(os.path.basename(selected_gold_item))[0]
                
                # 创建事件消息
                event_message = (
                    "🐭 特殊事件触发！\n"
                    "👋 你遇到了路人鼠鼠，你们打了暗号！\n"
                    f"🎁 ta送给了你金色物品\n"
                    "🍽️ 本次偷吃物品已获得！"
                )
                
                # 返回原始物品和价值，金色物品将在重新生成时添加
                return True, "passerby_mouse", placed_items, total_value, event_message, selected_gold_item  # 返回选中的金色物品路径
            else:
                # 如果没有金色物品，返回正常结果
                return False, None, placed_items, total_value, None, None
                
        except Exception as e:
            print(f"处理路人鼠鼠事件时出错: {e}")
            return False, None, placed_items, total_value, None, None
    
    async def _handle_system_compensation_event(self, event, user_id, placed_items, total_value):
        """处理系统补偿局事件"""
        try:
            # 创建事件消息
            event_message = (
                "🎯 特殊事件触发！\n"
                "🔧 系统补偿局已启动！\n"
                "⚡ 本次偷吃概率和六套模式一致！\n"
                "🕐 下次偷吃冷却时间减半！\n"
                "🍽️ 偷吃物品已获得！"
            )
            
            return True, "system_compensation", placed_items, total_value, event_message
            
        except Exception as e:
            print(f"处理系统补偿局事件时出错: {e}")
            return False, None, placed_items, total_value, None
     
    async def get_event_image(self, event_type):
        """获取事件对应的图片路径"""
        event_images = {
             "broken_liutao": "menggong.gif",  # 使用猛攻图片表示刘涛
             "genius_kick": "touchi1.gif",    # 使用偷吃图片表示被踢
             "genius_fine": "touchi2.gif",    # 使用偷吃图片表示被追缴
             "noob_teammate": "touchi1.gif",  # 使用偷吃图片表示菜b队友
             "hunted_escape": "touchi2.gif",  # 使用偷吃图片表示被追杀
             "passerby_mouse": "touchi3.gif", # 使用偷吃图片表示路人鼠鼠
             "system_compensation": "touchi4.gif"  # 使用偷吃图片表示系统补偿局
         }
        
        image_name = event_images.get(event_type)
        if image_name:
            image_path = os.path.join(self.biaoqing_dir, image_name)
            if os.path.exists(image_path):
                return image_path
        return None
    
    def get_event_statistics(self):
        """获取事件概率统计信息"""
        total_prob = sum(self.event_probabilities.values())
        normal_prob = 1 - total_prob
        
        return {
            "normal": f"{normal_prob:.1%}",
            "broken_liutao": f"{self.event_probabilities['broken_liutao']:.1%}",
            "genius_kick": f"{self.event_probabilities['genius_kick']:.1%}",
            "genius_fine": f"{self.event_probabilities['genius_fine']:.1%}",
            "noob_teammate": f"{self.event_probabilities['noob_teammate']:.1%}",
            "hunted_escape": f"{self.event_probabilities['hunted_escape']:.1%}",
            "passerby_mouse": f"{self.event_probabilities['passerby_mouse']:.1%}",
            "system_compensation": f"{self.event_probabilities['system_compensation']:.1%}",
            "total_event": f"{total_prob:.1%}"
        }
    
    async def _get_menggong_time_multiplier(self):
        """获取当前六套时间倍率"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT config_value FROM system_config WHERE config_key = 'menggong_time_multiplier'"
                )
                result = await cursor.fetchone()
                if result:
                    return float(result[0])
                else:
                    return 1.0  # 默认倍率
        except Exception as e:
            print(f"获取六套时间倍率时出错: {e}")
            return 1.0  # 默认倍率