const { DBConnection } = require('../config/DBConnection');

module.exports = {
    insertKLine: (kLine) => {
        try {
            const values = [[
                kLine.s, kLine.k.i, new Date(kLine.k.t), kLine.k.o,
                kLine.k.h, kLine.k.l, kLine.k.c, kLine.k.v, kLine.k.n, new Date(kLine.k.T)
            ]];

            DBConnection.db.query(
                'INSERT IGNORE INTO history (symbol,width,openTime,openPrice,highPrice,lowPrice,closePrice,volume,numberTrades,closeTime) VALUES (?)',
                values,
                (error) => {
                    if (error) {
                        console.log(`Failed to Insert ${kLine.s}-${kLine.k.i} at ${new Date(kLine.k.T)}: ${error}`);
                        return;
                    } else {
                        console.log(`Inserted ${kLine.s}-${kLine.k.i} at ${new Date(kLine.k.T)}`);
                    }
                }
            );
        } catch (error) {
            console.log(`Unknown Error for kLine ${kLine}: ${error}`);
        }
    },

    getCount: async (symbol) => {
        return await new Promise((resolve, reject) => {
            DBConnection.db.query(
                `SELECT COUNT(*) FROM history${symbol ? ` WHERE SYMBOL='${symbol}'` : ''}`,
                (error, result) => {
                    if (error) {
                        reject(error);
                    }
                    resolve(result[0]['COUNT(*)']);
                }
            );
        });
    }
}