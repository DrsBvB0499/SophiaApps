import React from 'react'

interface Props {
  action?: 'idle' | 'walk-right' | 'walk-left' | 'jump' | 'grab' | 'dance'
  flipX?: boolean
  size?: number
  style?: React.CSSProperties
}

const Character: React.FC<Props> = ({ action = 'idle', flipX = false, size = 110, style }) => {
  const animMap: Record<string, React.CSSProperties> = {
    idle:        { animation: 'bounce-idle 1.2s ease-in-out infinite' },
    dance:       { animation: 'dance 0.5s ease-in-out infinite' },
    'walk-right':{ animation: 'bounce-idle 0.4s ease-in-out infinite' },
    'walk-left': { animation: 'bounce-idle 0.4s ease-in-out infinite' },
    jump:        { animation: 'none' },
    grab:        { animation: 'none' },
  }

  const grabRightArm = action === 'grab'
  const wrapStyle: React.CSSProperties = {
    display: 'inline-block',
    transform: `scaleX(${flipX ? -1 : 1})`,
    ...animMap[action] ?? animMap.idle,
    ...style,
  }

  return (
    <div style={wrapStyle}>
      <svg width={size} height={size * 1.25} viewBox="0 0 80 100" xmlns="http://www.w3.org/2000/svg">
        {/* Tail */}
        <path d="M22 76 Q6 64 10 46 Q14 32 24 40" stroke="#5C3010" strokeWidth="5"
              fill="none" strokeLinecap="round"/>

        {/* Left arm */}
        <ellipse cx="19" cy="72" rx="7" ry="17" fill="#8B5A2B" transform="rotate(-8 19 72)"/>

        {/* Right arm — raised if grabbing */}
        <ellipse cx="61" cy={grabRightArm ? 60 : 72} rx="7" ry="17" fill="#8B5A2B"
                 transform={grabRightArm ? 'rotate(-50 61 60)' : 'rotate(8 61 72)'}
                 style={{ transition: 'all 0.3s ease' }}/>

        {/* Body */}
        <ellipse cx="40" cy="74" rx="20" ry="22" fill="#8B5A2B"/>

        {/* Shirt / belly */}
        <ellipse cx="40" cy="76" rx="13" ry="13" fill="#F7B731"/>

        {/* Legs */}
        <ellipse cx="32" cy="93" rx="9" ry="12" fill="#5C3010"/>
        <ellipse cx="48" cy="93" rx="9" ry="12" fill="#5C3010"/>

        {/* Head */}
        <circle cx="40" cy="38" r="22" fill="#8B5A2B"/>

        {/* Ears */}
        <circle cx="19" cy="38" r="9" fill="#A06830"/>
        <circle cx="61" cy="38" r="9" fill="#A06830"/>
        <circle cx="19" cy="38" r="5" fill="#C88040"/>
        <circle cx="61" cy="38" r="5" fill="#C88040"/>

        {/* Face plate */}
        <ellipse cx="40" cy="43" rx="14" ry="12" fill="#D2976E"/>

        {/* Eyes */}
        <circle cx="33" cy="34" r="5.5" fill="white"/>
        <circle cx="47" cy="34" r="5.5" fill="white"/>
        <circle cx="34" cy="34" r="3"   fill="#1A1A2E"/>
        <circle cx="48" cy="34" r="3"   fill="#1A1A2E"/>
        <circle cx="35" cy="33" r="1.2" fill="white"/>
        <circle cx="49" cy="33" r="1.2" fill="white"/>

        {/* Nose */}
        <ellipse cx="40" cy="42" rx="3.5" ry="2.5" fill="#5C3010"/>

        {/* Mouth */}
        <path d={action === 'dance' ? 'M33 48 Q40 56 47 48' : 'M33 48 Q40 54 47 48'}
              stroke="#5C3010" strokeWidth="2.5" fill="none" strokeLinecap="round"/>
      </svg>
    </div>
  )
}

export default Character
