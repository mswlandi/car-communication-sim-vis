import React, { useEffect, useRef, useState } from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';

import Navbar from './navbar.js';
import Map from './map.js';

import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";

const Dashboard = () => {

    const map = useRef(null);
    // const [value, setValue] = useState(1);

    // console.log(map.current.getCanvas());

    return (
        <div>
            <Navbar />
            <Map map={map}/>
        </div>
    )
}

// ========================================

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<Dashboard />);
