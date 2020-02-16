const { ExpressApp } = require('./config/ExpressApp');
const { BinanceConnection } = require('./config/BinanceConnection');
const { DBConnection } = require('./config/DBConnection');
const candlesticks = require('./streams/candlesticks');

function handleError(error) {
    console.log(error);
    process.exit(1);
}

async function startServer() {
    await ExpressApp.create()
        .then((app) => ExpressApp.app = app)
        .catch(handleError);
    console.log('ExpressJS is Setup!');

    await BinanceConnection.connect()
        .then((connection) => BinanceConnection.binance = connection)
        .catch(handleError);
    console.log('Connected to the Binance Exchange API!');

    await DBConnection.connect()
        .then((connection) => DBConnection.db = connection)
        .catch(handleError);
    console.log('Connected to the DB!');

    await candlesticks().catch(handleError);
    console.log('Websocket Streams Started!')

    ExpressApp.app.listen(process.env.PORT, () => {
        console.log(`Server has Started on Port ${process.env.PORT}!`);
    }).on('error', handleError);
}

startServer();