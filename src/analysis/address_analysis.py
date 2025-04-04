import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class AddressAnalysis:
    """交易地址分析类"""
    
    def __init__(self):
        """初始化分析器"""
        pass
    
    def analyze_trades(self, trades: List[Dict], address: str) -> Dict:
        """分析特定地址的交易
        
        Args:
            trades: 交易记录列表
            address: 要分析的交易地址
            
        Returns:
            分析结果字典
        """
        try:
            # 过滤出该地址的交易
            address_trades = [t for t in trades if t.get('address') == address]
            if not address_trades:
                logger.warning(f"未找到地址 {address} 的交易记录")
                return {}
            
            # 计算基本指标
            total_trades = len(address_trades)
            winning_trades = [t for t in address_trades if t.get('profit', 0) > 0]
            losing_trades = [t for t in address_trades if t.get('profit', 0) < 0]
            
            win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
            total_profit = sum(t.get('profit', 0) for t in winning_trades)
            total_loss = sum(t.get('profit', 0) for t in losing_trades)
            avg_profit = total_profit / len(winning_trades) if winning_trades else 0
            avg_loss = total_loss / len(losing_trades) if losing_trades else 0
            max_profit = max((t.get('profit', 0) for t in winning_trades), default=0)
            max_loss = min((t.get('profit', 0) for t in losing_trades), default=0)
            
            # 计算盈亏比
            profit_factor = abs(total_profit / total_loss) if total_loss != 0 else float('inf')
            
            # 计算夏普比率
            returns = [t.get('profit', 0) for t in address_trades]
            sharpe_ratio = self._calculate_sharpe_ratio(returns)
            
            # 计算最大回撤
            max_drawdown = self._calculate_max_drawdown(returns)
            
            # 分析时间分布
            time_distribution = self._analyze_time_distribution(address_trades)
            
            # 分析交易对分布
            symbol_distribution = self._analyze_symbol_distribution(address_trades)
            
            return {
                'address': address,
                'total_trades': total_trades,
                'win_rate': win_rate,
                'total_profit': total_profit,
                'total_loss': total_loss,
                'avg_profit': avg_profit,
                'avg_loss': avg_loss,
                'max_profit': max_profit,
                'max_loss': max_loss,
                'profit_factor': profit_factor,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'time_distribution': time_distribution,
                'symbol_distribution': symbol_distribution
            }
            
        except Exception as e:
            logger.error(f"分析地址 {address} 的交易时出错: {str(e)}")
            return {}
    
    def _calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """计算夏普比率
        
        Args:
            returns: 收益率列表
            risk_free_rate: 无风险利率
            
        Returns:
            夏普比率
        """
        if not returns:
            return 0.0
        
        returns = np.array(returns)
        excess_returns = returns - risk_free_rate/252  # 转换为日化收益率
        
        if len(excess_returns) < 2:
            return 0.0
            
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
    
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """计算最大回撤
        
        Args:
            returns: 收益率列表
            
        Returns:
            最大回撤
        """
        if not returns:
            return 0.0
            
        cumulative = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = running_max - cumulative
        return np.max(drawdown) if len(drawdown) > 0 else 0.0
    
    def _analyze_time_distribution(self, trades: List[Dict]) -> Dict:
        """分析交易时间分布
        
        Args:
            trades: 交易记录列表
            
        Returns:
            时间分布分析结果
        """
        try:
            # 提取交易时间
            timestamps = [datetime.fromtimestamp(t.get('timestamp', 0)/1000) for t in trades]
            hours = [t.hour for t in timestamps]
            
            # 统计每个小时的交易次数
            hour_counts = pd.Series(hours).value_counts()
            most_active_hour = hour_counts.index[0] if not hour_counts.empty else None
            
            return {
                'most_active_hour': most_active_hour
            }
            
        except Exception as e:
            logger.error(f"分析时间分布时出错: {str(e)}")
            return {}
    
    def _analyze_symbol_distribution(self, trades: List[Dict]) -> Dict:
        """分析交易对分布
        
        Args:
            trades: 交易记录列表
            
        Returns:
            交易对分布分析结果
        """
        try:
            # 统计每个交易对的交易次数和盈利
            symbol_stats = {}
            for trade in trades:
                symbol = trade.get('symbol')
                if not symbol:
                    continue
                    
                if symbol not in symbol_stats:
                    symbol_stats[symbol] = {
                        'count': 0,
                        'profit': 0
                    }
                    
                symbol_stats[symbol]['count'] += 1
                symbol_stats[symbol]['profit'] += trade.get('profit', 0)
            
            if not symbol_stats:
                return {}
            
            # 找出交易次数最多的交易对
            most_traded = max(symbol_stats.items(), key=lambda x: x[1]['count'])
            
            # 找出盈利最多的交易对
            most_profitable = max(symbol_stats.items(), key=lambda x: x[1]['profit'])
            
            return {
                'most_traded_symbol': most_traded[0],
                'most_profitable_symbol': most_profitable[0]
            }
            
        except Exception as e:
            logger.error(f"分析交易对分布时出错: {str(e)}")
            return {}
    
    def find_top_traders(self, trades: List[Dict], min_trades: int = 10) -> List[Dict]:
        """找出表现最好的交易地址
        
        Args:
            trades: 所有交易记录
            min_trades: 最小交易次数要求
            
        Returns:
            按夏普比率排序的交易地址列表
        """
        try:
            # 获取所有唯一的交易地址
            addresses = set(t.get('address') for t in trades if t.get('address'))
            
            # 分析每个地址
            trader_results = []
            for address in addresses:
                result = self.analyze_trades(trades, address)
                if result and result['total_trades'] >= min_trades:
                    trader_results.append(result)
            
            # 按夏普比率排序
            trader_results.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
            
            return trader_results
            
        except Exception as e:
            logger.error(f"查找顶级交易者时出错: {str(e)}")
            return [] 