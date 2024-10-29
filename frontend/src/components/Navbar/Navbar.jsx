import { Link } from 'react-router-dom';
import logo from '../../../public/logoOU.webp';

const Navbar = () => {
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
          <Link to="/login" className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">Login</Link>
          <Link to="/register" className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">Register</Link>
        </div>
      </nav>

      {/* Parking Lot Interface */}
      
    </div>
  );
};

export default Navbar;
