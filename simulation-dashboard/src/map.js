import React, {useRef, useEffect, useState} from 'react';
import maplibregl from 'maplibre-gl';
import './map.css';
import 'maplibre-gl/dist/maplibre-gl.css';
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader'

function loadGLTFModel(scene, glbPath, position, options) {
    const { receiveShadow, castShadow } = options;
    const [ lat, lng ] = position;

    // var modelAsMercatorCoordinate = maplibregl.MercatorCoordinate.fromLngLat(
    //     position,
    //     0
    // );

    return new Promise((resolve, reject) => {
        const dracoLoader = new DRACOLoader();
        dracoLoader.setDecoderPath('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/js/libs/draco/');
        const loader = new GLTFLoader();
        loader.setDRACOLoader(dracoLoader);
        loader.load(
            glbPath,
            (gltf) => {
                const obj = gltf.scene;
                obj.position.y = 0;
                obj.position.x = lat;
                obj.position.z = lng;
                obj.receiveShadow = receiveShadow;
                obj.castShadow = castShadow;
                scene.add(obj);

                obj.traverse(function(child) {
                    if(child.isMesh) {
                        child.castShadow = castShadow;
                        child.receiveShadow = receiveShadow;
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
    const [lat] = useState(48.744715);
    const [lng] = useState(9.1066383);
    const [zoom] = useState(21);
    const [API_KEY] = useState('cqvAKHMBJexanBFc1owH ');

    useEffect(() => {
        // stops map from intializing more than once
        if (props.map.current) 
            return;
        
        props.map.current = new maplibregl.Map({
            container: mapContainer.current,
            style: `https://api.maptiler.com/maps/streets/style.json?key=${API_KEY}`,
            center: [lng, lat],
            zoom: zoom,
            pitch: 60,
            antialias: true
        });

        // parameters to ensure the model is georeferenced correctly on the map
        var modelOrigin = [9.106596, 48.744459];
        // var modelAltitude = 456;
        var modelAltitude = 0;
        var modelRotate = [Math.PI / 2, 5.5 * Math.PI / 8, 0];

        var modelAsMercatorCoordinate = maplibregl.MercatorCoordinate.fromLngLat(
            modelOrigin,
            modelAltitude
        );
        
        // transformation parameters to position, rotate and scale the 3D model onto the map
        var modelTransform = {
            translateX: modelAsMercatorCoordinate.x,
            translateY: modelAsMercatorCoordinate.y,
            translateZ: modelAsMercatorCoordinate.z,
            rotateX: modelRotate[0],
            rotateY: modelRotate[1],
            rotateZ: modelRotate[2],
            /* Since our 3D model is in real world meters, a scale transform needs to be
            * applied since the CustomLayerInterface expects units in MercatorCoordinates.
            */
            scale: modelAsMercatorCoordinate.meterInMercatorCoordinateUnits()
        };

        // create a custom style layer to implement the WebGL content
        var customCarLayer = {
            id: 'threedee',
            type: 'custom',
            renderingMode: '3d',

            // method called when the layer is added to the map
            // https://maplibre.org/maplibre-gl-js-docs/api/properties/#styleimageinterface#onadd
            onAdd: function (map, gl) {
                this.camera = new THREE.Camera();
                this.scene = new THREE.Scene();

                // create two three.js lights to illuminate the model
                var directionalLight = new THREE.DirectionalLight(0xffffff);
                directionalLight.position.set(0, -70, 100).normalize();
                this.scene.add(directionalLight);

                var directionalLight2 = new THREE.DirectionalLight(0xffffff);
                directionalLight2.position.set(0, 70, 100).normalize();
                this.scene.add(directionalLight2);

                // use the GLTF loader to add the 3D model to the three.js scene
                loadGLTFModel(this.scene, "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/ferrari.glb", [0,0], {
                    receiveShadow: false,
                    castShadow: false
                }).then(() => {
                    console.log("model loaded");
                });

                // var secondModelOrigin = [48.744746, 9.106607];
                // // use the GLTF loader to add the 3D model to the three.js scene
                // loadGLTFModel(this.scene, "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/ferrari.glb", secondModelOrigin, {
                //     receiveShadow: false,
                //     castShadow: false
                // }).then(() => {
                //     console.log("model 2 loaded");
                // });

                this.map = map;

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
                var rotationX = new THREE.Matrix4().makeRotationAxis(
                    new THREE.Vector3(1, 0, 0),
                    modelTransform.rotateX
                );
                var rotationY = new THREE.Matrix4().makeRotationAxis(
                    new THREE.Vector3(0, 1, 0),
                    modelTransform.rotateY
                );
                var rotationZ = new THREE.Matrix4().makeRotationAxis(
                    new THREE.Vector3(0, 0, 1),
                    modelTransform.rotateZ
                );

                var m = new THREE.Matrix4().fromArray(matrix);
                var l = new THREE.Matrix4()
                    .makeTranslation(
                        modelTransform.translateX,
                        modelTransform.translateY,
                        modelTransform.translateZ
                    )
                    .scale(
                        new THREE.Vector3(
                            modelTransform.scale,
                            -modelTransform.scale,
                            modelTransform.scale
                        )
                    )
                    .multiply(rotationX)
                    .multiply(rotationY)
                    .multiply(rotationZ);

                this.camera.projectionMatrix = m.multiply(l);
                this.renderer.state.reset();
                this.renderer.render(this.scene, this.camera);
                this.map.triggerRepaint();
            }
        };

        // add the custom style layer to the map
        props.map.current.on('style.load', function () {
            props.map.current.addLayer(customCarLayer);
        });
    });

    const animateCar = function () {
        console.log("ehrm");
    };

    return (
    <div className="map-wrap">
        <div ref={mapContainer}
            className="map"/>
        <button onClick={() => animateCar()}>animate</button>
    </div>
    );
}
