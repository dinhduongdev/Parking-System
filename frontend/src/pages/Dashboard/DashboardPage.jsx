import { useState } from "react";
import { Line } from "react-chartjs-2";
import { Link } from "react-router-dom";
import defaultAvatar from "../../../public/defaultAvatar.png";
import { Chart as ChartJS } from "chart.js/auto";

const Dashboard = () => {
  const [chartData, setChartData] = useState({
    labels: ["January", "February", "March", "April", "May", "June"],
    datasets: [
      {
        label: "Vehicle Entries",
        data: [65, 59, 80, 81, 56, 55],
        fill: false,
        backgroundColor: "rgba(75,192,192,1)",
        borderColor: "rgba(75,192,192,1)",
      },
    ],
  });

  return (
    <div className="flex p-6">
      <aside className="w-1/5 bg-blue-800 text-white shadow-md p-4">
        <div className="flex flex-col items-center mb-6">
          <img
            src={defaultAvatar}
            alt="User Avatar"
            className="w-24 h-24 rounded-full mb-2"
          />
          <h2 className="text-lg font-semibold">Administrator</h2>
        </div>
        <nav className="space-y-4">
          <Link
            to="/dashboard/entry"
            className="flex items-center p-2 hover:bg-blue-100 rounded"
          >
            Vehicle Entry
          </Link>
          <Link
            to="/dashboard/user"
            className="flex items-center p-2 hover:bg-blue-100 rounded"
          >
            User
          </Link>
          <button className="flex items-center p-2 text-red-500 hover:bg-red-100 rounded w-full">
            Logout
          </button>
        </nav>
      </aside>
      <main className="w-3/4 p-6">
        <div className="flex-1 p-6">
          <h1 className="text-2xl font-bold mb-4">Vehicle Entry Statistics</h1>
          <div className="bg-white p-6 rounded shadow-md">
            <Line data={chartData} />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
