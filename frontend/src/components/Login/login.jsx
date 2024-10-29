// Login.js
import { Link } from 'react-router-dom';

const Login = () => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h2 className="text-2xl font-bold mb-6 text-center">Login</h2>
        <form>
          <div className="mb-4">
            <label htmlFor="email" className="block text-sm font-semibold mb-1">Email</label>
            <input
              type="email"
              id="email"
              placeholder="Enter your email"
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div className="mb-6">
            <label htmlFor="password" className="block text-sm font-semibold mb-1">Password</label>
            <input
              type="password"
              id="password"
              placeholder="Enter your password"
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600 transition duration-200"
          >
            Login
          </button>
        </form>
        <p className="mt-4 text-sm text-center">
          Do not have an account? 
          <Link to="/register" className="text-blue-500 hover:underline"> Register</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
