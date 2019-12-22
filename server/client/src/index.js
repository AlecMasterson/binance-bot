import React from 'react';
import ReactDOM from 'react-dom';
import './styles/index.css';
import NavBar from './components/common/navbar/NavBar';
import Analyze from './components/pages/Analyze';
import TradingModels from './components/pages/TradingModels';

const AppTitle = "Binance Bot Admin Server";

class App extends React.Component {
    constructor(props) {
        super(props);

        this.pages = {
            "Analyze": <Analyze />,
            "Trading Models": <TradingModels />,
            "Positions": null
        };

        this.state = { currentPage: "Trading Models" };
    }

    render() {
        return (
            <div>
                <NavBar
                    title={AppTitle}
                    pages={this.pages}
                    currentPage={this.state.currentPage}
                    changePage={(newPage) => this.setState({
                        currentPage: newPage
                    })}
                />

                <div className="d-flex">
                    <div className="container-fluid col-6 my-4 mx-auto">
                        {this.pages[this.state.currentPage]}
                    </div>
                </div>
            </div>
        );
    }
}

ReactDOM.render(<App />, document.getElementById('root'));