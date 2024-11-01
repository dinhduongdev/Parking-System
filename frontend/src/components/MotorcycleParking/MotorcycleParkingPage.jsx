import { useEffect, useState } from 'react';

// eslint-disable-next-line react/prop-types
const MotorcycleParking = ({ apiEndpoint , title}) => {
  const [spots, setSpots] = useState([]);

  useEffect(() => {
    const fetchSpots = async () => {
      const response = await fetch(apiEndpoint);
      const data = await response.json();
      setSpots(data);
    };

    fetchSpots();
  }, [apiEndpoint]); // Add apiEndpoint to the dependency array

  // Calculate the number of available spots
  const availableSpotsCount = spots.filter(spot => spot.status === 'Available').length;

  return (
    <div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="mb-4">Available Spots: <strong>{availableSpotsCount}</strong></p>
      <div className="grid grid-cols-4 gap-6">
        {spots.map((spot) => (
          <div key={spot.id} className={`p-4 rounded shadow ${spot.status === 'Available' ? 'bg-blue-200' : 'bg-yellow-200'}`}>
            <h4 className="text-lg font-semibold">{spot.name}</h4>
            <p>{spot.status}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MotorcycleParking;
