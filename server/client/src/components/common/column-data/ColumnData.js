import React from 'react';

export default function ColumnData(props) {
    return (
        <div className="col-xs-12 col-sm-6 col-md-4 col-lg-3 mb-3">
            <div className="row no-gutters justify-content-center">
                <h5 className="mb-0"><u>{props.name}</u></h5>
            </div>
            <div className="row no-gutters justify-content-center">{props.value}</div>
        </div>
    );
}