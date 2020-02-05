const { ExpressApp } = require('./config/SetupExpress');
const { BinanceConnection } = require('./config/BinanceConnection');
const { DBConnection } = require('./config/DBConnection');
const startWebsockets = require('./services/websockets');

async function startServer() {
    await BinanceConnection.connect;
    await DBConnection.connect;

    startWebsockets();

    ExpressApp.listen(process.env.PORT, () => {
        console.log(`Server has Started on Port ${process.env.PORT}!`);
    }).on('error', (error) => {
        console.log(error);
        process.exit(1);
    });
}

startServer();