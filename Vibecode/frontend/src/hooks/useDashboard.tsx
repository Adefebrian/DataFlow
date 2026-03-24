/**
 * Dashboard Store v3
 * - Manages pinned charts/analytics/KPIs across the app
 * - Supports reordering (drag-and-drop order saved)
 * - Deduplication by title only (not jobId+title) so custom charts with same title don't clash
 */
import { createContext, useContext, useState, useEffect, useCallback } from 'react'

export type DashItemType = 'recharts' | 'kpi' | 'chart_image' | 'chart'

export type DashItem = {
  id: string
  jobId: string
  jobName: string
  type: DashItemType
  subtype: string
  title: string
  analyticsSlice?: any
  chartConfig?: any
  image_base64?: string
  data?: any
  pinnedAt: number
}

type Store = {
  items: DashItem[]
  addItem: (item: Omit<DashItem, 'id' | 'pinnedAt'>) => void
  removeItem: (id: string) => void
  reorderItems: (newOrder: DashItem[]) => void
  hasItem: (jobId: string, title: string) => boolean
  clearAll: () => void
}

const Ctx = createContext<Store>({
  items: [], addItem: () => {}, removeItem: () => {},
  reorderItems: () => {}, hasItem: () => false, clearAll: () => {},
})

const STORAGE_KEY = 'df_dashboard_v3'

export function DashboardProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<DashItem[]>(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      // Also try v2 key for migration
      if (!raw) {
        const v2 = localStorage.getItem('df_dashboard_v2')
        return v2 ? JSON.parse(v2) : []
      }
      return JSON.parse(raw)
    } catch { return [] }
  })

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(items)) } catch {}
  }, [items])

  const addItem = useCallback((item: Omit<DashItem, 'id' | 'pinnedAt'>) => {
    setItems(prev => {
      // Deduplicate by title + jobId combination
      if (prev.some(i => i.jobId === item.jobId && i.title === item.title)) return prev
      const id = `${item.jobId}_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`
      return [{ ...item, id, pinnedAt: Date.now() }, ...prev]
    })
  }, [])

  const removeItem = useCallback((id: string) => {
    setItems(prev => prev.filter(i => i.id !== id))
  }, [])

  const reorderItems = useCallback((newOrder: DashItem[]) => {
    setItems(newOrder)
  }, [])

  const hasItem = useCallback((jobId: string, title: string) => {
    return items.some(i => i.jobId === jobId && i.title === title)
  }, [items])

  const clearAll = useCallback(() => setItems([]), [])

  return (
    <Ctx.Provider value={{ items, addItem, removeItem, reorderItems, hasItem, clearAll }}>
      {children}
    </Ctx.Provider>
  )
}

export function useDashboard() { return useContext(Ctx) }
