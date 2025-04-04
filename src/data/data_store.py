import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

class DataStore:
    """数据存储类，用于保存和管理 API 数据"""
    
    def __init__(self, base_dir: str = "data"):
        """初始化数据存储
        
        Args:
            base_dir: 数据存储的基础目录
        """
        self.base_dir = base_dir
        self.logger = logging.getLogger(__name__)
        
        # 创建必要的目录
        self._create_directories()
    
    def _create_directories(self):
        """创建必要的目录结构"""
        directories = [
            self.base_dir,
            os.path.join(self.base_dir, "markets"),
            os.path.join(self.base_dir, "traders"),
            os.path.join(self.base_dir, "trades"),
            os.path.join(self.base_dir, "klines")
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.logger.info(f"创建目录: {directory}")
    
    def _get_file_path(self, data_type: str, identifier: str) -> str:
        """获取数据文件的路径
        
        Args:
            data_type: 数据类型（markets, traders, trades, klines）
            identifier: 数据标识符（如市场符号、交易员ID等）
            
        Returns:
            str: 数据文件的完整路径
        """
        return os.path.join(self.base_dir, data_type, f"{identifier}.json")
    
    def save_data(self, data_type: str, identifier: str, data: Union[Dict, List]) -> bool:
        """保存数据到文件
        
        Args:
            data_type: 数据类型
            identifier: 数据标识符
            data: 要保存的数据
            
        Returns:
            bool: 是否保存成功
        """
        try:
            file_path = self._get_file_path(data_type, identifier)
            
            # 添加时间戳
            data_with_timestamp = {
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_with_timestamp, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"数据已保存到: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"保存数据失败: {str(e)}")
            return False
    
    def load_data(self, data_type: str, identifier: str) -> Optional[Union[Dict, List]]:
        """从文件加载数据
        
        Args:
            data_type: 数据类型
            identifier: 数据标识符
            
        Returns:
            Optional[Union[Dict, List]]: 加载的数据，如果加载失败则返回 None
        """
        try:
            file_path = self._get_file_path(data_type, identifier)
            
            if not os.path.exists(file_path):
                self.logger.warning(f"数据文件不存在: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"数据已从 {file_path} 加载")
            return data.get("data")
        except Exception as e:
            self.logger.error(f"加载数据失败: {str(e)}")
            return None
    
    def save_market_data(self, symbol: str, data: Dict) -> bool:
        """保存市场数据
        
        Args:
            symbol: 市场符号
            data: 市场数据
            
        Returns:
            bool: 是否保存成功
        """
        return self.save_data("markets", symbol, data)
    
    def load_market_data(self, symbol: str) -> Optional[Dict]:
        """加载市场数据
        
        Args:
            symbol: 市场符号
            
        Returns:
            Optional[Dict]: 市场数据
        """
        return self.load_data("markets", symbol)
    
    def save_trader_data(self, trader_id: str, data: Dict) -> bool:
        """保存交易员数据
        
        Args:
            trader_id: 交易员ID
            data: 交易员数据
            
        Returns:
            bool: 是否保存成功
        """
        return self.save_data("traders", trader_id, data)
    
    def load_trader_data(self, trader_id: str) -> Optional[Dict]:
        """加载交易员数据
        
        Args:
            trader_id: 交易员ID
            
        Returns:
            Optional[Dict]: 交易员数据
        """
        return self.load_data("traders", trader_id)
    
    def save_trade_data(self, identifier: str, data: List[Dict]) -> bool:
        """保存交易数据
        
        Args:
            identifier: 交易标识符（可以是市场符号或交易员ID）
            data: 交易数据列表
            
        Returns:
            bool: 是否保存成功
        """
        return self.save_data("trades", identifier, data)
    
    def load_trade_data(self, identifier: str) -> Optional[List[Dict]]:
        """加载交易数据
        
        Args:
            identifier: 交易标识符
            
        Returns:
            Optional[List[Dict]]: 交易数据列表
        """
        return self.load_data("trades", identifier)
    
    def save_kline_data(self, symbol: str, interval: str, data: List[Dict]) -> bool:
        """保存K线数据
        
        Args:
            symbol: 市场符号
            interval: K线间隔
            data: K线数据列表
            
        Returns:
            bool: 是否保存成功
        """
        identifier = f"{symbol}_{interval}"
        return self.save_data("klines", identifier, data)
    
    def load_kline_data(self, symbol: str, interval: str) -> Optional[List[Dict]]:
        """加载K线数据
        
        Args:
            symbol: 市场符号
            interval: K线间隔
            
        Returns:
            Optional[List[Dict]]: K线数据列表
        """
        identifier = f"{symbol}_{interval}"
        return self.load_data("klines", identifier) 