const candlesticks = require('../streams/candlesticks');

function startWebsockets() {
    const symbols = process.env.SYMBOLS.split(',');
    const intervals = process.env.INTERVALS.split(',');
    console.log(`Active Symbols: ${symbols}`);
    console.log(`Active Intervals: ${intervals}`);

    let streams = [];
    for (const i in intervals) {
        streams.push(candlesticks(symbols, intervals[i]));
    }
    console.log('WebSockets Started!');
}

module.exports = startWebsockets;