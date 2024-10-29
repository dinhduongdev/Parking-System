import MotorcycleParking from '../../components/MotorcycleParking/MotorcycleParkingPage'; 
const HomePage = () => {
  return (
    <div>
      <main className="p-5">
        {/* <MotorcycleParking /> */}

        {/* Motorcycle Parking Section */}
        <MotorcycleParking apiEndpoint="http://127.0.0.1:5000/motorcycle_spots" title="Motorcycle Parking" />
        {/* Car Parking Section */}
        <MotorcycleParking apiEndpoint="http://127.0.0.1:5000/oto_spots" title="Oto Parking" />
      </main>
    </div>
  );
}

export default HomePage;