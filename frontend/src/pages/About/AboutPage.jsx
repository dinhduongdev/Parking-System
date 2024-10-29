import { useState, useEffect } from 'react';


const AccountPage = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Fetch user details from local storage or an API
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const handleEditProfile = () => {
    // Logic for editing profile
    alert("Edit Profile clicked!");
  };

  const handleChangePassword = () => {
    // Logic for changing password
    alert("Change Password clicked!");
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    window.location.href = '/';
  };

  return (
    <div className="min-h-screen flex flex-col items-center p-6 bg-gray-100">
      <div className="bg-white shadow-md rounded-lg p-6 w-full max-w-md">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Account Details</h2>
        
        {user ? (
          <div>
            <img src={user.avatar} alt="User Avatar" className="w-24 h-24 rounded-full mx-auto mb-4" />
            <p className="text-center text-gray-800 text-xl font-semibold">{user.username}</p>
            <p className="text-center text-gray-500 mb-6">{user.email}</p>

            <div className="space-y-4">
              <button
                onClick={handleEditProfile}
                className="w-full flex items-center justify-center bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
              >
                Edit Profile
              </button>

              <button
                onClick={handleChangePassword}
                className="w-full flex items-center justify-center bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600"
              >

                Change Password
              </button>

              <button
                onClick={handleLogout}
                className="w-full flex items-center justify-center bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600"
              >

                Log Out
              </button>
            </div>
          </div>
        ) : (
          <p className="text-center text-gray-500">Loading...</p>
        )}
      </div>
    </div>
  );
};

export default AccountPage;
