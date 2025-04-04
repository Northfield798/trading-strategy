import asyncio
import logging
from api.backpack_client import BackpackClient
from data.data_store import DataStore
from analysis.address_analysis import AddressAnalysis

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_address_analysis():
    """测试地址分析功能"""
    client = BackpackClient()
    data_store = DataStore()
    analyzer = AddressAnalysis()
    
    # 1. 获取市场数据
    logger.info("正在获取市场数据...")
    markets = await client.get_markets()
    if not markets:
        logger.error("获取市场数据失败")
        return
    
    logger.info(f"获取到 {len(markets)} 个市场")
    
    # 2. 获取前3个市场的交易数据
    all_trades = []
    for i, market in enumerate(markets[:3]):
        symbol = market.get('symbol')
        if symbol:
            logger.info(f"\n正在获取市场 {symbol} 的交易数据...")
            trades = await client.get_trades(symbol, limit=100)
            if trades:
                logger.info(f"获取到 {len(trades)} 条交易记录")
                # 打印第一条交易记录的结构
                if trades:
                    logger.info("\n交易记录结构示例:")
                    logger.info(trades[0])
                all_trades.extend(trades)
    
    if not all_trades:
        logger.error("未获取到任何交易数据")
        return
    
    logger.info(f"\n总共获取到 {len(all_trades)} 条交易记录")
    
    # 3. 分析交易地址
    logger.info("\n正在分析交易地址...")
    top_traders = analyzer.find_top_traders(all_trades, min_trades=5)
    
    if not top_traders:
        logger.error("未找到符合条件的交易地址")
        return
    
    logger.info(f"\n找到 {len(top_traders)} 个符合条件的交易地址")
    
    # 4. 打印前5个交易地址的分析结果
    logger.info("\n前5个交易地址的分析结果:")
    for i, trader in enumerate(top_traders[:5]):
        logger.info(f"\n交易地址 {i+1}:")
        logger.info(f"地址: {trader['address']}")
        logger.info(f"总交易次数: {trader['total_trades']}")
        logger.info(f"胜率: {trader['win_rate']:.2%}")
        logger.info(f"总盈利: {trader['total_profit']:.2f}")
        logger.info(f"总亏损: {trader['total_loss']:.2f}")
        logger.info(f"平均盈利: {trader['avg_profit']:.2f}")
        logger.info(f"平均亏损: {trader['avg_loss']:.2f}")
        logger.info(f"最大盈利: {trader['max_profit']:.2f}")
        logger.info(f"最大亏损: {trader['max_loss']:.2f}")
        logger.info(f"盈亏比: {trader['profit_factor']:.2f}")
        logger.info(f"夏普比率: {trader['sharpe_ratio']:.2f}")
        logger.info(f"最大回撤: {trader['max_drawdown']:.2f}")
        
        # 打印时间分布
        time_dist = trader['time_distribution']
        if time_dist:
            logger.info("\n交易时间分布:")
            logger.info(f"最活跃的交易时间: {time_dist['most_active_hour']} 时")
        
        # 打印交易对分布
        symbol_dist = trader['symbol_distribution']
        if symbol_dist:
            logger.info("\n交易对分布:")
            logger.info(f"最常交易的交易对: {symbol_dist['most_traded_symbol']}")
            logger.info(f"最盈利的交易对: {symbol_dist['most_profitable_symbol']}")

if __name__ == "__main__":
    asyncio.run(test_address_analysis()) 