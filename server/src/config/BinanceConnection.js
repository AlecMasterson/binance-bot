const binance = require('node-binance-api');

exports.BinanceConnection = {
    connect: async () => binance().options({
        APIKEY: process.env.BINANCE_APIKEY,
        APISECRET: process.env.BINANCE_APISECRET,
        useServerTime: true,
        verbose: true
    })
};