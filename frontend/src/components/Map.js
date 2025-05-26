import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap, Polyline } from "react-leaflet";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

const Map = ({ places, center, currentLocation }) => {

  return (
    <MapContainer center={center ?? [0, 0]} zoom={4} key={center ? `${center[0]}-${center[1]}` : 'default'} className="w-full h-full">
      <MapController center={center} />
      <TileLayer
        attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {currentLocation &&
        <Marker
          key={`current`}
          position={currentLocation}
          icon={L.icon({
            iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png",
            shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41],
          })}
        >
          <Popup>
            <div className="flex flex-col space-y-1">
              <span className="font-bold">Lokasi Anda</span>
            </div>
          </Popup>
        </Marker>
      }
      { places &&
        places.map((place, idx) => (
          <Marker key={idx} position={[place.latitude, place.longitude]}>
            <Popup>
              <div className="flex flex-col space-y-1">
                <span>Destinasi {idx + 1}</span>
                <span className="font-bold">{place.name}</span>
              </div>
            </Popup>
          </Marker>
        ))
      }
      {/* <Polyline positions={coordinates} color="blue" /> */}
    </MapContainer>
  );
}

const MapController = ({ center }) => {
  const map = useMap();

  useEffect(() => {
    if (center) {
      map.flyTo(center, 8, {
        duration1: 1,
      });
    }
  }, [center, map]);

  return null;
}

export default Map;