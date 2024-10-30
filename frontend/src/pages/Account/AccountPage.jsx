import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import defaultAvatar from '../../../public/defaultAvatar.png';

const AccountPage = () => {
  const [user, setUser] = useState(null);
  const [rechargeAmount, setRechargeAmount] = useState('');
  const [licensePlate, setLicensePlate] = useState('');
  const [modalPurpose, setModalPurpose] = useState('');

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
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
