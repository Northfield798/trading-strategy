import asyncio
import logging
from api.backpack_client import BackpackClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def explore_api():
    """探索 Backpack API 的功能"""
    client = BackpackClient()
    
    # 1. 获取市场信息
    logger.info("正在获取市场信息...")
    markets = await client.get_markets()
    if markets:
        logger.info(f"获取到 {len(markets)} 个市场")
        # 打印前5个市场的信息
        for market in markets[:5]:
            logger.info(f"市场: {market}")
    
    # 2. 获取交易员列表
    logger.info("\n正在获取交易员列表...")
    traders = await client.get_traders(limit=10)
    if traders:
        logger.info(f"获取到 {len(traders)} 个交易员")
        # 打印前3个交易员的信息
        for trader in traders[:3]:
            logger.info(f"交易员: {trader}")
    
    # 3. 如果有交易员，获取第一个交易员的详细信息
    if traders:
        trader_id = traders[0].get('id')
        if trader_id:
            logger.info(f"\n正在获取交易员 {trader_id} 的详细信息...")
            trader_info = await client.get_trader_info(trader_id)
            logger.info(f"交易员信息: {trader_info}")
            
            # 获取交易员的交易历史
            logger.info(f"\n正在获取交易员 {trader_id} 的交易历史...")
            trades = await client.get_trader_trades(trader_id, limit=10)
            if trades:
                logger.info(f"获取到 {len(trades)} 条交易记录")
                # 打印前3条交易记录
                for trade in trades[:3]:
                    logger.info(f"交易: {trade}")
            
            # 获取交易员的持仓信息
            logger.info(f"\n正在获取交易员 {trader_id} 的持仓信息...")
            positions = await client.get_trader_positions(trader_id)
            if positions:
                logger.info(f"获取到 {len(positions)} 个持仓")
                # 打印所有持仓信息
                for position in positions:
                    logger.info(f"持仓: {position}")
            
            # 获取交易员的资金信息
            logger.info(f"\n正在获取交易员 {trader_id} 的资金信息...")
            balance = await client.get_trader_balance(trader_id)
            if balance:
                logger.info(f"资金信息: {balance}")
    
    # 4. 获取特定市场的交易历史
    if markets:
        market_symbol = markets[0].get('symbol')
        if market_symbol:
            logger.info(f"\n正在获取市场 {market_symbol} 的交易历史...")
            trades = await client.get_trades(market_symbol, limit=10)
            if trades:
                logger.info(f"获取到 {len(trades)} 条交易记录")
                # 打印前3条交易记录
                for trade in trades[:3]:
                    logger.info(f"交易: {trade}")
    
    # 5. 获取特定市场的K线数据
    if markets:
        market_symbol = markets[0].get('symbol')
        if market_symbol:
            logger.info(f"\n正在获取市场 {market_symbol} 的K线数据...")
            klines = await client.get_klines(market_symbol, interval="1h", limit=10)
            if klines:
                logger.info(f"获取到 {len(klines)} 条K线数据")
                # 打印前3条K线数据
                for kline in klines[:3]:
                    logger.info(f"K线: {kline}")

if __name__ == "__main__":
    asyncio.run(explore_api()) 