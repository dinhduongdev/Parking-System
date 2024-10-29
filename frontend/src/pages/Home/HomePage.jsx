
const HomePage = () => {
  return (
    <div>
      <main className="p-5">
        {/* Car Parking Section */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold mb-2">Car Parking (Oto)</h3>
          <div className="grid grid-cols-4 gap-6">
            {[...Array(12)].map((_, i) => (
              <div key={i} className={`p-4 rounded shadow ${i % 2 === 0 ? 'bg-green-200' : 'bg-red-200'}`}>
                <h4 className="text-lg font-semibold">Car Spot {i + 1}</h4>
                <p>{i % 2 === 0 ? 'Available' : 'Occupied'}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Motorcycle Parking Section */}
        <div>
          <h3 className="text-xl font-semibold mb-2">Motorcycle Parking (Motobike)</h3>
          <div className="grid grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <div key={i} className={`p-4 rounded shadow ${i % 2 === 0 ? 'bg-blue-200' : 'bg-yellow-200'}`}>
                <h4 className="text-lg font-semibold">Motorcycle Spot {i + 1}</h4>
                <p>{i % 2 === 0 ? 'Available' : 'Occupied'}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default HomePage;