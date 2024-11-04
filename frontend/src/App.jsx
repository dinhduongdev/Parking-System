import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar/Navbar";
import HomePage from "./pages/Home/HomePage";
import Login from "./components/Login/login";
import Register from "./components/Register/Register";
import Services from "./pages/Service/ServicePage";
import Contact from "./pages/Contact/ContactPage";
import About from "./pages/About/AboutPage";
import Account from "./pages/Account/AccountPage";
import Dashboard from "./pages/Dashboard/DashboardPage";

import Footer from "./components/Footer/Footer";
// import  { useState, useEffect } from 'react';
// import axios from 'axios';

function App() {
  //   const [data, setData] = useState([]);
  //     const [name, setName] = useState('');

  //     useEffect(() => {
  //         fetchData();
  //     }, []);

  //     const fetchData = async () => {
  //         const response = await axios.get('http://127.0.0.1:5000/api/data');
  //         setData(response.data);
  //     };

  //     const handleSubmit = async () => {
  //         await axios.post('http://127.0.0.1:5000/api/data', { name });
  //         setName('');
  //         fetchData();
  //     };
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/services" element={<Services />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/about" element={<About />} />
        <Route path="/account" element={<Account />} />
        <Route path="/dashboard/entry" element={<Dashboard />} />
      </Routes>
      <Footer />
    </Router>
    // <div>
    //         <h1>Data from MongoDB</h1>
    //         <ul>
    //             {data.map(item => (
    //                 <li key={item.id}>{item.name}</li>
    //             ))}
    //         </ul>
    //         <form onSubmit={handleSubmit}>
    //             <input
    //                 type="text"
    //                 value={name}
    //                 onChange={(e) => setName(e.target.value)}
    //                 placeholder="Enter name"
    //                 required
    //             />
    //             <button type="submit">Add Data</button>
    //         </form>
    //     </div>
  );
}

export default App;
