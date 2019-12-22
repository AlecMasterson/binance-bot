import React from 'react';

export default function MainNavBarItem(props) {
    return (
        <li className={props.active ? "nav-item active" : "nav-item"} onClick={() => props.changePage(props.pageName)}>
            <span className="nav-link">
                {props.pageName}
            </span>
        </li>
    );
}