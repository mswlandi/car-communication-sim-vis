import './FixImport';
import React, { useEffect, useRef, useState } from 'react';
import ReactDOM from 'react-dom/client';

import { Connector, useSubscription } from 'mqtt-react-hooks';

import './index.css';
import Navbar from './navbar.js';
import Map from './map.js';

export default function Status() {
    /* Message structure:
     *  topic: string
     *  message: string
     */
    const { message } = useSubscription([
        'carInfo/update',
    ]);

    return (
        <>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span>{`topic:${message ? message.topic : 'empty'} - message: ${message ? message.message : 'empty'}`}</span>
            </div>
        </>
    );
}

const Dashboard = () => {

    const map = useRef(null);

    return (
        <div>
            <Navbar />
            <Connector brokerUrl={`ws://${process.env.REACT_APP_CLUSTERIP}:${process.env.REACT_APP_MQTTPORT}/mqtt`}>
                <Map map={map}/>
                {/* <Status /> */}
            </Connector>
        </div>
    )
}

// ========================================

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<Dashboard />);
