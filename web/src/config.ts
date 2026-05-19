export const COLORS = {
  bg:          '#1A1A2E',
  primary:     '#F7B731',
  secondary:   '#20BF6B',
  accent:      '#FC5C65',
  textLight:   '#FFFFFF',
  textDark:    '#2D3436',
  panelBg:     'rgba(40,40,80,0.95)',
  panelBorder: 'rgba(100,100,180,0.6)',
  locked:      '#636e72',
}

export const BLOCK_COLORS = [
  '#FF6B6B', // red
  '#FFB74D', // orange
  '#66CC66', // green
  '#4DA6FF', // blue
  '#CC66FF', // purple
]

export const XP_PER_LEVEL = 200
export const MAX_PLAYER_LEVEL = 10

export const ISLAND_ICONS: Record<number, string> = {
  1: '🍌',
  2: '🥥',
  3: '🐟',
}

export const BADGE_DEFS: Record<string, { name: string; desc: string; icon: string; color: string }> = {
  first_win:   { name: 'Eerste stap!',      desc: 'Je eerste level gehaald',          icon: '⭐', color: '#20BF6B' },
  no_mistakes: { name: 'Perfect!',           desc: 'Geen enkele fout gemaakt',          icon: '✨', color: '#F7B731' },
  island_1:    { name: 'Bananeneiland held', desc: 'Alle levels van eiland 1 voltooid', icon: '🍌', color: '#FFB74D' },
  island_2:    { name: 'Jungleheld',         desc: 'Alle levels van eiland 2 voltooid', icon: '🥥', color: '#66CC66' },
  island_3:    { name: 'IJsheld',            desc: 'Alle levels van eiland 3 voltooid', icon: '🐟', color: '#4DA6FF' },
  streak_3:    { name: 'Op dreef!',          desc: '3 levels op rij zonder fouten',     icon: '🔥', color: '#FC5C65' },
  explorer:    { name: 'Ontdekker',          desc: 'Eiland 2 ontgrendeld',              icon: '🗺️', color: '#4DA6FF' },
  bug_finder:  { name: 'Bug vinder',         desc: '5 fout-levels voltooid',            icon: '🐛', color: '#CC66FF' },
  loop_master: { name: 'Lus-meester',        desc: 'Eerste herhaling-level voltooid',   icon: '🔄', color: '#FFB74D' },
  collector:   { name: 'Verzamelaar',        desc: '5 badges behaald',                  icon: '🏅', color: '#F7B731' },
  champion:    { name: 'Kampioen',           desc: 'Alle eilanden voltooid',            icon: '🏆', color: '#F7B731' },
  speed_star:  { name: 'Razendsnel',         desc: 'Level in minder dan 30 seconden',   icon: '⚡', color: '#FC5C65' },
}
