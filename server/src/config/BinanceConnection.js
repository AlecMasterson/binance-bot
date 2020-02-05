const binance = require('node-binance-api');

async function connect() {
    try {
        const data = await new Promise((resolve) => {
            const connection = binance().options({
                APIKEY: process.env.BINANCE_APIKEY,
                APISECRET: process.env.BINANCE_APISECRET,
                useServerTime: true,
                verbose: true
            });

            resolve(connection);
        });
        console.log('Connected to the Binance API!');

        return data;
    } catch (error) {
        console.log(error);
        process.exit(1);
    }
}

const setup = {
    connect: connect().then((connection) => {
        setup.binance = connection;
        delete setup.connect;
    })
}

exports.BinanceConnection = setup;