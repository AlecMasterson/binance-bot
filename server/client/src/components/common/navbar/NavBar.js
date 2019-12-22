import React from 'react';
import MainNavBarItem from './MainNavBarItem';

export default function NavBar(props) {
    let navItems = [];
    for (var page in props.pages) {
        navItems.push(
            <MainNavBarItem
                key={page}
                pageName={page}
                active={page === props.currentPage}
                changePage={props.changePage}
            />
        );
    }

    return (
        <nav className="navbar navbar-dark navbar-expand-lg py-3">
            <span className="navbar-brand">{props.title}</span>
            <button
                className="navbar-toggler"
                aria-controls="#mainNavBar"
                aria-expanded="false"
                aria-label="Toggle Navigation"
                data-toggle="collapse"
                data-target="#mainNavBar"
            >
                <span className="navbar-toggler-icon"></span>
            </button>

            <div id="mainNavBar" className="collapse navbar-collapse justify-content-between">
                <div></div>
                <ul className="navbar-nav">
                    {navItems}
                </ul>
            </div>
        </nav>
    );
}