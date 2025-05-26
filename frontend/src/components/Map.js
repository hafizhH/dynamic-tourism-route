import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { use, useEffect, useState } from "react";
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

const Map = ({ places, visitedPlaceIds, remainingPlaceIds, currentUserLocation }) => {
  const [key, setKey] = useState(0);
  const [center, setCenter] = useState(currentUserLocation ?? [0, 0]);

  useEffect(() => {
    setKey(prevKey => prevKey + 1);
  }, [places, visitedPlaceIds, remainingPlaceIds, center]);

  useEffect(() => {
    if (visitedPlaceIds.length > 0) {
      const lastVisitedPlace = places[visitedPlaceIds[visitedPlaceIds.length - 1] - 1];
      setCenter([lastVisitedPlace.latitude, lastVisitedPlace.longitude]);
    } else if (places.length > 0) {
      const firstPlace = places[0];
      setCenter([firstPlace.latitude, firstPlace.longitude]);
    } else if (currentUserLocation) {
      setCenter(currentUserLocation);
    }
  }, [visitedPlaceIds, places, currentUserLocation]);

  return (
    <MapContainer center={center} zoom={4} key={key} className="w-full h-full">
      <MapController center={center} />
      <TileLayer
        attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {/* {currentUserLocation &&
        <Marker key={`current`} position={currentUserLocation}
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
      } */}
      { visitedPlaceIds &&
        visitedPlaceIds.map((id, idx) => {
          const place = places[id - 1];

          if (idx === visitedPlaceIds.length - 1) {
            return (
              <Marker key={place.id} position={[place.latitude, place.longitude]}
                icon={L.icon({
                  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png",
                  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
                  iconSize: [25, 41],
                  iconAnchor: [12, 41],
                  popupAnchor: [1, -34],
                  shadowSize: [41, 41],
                })}
              >
                <Popup>
                  <div className="flex flex-col space-y-1">
                    <span>Destinasi {idx + 1}</span>
                    <span className="font-bold">{place.name}</span>
                  </div>
                </Popup>
              </Marker>
            )
          } else {
            return (
              <Marker key={place.id} position={[place.latitude, place.longitude]}
                icon={L.icon({
                  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-grey.png",
                  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
                  iconSize: [25, 41],
                  iconAnchor: [12, 41],
                  popupAnchor: [1, -34],
                  shadowSize: [41, 41],
                })}
              >
                <Popup>
                  <div className="flex flex-col space-y-1">
                    <span>Destinasi {idx + 1}</span>
                    <span className="font-bold">{place.name}</span>
                  </div>
                </Popup>
              </Marker>
            )
          }
        })
      }
      { remainingPlaceIds &&
        remainingPlaceIds.map((id, idx) => {
          const place = places[id - 1];

          return (
            <Marker key={place.id} position={[place.latitude, place.longitude]}
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
                <div className="flex flex-col">
                  <span>Destinasi {idx + visitedPlaceIds.length + 1}</span>
                  <span className="mt-1 font-bold">{place.name}</span>
                  <span className="mt-1 font-medium text-xs italic">Scheduled</span>
                </div>
              </Popup>
            </Marker>
          )
        })
      }
      <Polyline color="#88a"
        positions={visitedPlaceIds.reduce((acc, id, idx, arr) => {
          const place = places[id - 1];
          acc.push([place.latitude, place.longitude]);
          return acc;
        }, [])}
      />
      <Polyline color="#155dfc"
        positions={[visitedPlaceIds[visitedPlaceIds.length - 1], remainingPlaceIds[0] ?? null].reduce((acc, id, idx, arr) => {
          if (id) {
            const place = places[id - 1];
            acc.push([place.latitude, place.longitude]);
          }
          return acc;
        }, [])}
      />
      <Polyline color="#51a2ff"
        positions={remainingPlaceIds.reduce((acc, id, idx, arr) => {
          if (id) {
            const place = places[id - 1];
            acc.push([place.latitude, place.longitude]);
          }
          return acc;
        }, [])}
      />
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