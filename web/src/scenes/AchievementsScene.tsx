import React from 'react'
import { Progress } from '../types'
import { BADGE_DEFS } from '../config'
import { sounds } from '../sounds'

interface Props { progress: Progress; onBack: () => void }

const AchievementsScene: React.FC<Props> = ({ progress, onBack }) => {
  const earned = new Set(progress.badges_earned)
  const total  = Object.keys(BADGE_DEFS).length

  return (
    <div style={{
      display: 'flex', flexDirection: 'column', height: '100vh',
      background: 'linear-gradient(180deg, #1A1A2E 0%, #1A2040 100%)',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px',
        background: 'rgba(0,0,0,0.4)', borderBottom: '2px solid rgba(100,100,200,0.3)',
        flexShrink: 0,
      }}>
        <button className="btn btn-panel btn-sm" onClick={() => { sounds.click(); onBack() }}>← Terug</button>
        <div style={{ flex: 1 }}>
          <h2 style={{ fontFamily: 'var(--font-head)', fontSize: '1.5rem', color: 'var(--primary)' }}>
            Mijn Badges
          </h2>
        </div>
        <span style={{ fontFamily: 'var(--font-head)', color: 'var(--secondary)', fontSize: '1rem' }}>
          {earned.size}/{total}
        </span>
      </div>

      {/* Badge grid */}
      <div className="scrollable" style={{
        flex: 1, padding: '20px 16px',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
        gap: 16,
        alignContent: 'start',
      }}>
        {Object.entries(BADGE_DEFS).map(([id, def]) => {
          const unlocked = earned.has(id)
          return (
            <div key={id} style={{
              background: unlocked ? def.color : 'rgba(60,60,90,0.6)',
              borderRadius: 16,
              padding: '16px 10px',
              textAlign: 'center',
              transition: 'transform 0.15s',
              cursor: 'default',
              boxShadow: unlocked ? `0 4px 16px ${def.color}66` : 'none',
              animation: unlocked ? 'none' : 'none',
              filter: unlocked ? 'none' : 'grayscale(0.8)',
            }}
              onMouseOver={e => { if (unlocked) (e.currentTarget as HTMLElement).style.transform = 'scale(1.05)' }}
              onMouseOut={e => { (e.currentTarget as HTMLElement).style.transform = 'scale(1)' }}
            >
              <div style={{ fontSize: '2.4rem', marginBottom: 8, filter: unlocked ? 'none' : 'grayscale(1)' }}>
                {unlocked ? def.icon : '❓'}
              </div>
              <div style={{
                fontFamily: 'var(--font-head)', fontSize: '0.9rem',
                color: unlocked ? 'white' : 'rgba(180,180,200,0.5)',
              }}>
                {unlocked ? def.name : '???'}
              </div>
              {unlocked && (
                <div style={{ fontSize: '0.72rem', color: 'rgba(255,255,255,0.75)', marginTop: 4 }}>
                  {def.desc}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default AchievementsScene
