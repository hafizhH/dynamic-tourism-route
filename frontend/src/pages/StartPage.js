import { useEffect, useState } from "react";

const API_URL = 'http://localhost:5000';

const defaultParams = {
  startTime: '08:00',
  endTime: '20:00',
  lunchTime: '12:00',
  maxPlaces: 5,
  crossover: 'original',
  algorithm: 'simple',
}

const StartPage = ({ setCurrentPage, mainData, setMainData, setMainConfig, loading, setLoading }) => {

  const [startTime, setStartTime] = useState(defaultParams.startTime);
  const [endTime, setEndTime] = useState(defaultParams.endTime);
  const [lunchTime, setLunchTime] = useState(defaultParams.lunchTime);
  const [startLocation, setStartLocation] = useState(null);
  const [budget, setBudget] = useState(0);
  const [maxPlaces, setMaxPlaces] = useState(defaultParams.maxPlaces);
  const [mustVisit, setMustVisit] = useState([]);
  const [preferredCategories, setPreferredCategories] = useState([]);
  const [crossover, setCrossover] = useState(defaultParams.crossover);
  const [algorithm, setAlgorithm] = useState(defaultParams.algorithm);

  const [placesData, setPlacesData] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = () => {
    fetch(API_URL + '/api/places', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })
      .then(response => response.json())
      .then(data => {
        setPlacesData(data.data.places);
      })
      .catch(error => {
        console.error('Error fetching trip data:', error);
      });
  }

  const handleStart = () => {
    const preferences = {
      startTime,
      endTime,
      lunchTime,
      startLocation,
      maxPlaces,
      budget,
      preferredCategories,
      mustVisit,
      crossover,
      algorithm,
    }
    console.log('Starting trip with preferences:', preferences);
    setMainConfig(preferences);

    setLoading(true);

    fetch(API_URL + '/api/end-journey', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(async response => {
        const responseText = await response.text();
        const parsedJson = JSON.parse(responseText.replace(/\bNaN\b/g, "null"));
        return parsedJson;
      })
      .then(data => {
        optimize();
      })
      .catch(error => {
        console.error('Error during ending trip:', error);
        setLoading(false);
      })
  }

  const optimize = () => {
    fetch(API_URL + '/api/optimize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      // body: JSON.stringify({
      //   start_time: startTime,
      //   end_time: endTime,
      //   lunch_time: lunchTime,
      //   start_location: startLocation,
      //   max_places: maxPlaces,
      //   must_visit: mustVisit.filter(place => place !== ''),
      //   budget: budget,
      //   preferred_categories: preferredCategories.filter(cat => cat !== ''),
      //   crossover_method: crossover,
      //   algorithm: algorithm,
      // }),
      body: JSON.stringify(
      {
        "preferences": {
          "start_time": startTime,
          "end_time": endTime,
          "max_places": maxPlaces,
          "budget": budget,
          "must_visit": mustVisit.filter(place => place !== ''),
          "lunch_time": lunchTime,
          "start_location" : startLocation,
          "preferred_categories": preferredCategories.filter(cat => cat !== ''),
        },
        "crossover_method": crossover,
        "algorithm": algorithm
      }),
    })
      .then(async response => {
        const responseText = await response.text();
        const parsedJson = JSON.parse(responseText.replace(/\bNaN\b/g, "null"));
        return parsedJson;
      })
      .then(data => {
        console.log(startLocation)
        console.log('Optimization result:', data.data);
        setMainData(data.data);
        setCurrentPage(1);
      })
      .catch(error => {
        console.error('Error during optimization:', error);
      })
      .finally(() => {
        setLoading(false);
      });
  }


  const handleCategoryChange = (event) => {
    const { value, checked } = event.target;
    setPreferredCategories(prev => {
      if (checked) {
        return [...prev, value];
      } else {
        return prev.filter(cat => cat !== value);
      }
    });
  }

  const handleMustVisitChange = (event) => {
    const { value, checked } = event.target;
    setMustVisit(prev => {
      if (checked) {
        return [...prev, parseInt(value)];
      } else {
        return prev.filter(place => place !== parseInt(value));
      }
    });
  }

  return (
    <div className="px-4 py-8 min-h-screen flex flex-col justify-center items-center bg-gray-100">
      <div className="text-3xl font-bold leading-tight tracking-tight">Dynamic Tourism Attraction Routing App</div>
      <div className="mt-5 px-4 py-4 bg-white rounded-xl shadow-lg w-full flex flex-col">
        <div className="font-bold text-lg">Preferences</div>
        <div className="mt-3.5 w-full flex flex-row">
          <div className="flex-1 flex flex-col">
            <div className="text-sm font-medium">Trip Time</div>
            <div className="mt-1.5 flex flex-row">
              <input onChange={(e) => setStartTime(e.target.value)}
                type="time" defaultValue={defaultParams.startTime}
                className="px-1 py-2 text-sm border border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
                placeholder="Start time"
              />
              {/* <span className="mx-2 self-center text-sm text-gray-500">to</span>
              <input onChange={(e) => setEndTime(e.target.value)}
                type="time" defaultValue={defaultParams.endTime}
                className="px-1 py-2 text-sm border border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
                placeholder="End time"
              /> */}
            </div>
          </div>
          <div className="ml-auto w-fit flex flex-col">
            <div className="text-sm font-medium">Lunch Time</div>
            <div className="mt-1.5 w-fit flex flex-row">
              <input onChange={(e) => setLunchTime(e.target.value)}
                type="time"
                defaultValue={defaultParams.lunchTime}
                className="px-1 py-2 text-sm border border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
                placeholder="Lunch time"
              />
            </div>
          </div>
        </div>
        <div className="mt-3.5 w-full">
          <div className="text-sm font-medium">Start location</div>
          <select
            className="mt-1.5 w-full px-3 py-2.5 text-sm border border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            defaultValue=""
            onChange={(e) => setStartLocation(prev => {
              if (e.target.value === '') return null;
              const index = parseInt(e.target.value);
              return {
                name: placesData[index].name,
                latitude: placesData[index].latitude,
                longitude: placesData[index].longitude
              }
            })}
          >
            <option value="" disabled>Select starting location</option>
            { placesData &&
              placesData.map((place, index) => (
                <option key={place.name} value={index}>{place.name}</option>
              ))
            }
          </select>
        </div>
        <div className="mt-3.5 w-full">
          <div className="text-sm font-medium">Max. places to visit</div>
          <input onChange={(e) => setMaxPlaces(parseInt(e.target.value))}
            type="number"
            min="1"
            defaultValue={defaultParams.maxPlaces}
            placeholder="Max. places to visit"
            className="mt-1.5 w-full px-3 py-2.5 text-sm border border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>
        <div>
          <div className="text-sm font-medium mt-3.5">Must visit</div>
          <div className="mt-1.5 px-3 max-h-20 border border-gray-200 rounded-md overflow-auto flex flex-wrap gap-x-3 gap-y-1.5">
            {placesData && placesData.map((place, index) => (
              <label key={place.name} className="flex items-center gap-x-1.5">
                <input type="checkbox" value={index + 1} className="accent-blue-500" onChange={handleMustVisitChange} />
                <span className="text-xs">{place.name}</span>
              </label>
            ))}
          </div>
        </div>
        <div className="mt-3.5 w-full">
          <div className="text-sm font-medium">Budget</div>
          <input onChange={(e) => setBudget(parseInt(e.target.value))}
            type="number"
            placeholder="Budget"
            className="mt-1.5 w-full px-3 py-2.5 text-sm border border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>
        <div className="mt-3.5 w-full">
          <div className="text-sm font-medium mb-1">Preferred Categories</div>
          <div className="mt-1.5 flex flex-wrap gap-x-3 gap-y-1">
            <label className="flex items-center gap-x-1.5">
              <input type="checkbox" value="Alam" className="accent-blue-500" onChange={handleCategoryChange} />
              <span className="text-sm">Alam</span>
            </label>
            <label className="flex items-center gap-x-1.5">
              <input type="checkbox" value="Budaya" className="accent-blue-500" onChange={handleCategoryChange} />
              <span className="text-sm">Budaya</span>
            </label>
            <label className="flex items-center gap-x-1.5">
              <input type="checkbox" value="Rekreasi" className="accent-blue-500" onChange={handleCategoryChange} />
              <span className="text-sm">Rekreasi</span>
            </label>
            <label className="flex items-center gap-x-1.5">
              <input type="checkbox" value="Belanja" className="accent-blue-500" onChange={handleCategoryChange} />
              <span className="text-sm">Belanja</span>
            </label>
          </div>
          <div className="mt-4 flex flex-col">
            <div className="font-semibold tracking-tight">Routing Algorithm Options</div>
            <div className="mt-1 flex flex-col">
              <select
                className="mt-1.5 w-full px-3 py-2.5 text-sm border border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
                defaultValue={defaultParams.crossover}
                onChange={(e) => setCrossover(e.target.value)}
              >
                <option value="" disabled>Select crossover method</option>
                <option value={'original'}>One-point crossover</option>
                <option value={'order'}>Order crossover</option>
                <option value={'cycle'}>Cycle crossover</option>
              </select>
              <select
                className="mt-1.5 w-full px-3 py-2.5 text-sm border border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
                defaultValue={defaultParams.algorithm}
                onChange={(e) => setAlgorithm(e.target.value)}
              >
                <option value="" disabled>Select algorithm</option>
                <option value={'simple'}>Generational GA</option>
                <option value={'mu_plus_lambda'}>Steady-state GA (μ + λ)</option>
                <option value={'mu_comma_lambda'}>Evolutionary Strategy (μ, λ)</option>
              </select>
            </div>
          </div>
          <button onClick={() => handleStart()} disabled={loading} className="mt-6 px-5 py-2.5 w-full bg-blue-500 disabled:bg-blue-300 rounded-lg font-semibold text-md text-white">Start Trip</button>
        </div>
      </div>
    </div>
  );
}

export default StartPage;
