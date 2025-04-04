import logging
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants

class HyperliquidClient:
    """Hyperliquid API 客户端"""
    
    def __init__(self):
        """初始化客户端"""
        self.info = Info(constants.TESTNET_API_URL)
        self.exchange = Exchange(constants.TESTNET_API_URL)
        self.logger = logging.getLogger(__name__)
        
        # API 限制
        self.rate_limit = {
            'requests_per_minute': 2000,
            'last_request_time': 0
        }
    
    def _check_rate_limit(self):
        """检查并等待直到可以发送下一个请求"""
        current_time = time.time()
        time_since_last_request = current_time - self.rate_limit['last_request_time']
        
        # 计算需要等待的时间（毫秒）
        wait_time = max(0, (60 / self.rate_limit['requests_per_minute']) - time_since_last_request)
        if wait_time > 0:
            time.sleep(wait_time)
        
        self.rate_limit['last_request_time'] = time.time()
    
    async def get_trader_list(self):
        """获取交易员列表"""
        try:
            self._check_rate_limit()
            # 获取所有交易对
            markets = self.info.meta()
            self.logger.info(f"获取到 {len(markets.get('universe', []))} 个交易对")
            
            # 获取所有交易对的市场数据
            all_traders = set()
            for market in markets.get('universe', []):
                market_name = market.get('name')
                if market_name and not market.get('isDelisted', False):
                    self.logger.debug(f"处理交易对: {market_name}")
                    
                    # 获取该交易对的市场数据
                    self._check_rate_limit()
                    market_data = self.info.all_mids()
                    self.logger.debug(f"市场数据: {market_data}")
                    
                    # 从市场数据中提取交易员地址
                    if isinstance(market_data, dict):
                        traders = market_data.get('traders', [])
                        all_traders.update(traders)
            
            traders_list = list(all_traders)
            self.logger.info(f"找到 {len(traders_list)} 个交易员")
            return traders_list
        except Exception as e:
            self.logger.error(f"获取交易员列表失败: {str(e)}")
            return []
    
    async def get_trader_info(self, address):
        """获取交易员信息"""
        try:
            self._check_rate_limit()
            # 获取交易员状态
            state = self.info.user_state(address)
            self.logger.debug(f"交易员 {address} 状态: {state}")
            return state
        except Exception as e:
            self.logger.error(f"获取交易员 {address} 信息失败: {str(e)}")
            return None
    
    async def get_trader_trades(self, address, days=1):
        """获取交易员交易历史"""
        try:
            self._check_rate_limit()
            # 获取交易历史
            trades = self.info.user_trades(address)
            self.logger.debug(f"交易员 {address} 交易历史数量: {len(trades)}")
            return trades
        except Exception as e:
            self.logger.error(f"获取交易员 {address} 交易历史失败: {str(e)}")
            return []
    
    async def get_trader_positions(self, address):
        """获取交易员持仓信息"""
        try:
            self._check_rate_limit()
            # 获取持仓信息
            positions = self.info.user_state(address)
            self.logger.debug(f"交易员 {address} 持仓信息: {positions.get('positions', [])}")
            return positions.get('positions', [])
        except Exception as e:
            self.logger.error(f"获取交易员 {address} 持仓信息失败: {str(e)}")
            return []
    
    async def get_trader_balance(self, address):
        """获取交易员资金信息"""
        try:
            self._check_rate_limit()
            # 获取资金信息
            state = self.info.user_state(address)
            self.logger.debug(f"交易员 {address} 资金信息: {state.get('marginSummary', {})}")
            return state.get('marginSummary', {})
        except Exception as e:
            self.logger.error(f"获取交易员 {address} 资金信息失败: {str(e)}")
            return None 