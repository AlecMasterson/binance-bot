import React from 'react';
import BaseAPI from '../../api/BaseAPI';
import Select from '../common/select/Select';

export default class Analyze extends React.Component {
    constructor(props) {
        super(props);

        this.getSymbols = this.getSymbols.bind(this);
        this.getIntervals = this.getIntervals.bind(this);
        this.getData = this.getData.bind(this);

        this.state = {
            isLoading: false,
            error: false,
            symbols: [],
            intervals: [],
            data: []
        };
    }

    componentDidMount() {
        this.getSymbols();
    }

    getSymbols() {
        this.setState({
            isLoading: true
        }, () => BaseAPI.getData("/analyze/symbols")
            .then((response) => {
                this.setState({
                    isLoading: false,
                    error: response.error,
                    symbols: (response.data ? response.data : []),
                    intervals: []
                });
            })
        );
    }

    getIntervals() {
        this.setState({
            isLoading: true
        }, () => BaseAPI.getData("/analyze/intervals?symbol=" + this.state.currentSymbol)
            .then((response) => {
                this.setState({
                    isLoading: false,
                    error: response.error,
                    intervals: (response.data ? response.data : [])
                });
            })
        );
    }

    getData() {
        this.setState({
            isLoading: true
        }, () => BaseAPI.getData("/analyze/data?symbol=" + this.state.currentSymbol + "&interval=" + this.state.currentInterval)
            .then((response) => {
                this.setState({
                    isLoading: false,
                    error: response.error,
                    data: (response.data ? response.data : [])
                });
            })
        );
    }

    render() {
        return (
            <div className="mt-4">
                <h4>Historical Data</h4>
                <div className="card">
                    <div className="card-body">
                        <form>
                            <Select
                                name="Symbol"
                                items={this.state.symbols}
                                default={"Choose a Symbol"}
                                value={this.state.currentSymbol ? this.state.currentSymbol : ""}
                                onChange={(event) => this.setState({
                                    currentSymbol: event.target.value,
                                    currentInterval: null
                                }, () => this.getIntervals())}
                                small={"Crypto Exchange"} />

                            <Select
                                name="Interval"
                                items={this.state.intervals}
                                default={"Choose an Interval"}
                                value={this.state.currentInterval ? this.state.currentInterval : ""}
                                onChange={(event) => this.setState({
                                    currentInterval: event.target.value,
                                }, () => this.getData())}
                                small={"Candlestick Duration (in hours)"} />
                        </form>
                    </div>
                </div>
            </div>
        );
    }
}