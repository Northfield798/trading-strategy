import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from api.backpack_client import BackpackClient

logger = logging.getLogger(__name__)

class MarketAnalysis:
    """市场分析类"""
    
    def __init__(self, client: BackpackClient):
        """初始化分析器
        
        Args:
            client: Backpack API 客户端
        """
        self.client = client
    
    async def analyze_market(self, symbol: str) -> Dict:
        """分析市场状态
        
        Args:
            symbol: 交易对符号
            
        Returns:
            市场分析结果，包含：
            - market_depth: 市场深度分析
            - trade_analysis: 交易分析
            - price_analysis: 价格分析
        """
        try:
            # 1. 分析市场深度
            depth_analysis = await self.client.analyze_market_depth(symbol)
            
            # 2. 分析最近的交易
            trades = await self.client.get_trades(symbol, limit=100)
            trade_analysis = self._analyze_trades(trades)
            
            # 3. 分析价格走势
            klines = await self.client.get_klines(symbol, interval="1h", limit=24)
            price_analysis = self._analyze_price(klines)
            
            return {
                'market_depth': depth_analysis,
                'trade_analysis': trade_analysis,
                'price_analysis': price_analysis
            }
            
        except Exception as e:
            logger.error(f"分析市场失败: {str(e)}")
            return {}
    
    def _analyze_trades(self, trades: List[Dict]) -> Dict:
        """分析交易数据
        
        Args:
            trades: 交易记录列表
            
        Returns:
            交易分析结果，包含：
            - total_trades: 总成交笔数
            - total_volume: 总成交量
            - total_value: 总成交额
            - avg_trade_size: 平均成交量
            - avg_trade_value: 平均成交额
            - buy_ratio: 买单比例
            - price_trend: 价格趋势（1: 上涨, 0: 横盘, -1: 下跌）
            - volatility: 波动率
        """
        try:
            if not trades:
                return {}
            
            # 转换为 DataFrame
            df = pd.DataFrame(trades)
            df['price'] = df['price'].astype(float)
            df['quantity'] = df['quantity'].astype(float)
            df['quoteQuantity'] = df['quoteQuantity'].astype(float)
            
            # 计算基本指标
            total_trades = len(df)
            total_volume = df['quantity'].sum()
            total_value = df['quoteQuantity'].sum()
            avg_trade_size = total_volume / total_trades
            avg_trade_value = total_value / total_trades
            
            # 计算买单比例
            buy_ratio = len(df[~df['isBuyerMaker']]) / total_trades
            
            # 计算价格趋势
            first_price = df.iloc[-1]['price']  # 最早的价格
            last_price = df.iloc[0]['price']   # 最新的价格
            price_change = (last_price - first_price) / first_price
            
            if price_change > 0.001:  # 0.1% 的阈值
                price_trend = 1
            elif price_change < -0.001:
                price_trend = -1
            else:
                price_trend = 0
            
            # 计算波动率
            returns = df['price'].pct_change()
            volatility = returns.std() * np.sqrt(len(df))  # 年化波动率
            
            return {
                'total_trades': total_trades,
                'total_volume': total_volume,
                'total_value': total_value,
                'avg_trade_size': avg_trade_size,
                'avg_trade_value': avg_trade_value,
                'buy_ratio': buy_ratio,
                'price_trend': price_trend,
                'volatility': volatility
            }
            
        except Exception as e:
            logger.error(f"分析交易数据失败: {str(e)}")
            return {}
    
    def _analyze_price(self, klines: List[Dict]) -> Dict:
        """分析价格数据
        
        Args:
            klines: K线数据列表
            
        Returns:
            价格分析结果，包含：
            - current_price: 当前价格
            - price_change_24h: 24小时价格变化
            - price_change_percentage_24h: 24小时价格变化百分比
            - high_24h: 24小时最高价
            - low_24h: 24小时最低价
            - volume_24h: 24小时成交量
            - ma7: 7小时均价
            - ma25: 25小时均价
            - rsi: RSI指标
            - trend: 趋势（strong_up, up, neutral, down, strong_down）
        """
        try:
            if not klines:
                return {}
            
            # 转换为 DataFrame
            df = pd.DataFrame(klines, columns=[
                'openTime', 'open', 'high', 'low', 'close', 'volume',
                'closeTime', 'quoteVolume', 'trades'
            ])
            
            # 转换数据类型
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            # 计算基本指标
            current_price = float(df.iloc[-1]['close'])
            price_24h_ago = float(df.iloc[0]['close'])
            price_change_24h = current_price - price_24h_ago
            price_change_percentage_24h = (price_change_24h / price_24h_ago) * 100
            high_24h = df['high'].max()
            low_24h = df['low'].min()
            volume_24h = df['volume'].sum()
            
            # 计算移动平均线
            ma7 = df['close'].rolling(window=7).mean().iloc[-1]
            ma25 = df['close'].rolling(window=25).mean().iloc[-1]
            
            # 计算RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs.iloc[-1]))
            
            # 判断趋势
            if current_price > ma7 and ma7 > ma25 and rsi > 70:
                trend = 'strong_up'
            elif current_price > ma7 and ma7 > ma25:
                trend = 'up'
            elif current_price < ma7 and ma7 < ma25 and rsi < 30:
                trend = 'strong_down'
            elif current_price < ma7 and ma7 < ma25:
                trend = 'down'
            else:
                trend = 'neutral'
            
            return {
                'current_price': current_price,
                'price_change_24h': price_change_24h,
                'price_change_percentage_24h': price_change_percentage_24h,
                'high_24h': high_24h,
                'low_24h': low_24h,
                'volume_24h': volume_24h,
                'ma7': ma7,
                'ma25': ma25,
                'rsi': rsi,
                'trend': trend
            }
            
        except Exception as e:
            logger.error(f"分析价格数据失败: {str(e)}")
            return {}
    
    async def find_active_markets(self, min_trades: int = 100, min_volume: float = 1000) -> List[Dict]:
        """查找活跃的市场
        
        Args:
            min_trades: 最小成交笔数
            min_volume: 最小成交量（以USDC计价）
            
        Returns:
            活跃市场列表，每个市场包含：
            - symbol: 交易对符号
            - analysis: 市场分析结果
        """
        try:
            # 1. 获取所有市场
            markets = await self.client.get_markets()
            
            # 2. 分析每个市场
            active_markets = []
            for market in markets:
                symbol = market.get('symbol')
                if not symbol:
                    continue
                
                # 分析市场
                analysis = await self.analyze_market(symbol)
                if not analysis:
                    continue
                
                # 检查是否满足活跃度条件
                trade_analysis = analysis.get('trade_analysis', {})
                if (trade_analysis.get('total_trades', 0) >= min_trades and
                    trade_analysis.get('total_value', 0) >= min_volume):
                    active_markets.append({
                        'symbol': symbol,
                        'analysis': analysis
                    })
            
            # 3. 按成交量排序
            active_markets.sort(
                key=lambda x: x['analysis'].get('trade_analysis', {}).get('total_value', 0),
                reverse=True
            )
            
            return active_markets
            
        except Exception as e:
            logger.error(f"查找活跃市场失败: {str(e)}")
            return [] 