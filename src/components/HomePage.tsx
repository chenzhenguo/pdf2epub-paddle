import React from 'react';
import { useNavigate } from 'react-router-dom';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const handleStartGame = () => {
    navigate('/game');
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white">
      <div className="text-center">
        <h1 className="text-5xl font-bold mb-8 text-yellow-400 animate-pulse font-pixel">
          像素风机甲对战
        </h1>
        <div className="mb-12">
          <div className="w-64 h-64 mx-auto bg-blue-800 rounded-lg flex items-center justify-center border-4 border-yellow-400 shadow-lg">
            <div className="text-6xl">🤖</div>
          </div>
        </div>
        <button
          onClick={handleStartGame}
          className="bg-red-600 hover:bg-red-700 text-white font-bold py-4 px-8 rounded-lg shadow-lg transform hover:scale-110 transition-transform duration-200 font-pixel text-lg"
        >
          开始游戏
        </button>
        <div className="mt-12 bg-gray-800 p-6 rounded-lg border-2 border-blue-500 max-w-md mx-auto">
          <h2 className="text-xl font-bold mb-4 text-blue-400 font-pixel">游戏规则</h2>
          <ul className="text-left space-y-2 font-pixel text-sm">
            <li>🎮 玩家1：使用WASD键移动，J键攻击，K键防御</li>
            <li>🎮 玩家2：使用方向键移动，1键攻击，2键防御</li>
            <li>⚔️ 攻击会对敌方造成伤害</li>
            <li>🛡️ 防御会减少受到的伤害</li>
            <li>🏆 先将对方血量降至0的一方获胜</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default HomePage;