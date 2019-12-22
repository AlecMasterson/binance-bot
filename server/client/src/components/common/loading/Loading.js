import React from 'react';

export default function Loading(props) {
    return (
        <div>
            <div className="spinner-border mx-auto" style={{ width: "3rem", height: "3rem" }}>
                <span className="sr-only">Loading...</span>
            </div>
        </div>
    );
}