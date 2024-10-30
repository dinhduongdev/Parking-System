import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import defaultAvatar from '../../../public/defaultAvatar.png';

const AccountPage = () => {
  const [user, setUser] = useState(null);
  const [rechargeAmount, setRechargeAmount] = useState('');
  const [licensePlate, setLicensePlate] = useState('');
  const [modalPurpose, setModalPurpose] = useState('');
  const [qrCodes, setQrCodes] = useState([]);


  
  // let serviceFee = (currentHour >= 7 && currentHour < 17) ? 5000 : 10000;
  // let previousMoney = user.balance
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      const userData = JSON.parse(storedUser);
      fetch(`http://127.0.0.1:5000/user?id=${userData.user_id}`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          setUser(data); // Set the real user data
        })
        .catch(error => {
          console.error('Error fetching user:', error);
        });
      
    }
    
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('user');
    window.location.href = '/';
  };

  const openModal = (purpose) => {
    setModalPurpose(purpose);
  };

  const handleRechargeSubmit = async (e) => {
    e.preventDefault();
    if (parseFloat(rechargeAmount) <= 0) {
      alert("Please enter a valid amount.");
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:5000/account/vallet', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          username: user.username,
          amount: parseInt(rechargeAmount),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to recharge wallet");
      }

      

      const updatedUser = await response.json();
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
      setRechargeAmount('');
      setModalPurpose('');
    } catch (error) {
      alert(error.message);
    }
  };

  const handleUpdatePlateSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('http://127.0.0.1:5000/account/license_plate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: user.username,
          license_plate: licensePlate,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update license plate');
      }

      const updatedUser = await response.json();
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
      setLicensePlate('');
      setModalPurpose('');
    } catch (error) {
      alert(error.message);
    }
  };
  const dateInVietnam = new Intl.DateTimeFormat('en-US', {
    timeZone: 'Asia/Ho_Chi_Minh',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false // Set to true for 12-hour format
  }).format(new Date());

  // Function to fetch existing QR codes when the component mounts
  const fetchQrCodes = async () => {
    try {
        const response = await fetch(`http://127.0.0.1:5000/get_qr_codes?username=${encodeURIComponent(user.username)}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch QR codes. Status: ${response.status}`);
        }

        const result = await response.json();
        setQrCodes(result.qrCodes || []); // Assume response contains a qrCodes array
    } catch (error) {
        console.error(error);
        alert(error.message);
    }
  };

  // useEffect(() => {
  //     fetchQrCodes(); // Fetch QR codes when component mounts
  // }, []);

  const handleCreateQR = async (e) => {
      e.preventDefault();
      try {
          const response = await fetch(`http://127.0.0.1:5000/generate_qr?username=${encodeURIComponent(user.username)}&date=${encodeURIComponent(dateInVietnam)}`, {
              method: 'GET',
              headers: { 'Content-Type': 'application/json' },
          });
          
          if (!response.ok) {
              throw new Error(`Failed to generate QR code. Status: ${response.status}`);
          }
          
          const result = await response.json();
          console.log(result); // Check the information returned from the server

          // Deduct $10 from the wallet
          const rechargeResponse = await fetch('http://127.0.0.1:5000/account/vallet', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ username: user.username, amount: -10 }),
          });

          if (!rechargeResponse.ok) {
              throw new Error("Failed to deduct amount from wallet");
          }

          const updatedUser = await rechargeResponse.json();
          setUser(updatedUser);  // Update user data
          
          // Fetch the updated list of QR codes
          fetchQrCodes();

      } catch (error) {
          console.error(error); // Log error for monitoring
          alert(error.message);
      }
  };

  return (
    <div className="min-h-screen flex bg-gray-100">
      {/* Sidebar */}
      <aside className="w-1/5 bg-blue-800 text-white shadow-md p-4">
        <div className="flex flex-col items-center mb-6">
          <img
            src={user?.avatar || defaultAvatar}
            alt="User Avatar"
            className="w-24 h-24 rounded-full mb-2"
          />
          <h2 className="text-lg font-semibold">{user?.username || "Default name"}</h2>
          <p className="text-gray-300">Balance: ${user?.balance || '0.00'}</p>
        </div>

        <nav className="space-y-4">
          <Link to="/dashboard" className="flex items-center p-2 hover:bg-blue-100 rounded">Dashboard</Link>
          <Link to="/orders" className="flex items-center p-2 hover:bg-blue-100 rounded">Orders</Link>
          <Link to="/downloads" className="flex items-center p-2 hover:bg-blue-100 rounded">Downloads</Link>
          <Link to="/addresses" className="flex items-center p-2 hover:bg-blue-100 rounded">Addresses</Link>
          <Link to="/account-details" className="flex items-center p-2 hover:bg-blue-100 rounded">Account details</Link>
          <button onClick={handleLogout} className="flex items-center p-2 text-red-500 hover:bg-red-100 rounded w-full">Logout</button>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="w-3/4 p-6">
        <h1 className="text-2xl font-semibold mb-4">Hello, {user?.username}</h1>
        <p className="text-gray-600">
          From your account dashboard you can view your recent orders, manage your
          shipping and billing addresses, and edit your password and account details.
        </p>

        {/* Wallet Section */}
        <section className="mt-6 p-4 bg-white shadow rounded">
          <h2 className="text-xl font-semibold mb-2">Wallet</h2>
          <p className="text-gray-700">Current Balance: ${user?.balance || '0.00'}</p>
          <button
            onClick={() => openModal('wallet')}
            className="mt-4 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
          >
            Recharge Wallet
          </button>
        </section>

        {/* License Plate Section */}
        <section className="mt-6 p-4 bg-white shadow rounded">
          <h2 className="text-xl font-semibold mb-2">License Plate Number</h2>
          <p className="text-gray-700">Current Plate: {user?.license_plate || 'Not Set'}</p>
          <button
            onClick={() => openModal('plate')}
            className="mt-4 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
          >
            Update Plate
          </button>
        </section>
        <section className="mt-6 p-4 bg-white shadow rounded">
          <div>
              <form onSubmit={handleCreateQR}>
                  {/* Your form inputs here */}
                  <button 
                    type="submit"
                    className="mt-4 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
                    >Generate QR Code</button>
              </form>

              <h2>Previous QR Codes:</h2>
              <ul>
                  {qrCodes.map((qr, index) => (
                      <li key={index}>
                          {/* Render the QR code here; assuming qr contains a 'code' property */}
                          {/* <img src={qr.code} alt={`QR Code ${index + 1}`} /> */}
                          <p>Time: {qr.date}</p>
                          <img 
                            src={`data:image/png;base64,${qr.qr_image}`} alt={`QR Code ${index + 1}`}
                            style={{ width: '150px', height: '150px' }} 
                            
                            />

                      </li>
                  ))}
              </ul>
          </div>
        </section>


        {/* Modal */}
        {modalPurpose && (
          <div className="fixed inset-0 flex items-center justify-center bg-gray-600 bg-opacity-50">
            <div className="bg-white p-6 rounded shadow-lg">
              {modalPurpose === 'wallet' ? (
                <>
                  <h3 className="text-lg font-semibold mb-4">Recharge Wallet</h3>
                  <form onSubmit={handleRechargeSubmit}>
                    <input
                      type="number"
                      value={rechargeAmount}
                      onChange={(e) => setRechargeAmount(e.target.value)}
                      className="border border-gray-300 p-2 rounded w-full mb-4"
                      placeholder="Enter amount"
                      required
                    />
                    <div className="flex justify-end">
                      <button
                        type="button"
                        onClick={() => setModalPurpose('')}
                        className="mr-2 text-gray-600 hover:text-gray-800"
                      >
                        Cancel
                      </button>
                      <button type="submit" className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700">
                        Recharge
                      </button>
                    </div>
                  </form>
                </>
              ) : (
                <>
                  <h3 className="text-lg font-semibold mb-4">Update License Plate</h3>
                  <form onSubmit={handleUpdatePlateSubmit}>
                    <input
                      type="text"
                      value={licensePlate}
                      onChange={(e) => setLicensePlate(e.target.value)}
                      placeholder="Enter plate number"
                      className="border border-gray-300 p-2 rounded w-full mb-4"
                      required
                    />
                    <div className="flex justify-end">
                      <button
                        type="button"
                        onClick={() => setModalPurpose('')}
                        className="mr-2 text-gray-600 hover:text-gray-800"
                      >
                        Cancel
                      </button>
                      <button type="submit" className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700">
                        Update Plate
                      </button>
                    </div>
                  </form>
                </>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AccountPage;
