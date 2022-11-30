import React, {useRef, useEffect, useState} from 'react';
import maplibregl from 'maplibre-gl';
import './map.css';
import 'maplibre-gl/dist/maplibre-gl.css';
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader'
import { useSubscription } from 'mqtt-react-hooks';


// uses the longitude and latitude of the model to give its position in threejs coordinates
// uses the center of the rendering layer as reference for translating, and scaling according to the latitude
function getPositionFromLongLat(center, carData){
    
    var centerCoords = maplibregl.MercatorCoordinate.fromLngLat(center.LngLat, 0);
    var objectCoords = maplibregl.MercatorCoordinate.fromLngLat(carData.LngLat, 0);
    
    var dx = centerCoords.x - objectCoords.x;
    var dy = centerCoords.y - objectCoords.y;
    
    dx /= center.scale;
    dy /= center.scale;

    return new THREE.Vector3(-dx, 0, -dy);
}


// loads a GLTF 3D model of a car into the threejs scene
function loadGLTFModel(scene, center, carData) {
    return new Promise((resolve, reject) => {
        const dracoLoader = new DRACOLoader();
        dracoLoader.setDecoderPath('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/js/libs/draco/');
        const loader = new GLTFLoader();
        loader.setDRACOLoader(dracoLoader);

        const position = getPositionFromLongLat(center, carData);

        loader.load(
            "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/ferrari.glb",
            (gltf) => {
                const obj = gltf.scene;
                obj.position.set(position.x, position.y, position.z);
                obj.rotation.set(carData.rotateX, carData.rotateY, carData.rotateZ);
                obj.receiveShadow = false;
                obj.castShadow = false;
                scene.add(obj);

                obj.traverse(function(child) {
                    if(child.isMesh) {
                        child.castShadow = false;
                        child.receiveShadow = false;
                    }
                });

                resolve(obj);
            },
            undefined,
            function(error) {
                console.log(error);
                reject(error);
            }
        );
    });
}


