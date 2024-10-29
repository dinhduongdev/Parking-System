import { Link, useNavigate } from 'react-router-dom';
import logo from '../../../public/logoOU.webp';
import defaultAvatar from '../../../public/defaultAvatar.png';
import { useState, useEffect } from 'react';


const Navbar = () => {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('user'); // Clear user data from localStorage
    setUser(null);                   // Reset user state to null
    navigate('/');                   // Redirect to home page or login page
  };

  return (
    <div>
      <nav className="flex items-center justify-between p-4 bg-white shadow-md">
        <div className="navbar-logo flex items-center">
          <Link to="/">
            <img src={logo} alt="MyLogo" className="w-12 h-auto mr-2" />
          </Link>
          <h1 className="text-xl font-semibold text-gray-800">Parking System</h1>
        </div>
        <ul className="flex space-x-6">
          <li><Link to="/" className="text-gray-700 hover:text-blue-500">Home</Link></li>
          <li><Link to="/about" className="text-gray-700 hover:text-blue-500">About</Link></li>
          <li><Link to="/services" className="text-gray-700 hover:text-blue-500">Services</Link></li>
          <li><Link to="/contact" className="text-gray-700 hover:text-blue-500">Contact</Link></li>
        </ul>
        
        <div className="flex space-x-4">
          {user ? (
            <div className="relative inline-block group">
              <div className="flex items-center cursor-pointer">
                <img
                  src={user.avatar || defaultAvatar}
                  alt="User Avatar"
                  className="w-8 h-8 rounded-full mr-2"
                />
                <span className="text-gray-800">{user.username}</span>
              </div>
              {/* Dropdown menu */}
              <div className="absolute right-0 w-48 bg-white rounded-md shadow-lg hidden group-hover:block">
                <ul className="py-1 text-gray-700">
                  <li>
                    <Link to="/account" className="block px-4 py-2 hover:bg-gray-100">

                      My Account
                    </Link>
                  </li>
                  <li>
                    <button
                      onClick={handleLogout}
                      className="w-full text-left block px-4 py-2 hover:bg-gray-100 text-red-500"
                    >

                      Log Out
                    </button>
                  </li>
                </ul>
              </div>
            </div>            
          ) : (
            <>
              <Link to="/login" className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">Login</Link>
              <Link to="/register" className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">Register</Link>
            </>
          )}
        </div>
      </nav>

      {/* Parking Lot Interface */}
      
    </div>
  );
};

export default Navbar;
