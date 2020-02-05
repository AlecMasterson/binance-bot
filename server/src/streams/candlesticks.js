const { BinanceConnection } = require('../config/BinanceConnection');
const { DBConnection } = require('../config/DBConnection');

const SQL_INSERT = 'INSERT IGNORE INTO history (symbol,width,openTime,openPrice,high,low,closePrice,volume,numberTrades,closeTime) VALUES (?)';

module.exports = (symbols, interval) => {
    return BinanceConnection.binance.websockets.candlesticks(symbols, interval, (kLine) => {
        if (kLine.k.x) {
            console.log(`New ${kLine.s}-${kLine.k.i} kLine: ${new Date(kLine.k.T)}`);

            const values = [[
                kLine.s, kLine.k.i, new Date(kLine.k.t), kLine.k.o,
                kLine.k.h, kLine.k.l, kLine.k.c, kLine.k.v, kLine.k.n, new Date(kLine.k.T)
            ]];

            DBConnection.db.query(SQL_INSERT, values, (error) => {
                if (error) {
                    console.log(error);
                }
            });
        }
    });
}