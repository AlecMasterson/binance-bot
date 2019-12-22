import React from 'react';

function MainNavBarItem(props) {
    return (
        <li className={props.active ? "nav-item active" : "nav-item"} onClick={() => props.changePage(props.index)}>
            <span className="nav-link">{props.pageName}</span>
        </li>
    );
}

export default MainNavBarItem;