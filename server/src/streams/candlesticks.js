const { BinanceConnection } = require('../config/BinanceConnection');
const History = require('../services/History');

module.exports = async () => {
    const symbols = process.env.SYMBOLS.split(',');
    const intervals = process.env.INTERVALS.split(',');
    console.log(`Active Symbols: ${symbols}`);
    console.log(`Active Intervals: ${intervals}`);

    for (const i in intervals) {
        BinanceConnection.binance.websockets.candlesticks(symbols, intervals[i], (kLine) => {
            if (kLine.k.x) {
                History.insertKLine(kLine)
            }
        });
    }
}