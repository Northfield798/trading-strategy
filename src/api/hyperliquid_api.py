import aiohttp
import asyncio
from datetime import datetime, timedelta
import yaml
import os
from typing import Dict, List, Optional

class HyperliquidAPI:
    def __init__(self):
        self.config = self._load_config()
        self.base_url = self.config['api']['base_url']
        self.timeout = self.config['api']['timeout']
        self.session = None

    def _load_config(self) -> Dict:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                 'config', 'config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_trader_info(self, address: str) -> Dict:
        """获取交易员信息"""
        async with self.session.get(f"{self.base_url}/info/trader/{address}") as response:
            return await response.json()

    async def get_trader_trades(self, address: str, days: int = 7) -> List[Dict]:
        """获取交易员交易历史"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        async with self.session.get(
            f"{self.base_url}/trades",
            params={
                "address": address,
                "start_time": int(start_time.timestamp()),
                "end_time": int(end_time.timestamp())
            }
        ) as response:
            return await response.json()

    async def get_all_traders(self) -> List[str]:
        """获取所有交易员地址"""
        async with self.session.get(f"{self.base_url}/traders") as response:
            return await response.json()

    async def get_trader_performance(self, address: str, days: int = 7) -> Dict:
        """获取交易员表现数据"""
        trades = await this.get_trader_trades(address, days)
        
        if not trades:
            return {
                "address": address,
                "win_rate": 0,
                "return_rate": 0,
                "max_drawdown": 0,
                "total_trades": 0
            }

        # 计算胜率
        winning_trades = sum(1 for trade in trades if trade['pnl'] > 0)
        total_trades = len(trades)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        # 计算收益率
        initial_balance = trades[0]['balance']
        final_balance = trades[-1]['balance']
        return_rate = (final_balance - initial_balance) / initial_balance

        # 计算最大回撤
        max_drawdown = 0
        peak = initial_balance
        for trade in trades:
            if trade['balance'] > peak:
                peak = trade['balance']
            drawdown = (peak - trade['balance']) / peak
            max_drawdown = max(max_drawdown, drawdown)

        return {
            "address": address,
            "win_rate": win_rate,
            "return_rate": return_rate,
            "max_drawdown": max_drawdown,
            "total_trades": total_trades
        } 