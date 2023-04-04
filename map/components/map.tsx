import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import React from "react";

const Map = () => {

  // access token
  const key: any = 'pk.eyJ1Ijoic2hlbGJ5LWdyZWVuIiwiYSI6ImNrMHNobWdrNTAwZW8zYnA5czQ5cWh4ankifQ.TWYVyG-n0cmhTGvKg31eow';

  // // this ref holds the map DOM node so that we can pass it into Mapbox GL
  // const mapContainer = useRef(HTMLElement)

  // // this ref holds the map object once we have instantiated it, so that it
  // // can be used in other hooks
  // const mapRef = useRef(null)

  // this is where the map instance will be stored after initialization
  const [map, setMap] = React.useState<mapboxgl.Map>();

  const mapNode = React.useRef(null);

  React.useEffect(() => {
    const node = mapNode.current;

    if (typeof window === "undefined" || node === null) return;

    mapboxgl.accessToken = key;
    // map's basic settings
    const map = new mapboxgl.Map({
      container: node,
      style: "mapbox://styles/mapbox/dark-v10",
      center: [-84.2830590599657, 30.43936603257657],
      interactive: true,
      zoom: 9,
      minZoom: 0
    });

    // Add zoom and rotation controls to the map.
    map.addControl(new mapboxgl.NavigationControl());

    // Add geolocate control to the map.
    map.addControl(
      new mapboxgl.GeolocateControl({
      positionOptions: {
      enableHighAccuracy: true
      },
      // When active the map will receive updates to the device's location as it changes.
      trackUserLocation: true,
      // Draw an arrow next to the location dot to indicate which direction the device is heading.
      showUserHeading: true
      })
      );

    // load layer
    map.on("load", function () {
      // import layer
      map.addSource("districts", {
        type: "geojson",
        data:
          "https://raw.githubusercontent.com/shelbygreen/florida-legislature/main/data/geospatial/clipped/senate/FL-senate.geojson",
        generateId: true,
      });

      // add styling
      map.addLayer({
        id: "districts-fill",
        type: "fill",
        source: "districts",
        layout: {},
        paint: {
            'fill-color': '#D8B365'
        },
      });
      map.addLayer({
        id: "districts-outline",
        type: "line",
        source: "districts",
        layout: {},
        paint: {
            'line-color': '#000000'
        },
      });
    });

    // after the map loads
    map.on('click', function(mapElement) {
      const features = map.queryRenderedFeatures(mapElement.point, {
        layers: ['districts-fill']
      })

      if (typeof window === "undefined" || node === null) return;

      const name = features[0]?.properties?.name // optional chaining to avoid "object is null" error
    //   const amount = features[0]?.properties?.amount

      const html = `${name}`

      // create tooltip variable for the floating card div
      const tooltip = document.getElementById('popup')
            
      // store html in the tooltip, which will be displayed in the floating card div
      tooltip!.innerHTML = html

    });

  }, []);

  return (
    <div>
      <div id="popup">Select a district to display details.</div>
      <div ref={mapNode} style={{ height: "100vh" }} />
    </div>
  );
};

export default Map;