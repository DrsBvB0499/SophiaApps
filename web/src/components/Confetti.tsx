import React, { useMemo } from 'react'

const COLORS = ['#F7B731','#20BF6B','#FC5C65','#74B9FF','#CC66FF','#FFB74D']

const Confetti: React.FC = () => {
  const pieces = useMemo(() =>
    Array.from({ length: 70 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      delay: Math.random() * 2,
      dur: 2.5 + Math.random() * 2,
      size: 8 + Math.random() * 10,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      rotate: Math.random() * 360,
    })), [])

  return (
    <div style={{ position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 50, overflow: 'hidden' }}>
      {pieces.map(p => (
        <div key={p.id} style={{
          position: 'absolute',
          top: '-20px',
          left: `${p.x}%`,
          width: p.size,
          height: p.size * 0.6,
          background: p.color,
          borderRadius: '2px',
          animation: `confetti-fall ${p.dur}s ${p.delay}s linear infinite`,
          transform: `rotate(${p.rotate}deg)`,
        }}/>
      ))}
    </div>
  )
}

export default Confetti
