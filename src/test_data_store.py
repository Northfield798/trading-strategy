import asyncio
import logging
from api.backpack_client import BackpackClient
from data.data_store import DataStore

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_data_store():
    """测试数据存储功能"""
    client = BackpackClient()
    data_store = DataStore()
    
    # 1. 获取并保存市场数据
    logger.info("正在获取市场数据...")
    markets = await client.get_markets()
    if markets:
        logger.info(f"获取到 {len(markets)} 个市场")
        # 保存前5个市场的数据
        for i, market in enumerate(markets[:5]):
            symbol = market.get('symbol')
            if symbol:
                logger.info(f"保存市场数据: {symbol}")
                data_store.save_market_data(symbol, market)
                
                # 加载并验证数据
                loaded_data = data_store.load_market_data(symbol)
                if loaded_data:
                    logger.info(f"成功加载市场数据: {symbol}")
                    logger.info(f"数据内容: {loaded_data}")
    
    # 2. 获取并保存交易数据
    if markets and len(markets) > 0:
        # 测试前3个市场
        for i, market in enumerate(markets[:3]):
            symbol = market.get('symbol')
            if symbol:
                logger.info(f"\n正在获取交易数据: {symbol}")
                trades = await client.get_trades(symbol, limit=10)
                if trades:
                    logger.info(f"获取到 {len(trades)} 条交易记录")
                    logger.info(f"保存交易数据: {symbol}")
                    data_store.save_trade_data(symbol, trades)
                    
                    # 加载并验证数据
                    loaded_data = data_store.load_trade_data(symbol)
                    if loaded_data:
                        logger.info(f"成功加载交易数据: {symbol}")
                        logger.info(f"数据条数: {len(loaded_data)}")
    
    # 3. 获取并保存K线数据
    if markets and len(markets) > 0:
        # 测试前3个市场
        for i, market in enumerate(markets[:3]):
            symbol = market.get('symbol')
            if symbol:
                logger.info(f"\n正在获取K线数据: {symbol}")
                klines = await client.get_klines(symbol, interval="1h", limit=10)
                if klines:
                    logger.info(f"获取到 {len(klines)} 条K线数据")
                    logger.info(f"保存K线数据: {symbol}")
                    data_store.save_kline_data(symbol, "1h", klines)
                    
                    # 加载并验证数据
                    loaded_data = data_store.load_kline_data(symbol, "1h")
                    if loaded_data:
                        logger.info(f"成功加载K线数据: {symbol}")
                        logger.info(f"数据条数: {len(loaded_data)}")
    
    # 4. 测试不同的K线间隔
    if markets and len(markets) > 0:
        symbol = markets[0].get('symbol')
        if symbol:
            intervals = ["1m", "5m", "15m", "1h", "4h", "1d"]
            for interval in intervals:
                logger.info(f"\n正在获取K线数据: {symbol}, 间隔: {interval}")
                klines = await client.get_klines(symbol, interval=interval, limit=10)
                if klines:
                    logger.info(f"获取到 {len(klines)} 条K线数据")
                    logger.info(f"保存K线数据: {symbol}, 间隔: {interval}")
                    data_store.save_kline_data(symbol, interval, klines)
                    
                    # 加载并验证数据
                    loaded_data = data_store.load_kline_data(symbol, interval)
                    if loaded_data:
                        logger.info(f"成功加载K线数据: {symbol}, 间隔: {interval}")
                        logger.info(f"数据条数: {len(loaded_data)}")

if __name__ == "__main__":
    asyncio.run(test_data_store()) 