import React, { useState } from 'react'
import { Island, Level, LevelsData, Progress } from '../types'
import StarDisplay from '../components/StarDisplay'
import { XP_PER_LEVEL, ISLAND_ICONS } from '../config'
import { sounds } from '../sounds'

interface Props {
  progress: Progress
  levelsData: LevelsData
  onSelectLevel: (island: Island, level: Level) => void
  onMenu: () => void
  onBadges: () => void
}

const WorldMapScene: React.FC<Props> = ({ progress, levelsData, onSelectLevel, onMenu, onBadges }) => {
  const [selectedIslandId, setSelectedIslandId] = useState<number | null>(null)

  const xpInLevel = progress.player_xp % XP_PER_LEVEL
  const xpRatio   = xpInLevel / XP_PER_LEVEL

  function isLevelUnlocked(islandId: number, levelId: number): boolean {
    if (levelId === 1) return true
    return !!progress.levels_completed[`${islandId}-${levelId - 1}`]
  }

  const selectedIsland = levelsData.islands.find(i => i.id === selectedIslandId)

  return (
    <div style={{
      display: 'flex', flexDirection: 'column', height: '100%',
      background: 'linear-gradient(180deg, #1A2A4A 0%, #1A3A5A 50%, #1A4A6A 100%)',
    }}>
      {/* Top bar */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 12,
        padding: '10px 16px',
        background: 'rgba(0,0,0,0.3)',
        borderBottom: '2px solid rgba(100,100,200,0.3)',
      }}>
        <button className="btn btn-panel btn-sm" onClick={() => { sounds.click(); onMenu() }}>← Menu</button>

        {/* XP bar */}
        <div className="xp-bar-wrap" style={{ flex: 1 }}>
          <span style={{ fontFamily: 'var(--font-head)', fontSize: '0.9rem', whiteSpace: 'nowrap' }}>
            Lv {progress.player_level}
          </span>
          <div className="xp-bar-track">
            <div className="xp-bar-fill" style={{ width: `${xpRatio * 100}%` }}/>
          </div>
          <span className="xp-bar-label">{xpInLevel}/{XP_PER_LEVEL} XP</span>
        </div>

        <button className="btn btn-primary btn-sm" onClick={() => { sounds.click(); onBadges() }}>🏅 Badges</button>
      </div>

      {/* Main content */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Island grid */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
          <h2 style={{
            fontFamily: 'var(--font-head)', fontSize: '1.8rem',
            textAlign: 'center', marginBottom: 24,
            color: 'var(--primary)',
          }}>
            Kies een eiland!
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
            gap: 20,
            maxWidth: 900, margin: '0 auto',
          }}>
            {levelsData.islands.map(island => {
              const unlocked = progress.islands_unlocked.includes(island.id)
              const isSelected = selectedIslandId === island.id
              const completedCount = island.levels.filter(
                lv => progress.levels_completed[`${island.id}-${lv.id}`]
              ).length

              return (
                <button key={island.id}
                  onClick={() => {
                    if (!unlocked) return
                    sounds.click()
                    setSelectedIslandId(isSelected ? null : island.id)
                  }}
                  style={{
                    background: unlocked
                      ? `linear-gradient(135deg, ${island.color}CC, ${island.color}88)`
                      : 'rgba(80,80,100,0.5)',
                    border: isSelected ? '3px solid white' : `3px solid ${unlocked ? island.color : 'transparent'}`,
                    borderRadius: 20,
                    padding: '20px 16px',
                    cursor: unlocked ? 'pointer' : 'default',
                    textAlign: 'center',
                    transition: 'transform 0.15s, box-shadow 0.15s',
                    transform: isSelected ? 'scale(1.04)' : 'scale(1)',
                    boxShadow: isSelected ? `0 0 20px ${island.color}88` : '0 4px 12px rgba(0,0,0,0.3)',
                    animation: isSelected ? 'pulse 1.5s infinite' : 'none',
                  }}>
                  <div style={{ fontSize: '3rem', marginBottom: 8 }}>
                    {unlocked ? ISLAND_ICONS[island.id] ?? '🏝️' : '🔒'}
                  </div>
                  <div style={{
                    fontFamily: 'var(--font-head)', fontSize: '1.2rem',
                    color: unlocked ? 'white' : 'rgba(200,200,220,0.6)',
                  }}>
                    {island.name}
                  </div>
                  {unlocked && (
                    <div style={{ marginTop: 6, fontSize: '0.85rem', opacity: 0.85 }}>
                      {completedCount}/{island.levels.length} levels
                    </div>
                  )}
                </button>
              )
            })}
          </div>
        </div>

        {/* Level panel — shown when island is selected */}
        {selectedIsland && (
          <div style={{
            width: 300, flexShrink: 0,
            background: 'rgba(20,20,50,0.97)',
            borderLeft: '2px solid rgba(100,100,200,0.4)',
            display: 'flex', flexDirection: 'column',
            animation: 'slide-in-right 0.2s ease',
          }}>
            <div style={{
              padding: '16px',
              background: `linear-gradient(135deg, ${selectedIsland.color}44, transparent)`,
              borderBottom: '1px solid rgba(100,100,200,0.3)',
            }}>
              <div style={{ fontSize: '2rem', marginBottom: 4 }}>{ISLAND_ICONS[selectedIsland.id] ?? '🏝️'}</div>
              <h3 style={{ fontFamily: 'var(--font-head)', fontSize: '1.3rem', color: selectedIsland.color }}>
                {selectedIsland.name}
              </h3>
            </div>

            <div className="scrollable" style={{ flex: 1, padding: '12px' }}>
              {selectedIsland.levels.map(lv => {
                const unlocked = isLevelUnlocked(selectedIsland.id, lv.id)
                const key = `${selectedIsland.id}-${lv.id}`
                const done = progress.levels_completed[key]

                return (
                  <button key={lv.id}
                    disabled={!unlocked}
                    onClick={() => { sounds.click(); onSelectLevel(selectedIsland, lv) }}
                    style={{
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      width: '100%', padding: '12px 14px', marginBottom: 10,
                      background: unlocked ? 'rgba(32,191,107,0.15)' : 'rgba(80,80,100,0.2)',
                      border: `2px solid ${unlocked ? 'rgba(32,191,107,0.4)' : 'rgba(100,100,120,0.3)'}`,
                      borderRadius: 12, cursor: unlocked ? 'pointer' : 'default',
                      textAlign: 'left', transition: 'background 0.15s',
                    }}
                    onMouseOver={e => { if (unlocked) (e.currentTarget as HTMLElement).style.background = 'rgba(32,191,107,0.25)' }}
                    onMouseOut={e => { if (unlocked) (e.currentTarget as HTMLElement).style.background = 'rgba(32,191,107,0.15)' }}
                  >
                    <div>
                      <div style={{
                        fontFamily: 'var(--font-head)', fontSize: '1rem',
                        color: unlocked ? 'white' : 'rgba(180,180,200,0.5)',
                      }}>
                        {lv.id}. {lv.title}
                      </div>
                      <div style={{ fontSize: '0.75rem', opacity: 0.6, marginTop: 2 }}>
                        {lv.type === 'sequence' && 'Volgorde'}
                        {lv.type === 'choice'   && 'Keuze'}
                        {lv.type === 'debug'    && 'Fout zoeken'}
                        {lv.type === 'loop'     && 'Herhaling'}
                      </div>
                    </div>
                    <div>
                      {!unlocked && <span style={{ fontSize: '1.2rem' }}>🔒</span>}
                      {unlocked && done && <StarDisplay stars={done.stars} size="1rem"/>}
                      {unlocked && !done && (
                        <span style={{ fontSize: '0.75rem', color: 'var(--primary)',
                                       fontFamily: 'var(--font-head)' }}>Nieuw!</span>
                      )}
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default WorldMapScene
