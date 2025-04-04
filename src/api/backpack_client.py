import logging
import time
import aiohttp
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import requests

class BackpackClient:
    """Backpack API 客户端"""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """初始化BackpackClient
        
        Args:
            api_key: API密钥
            api_secret: API密钥对应的secret
        """
        self.base_url = "https://api.backpack.exchange"
        self.api_key = api_key
        self.api_secret = api_secret
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        if api_key and api_secret:
            self.session.headers.update({
                'X-API-Key': api_key,
                'X-Timestamp': str(int(time.time() * 1000)),
                'X-Signature': self._generate_signature()
            })
        
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
    
    async def get_markets(self) -> List[Dict]:
        """获取所有市场信息"""
        try:
            self._check_rate_limit()
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/markets") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"获取到 {len(data)} 个市场")
                        return data
                    else:
                        self.logger.error(f"获取市场信息失败: {response.status}")
                        return []
        except Exception as e:
            self.logger.error(f"获取市场信息失败: {str(e)}")
            return []
    
    async def get_trades(self, symbol: str, limit: int = 100) -> List[Dict]:
        """获取交易历史
        
        Args:
            symbol: 交易对符号
            limit: 返回的记录数量
            
        Returns:
            交易记录列表，每条记录包含：
            - id: 交易ID
            - price: 成交价格
            - quantity: 成交数量
            - quoteQuantity: 成交金额
            - timestamp: 成交时间戳
            - isBuyerMaker: 买方是否为maker
        """
        try:
            self._check_rate_limit()
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/v1/trades",
                    params={"symbol": symbol, "limit": limit}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"获取到 {len(data)} 条交易记录")
                        return data
                    else:
                        self.logger.error(f"获取交易历史失败: {response.status}")
                        return []
        except Exception as e:
            self.logger.error(f"获取交易历史失败: {str(e)}")
            return []
    
    async def get_klines(self, symbol: str, interval: str = '1h', limit: int = 24, start_time: Optional[int] = None, end_time: Optional[int] = None) -> List[Dict]:
        """获取K线数据
        
        Args:
            symbol: 交易对
            interval: K线间隔, 默认1h
            limit: 返回的K线数量, 默认24
            start_time: 开始时间戳(毫秒)
            end_time: 结束时间戳(毫秒)
            
        Returns:
            K线数据列表
        """
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        # 获取当前时间戳（毫秒）
        current_time = int(time.time() * 1000)
        
        # 如果没有提供时间参数，使用当前时间的前24小时
        if start_time is None:
            start_time = current_time - (24 * 60 * 60 * 1000)  # 24小时前
        if end_time is None:
            end_time = current_time
            
        # 确保时间戳在合理范围内
        if start_time > current_time:
            start_time = current_time - (24 * 60 * 60 * 1000)
        if end_time > current_time:
            end_time = current_time
            
        # 确保开始时间不大于结束时间
        if start_time >= end_time:
            start_time = end_time - (24 * 60 * 60 * 1000)
            
        # 确保时间戳不是未来时间
        if start_time > current_time:
            start_time = current_time - (24 * 60 * 60 * 1000)
        if end_time > current_time:
            end_time = current_time
            
        # 将时间戳转换为UTC时间
        start_time = start_time - (8 * 60 * 60 * 1000)  # 减去8小时
        end_time = end_time - (8 * 60 * 60 * 1000)  # 减去8小时
            
        params['startTime'] = start_time
        params['endTime'] = end_time
            
        self.logger.info(f'请求K线数据参数: {params}')
        
        try:
            headers = {}
            if self.api_key and self.api_secret:
                timestamp = str(int(time.time() * 1000))
                headers = {
                    'X-API-Key': self.api_key,
                    'X-Timestamp': timestamp,
                    'X-Signature': self._generate_signature()
                }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/v1/klines",
                    params=params,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"获取到 {len(data)} 条K线数据")
                        return data
                    else:
                        error_text = await response.text()
                        self.logger.error(f"获取K线数据失败: {response.status}, {error_text}")
                        return []
        except Exception as e:
            self.logger.error(f"获取K线数据失败: {str(e)}")
            return []
    
    async def get_orderbook(self, symbol: str, limit: Optional[int] = None) -> Dict[str, List[List[str]]]:
        """获取订单簿数据
        
        Args:
            symbol: 交易对符号
            limit: 返回的档位数量，可选值：5, 10, 20, 50, 100, 500, 1000
            
        Returns:
            订单簿数据，包含：
            - bids: 买单列表，每个元素为 [价格, 数量]
            - asks: 卖单列表，每个元素为 [价格, 数量]
        """
        try:
            self._check_rate_limit()
            params = {"symbol": symbol}
            if limit is not None:
                params["limit"] = limit
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/v1/depth",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"获取到订单簿数据: {len(data.get('bids', []))} 个买单, {len(data.get('asks', []))} 个卖单")
                        return data
                    else:
                        self.logger.error(f"获取订单簿数据失败: {response.status}")
                        return {"bids": [], "asks": []}
        except Exception as e:
            self.logger.error(f"获取订单簿数据失败: {str(e)}")
            return {"bids": [], "asks": []}
    
    async def analyze_market_depth(self, symbol: str, depth: int = 20) -> Dict:
        """分析市场深度
        
        Args:
            symbol: 交易对符号
            depth: 分析的深度
            
        Returns:
            市场深度分析结果，包含：
            - bid_volume: 买单总量
            - ask_volume: 卖单总量
            - bid_value: 买单总价值
            - ask_value: 卖单总价值
            - spread: 买卖价差
            - spread_percentage: 买卖价差百分比
            - mid_price: 中间价格
            - imbalance: 买卖失衡程度 (-1 到 1，负值表示卖压更大)
        """
        try:
            orderbook = await self.get_orderbook(symbol, depth)
            if not orderbook['bids'] or not orderbook['asks']:
                return {}
            
            # 计算买单和卖单的总量和总价值
            bid_volume = sum(float(bid[1]) for bid in orderbook['bids'])
            ask_volume = sum(float(ask[1]) for ask in orderbook['asks'])
            
            bid_value = sum(float(bid[0]) * float(bid[1]) for bid in orderbook['bids'])
            ask_value = sum(float(ask[0]) * float(ask[1]) for ask in orderbook['asks'])
            
            # 计算买卖价差
            best_bid = float(orderbook['bids'][0][0])
            best_ask = float(orderbook['asks'][0][0])
            spread = best_ask - best_bid
            mid_price = (best_bid + best_ask) / 2
            spread_percentage = (spread / mid_price) * 100
            
            # 计算买卖失衡程度
            total_volume = bid_volume + ask_volume
            imbalance = (bid_volume - ask_volume) / total_volume if total_volume > 0 else 0
            
            return {
                'bid_volume': bid_volume,
                'ask_volume': ask_volume,
                'bid_value': bid_value,
                'ask_value': ask_value,
                'spread': spread,
                'spread_percentage': spread_percentage,
                'mid_price': mid_price,
                'imbalance': imbalance
            }
            
        except Exception as e:
            self.logger.error(f"分析市场深度失败: {str(e)}")
            return {}
    
    async def get_traders(self, limit: int = 100) -> List[Dict]:
        """获取交易员列表
        
        注意：此API可能不存在，返回空列表
        """
        self.logger.warning("交易员列表API可能不存在，返回空列表")
        return []
    
    async def get_trader_info(self, trader_id: str) -> Dict:
        """获取交易员详细信息
        
        注意：此API可能不存在，返回空字典
        """
        self.logger.warning(f"交易员信息API可能不存在，返回空字典: {trader_id}")
        return {}
    
    async def get_trader_trades(self, trader_id: str, limit: int = 100) -> List[Dict]:
        """获取交易员交易历史
        
        注意：此API可能不存在，返回空列表
        """
        self.logger.warning(f"交易员交易历史API可能不存在，返回空列表: {trader_id}")
        return []
    
    async def get_trader_positions(self, trader_id: str) -> List[Dict]:
        """获取交易员持仓信息
        
        注意：此API可能不存在，返回空列表
        """
        self.logger.warning(f"交易员持仓信息API可能不存在，返回空列表: {trader_id}")
        return []
    
    async def get_trader_balance(self, trader_id: str) -> Dict:
        """获取交易员资金信息
        
        注意：此API可能不存在，返回空字典
        """
        self.logger.warning(f"交易员资金信息API可能不存在，返回空字典: {trader_id}")
        return {} 