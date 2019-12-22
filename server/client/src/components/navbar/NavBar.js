import React from 'react';
import MainNavBarItem from './MainNavBarItem';

function NavBar(props) {
    const navItems = props.pages.map((item, index) =>
        <MainNavBarItem
            key={index}
            index={index}
            pageName={props.pages[index]["name"]}
            active={index === props.currentPageIndex}
            pages={props.pages}
            changePage={props.changePage}
        />
    );

    return (
        <nav className="navbar navbar-dark navbar-expand-lg py-3">
            <span className="navbar-brand" href="#">{props.title}</span>
            <button
                className="navbar-toggler"
                type="button"
                data-toggle="collapse"
                data-target="#mainNavBar"
                aria-controls="mainNavBar"
                aria-expanded="false"
                aria-label="Toggle Navigation"
            >
                <span className="navbar-toggler-icon"></span>
            </button>

            <div id="mainNavBar" className="collapse navbar-collapse justify-content-between">
                <div></div>
                <ul className="navbar-nav">{navItems}</ul>
            </div>
        </nav>
    );
}

export default NavBar;