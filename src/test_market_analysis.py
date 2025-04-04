import asyncio
import logging
from api.backpack_client import BackpackClient
from analysis.market_analysis import MarketAnalysis

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_market_analysis():
    """测试市场分析功能"""
    client = BackpackClient()
    analyzer = MarketAnalysis(client)
    
    # 1. 查找活跃市场
    logger.info("正在查找活跃市场...")
    active_markets = await analyzer.find_active_markets(min_trades=50, min_volume=1000)
    
    if not active_markets:
        logger.error("未找到活跃市场")
        return
    
    logger.info(f"\n找到 {len(active_markets)} 个活跃市场")
    
    # 2. 分析前3个最活跃的市场
    for i, market in enumerate(active_markets[:3]):
        symbol = market['symbol']
        analysis = market['analysis']
        
        logger.info(f"\n市场 {i+1}: {symbol}")
        
        # 打印市场深度分析
        depth = analysis.get('market_depth', {})
        if depth:
            logger.info("\n市场深度分析:")
            logger.info(f"买单总量: {depth['bid_volume']:.2f}")
            logger.info(f"卖单总量: {depth['ask_volume']:.2f}")
            logger.info(f"买单总价值: {depth['bid_value']:.2f} USDC")
            logger.info(f"卖单总价值: {depth['ask_value']:.2f} USDC")
            logger.info(f"买卖价差: {depth['spread']:.8f}")
            logger.info(f"买卖价差百分比: {depth['spread_percentage']:.2f}%")
            logger.info(f"中间价格: {depth['mid_price']:.8f}")
            logger.info(f"买卖失衡程度: {depth['imbalance']:.2f}")
        
        # 打印交易分析
        trades = analysis.get('trade_analysis', {})
        if trades:
            logger.info("\n交易分析:")
            logger.info(f"总成交笔数: {trades['total_trades']}")
            logger.info(f"总成交量: {trades['total_volume']:.2f}")
            logger.info(f"总成交额: {trades['total_value']:.2f} USDC")
            logger.info(f"平均成交量: {trades['avg_trade_size']:.2f}")
            logger.info(f"平均成交额: {trades['avg_trade_value']:.2f} USDC")
            logger.info(f"买单比例: {trades['buy_ratio']:.2%}")
            logger.info(f"价格趋势: {trades['price_trend']}")
            logger.info(f"波动率: {trades['volatility']:.2%}")
        
        # 打印价格分析
        price = analysis.get('price_analysis', {})
        if price:
            logger.info("\n价格分析:")
            logger.info(f"当前价格: {price['current_price']:.8f}")
            logger.info(f"24小时价格变化: {price['price_change_24h']:.8f}")
            logger.info(f"24小时价格变化百分比: {price['price_change_percentage_24h']:.2f}%")
            logger.info(f"24小时最高价: {price['high_24h']:.8f}")
            logger.info(f"24小时最低价: {price['low_24h']:.8f}")
            logger.info(f"24小时成交量: {price['volume_24h']:.2f}")
            logger.info(f"7小时均价: {price['ma7']:.8f}")
            logger.info(f"25小时均价: {price['ma25']:.8f}")
            logger.info(f"RSI: {price['rsi']:.2f}")
            logger.info(f"趋势: {price['trend']}")

if __name__ == "__main__":
    asyncio.run(test_market_analysis()) 