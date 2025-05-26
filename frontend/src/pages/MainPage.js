import { useEffect, useState } from "react";
import Map from "../components/Map";

const API_URL = 'http://localhost:5000';

const MainPage = ({ setCurrentPage }) => {
  const [placesData, setPlacesData] = useState(null);
  const [mapData, setMapData] = useState(null);
  const [scheduleData, setScheduleData] = useState(null);
  const [routeData, setRouteData] = useState(null);

  const [userLocation, setUserLocation] = useState([0, 0]);

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getUserLocation();
    fetchTripData();
  }, []);

  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation([position.coords.latitude, position.coords.longitude]);
        },
        (error) => {
          console.error('Error getting user location:', error);
        }
      );
    } else {
      console.error('Geolocation is not supported by this browser.');
    }
  }

  const fetchTripData = () => {
    fetch(API_URL + '/api/places', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })
      .then(async response => {
        const responseText = await response.text();
        const parsedJson = JSON.parse(responseText.replace(/\bNaN\b/g, "null"));
        return parsedJson;
      })
      .then(data => {
        setPlacesData(data.data.places);
      })
      .catch(error => {
        console.error('Error fetching trip data:', error);
      });

    fetch(API_URL + '/api/route', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })
      .then(async response => {
        const responseText = await response.text();
        const parsedJson = JSON.parse(responseText.replace(/\bNaN\b/g, "null"));
        return parsedJson;
      })
      .then(data => {
        setRouteData(data.data);
      })
      .catch(error => {
        console.error('Error fetching trip data:', error);
      });

    fetch(API_URL + '/api/schedule', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })
      .then(async response => {
        const responseText = await response.text();
        const parsedJson = JSON.parse(responseText.replace(/\bNaN\b/g, "null"));
        return parsedJson;
      })
      .then(data => {
        setScheduleData(data.data.schedule);
      })
      .catch(error => {
        console.error('Error fetching trip data:', error);
      });
  }

  const handleNextPlace = () => {
    setLoading(true);

    fetch(API_URL + '/api/next-and-reoptimize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        // start_time: startTime,
        // end_time: endTime,
        // start_location: startLocation,
        // max_places: maxPlaces,
        // budget: budget,
        // preferred_categories: preferredCategories.filter(cat => cat !== ''),
        // must_visit: mustVisit.filter(place => place !== ''),
      }),
    })
      .then(async response => {
        const responseText = await response.text();
        const parsedJson = JSON.parse(responseText.replace(/\bNaN\b/g, "null"));
        return parsedJson;
      })
      .then(data => {
        console.log('Re-optimization result:', data.data);
        fetchTripData();
      })
      .catch(error => {
        console.error('Error during reoptimization:', error);
        setLoading(false);
      })
  }

  const handleEndTrip = () => {
    fetch(API_URL + '/api/end-journey', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      // body: JSON.stringify({
      //   // start_time: startTime,
      //   // end_time: endTime,
      //   // start_location: startLocation,
      //   // max_places: maxPlaces,
      //   // budget: budget,
      //   // preferred_categories: preferredCategories.filter(cat => cat !== ''),
      //   // must_visit: mustVisit.filter(place => place !== ''),
      // }),
    })
      .then(async response => {
        const responseText = await response.text();
        const parsedJson = JSON.parse(responseText.replace(/\bNaN\b/g, "null"));
        return parsedJson;
      })
      .then(data => {
        setCurrentPage(0);
      })
      .catch(error => {
        console.error('Error during ending trip:', error);
        setLoading(false);
      })
  }

  return (
    <div className="px-3 pt-4 pb-8 flex flex-col min-h-screen bg-gray-100">
      {/* <div className="text-2xl font-bold text-center tracking-tight leading-tight">Dynamic Tourism Attraction Route</div> */}
      <button onClick={() => setCurrentPage(0)} className="w-fit px-3 py-2 font-semibold text-md tracking-tight">{'< '}Back</button>
      <div className="mt-3 w-full aspect-square bg-white border border-gray-200 shadow-xl shadow-gray-300 rounded-lg overflow-hidden flex justify-center items-center">
        <Map places={placesData} center={userLocation} currentLocation={userLocation} />
      </div>
      <div className="mt-6 px-4 py-4 w-full bg-white shadow-lg rounded-lg">
        <div className="text-md font-bold tracking-tight">Trip Status</div>
        <div className="mt-4 text-sm text-gray-600 space-y-3">
          <div className="flex flex-row items-center space-x-3">
            <div className="w-1/2 flex flex-col">
              <div className="text-xs">Current location</div>
              <div className="font-semibold text-xs">Malioboro</div>
            </div>
            <div className="w-1/4 flex flex-col">
              <div className="text-xs">Weather</div>
              <div className="font-semibold text-xs">Sunny</div>
            </div>
            <div className="w-1/4 flex flex-col">
              <div className="text-xs">Scheduled</div>
              <div className="font-semibold text-xs">10:00 AM</div>
            </div>
          </div>
          <div className="flex flex-row items-center space-x-3">
            <div className="w-1/2 flex flex-col">
              <div className="text-xs">Next destination</div>
              <div className="font-semibold text-xs">Candi Borobudur</div>
            </div>
            <div className="w-1/4 flex flex-col">
              <div className="text-xs">Weather</div>
              <div className="font-semibold text-xs">Sunny</div>
            </div>
            <div className="w-1/4 flex flex-col">
              <div className="text-xs">Scheduled</div>
              <div className="font-semibold text-xs">10:00 AM</div>
            </div>
          </div>
        </div>
        <div className="mt-5 flex flex-row justify-between items-center space-x-3">
          <button onClick={() => handleEndTrip()} className="px-6 py-2 w-1/2 rounded-md bg-white border border-red-500 flex justify-center items-center text-red-500 text-sm">End Trip</button>
          <button onClick={() => handleNextPlace()} className="px-6 py-2 w-1/2 rounded-md bg-blue-500 border border-blue-500 flex justify-center items-center text-white text-sm">Next Destination</button>
        </div>
      </div>
      <div className="mt-6 px-4 py-4 w-full bg-white shadow-lg rounded-lg">
        <div className="font-bold text-md tracking-tight">Full Trip Schedule</div>
        <table className="mt-3 w-full">
          <thead className="!text-xs font-medium">
            <tr>
              <th className="px-0 py-2">No</th>
              <th className="px-2 py-2">Activity</th>
              <th className="px-2 py-2">Location</th>
              <th className="px-2 py-2">Time</th>
            </tr>
          </thead>
          <tbody className="text-xs">
            {scheduleData && scheduleData.map((activity, index) => (
              <tr key={index}>
                <td className="px-0 py-2">{index + 1}</td>
                <td className="px-2 py-2">{activity.activity}</td>
                <td className="px-2 py-2">{activity.location}</td>
                <td className="px-2 py-2">{activity.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default MainPage;
