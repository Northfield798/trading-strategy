import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.api.hyperliquid_api import HyperliquidAPI

class TraderAnalysis:
    """交易员分析类"""
    
    def __init__(self):
        """初始化分析类"""
        self.logger = logging.getLogger(__name__)
        self.api = HyperliquidAPI()
        self.config = self.api.config

    async def analyze_traders(self, days: int = 7, limit: int = 100) -> pd.DataFrame:
        """分析所有交易员数据"""
        async with self.api as api:
            # 获取所有交易员
            traders = await api.get_all_traders()
            
            # 获取每个交易员的性能数据
            tasks = [api.get_trader_performance(trader, days) for trader in traders]
            results = await asyncio.gather(*tasks)
            
            # 转换为DataFrame
            df = pd.DataFrame(results)
            
            # 过滤掉交易次数过少的交易员
            df = df[df['total_trades'] >= self.config['analysis']['min_trades']]
            
            # 按收益率排序
            df = df.sort_values('return_rate', ascending=False)
            
            # 限制返回数量
            return df.head(limit)

    def calculate_statistics(self, df: pd.DataFrame) -> Dict:
        """计算统计数据"""
        return {
            "total_traders": len(df),
            "avg_win_rate": df['win_rate'].mean(),
            "avg_return_rate": df['return_rate'].mean(),
            "avg_max_drawdown": df['max_drawdown'].mean(),
            "top_return_rate": df['return_rate'].max(),
            "top_win_rate": df['win_rate'].max(),
            "min_max_drawdown": df['max_drawdown'].min()
        }

    def get_top_traders(self, df: pd.DataFrame, metric: str = 'return_rate', top_n: int = 10) -> pd.DataFrame:
        """获取特定指标的前N名交易员"""
        return df.nlargest(top_n, metric)[['address', metric, 'total_trades']]

    def analyze_trades(self, trades: List[Dict]) -> Dict:
        """分析交易数据
        
        Args:
            trades: 交易记录列表
            
        Returns:
            分析结果字典
        """
        try:
            if not trades:
                return {
                    "total_trades": 0,
                    "win_rate": 0,
                    "profit_loss": 0,
                    "avg_profit": 0,
                    "max_profit": 0,
                    "max_loss": 0
                }
            
            # 转换为 DataFrame
            df = pd.DataFrame(trades)
            
            # 计算基本统计
            total_trades = len(df)
            
            # 根据 Backpack API 的数据格式计算盈亏
            # 使用 quantity 和 price 字段
            df['value'] = df['price'].astype(float) * df['quantity'].astype(float)
            
            # 使用 isBuyerMaker 判断买卖方向
            df['profit'] = df.apply(lambda x: 
                float(x['value']) if not x['isBuyerMaker'] else -float(x['value']), 
                axis=1
            )
            
            profitable_trades = len(df[df['profit'] > 0])
            win_rate = profitable_trades / total_trades if total_trades > 0 else 0
            
            # 计算盈亏统计
            total_profit = df['profit'].sum()
            avg_profit = df['profit'].mean()
            max_profit = df['profit'].max()
            max_loss = df['profit'].min()
            
            return {
                "total_trades": total_trades,
                "win_rate": win_rate,
                "profit_loss": total_profit,
                "avg_profit": avg_profit,
                "max_profit": max_profit,
                "max_loss": max_loss
            }
            
        except Exception as e:
            self.logger.error(f"分析交易数据时出错: {str(e)}")
            return {}
    
    def analyze_positions(self, positions: List[Dict]) -> Dict:
        """分析持仓数据
        
        Args:
            positions: 持仓记录列表
            
        Returns:
            分析结果字典
        """
        try:
            if not positions:
                return {
                    "total_positions": 0,
                    "long_positions": 0,
                    "short_positions": 0,
                    "total_value": 0
                }
            
            # 转换为 DataFrame
            df = pd.DataFrame(positions)
            
            # 计算基本统计
            total_positions = len(df)
            long_positions = len(df[df['side'] == 'long'])
            short_positions = len(df[df['side'] == 'short'])
            total_value = df['value'].sum()
            
            return {
                "total_positions": total_positions,
                "long_positions": long_positions,
                "short_positions": short_positions,
                "total_value": total_value
            }
            
        except Exception as e:
            self.logger.error(f"分析持仓数据时出错: {str(e)}")
            return {}
    
    def analyze_balance(self, balance: Dict) -> Dict:
        """分析资金数据
        
        Args:
            balance: 资金信息字典
            
        Returns:
            分析结果字典
        """
        try:
            if not balance:
                return {
                    "total_balance": 0,
                    "available_balance": 0,
                    "locked_balance": 0
                }
            
            return {
                "total_balance": balance.get('total', 0),
                "available_balance": balance.get('available', 0),
                "locked_balance": balance.get('locked', 0)
            }
            
        except Exception as e:
            self.logger.error(f"分析资金数据时出错: {str(e)}")
            return {} 