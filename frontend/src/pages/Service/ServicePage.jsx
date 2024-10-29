// Services.js
const Services = () => {
    const services = [
      { type: 'Car Parking (Oto)', price: '20,000 VND/hour' },
      { type: 'Motorcycle Parking (Motobike)', price: '5,000 VND/hour' },
      { type: 'Car Parking Monthly Pass', price: '1,500,000 VND/month' },
      { type: 'Motorcycle Parking Monthly Pass', price: '200,000 VND/month' },
      { type: 'VIP Car Parking', price: '40,000 VND/hour' },
      { type: 'VIP Motorcycle Parking', price: '10,000 VND/hour' },
    ];
  
    return (
      <div className="p-6 bg-gray-100 min-h-screen">
        <h2 className="text-2xl font-bold mb-6 text-center">Parking Services and Prices</h2>
        <div className="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow-md">
          <table className="min-w-full">
            <thead>
              <tr className="bg-gray-200">
                <th className="py-2 text-left text-gray-700">Service Type</th>
                <th className="py-2 text-left text-gray-700">Price</th>
              </tr>
            </thead>
            <tbody>
              {services.map((service, index) => (
                <tr key={index} className={`hover:bg-gray-100 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}`}>
                  <td className="py-2 px-4">{service.type}</td>
                  <td className="py-2 px-4">{service.price}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };
  
  export default Services;
  