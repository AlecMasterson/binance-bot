import React from 'react';

export default function Select(props) {
    const items = props.items.map((item, index) =>
        <option key={index} value={item}>{item}</option>
    );

    return (
        <div className="form-group">
            <h3 htmlFor={"#" + props.name + "Select"}>{props.name}</h3>
            <select id={props.name + "Select"} className="form-control" value={props.value} onChange={props.onChange}>
                <option value="" disabled>{props.default}</option>
                {items}
            </select>
            <small>{props.small}</small>
        </div>
    );
}