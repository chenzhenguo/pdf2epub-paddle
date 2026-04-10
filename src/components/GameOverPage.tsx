import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const GameOverPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const winner = location.state?.winner || '未知';

  const handleRestartGame = () => {
    navigate('/game');
  };

  const handleBackToHome = () => {
    navigate('/');
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white">
      <div className="text-center">
        <h1 className="text-5xl font-bold mb-8 text-yellow-400 animate-pulse font-pixel">
          游戏结束
        </h1>
        <div className="mb-12">
          <div className="w-64 h-64 mx-auto bg-blue-800 rounded-lg flex items-center justify-center border-4 border-yellow-400 shadow-lg">
            <div className="text-6xl">🏆</div>
          </div>
        </div>
        <h2 className="text-3xl font-bold mb-8 text-white font-pixel">
          {winner} 获胜！
        </h2>
        <div className="flex space-x-4">
          <button
            onClick={handleRestartGame}
            className="bg-red-600 hover:bg-red-700 text-white font-bold py-4 px-8 rounded-lg shadow-lg transform hover:scale-110 transition-transform duration-200 font-pixel text-lg"
          >
            重新开始
          </button>
          <button
            onClick={handleBackToHome}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded-lg shadow-lg transform hover:scale-110 transition-transform duration-200 font-pixel text-lg"
          >
            返回主页
          </button>
        </div>
      </div>
    </div>
  );
};

export default GameOverPage;