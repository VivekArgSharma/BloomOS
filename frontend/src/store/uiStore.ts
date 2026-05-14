import { create } from 'zustand'

type UIState = {
  selectedGardenId: string | null
  setSelectedGardenId: (gardenId: string | null) => void
}

export const useUIStore = create<UIState>((set) => ({
  selectedGardenId: null,
  setSelectedGardenId: (selectedGardenId) => set({ selectedGardenId }),
}))
