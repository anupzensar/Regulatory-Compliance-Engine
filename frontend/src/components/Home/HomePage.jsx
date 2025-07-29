import React, { useState } from 'react';
import axios from "axios";
import {
  ShieldCheck,
  RotateCcw,
  Repeat,
  Banknote,
  PlayCircle,
  Maximize2,
} from 'lucide-react';

const testOptions = [
  { label: 'Session Reminder', icon: <ShieldCheck className="w-5 h-5 text-green-400" /> },
  { label: 'Playcheck Regulation – limited to the base game', icon: <RotateCcw className="w-5 h-5 text-blue-400" /> },
  { label: 'Multiple Spin Test – limited to the base game', icon: <Repeat className="w-5 h-5 text-blue-400" /> },
  { label: 'Banking', icon: <Banknote className="w-5 h-5 text-green-400" /> },
  { label: 'Practice Play', icon: <PlayCircle className="w-5 h-5 text-blue-400" /> },
  { label: 'Max Bet Limit Testing', icon: <Maximize2 className="w-5 h-5 text-green-400" /> },
];

const HomePage = () => {
  const [gameUrl, setGameUrl] = useState("");
  const [testType, setTestType] = useState(testOptions[0].label);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      console.log("Game URL:", gameUrl);
      console.log("Test Type:", testType);

      await axios.post("http://localhost:7000/run-test", {
        gameUrl,
        testType,
      });
      
      console.log("Test submitted successfully");

      alert("Test submitted! Check backend console.");
    } catch {
      alert("Error submitting test"); 
      console.log("Error during test submission");
    }
  };

  return (
    <div className="fixed inset-0 overflow-hidden w-screen h-screen bg-gray-900 text-white flex flex-col items-center justify-center px-4">
      {/* Hero Section */}
      <section className="text-center mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-green-400 mb-2">
          Automated Compliance Test.
        </h1>
        <p className="text-gray-300 text-base md:text-lg">
          A smart platform for automated regulatory compliance testing.
        </p>
      </section>

      {/* Form Section */}
      <form onSubmit={handleSubmit} className="w-full max-w-lg bg-gray-800 rounded-2xl shadow-lg p-6">
        {/* Game URL */}
        <div className="mb-4">
          <label htmlFor="gameUrl" className="block mb-1 text-sm font-medium text-blue-300">
            Game URL
          </label>
          <input
            id="gameUrl"
            type="text"
            placeholder="Enter game URL"
            className="w-full px-4 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={gameUrl}
            onChange={e => setGameUrl(e.target.value)}
            required
          />
        </div>

        {/* Dropdown */}
        <div className="mb-4">
          <label htmlFor="testType" className="block mb-1 text-sm font-medium text-blue-300">
            Select Test Type
          </label>
          <select
            id="testType"
            className="w-full px-4 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500"
            value={testType}
            onChange={e => setTestType(e.target.value)}
          >
            {testOptions.map((opt, idx) => (
              <option key={idx} value={opt.label}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Submit Button */}
        <div className="text-center mt-4">
          <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-xl font-semibold shadow-md transition-all duration-300">
            Run Compliance Test
          </button>
        </div>
      </form>
    </div>
  );
};

export default HomePage;