export default function Map(props) {
    const mapContainer = useRef(null);
    const [carData2] = useState({
        id: "second_car", // test car 2
        LngLat: [9.106607, 48.744746],
        altitude: 0,
        rotateX: 0,
        rotateY: 3 * Math.PI / 8, // Actual desired car rotation
        rotateZ: 0
    });
    const [zoom] = useState(21);
    const [API_KEY] = useState('cqvAKHMBJexanBFc1owH ');

    const { message } = useSubscription([
        'carInfo/update',
    ]);
    
    const [lat] = useState(48.744715);
    const [lng] = useState(9.1066383);
    const [centerMercator] = useState(maplibregl.MercatorCoordinate.fromLngLat([lng, lat]));
    const [center] = useState({
        LngLat: [lng, lat],
        translateX: centerMercator.x,
        translateY: centerMercator.y,
        translateZ: centerMercator.z,
        rotateX: Math.PI / 2,
        rotateY: 0,
        rotateZ: 0,
        scale: centerMercator.meterInMercatorCoordinateUnits()
    });

    const [carDataList, setCarDataList] = useState([]);
    const [scene, setScene] = useState(new THREE.Scene());

    // updates information about car, if car doesn't exist in the car data array, adds it to the array.
    // will make a bunch of stuff even if no actual information about the car has changed
    // TODO:
    // - check if changes were made
    // - only change present fields
    function updateCarData(carData) {
        if (!carData.id) {
            console.log("requested car data update doesn't provide car ID");
            return false;
        }

        function updateState(carData, carIndexInList) {
            setCarDataList((oldList => {
                const updatedCarDataList = [...oldList];
    
                if (carIndexInList === -1) {
                    updatedCarDataList.push(carData);
                } else {
                    // console.log(`car data for car ID ${carData.id} updated.`);
                    updatedCarDataList.splice(carIndexInList, 1, carData);
                }
    
                return updatedCarDataList;
            }));
        }

        var carIndexInList = carDataList.findIndex((value, index, array) => {return carData.id === value.id});
        
        if (carIndexInList === -1) {
            // creates 3D model
            loadGLTFModel(scene, center, carData)
            .then((object) => {
                console.log(`model loaded for car ${carData.id}`);
                carData.obj = object;
                updateState(carData, carIndexInList);
            });
        } else {
            const position = getPositionFromLongLat(center, carData);
            
            const obj = carDataList[carIndexInList].obj;
            
            if (obj !== undefined) {
                obj.position.set(position.x, position.y, position.z);
                obj.rotation.set(carData.rotateX, carData.rotateY, carData.rotateZ);
                
                carData.obj = obj;
                updateState(carData, carIndexInList);
            }
        }

        return true;
    }

    // runs on message updates
    useEffect(() => {
        if (message) {
            if (message.topic === "carInfo/update") {
                const carData = JSON.parse(message.message);
                updateCarData(carData);
            }
        }
    }, [message]);

    // map initialization
    useEffect(() => {
        if (props.map.current) 
            return;
        
        props.map.current = new maplibregl.Map({
            container: mapContainer.current,
            style: `https://api.maptiler.com/maps/streets/style.json?key=${API_KEY}`,
            center: [lng, lat],
            zoom: zoom,
            pitch: 60,
            maxPitch: 85,
            antialias: true
        });

        // ----------- 1ST MODEL DATA ---------------------
        // transformation parameters to position, rotate and scale the 3D model onto the map
        var carData1 = {
            id: "first_car", // test car 1
            LngLat: [9.106596, 48.744459],
            altitude: 0,
            rotateX: 0,
            rotateY: 5.5 * Math.PI / 8, // Actual desired car rotation
            rotateZ: 0
        };
        // ------------------------------------------------

        // create a custom style layer for the map to implement the threejs WebGL content
        var customCarLayer = {
            id: 'threedee',
            type: 'custom',
            renderingMode: '3d',

            addLights: function (scene) {
                // create two three.js lights to illuminate the model
                var directionalLight = new THREE.DirectionalLight(0xffffff);
                directionalLight.position.set(0, -70, 100).normalize();
                scene.add(directionalLight);

                var directionalLight2 = new THREE.DirectionalLight(0xffffff);
                directionalLight2.position.set(0, 70, 100).normalize();
                scene.add(directionalLight2);

                return scene;
            },

            // method called when the layer is added to the map
            // https://maplibre.org/maplibre-gl-js-docs/api/properties/#styleimageinterface#onadd
            onAdd: function (map, gl) {
                this.camera = new THREE.Camera();
                setScene((oldScene) => {
                    this.addLights(oldScene);
                    return oldScene;
                });
                this.map = map;
                
                updateCarData(carData1);
                updateCarData(carData2);

                // use the MapLibre GL JS map canvas for three.js
                this.renderer = new THREE.WebGLRenderer({
                    canvas: map.getCanvas(),
                    context: gl,
                    antialias: true
                });

                this.renderer.autoClear = false;
            },

            // method fired on each animation frame
            // https://maplibre.org/maplibre-gl-js-docs/api/map/#map.event:render
            render: function (gl, matrix) {
                var rotationX = new THREE.Matrix4().makeRotationAxis(new THREE.Vector3(1, 0, 0), center.rotateX);
                var rotationY = new THREE.Matrix4().makeRotationAxis(new THREE.Vector3(0, 1, 0), center.rotateY);
                var rotationZ = new THREE.Matrix4().makeRotationAxis(new THREE.Vector3(0, 0, 1), center.rotateZ);

                var m = new THREE.Matrix4().fromArray(matrix);
                
                var l = new THREE.Matrix4().makeTranslation(center.translateX, center.translateY, center.translateZ)
                .scale(new THREE.Vector3(center.scale, -center.scale, center.scale))
                .multiply(rotationX)
                .multiply(rotationY)
                .multiply(rotationZ);

                this.camera.projectionMatrix.elements = matrix;
                this.camera.projectionMatrix = m.multiply(l);

                this.renderer.state.reset();
                this.renderer.render(scene, this.camera);
                this.map.triggerRepaint();
            }
        };

        // add the custom style layer to the map
        props.map.current.on('style.load', function () {
            props.map.current.addLayer(customCarLayer);
        });
    });

    const animateCar = function () {
        var newCarData = {...carData2, LngLat: [9.106625, 48.744658]};
        updateCarData(newCarData);
    };

    return (
    <div className="map-wrap">
        <div ref={mapContainer}
            className="map"/>
        <button onClick={() => animateCar()}>animate</button>
        <button onClick={() => console.log(carDataList)}>print</button>
        <div>{`topic:${message ? message.topic : 'empty'} - message: ${message ? message.message : 'empty'}`}</div>
    </div>
    );
}
