import React from 'react';
import BaseAPI from '../../api/BaseAPI';
import Loading from '../common/loading/Loading';
import Collapse from '../common/collapse/Collapse';
import ColumnData from '../common/column-data/ColumnData';

export default class TradingModels extends React.Component {
    constructor(props) {
        super(props);

        this.getTradingModels = this.getTradingModels.bind(this);

        this.buildModelsView = this.buildModelsView.bind(this);

        this.state = {
            isLoading: false,
            error: false,
            data: []
        };
    }

    componentDidMount() {
        this.getTradingModels();
    }

    getTradingModels() {
        this.setState({
            isLoading: true
        }, () => BaseAPI.getData("/tradingModels")
            .then((response) => {
                this.setState({
                    isLoading: false,
                    error: response.error,
                    data: (response.data ? response.data : [])
                })
            })
        );
    }

    buildModelsView(models) {
        const data = models.map((item, index) =>
            <Collapse
                key={index}
                parent="#accordion"
                title={item.name}
                additionalInfo={(index > 0) ? item.overall + "%" : null}
                temp={
                    <div>
                        <div className="row no-gutters">
                            <ColumnData name="Active Since" value={item.birth} />
                            <ColumnData name="Overall Return" value={item.overall + "%"} />
                            <ColumnData name="Weekly Return" value={item.weekly + "%"} />
                            <ColumnData name="No. of Trades" value={item.trades} />
                        </div>
                        <small className="mt-5">Last Updated: 2019-12-12 13:15:00</small>
                    </div>
                }
            />
        );

        return (
            <div id="accordion">
                {data}
            </div>
        );
    }

    render() {
        let view = null;
        if (!this.state.isLoading) {
            if (!this.state.error) {
                if (this.state.data && this.state.data.length > 0) {
                    view = this.buildModelsView(this.state.data);
                } else {
                    view = (
                        <div className="card align-items-center">
                            <div className="card-body">
                                <h5 className="mb-0">No Models Available</h5>
                            </div>
                        </div>
                    );
                }
            } else {
                view = (
                    <div className="card align-items-center">
                        <div className="card-body">
                            <h5 className="mb-0">An Error Occurred</h5>
                        </div>
                    </div>
                );
            }
        } else {
            view = (
                <div className="card align-items-center">
                    <div className="card-body">
                        <Loading />
                    </div>
                </div>
            );
        }

        return (
            <div>
                <div className="row no-gutters justify-content-between mb-2">
                    <h1 className="mb-0">Models</h1>
                    <i className="fas fa-refresh" style={{ backgroundColor: "white" }}></i>
                    <input className="btn btn-secondary" type="button" value="Refresh" disabled={this.state.isLoading} onClick={() => this.getTradingModels()} />
                </div>
                {view}
            </div>
        );
    }
}