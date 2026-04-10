import React, { useRef, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface Mecha {
  x: number;
  y: number;
  width: number;
  height: number;
  health: number;
  maxHealth: number;
  speed: number;
  attack: number;
  defense: number;
  state: 'idle' | 'moving' | 'attacking' | 'defending' | 'hit' | 'dead';
  direction: 'left' | 'right';
  attackCooldown: number;
  defenseCooldown: number;
  defenseDuration: number;
  isDefending: boolean;
}

const GamePage: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const navigate = useNavigate();
  const [mecha1, setMecha1] = useState<Mecha>({
    x: 100,
    y: 300,
    width: 50,
    height: 80,
    health: 100,
    maxHealth: 100,
    speed: 5,
    attack: 10,
    defense: 5,
    state: 'idle',
    direction: 'right',
    attackCooldown: 0,
    defenseCooldown: 0,
    defenseDuration: 0,
    isDefending: false
  });
  const [mecha2, setMecha2] = useState<Mecha>({
    x: 700,
    y: 300,
    width: 50,
    height: 80,
    health: 100,
    maxHealth: 100,
    speed: 5,
    attack: 10,
    defense: 5,
    state: 'idle',
    direction: 'left',
    attackCooldown: 0,
    defenseCooldown: 0,
    defenseDuration: 0,
    isDefending: false
  });
  const [keys, setKeys] = useState<Record<string, boolean>>({});

  // 处理键盘输入
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      setKeys(prev => ({ ...prev, [e.key.toLowerCase()]: true }));
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      setKeys(prev => ({ ...prev, [e.key.toLowerCase()]: false }));
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  // 游戏主循环
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const gameLoop = () => {
      // 更新游戏状态
      updateGame();
      // 渲染游戏
      renderGame(ctx);
      // 检查游戏结束
      checkGameOver();
      // 继续循环
      requestAnimationFrame(gameLoop);
    };

    gameLoop();
  }, [keys, mecha1, mecha2]);

  // 更新游戏状态
  const updateGame = () => {
    // 更新机甲1
    let newMecha1 = { ...mecha1 };
    let newMecha2 = { ...mecha2 };

    // 处理机甲1的移动
    if (keys['w'] && newMecha1.y > 0) {
      newMecha1.y -= newMecha1.speed;
      newMecha1.state = 'moving';
    } else if (keys['s'] && newMecha1.y < 520) {
      newMecha1.y += newMecha1.speed;
      newMecha1.state = 'moving';
    } else if (keys['a'] && newMecha1.x > 0) {
      newMecha1.x -= newMecha1.speed;
      newMecha1.state = 'moving';
      newMecha1.direction = 'left';
    } else if (keys['d'] && newMecha1.x < 450) {
      newMecha1.x += newMecha1.speed;
      newMecha1.state = 'moving';
      newMecha1.direction = 'right';
    } else {
      newMecha1.state = 'idle';
    }

    // 处理机甲1的攻击
    if (keys['j'] && newMecha1.attackCooldown === 0) {
      newMecha1.state = 'attacking';
      newMecha1.attackCooldown = 30;
      // 检测攻击是否命中
      if (checkCollision(newMecha1, newMecha2)) {
        const damage = newMecha2.isDefending ? Math.max(0, newMecha1.attack - newMecha2.defense) : newMecha1.attack;
        newMecha2.health = Math.max(0, newMecha2.health - damage);
        newMecha2.state = 'hit';
      }
    }

    // 处理机甲1的防御
    if (keys['k'] && newMecha1.defenseCooldown === 0) {
      newMecha1.state = 'defending';
      newMecha1.isDefending = true;
      newMecha1.defenseDuration = 20;
      newMecha1.defenseCooldown = 60;
    }

    // 处理机甲2的移动
    if (keys['arrowup'] && newMecha2.y > 0) {
      newMecha2.y -= newMecha2.speed;
      newMecha2.state = 'moving';
    } else if (keys['arrowdown'] && newMecha2.y < 520) {
      newMecha2.y += newMecha2.speed;
      newMecha2.state = 'moving';
    } else if (keys['arrowleft'] && newMecha2.x > 500) {
      newMecha2.x -= newMecha2.speed;
      newMecha2.state = 'moving';
      newMecha2.direction = 'left';
    } else if (keys['arrowright'] && newMecha2.x < 850) {
      newMecha2.x += newMecha2.speed;
      newMecha2.state = 'moving';
      newMecha2.direction = 'right';
    } else {
      newMecha2.state = 'idle';
    }

    // 处理机甲2的攻击
    if (keys['1'] && newMecha2.attackCooldown === 0) {
      newMecha2.state = 'attacking';
      newMecha2.attackCooldown = 30;
      // 检测攻击是否命中
      if (checkCollision(newMecha2, newMecha1)) {
        const damage = newMecha1.isDefending ? Math.max(0, newMecha2.attack - newMecha1.defense) : newMecha2.attack;
        newMecha1.health = Math.max(0, newMecha1.health - damage);
        newMecha1.state = 'hit';
      }
    }

    // 处理机甲2的防御
    if (keys['2'] && newMecha2.defenseCooldown === 0) {
      newMecha2.state = 'defending';
      newMecha2.isDefending = true;
      newMecha2.defenseDuration = 20;
      newMecha2.defenseCooldown = 60;
    }

    // 更新冷却时间
    if (newMecha1.attackCooldown > 0) newMecha1.attackCooldown--;
    if (newMecha1.defenseCooldown > 0) newMecha1.defenseCooldown--;
    if (newMecha1.defenseDuration > 0) {
      newMecha1.defenseDuration--;
    } else {
      newMecha1.isDefending = false;
    }

    if (newMecha2.attackCooldown > 0) newMecha2.attackCooldown--;
    if (newMecha2.defenseCooldown > 0) newMecha2.defenseCooldown--;
    if (newMecha2.defenseDuration > 0) {
      newMecha2.defenseDuration--;
    } else {
      newMecha2.isDefending = false;
    }

    // 检查是否死亡
    if (newMecha1.health <= 0) newMecha1.state = 'dead';
    if (newMecha2.health <= 0) newMecha2.state = 'dead';

    setMecha1(newMecha1);
    setMecha2(newMecha2);
  };

  // 检查碰撞
  const checkCollision = (attacker: Mecha, defender: Mecha) => {
    return (
      attacker.x < defender.x + defender.width &&
      attacker.x + attacker.width > defender.x &&
      attacker.y < defender.y + defender.height &&
      attacker.y + attacker.height > defender.y
    );
  };

  // 渲染游戏
  const renderGame = (ctx: CanvasRenderingContext2D) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // 清空画布
    ctx.fillStyle = '#1a237e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 绘制地面
    ctx.fillStyle = '#333';
    ctx.fillRect(0, 500, canvas.width, 100);

    // 绘制机甲1
    drawMecha(ctx, mecha1, '#4caf50');

    // 绘制机甲2
    drawMecha(ctx, mecha2, '#d32f2f');
  };

  // 绘制机甲
  const drawMecha = (ctx: CanvasRenderingContext2D, mecha: Mecha, color: string) => {
    // 绘制身体
    ctx.fillStyle = color;
    ctx.fillRect(mecha.x, mecha.y, mecha.width, mecha.height);

    // 绘制头部
    ctx.fillStyle = '#ffeb3b';
    ctx.fillRect(mecha.x + 15, mecha.y - 20, 20, 20);

    // 绘制眼睛
    ctx.fillStyle = '#000';
    ctx.fillRect(mecha.x + 20, mecha.y - 15, 5, 5);
    ctx.fillRect(mecha.x + 25, mecha.y - 15, 5, 5);

    // 绘制武器
    if (mecha.direction === 'right') {
      ctx.fillStyle = '#9e9e9e';
      ctx.fillRect(mecha.x + mecha.width, mecha.y + 20, 20, 10);
    } else {
      ctx.fillStyle = '#9e9e9e';
      ctx.fillRect(mecha.x - 20, mecha.y + 20, 20, 10);
    }

    // 绘制防御护盾
    if (mecha.isDefending) {
      ctx.strokeStyle = '#2196f3';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(mecha.x + mecha.width / 2, mecha.y + mecha.height / 2, mecha.width / 2 + 10, 0, Math.PI * 2);
      ctx.stroke();
    }
  };

  // 检查游戏结束
  const checkGameOver = () => {
    if (mecha1.health <= 0) {
      navigate('/game-over', { state: { winner: '玩家2' } });
    } else if (mecha2.health <= 0) {
      navigate('/game-over', { state: { winner: '玩家1' } });
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white">
      <div className="text-center mb-4">
        <h1 className="text-3xl font-bold text-yellow-400 font-pixel">像素风机甲对战</h1>
      </div>
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={900}
          height={600}
          className="border-4 border-yellow-400 bg-blue-900"
        />
        {/* 血量显示 */}
        <div className="absolute top-2 left-2 bg-black bg-opacity-70 p-2 rounded">
          <div className="text-sm font-pixel mb-1">玩家1</div>
          <div className="w-100 h-4 bg-gray-700 rounded">
            <div
              className="h-full bg-green-500 rounded"
              style={{ width: `${(mecha1.health / mecha1.maxHealth) * 100}%` }}
            />
          </div>
        </div>
        <div className="absolute top-2 right-2 bg-black bg-opacity-70 p-2 rounded">
          <div className="text-sm font-pixel mb-1">玩家2</div>
          <div className="w-100 h-4 bg-gray-700 rounded">
            <div
              className="h-full bg-red-500 rounded"
              style={{ width: `${(mecha2.health / mecha2.maxHealth) * 100}%` }}
            />
          </div>
        </div>
      </div>
      <div className="mt-8 grid grid-cols-2 gap-8 max-w-2xl">
        <div className="bg-gray-800 p-4 rounded-lg border-2 border-green-500">
          <h2 className="text-lg font-bold mb-2 text-green-400 font-pixel">玩家1控制</h2>
          <ul className="text-left space-y-1 font-pixel text-sm">
            <li>WASD - 移动</li>
            <li>J - 攻击</li>
            <li>K - 防御</li>
          </ul>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg border-2 border-red-500">
          <h2 className="text-lg font-bold mb-2 text-red-400 font-pixel">玩家2控制</h2>
          <ul className="text-left space-y-1 font-pixel text-sm">
            <li>方向键 - 移动</li>
            <li>1 - 攻击</li>
            <li>2 - 防御</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default GamePage;