const { DBConnection } = require('../config/DBConnection');

const SQL_INSERT = 'INSERT IGNORE INTO history (symbol,width,openTime,openPrice,highPrice,lowPrice,closePrice,volume,numberTrades,closeTime) VALUES (?)';

module.exports = {
    insertKLine: (kLine) => {
        try {
            const values = [[
                kLine.s, kLine.k.i, new Date(kLine.k.t), kLine.k.o,
                kLine.k.h, kLine.k.l, kLine.k.c, kLine.k.v, kLine.k.n, new Date(kLine.k.T)
            ]];

            DBConnection.db.query(SQL_INSERT, values, (error) => {
                if (error) {
                    console.log(`Failed to Insert ${kLine.s}-${kLine.k.i} at ${new Date(kLine.k.T)}:\n${error}`);
                    return;
                }
                console.log(`Inserted ${kLine.s}-${kLine.k.i} at ${new Date(kLine.k.T)}`);
            });
        } catch (error) {
            console.log(error);
        }
    }
}