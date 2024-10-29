// Footer.js
const Footer = () => {
    return (
      <footer className="bg-gray-800 text-white p-6 mt-10">
        <div className="container mx-auto flex justify-between items-center">
          <p className="text-sm">&copy; {new Date().getFullYear()} Siêu Bug Team.</p>
          <ul className="flex space-x-4">
            <li><a href="#" className="hover:text-gray-400">Privacy Policy</a></li>
            <li><a href="#" className="hover:text-gray-400">Terms of Service</a></li>
            <li><a href="#" className="hover:text-gray-400">Contact Us</a></li>
          </ul>
        </div>
      </footer>
    );
  };
  
  export default Footer;
  