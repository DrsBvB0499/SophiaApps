import React, { useEffect, useState } from 'react'
import Character from '../components/Character'
import StarDisplay from '../components/StarDisplay'
import Confetti from '../components/Confetti'
import { Island, Level, LevelResult, Progress } from '../types'
import { BADGE_DEFS, XP_PER_LEVEL, ISLAND_ICONS } from '../config'
import { sounds } from '../sounds'

interface Props {
  result: LevelResult
  newBadges: string[]
  prevXp: number
  prevLevel: number
  progress: Progress
  island: Island
  level: Level
  nextLevel: Level | null
  onNext: () => void
  onMap: () => void
}

const RewardScene: React.FC<Props> = ({
  result, newBadges, prevXp, progress, island, level, nextLevel, onNext, onMap,
}) => {
  const [xpDisplay, setXpDisplay] = useState(prevXp)
  const [showLevelUp, setShowLevelUp] = useState(false)
  const [badgeIdx, setBadgeIdx]       = useState(0)

  useEffect(() => {
    sounds.win()
    const target = progress.player_xp
    const step = (target - prevXp) / 40
    let cur = prevXp
    const iv = setInterval(() => {
      cur = Math.min(target, cur + Math.abs(step) + 1)
      setXpDisplay(Math.floor(cur))
      if (cur >= target) clearInterval(iv)
    }, 30)

    const levelUpPrev = 1 + Math.floor(prevXp / XP_PER_LEVEL)
    if (progress.player_level > levelUpPrev) {
      setTimeout(() => setShowLevelUp(true), 1200)
      setTimeout(() => setShowLevelUp(false), 3500)
    }

    if (newBadges.length > 0) {
      setTimeout(() => { sounds.badge() }, 1500)
      const cycler = setInterval(() => {
        setBadgeIdx(i => {
          if (i + 1 >= newBadges.length) { clearInterval(cycler); return i }
          sounds.badge()
          return i + 1
        })
      }, 2500)
    }
    return () => clearInterval(iv)
  }, [])  // intentionally run once on mount

  const xpInLevel = xpDisplay % XP_PER_LEVEL
  const xpRatio   = xpInLevel / XP_PER_LEVEL

  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'flex-start', height: '100vh', overflowY: 'auto',
      background: 'radial-gradient(ellipse at 50% 0%, #2A3A6E 0%, #1A1A2E 80%)',
      padding: '24px 20px 32px',
      gap: 20, textAlign: 'center',
    }}>
      <Confetti/>

      <h1 style={{
        fontFamily: 'var(--font-head)', fontSize: 'clamp(2rem, 6vw, 3.5rem)',
        color: 'var(--primary)',
        textShadow: '0 4px 20px rgba(247,183,49,0.5)',
      }}>
        Geweldig! 🎉
      </h1>

      <div style={{ fontFamily: 'var(--font-head)', fontSize: '1.2rem', opacity: 0.8 }}>
        {ISLAND_ICONS[island.id]} {island.name} — {level.title}
      </div>

      {/* Stars */}
      <StarDisplay stars={result.stars} size="3rem"/>

      {/* Character dancing */}
      <Character action="dance" size={120}/>

      {/* XP gained */}
      <div style={{
        fontFamily: 'var(--font-head)', fontSize: '1.6rem', color: 'var(--secondary)',
        animation: 'pop-in 0.4s ease',
      }}>
        +{result.xp} XP
      </div>

      {/* XP bar */}
      <div style={{ width: '100%', maxWidth: 400 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem',
                      marginBottom: 6, opacity: 0.75 }}>
          <span>Level {progress.player_level}</span>
          <span>{xpInLevel}/{XP_PER_LEVEL} XP</span>
        </div>
        <div className="xp-bar-track" style={{ height: 22 }}>
          <div className="xp-bar-fill" style={{ width: `${xpRatio * 100}%` }}/>
        </div>
      </div>

      {/* Badges */}
      {newBadges.length > 0 && badgeIdx < newBadges.length && (() => {
        const def = BADGE_DEFS[newBadges[badgeIdx]]
        return def ? (
          <div style={{
            background: def.color, borderRadius: 16, padding: '14px 24px',
            display: 'flex', alignItems: 'center', gap: 12, maxWidth: 380, width: '100%',
            animation: 'slide-in-right 0.4s ease',
          }}>
            <span style={{ fontSize: '2.2rem' }}>{def.icon}</span>
            <div style={{ textAlign: 'left' }}>
              <div style={{ fontFamily: 'var(--font-head)', fontSize: '1.1rem', color: 'white' }}>
                Badge: {def.name}
              </div>
              <div style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.8)' }}>{def.desc}</div>
            </div>
          </div>
        ) : null
      })()}

      {/* Level-up */}
      {showLevelUp && (
        <div style={{
          background: 'var(--primary)', color: 'var(--text-dark)',
          borderRadius: 16, padding: '14px 28px',
          fontFamily: 'var(--font-head)', fontSize: '1.6rem',
          animation: 'pop-in 0.3s ease',
        }}>
          🎊 Level {progress.player_level} bereikt!
        </div>
      )}

      {/* Navigation */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, width: '100%', maxWidth: 360 }}>
        {nextLevel && (
          <button className="btn btn-green btn-lg" style={{ width: '100%' }}
                  onClick={() => { sounds.click(); onNext() }}>
            Volgend level →
          </button>
        )}
        <button className="btn btn-panel" style={{ width: '100%' }}
                onClick={() => { sounds.click(); onMap() }}>
          ← Terug naar kaart
        </button>
      </div>
    </div>
  )
}

export default RewardScene
