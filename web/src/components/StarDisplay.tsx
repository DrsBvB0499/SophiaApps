import React from 'react'

interface Props { stars: number; max?: number; size?: string }

const StarDisplay: React.FC<Props> = ({ stars, max = 3, size = '1.8rem' }) => (
  <span style={{ display: 'inline-flex', gap: '4px' }}>
    {Array.from({ length: max }, (_, i) => (
      <span key={i} className={`star ${i < stars ? 'filled' : 'empty'}`}
            style={{ fontSize: size }}>★</span>
    ))}
  </span>
)

export default StarDisplay
