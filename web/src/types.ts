export interface Level {
  id: number
  title: string
  type: 'sequence' | 'choice' | 'debug' | 'loop' | 'if_else' | 'variable' | 'function' | 'nested_loop'
  instruction: string
  hint?: string
  // sequence
  available_blocks?: string[]
  correct_sequence?: string[]
  // choice
  program_prefix?: string[]
  program_suffix?: string[]
  correct_block?: string
  options?: string[]
  // debug
  program?: string[]
  wrong_index?: number
  // loop
  base_block?: string
  correct_count?: number
  // if_else
  condition_text?: string
  if_options?: string[]
  else_options?: string[]
  correct_if?: string
  correct_else?: string
  // variable
  variable_name?: string
  correct_value?: number
  // function
  function_name?: string
  function_options?: string[]
  correct_function_body?: string[]
  main_options?: string[]
  correct_main?: string[]
  // nested_loop
  correct_outer?: number
  correct_inner?: number
  // animation
  character_actions?: string[]
  banana_high?: boolean
  obstacle?: 'none' | 'stone' | 'river' | 'ice_mound' | 'cactus' | 'coral' | 'asteroid' | 'lava_rock'
  max_stars: number
  star_thresholds: { '3': number; '2': number; '1': number }
  xp: number
}

export interface Island {
  id: number
  name: string
  color: string
  position: [number, number]
  unlocked: boolean
  levels: Level[]
}

export interface LevelsData {
  islands: Island[]
}

export interface LevelProgress {
  stars: number
  xp_earned: number
}

export interface Progress {
  player_name: string
  player_xp: number
  player_level: number
  levels_completed: Record<string, LevelProgress>
  badges_earned: string[]
  islands_unlocked: number[]
}

export interface LevelResult {
  island_id: number
  level_id: number
  stars: number
  xp: number
  time: number
  mistakes: number
}

export type SceneName = 'menu' | 'world_map' | 'level' | 'reward' | 'achievements'
