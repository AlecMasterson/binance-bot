import React from 'react';

export default function Collapse(props) {
    const titleFormatted = props.title.replace(/\s/g, "");

    const header = titleFormatted + "Header";
    const body = titleFormatted + "Collapse";

    const additionalInfo = (props.additionalInfo == null) ? null : <span>{props.additionalInfo}</span>;

    return (
        <div className="card">
            <div
                id={header}
                className="card-header card-collapse py-4"
                aria-controls={"#" + body}
                aria-expanded="false"
                data-toggle="collapse"
                data-target={"#" + body}
                role="button"
            >
                <h4 className="d-flex mb-0 justify-content-between">
                    {props.title}
                    {additionalInfo}
                </h4>
            </div>

            <div id={body} className="collapse" aria-labelledby={"#" + header} data-parent={props.parent}>
                <div className="border-collapse mx-5"></div>
                <div className="card-body pb-0">
                    {props.temp}
                </div>
            </div>
        </div>
    );
}