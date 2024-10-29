import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import defaultAvatar from '../../../public/defaultAvatar.png';

const AccountPage = () => {
  const [user, setUser] = useState(null);
  const [rechargeAmount, setRechargeAmount] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  // const handleEditProfile = () => {
  //   alert("Edit Profile clicked!");
  // };

  // const handleChangePassword = () => {
  //   alert("Change Password clicked!");
  // };

  const handleLogout = () => {
    localStorage.removeItem('user');
    window.location.href = '/';
  };

  const handleRechargeWallet = () => {
    setIsModalOpen(true); // Open modal for recharge
  };

  const handleRechargeSubmit = async (e) => {
    e.preventDefault();
  
    if (parseFloat(rechargeAmount) <= 0) {
      alert("Please enter a valid amount.");
      return;
    }
  
    // Log the username and amount before sending
    console.log("Username:", user.username); // Check the username
    console.log("Recharge Amount:", parseFloat(rechargeAmount)); // Check the amount
  
    try {
      const response = await fetch('http://127.0.0.1:5000/account', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          username: user.username, // Now sending the username
          amount: parseInt(rechargeAmount) 
        }),
      });
  
      if (!response.ok) {
        throw new Error("Failed to recharge wallet");
      }
  
      const updatedUser = await response.json();
      setUser(updatedUser); // Update user state with new balance
      localStorage.setItem('user', JSON.stringify(updatedUser)); // Update local storage
      setRechargeAmount(''); // Reset recharge amount
      setIsModalOpen(false); // Close modal
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
          <p className="text-gray-300">Balance: ${user?.balance || '0.00'}</p> {/* Display account balance */}
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
            onClick={handleRechargeWallet}
            className="mt-4 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
          >
            Recharge Wallet
          </button>
        </section>

        {/* Recharge Modal */}
        {isModalOpen && (
          <div className="fixed inset-0 flex items-center justify-center bg-gray-600 bg-opacity-50">
            <div className="bg-white p-6 rounded shadow-lg">
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
                    onClick={() => setIsModalOpen(false)}
                    className="mr-2 text-gray-600 hover:text-gray-800"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700">
                    Recharge
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AccountPage;
