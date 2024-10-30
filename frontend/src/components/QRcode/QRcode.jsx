// QRCodeComponent.js
import { useState } from 'react';

const QRCodeComponent = () => {
  const [qrData, setQrData] = useState('');
  const [qrList, setQrList] = useState([]);

  const handleGenerateQRCode = async () => {
    if (!qrData) {
      alert('Please enter data for the QR code.');
      return;
    }

    try {
      const date = new Date().toISOString();
      const response = await fetch(`http://127.0.0.1:5000/generate_qr?username=${encodeURIComponent(qrData)}&date=${encodeURIComponent(date)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      setQrList((prevList) => [...prevList, data]); // Add the new QR code data to the list
      setQrData(''); // Clear the input after generating the QR code
    } catch (error) {
      alert(error.message);
    }
  };

  return (
    <div className="mt-6 p-4 bg-white shadow rounded">
      <h2 className="text-xl font-semibold mb-2">Generate QR Code</h2>
      <input
        type="text"
        value={qrData}
        onChange={(e) => setQrData(e.target.value)}
        placeholder="Enter data for QR Code"
        className="border border-gray-300 p-2 rounded w-full mb-4"
      />
      <button
        onClick={handleGenerateQRCode}
        className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
      >
        Generate QR Code
      </button>

      {/* Displaying the QR Code List */}
      <div className="mt-4">
        <h3 className="text-lg font-semibold">Generated QR Codes:</h3>
        <ul>
          {qrList.map((qr, index) => (
            <li key={index} className="mt-2">
              <img src={`http://127.0.0.1:5000/qr_image/${qr.qr_id}`} alt={`QR Code for ${qr.username}`} />
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default QRCodeComponent;
