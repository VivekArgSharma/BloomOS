export type Garden = {
  id: string
  name: string
  location_type: string
  city?: string | null
  health_score: number
  plant_count: number
}

export type CareProfile = {
  water_interval_days: number
  light: string
  humidity: string
  fertilizer: string
  soil: string
  notes: string[]
}

export type Plant = {
  id: string
  garden_id: string
  common_name: string
  species_name: string
  source: 'catalog' | 'image'
  care_profile: CareProfile
  current_health_score: number
  recovery_mode: boolean
}

export type CatalogItem = {
  id: string
  common_name: string
  species_name: string
  difficulty: 'easy' | 'moderate' | 'advanced'
  tags: string[]
  care_profile: CareProfile
}

export type DailyTask = {
  id: string
  title: string
  description: string
  category: 'water' | 'monitor' | 'feed' | 'sunlight' | 'photo'
  completed: boolean
}

export type DailyPlan = {
  id: string
  plant_id: string
  tasks: DailyTask[]
  weather_snapshot: {
    summary: string
    temperature_c: number
    humidity: number
    rain_chance: number
  }
}

export type DailyLog = {
  id: string
  photo_url: string
  observations: string
  analysis: {
    health_score: number
    visible_issues: string[]
    soil_moisture: string
    recommended_action: string
    diary_entry: string
  }
  created_at: string
}

export type PlantDetails = {
  plant: Plant
  latest_log?: DailyLog | null
  plan?: DailyPlan | null
}

export type Weather = {
  city: string
  summary: string
  temperature_c: number
  humidity: number
  rain_chance: number
}

export type ChatResponse = {
  answer: string
  grounding: string[]
}
